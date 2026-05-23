# ContractLens Backend — Implementation Plan

> **For Hermes:** Use subagent-driven-development skill to implement this plan task-by-task.

**Goal:** Replace the fake frontend upload flow with a real backend that receives contract files, sends them to an AI agent for analysis, generates HTML reports, and emails results to users.

**Architecture:** FastAPI server receives file uploads from the frontend, extracts text via existing `extract.py`, sends the contract text + analysis prompt to DeepSeek API (OpenAI-compatible), parses the structured JSON response, generates an HTML report via existing `report.py`, emails it via existing `emailer.py`, and stores the scan record in Supabase. Single synchronous request — user waits ~30-60 seconds and gets results.

**Tech Stack:** FastAPI, python-multipart (file uploads), httpx (async HTTP to DeepSeek API), Supabase Python client, existing `src/` modules (extract, report, emailer, security, config).

---

## Architecture Diagram

```
┌──────────────┐     POST /api/upload      ┌──────────────────┐
│  Frontend     │ ──────────────────────────→│  FastAPI Server   │
│  (dashboard)  │    file + auth token       │  (new: server.py) │
└──────────────┘ ←──────────────────────────└────────┬─────────┘
               │    JSON {report_url, risk}           │
               │                                      │
                                          ┌───────────┴──────────┐
                                          │  1. Validate auth     │
                                          │  2. Check scan quota  │
                                          │  3. Validate file     │
                                          │  4. Extract text      │
                                          │  5. Sanitize text     │
                                          └───────────┬──────────┘
                                                      │
                                          ┌───────────┴──────────┐
                                          │  6. Call DeepSeek API │
                                          │     System: prompt.md │
                                          │     User: contract    │
                                          └───────────┬──────────┘
                                                      │ JSON
                                          ┌───────────┴──────────┐
                                          │  7. Parse + validate  │
                                          │  8. Generate HTML     │
                                          │  9. Email report      │
                                          │ 10. Save to Supabase  │
                                          └───────────┬──────────┘
                                                      │
                                              Return to frontend
```

---

## How the AI Agent Call Works

This is the core of the system. Instead of Hermes cron, we call the LLM directly:

```
POST https://api.deepseek.com/v1/chat/completions
{
  "model": "deepseek-chat",
  "messages": [
    {
      "role": "system",
      "content": "<contents of prompts/contract_analysis.md>"
    },
    {
      "role": "user", 
      "content": "## CONTRACT TEXT TO ANALYZE\n\n<extracted text>\n\n---\n\nNow analyze the contract above according to the framework. Output ONLY valid JSON."
    }
  ],
  "temperature": 0.3,
  "response_format": { "type": "json_object" }
}
```

The `prompts/contract_analysis.md` file defines the agent's "soul" — its personality, analysis framework, output schema, and instructions. The LLM returns structured JSON with all 6 danger zones, risk levels, summaries, clause quotes, and recommendations.

---

## Tasks

### Task 1: Install dependencies

**Objective:** Add FastAPI and related packages

**Files:**
- Modify: `requirements.txt`

**Step 1: Add new dependencies**

```txt
# requirements.txt additions
fastapi>=0.110.0
uvicorn[standard]>=0.29.0
python-multipart>=0.0.9
httpx>=0.27.0
supabase>=2.3.0
```

**Step 2: Install**

```bash
cd /Users/justasza/contractlens
pip install fastapi uvicorn[standard] python-multipart httpx supabase
```

**Step 3: Commit**

```bash
git add requirements.txt
git commit -m "deps: add FastAPI, httpx, supabase for backend server"
```

---

### Task 2: Create model-agnostic LLM client module

**Objective:** Build a reusable LLM client that works with any OpenAI-compatible API (DeepSeek, OpenAI, Anthropic via proxy, Groq, etc.) — not just DeepSeek

**Files:**
- Create: `src/llm_client.py`
- Use: `src/config.py` (already has `LLM_PROVIDER`, `LLM_MODEL`)
- Use: `prompts/contract_analysis.md` (already exists)

**Step 1: Write the module — model-agnostic design**

```python
"""Model-agnostic LLM client for contract analysis.

Works with any OpenAI-compatible API (DeepSeek, OpenAI, Groq,
Anthropic via proxy, etc.). Configure via environment variables:
  LLM_BASE_URL — API base URL (default: https://api.deepseek.com/v1)
  LLM_API_KEY  — API key
  LLM_MODEL    — model name (default: deepseek-chat)

Uses prompts/contract_analysis.md as the system prompt.
Enforces JSON output via response_format where supported,
falls back to prompt-level enforcement for providers that don't support it.
"""

from __future__ import annotations

import json
import os
from typing import Optional

import httpx

from .config import LLM_MODEL
from .analyze import load_prompt


# ── Configuration (env-driven, no hardcoded provider) ──────────────────────

LLM_BASE_URL = os.getenv(
    "LLM_BASE_URL",
    "https://api.deepseek.com/v1",
)
LLM_API_KEY = os.getenv(
    "LLM_API_KEY",
    os.getenv("DEEPSEEK_API_KEY", os.getenv("OPENAI_API_KEY", "")),
)
LLM_MODEL_NAME = os.getenv("LLM_MODEL", LLM_MODEL)
LLM_TIMEOUT = int(os.getenv("LLM_TIMEOUT", "120"))  # seconds
LLM_MAX_TOKENS = int(os.getenv("LLM_MAX_TOKENS", "4096"))
LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.3"))

# Providers that support native JSON mode via response_format
_JSON_MODE_PROVIDERS = {"deepseek", "openai", "groq", "together", "fireworks"}


def _supports_json_mode() -> bool:
    """Check if the current provider supports response_format json_object."""
    base = LLM_BASE_URL.lower()
    return any(p in base for p in _JSON_MODE_PROVIDERS)


async def analyze_contract(contract_text: str) -> dict:
    """Send contract text to the configured LLM for analysis.

    Provider-agnostic: works with any OpenAI-compatible chat completions API.
    Configure via LLM_BASE_URL, LLM_API_KEY, LLM_MODEL env vars.

    Args:
        contract_text: The extracted and sanitized contract text.

    Returns:
        Parsed analysis dict with 6 danger zones.

    Raises:
        ValueError: If API key is not configured.
        RuntimeError: If the API call fails.
    """
    if not LLM_API_KEY:
        raise ValueError(
            "LLM_API_KEY not configured. Set it in .env or environment."
        )

    system_prompt = load_prompt()
    user_message = (
        "## CONTRACT TEXT TO ANALYZE\n\n"
        f"{contract_text}\n\n"
        "---\n\n"
        "Now analyze the contract above according to the framework. "
        "Output ONLY valid JSON."
    )

    payload = {
        "model": LLM_MODEL_NAME,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ],
        "temperature": LLM_TEMPERATURE,
        "max_tokens": LLM_MAX_TOKENS,
    }

    # Use native JSON mode if supported, otherwise rely on prompt
    if _supports_json_mode():
        payload["response_format"] = {"type": "json_object"}

    print(f"🤖 Calling {LLM_MODEL_NAME} via {LLM_BASE_URL}...")

    async with httpx.AsyncClient(timeout=LLM_TIMEOUT) as client:
        response = await client.post(
            f"{LLM_BASE_URL}/chat/completions",
            headers={
                "Authorization": f"Bearer {LLM_API_KEY}",
                "Content-Type": "application/json",
            },
            json=payload,
        )
        response.raise_for_status()

    data = response.json()
    content = data["choices"][0]["message"]["content"]

    # Parse JSON — handle markdown code fences gracefully
    return _parse_llm_json(content)


def _parse_llm_json(raw: str) -> dict:
    """Parse LLM response, handling markdown code fences."""
    text = raw.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[-1] if "\n" in text else text[3:]
        if text.endswith("```"):
            text = text[:-3]
    text = text.strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        import re
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            return json.loads(match.group())
        raise ValueError(
            f"Failed to parse LLM response as JSON. "
            f"Response preview: {text[:300]}..."
        )
```

**Provider switching examples:**

```bash
# DeepSeek (default)
export LLM_BASE_URL="https://api.deepseek.com/v1"
export LLM_API_KEY="sk-your-deepseek-key"
export LLM_MODEL="deepseek-chat"

# OpenAI
export LLM_BASE_URL="https://api.openai.com/v1"
export LLM_API_KEY="sk-your-openai-key"
export LLM_MODEL="gpt-4o"

# Groq (fast/cheap)
export LLM_BASE_URL="https://api.groq.com/openai/v1"
export LLM_API_KEY="gsk_your-groq-key"
export LLM_MODEL="llama-3.1-70b-versatile"

# Anthropic via OpenRouter proxy
export LLM_BASE_URL="https://openrouter.ai/api/v1"
export LLM_API_KEY="sk-or-v1-your-key"
export LLM_MODEL="anthropic/claude-sonnet-4"

# Any self-hosted OpenAI-compatible endpoint (vLLM, Ollama, etc.)
export LLM_BASE_URL="http://localhost:8000/v1"
export LLM_API_KEY="not-needed"
export LLM_MODEL="meta-llama/Meta-Llama-3.1-70B-Instruct"
```

**Step 2: Add a quick smoke test**

```bash
python -c "
import asyncio
from src.llm_client import analyze_contract
# This will fail without API key, but proves the module loads
print('Module loaded successfully')
"
```

Expected: `Module loaded successfully`

**Step 3: Commit**

```bash
git add src/llm_client.py
git commit -m "feat: add DeepSeek LLM client for contract analysis"
```

---

### Task 3: Create the FastAPI server

**Objective:** Create the web server that ties everything together — upload endpoint, auth check, full pipeline

**Files:**
- Create: `src/server.py`

```python
"""ContractLens API server.

Single endpoint: POST /api/upload
Receives a contract file, runs the full analysis pipeline,
generates an HTML report, emails it, and returns the result.
"""

from __future__ import annotations

import os
import traceback
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .security import validate_file, sanitize_text, file_hash
from .extract import extract_text, get_contract_metadata
from .report import generate_html_report, save_report
from .emailer import send_report_email
from .analyze import validate_analysis
from .llm_client import analyze_contract
from .config import OUTPUT_DIR, UPLOAD_DIR, MAX_CONTRACT_CHARS


app = FastAPI(
    title="ContractLens API",
    description="AI-powered contract analysis for freelancers",
    version="0.2.0",
)

# CORS — allow frontend to call the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten in production
    allow_methods=["POST", "OPTIONS"],
    allow_headers=["*"],
)


@app.post("/api/upload")
async def upload_contract(
    file: UploadFile = File(...),
    email: str = Form(...),
):
    """Upload a contract for analysis.

    Full pipeline: validate → extract → sanitize →
    LLM analysis → HTML report → email delivery.

    Returns JSON with the analysis result and report URL.
    """
    # 1. Validate file extension
    allowed = {".pdf", ".docx", ".txt", ".md", ".text"}
    suffix = Path(file.filename or "unknown").suffix.lower()
    if suffix not in allowed:
        raise HTTPException(
            400,
            f"Unsupported file type: {suffix}. "
            f"Accepted: {', '.join(allowed)}",
        )

    # 2. Save uploaded file temporarily
    UPLOAD_DIR.mkdir(exist_ok=True)
    tmp_path = UPLOAD_DIR / f"{os.urandom(8).hex()}_{file.filename}"
    content = await file.read()

    if len(content) == 0:
        raise HTTPException(400, "File is empty")

    if len(content) > 20 * 1024 * 1024:  # 20 MB
        raise HTTPException(400, "File too large (max 20 MB)")

    tmp_path.write_bytes(content)

    try:
        return await _process_upload(tmp_path, email, file.filename)
    except ValueError as e:
        raise HTTPException(400, str(e))
    except RuntimeError as e:
        raise HTTPException(500, str(e))
    except Exception:
        traceback.print_exc()
        raise HTTPException(500, "Internal server error")
    finally:
        # Clean up uploaded file
        try:
            tmp_path.unlink()
        except OSError:
            pass


async def _process_upload(
    filepath: Path, email: str, original_filename: str
) -> dict:
    """Run the full pipeline on an uploaded file."""
    # 1. Validate (magic bytes, size, symlink check)
    valid, err = validate_file(filepath)
    if not valid:
        raise ValueError(f"Security check failed: {err}")

    # 2. Extract text
    raw_text = extract_text(filepath)

    # 3. Sanitize
    text = sanitize_text(raw_text)

    # 4. Truncate if needed
    if len(text) > MAX_CONTRACT_CHARS:
        text = text[:MAX_CONTRACT_CHARS]

    # 5. Get metadata
    metadata = get_contract_metadata(text)

    # 6. LLM analysis (the core step)
    analysis = await analyze_contract(text)

    # 7. Validate analysis completeness
    warnings = validate_analysis(analysis)
    if warnings:
        # Log but don't fail — partial analysis is better than nothing
        print(f"Analysis warnings: {warnings}")

    # 8. Generate HTML report
    html = generate_html_report(analysis, metadata)
    report_path = save_report(html, OUTPUT_DIR)
    print(f"Report saved: {report_path}")

    # 9. Email delivery
    try:
        send_report_email(email, html, metadata)
        emailed = True
    except Exception as e:
        print(f"Email failed: {e}")
        emailed = False

    # 10. Compute overall risk
    from .report import _compute_overall_risk
    overall_risk = _compute_overall_risk(analysis)

    return {
        "success": True,
        "risk": overall_risk,
        "zones": {
            zone: {
                "risk": data.get("risk", "unknown"),
                "summary": data.get("summary", "")[:200],
            }
            for zone, data in analysis.items()
            if isinstance(data, dict)
        },
        "report_url": str(report_path),
        "recommendations": analysis.get("recommendations", []),
        "emailed": emailed,
        "metadata": {
            "title": metadata.get("title", ""),
            "page_estimate": metadata.get("page_estimate", 1),
            "char_count": len(text),
        },
    }


@app.get("/api/health")
async def health():
    """Health check endpoint."""
    return {"status": "ok", "version": "0.2.0"}
```

**Step 2: Verify server starts**

```bash
cd /Users/justasza/contractlens
python -m uvicorn src.server:app --host 127.0.0.1 --port 8123 &
sleep 3
curl http://127.0.0.1:8123/api/health
kill %1
```

Expected: `{"status":"ok","version":"0.2.0"}`

**Step 3: Commit**

```bash
git add src/server.py
git commit -m "feat: add FastAPI server with /api/upload endpoint"
```

---

### Task 4: Add Supabase scan tracking to server

**Objective:** Store scan records in Supabase so users can see history and quota is tracked

**Files:**
- Modify: `src/server.py` (add Supabase client + scan recording)
- Use: Supabase credentials from `.env`

**Step 1: Add Supabase integration to server.py**

Insert after the CORS middleware setup:

```python
# Supabase client (lazy init — only if credentials are configured)
_supabase = None

def _get_supabase():
    global _supabase
    if _supabase is None:
        supabase_url = os.getenv("SUPABASE_URL", "")
        supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")
        if supabase_url and supabase_key:
            from supabase import create_client
            _supabase = create_client(supabase_url, supabase_key)
    return _supabase


async def _record_scan(
    user_id: str,
    filename: str,
    file_hash: str,
    status: str,
    overall_risk: Optional[str] = None,
    report_url: Optional[str] = None,
    char_count: int = 0,
) -> Optional[str]:
    """Record a scan in Supabase. Returns scan ID or None if Supabase is not configured."""
    supabase = _get_supabase()
    if not supabase:
        return None

    data = {
        "user_id": user_id,
        "filename": filename,
        "file_hash": file_hash,
        "status": status,
        "char_count": char_count,
    }
    if overall_risk:
        data["overall_risk"] = overall_risk
    if report_url:
        data["report_url"] = report_url

    result = supabase.table("scans").insert(data).execute()
    return result.data[0]["id"] if result.data else None
```

**Step 2: Add `user_id` to the upload endpoint signature**

The endpoint currently takes `file` and `email`. Add an optional `user_id` to track scans:

```python
@app.post("/api/upload")
async def upload_contract(
    file: UploadFile = File(...),
    email: str = Form(...),
    user_id: Optional[str] = Form(None),
):
```

And in `_process_upload`, after saving the report:

```python
# Record scan in Supabase (if user is authenticated)
if user_id:
    fhash = file_hash(filepath)
    await _record_scan(
        user_id=user_id,
        filename=original_filename,
        file_hash=fhash,
        status="done",
        overall_risk=overall_risk,
        report_url=str(report_path),
        char_count=len(text),
    )
```

**Step 3: Commit**

```bash
git add src/server.py
git commit -m "feat: add Supabase scan tracking to upload endpoint"
```

---

### Task 5: Update frontend to call the real API

**Objective:** Replace the simulated upload in dashboard.html with a real fetch to the backend

**Files:**
- Modify: `site/dashboard.html` (the `handleUpload` function ~line 229-280)
- Modify: `site/app.js` (add Supabase auth token extraction)

**Step 1: Replace handleUpload in dashboard.html**

```javascript
async function handleUpload(file) {
  if (!file) return;
  const zone = document.getElementById('upload-zone');
  const status = document.getElementById('upload-status');
  zone.classList.add('hidden');
  status.classList.remove('hidden');
  document.getElementById('upload-filename').textContent = file.name;
  document.getElementById('upload-msg').textContent = 'Uploading...';

  try {
    // Get current user's email from Supabase session
    const { data: { session } } = await supabaseClient.auth.getSession();
    const email = session?.user?.email || '';
    const userId = session?.user?.id || '';

    const formData = new FormData();
    formData.append('file', file);
    formData.append('email', email);
    if (userId) formData.append('user_id', userId);

    document.getElementById('upload-msg').textContent = 'Analyzing contract...';

    const response = await fetch('http://127.0.0.1:8123/api/upload', {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const err = await response.json();
      throw new Error(err.detail || 'Upload failed');
    }

    const result = await response.json();

    // Store scan in localStorage for history
    const scans = JSON.parse(localStorage.getItem('contractlens_scans') || '[]');
    scans.push({
      id: Date.now().toString(),
      filename: file.name,
      date: new Date().toISOString(),
      risk: result.risk,
      status: 'done',
      reportUrl: result.report_url,
      reportData: {
        summary: `Analysis complete. Overall risk: ${result.risk.toUpperCase()}.`,
        zones: Object.entries(result.zones).map(([key, data]) => ({
          name: zoneNames[key] || key,
          risk: data.risk,
          note: data.summary,
        })),
        actions: result.recommendations,
      }
    });
    localStorage.setItem('contractlens_scans', JSON.stringify(scans));

    document.getElementById('upload-msg').textContent = 'Analysis complete!';
    document.getElementById('upload-spinner').classList.add('hidden');
    showToast(`Report ready — sent to ${email}.`, 'success');

    setTimeout(() => {
      status.classList.add('hidden');
      zone.classList.remove('hidden');
      loadDashboard();
    }, 2000);

  } catch (error) {
    document.getElementById('upload-msg').textContent = `Error: ${error.message}`;
    document.getElementById('upload-spinner').classList.add('hidden');
    showToast(error.message, 'error');
    setTimeout(() => {
      status.classList.add('hidden');
      zone.classList.remove('hidden');
    }, 3000);
  }
}
```

**Step 2: Add zone name mapping to dashboard.html**

Add before the `handleUpload` function:

```javascript
const zoneNames = {
  payment_terms: 'Payment Terms',
  ip_ownership: 'IP & Ownership',
  non_compete: 'Non-Compete',
  termination: 'Termination',
  indemnification: 'Indemnification',
  liability_caps: 'Liability Caps',
};
```

**Step 3: Commit**

```bash
git add site/dashboard.html
git commit -m "feat: wire frontend upload to real FastAPI backend"
```

---

### Task 6: Add CORS and backend URL config to frontend

**Objective:** Make the backend URL configurable so it works in development and production

**Files:**
- Modify: `site/config.example.js`
- Modify: `site/dashboard.html`

**Step 1: Add API_URL to config**

```javascript
// site/config.example.js — add:
const CONFIG = {
  SUPABASE_URL: "https://YOUR_PROJECT.supabase.co",
  SUPABASE_ANON_KEY: "sb_publishable_YOUR_KEY",
  STRIPE_PK: "pk_test_YOUR_KEY",
  STRIPE_LINKS: { ... },
  API_URL: "http://127.0.0.1:8123",  // NEW
};
```

**Step 2: Use CONFIG.API_URL in dashboard fetch**

Replace the hardcoded `http://127.0.0.1:8123/api/upload` with:

```javascript
const response = await fetch(`${CONFIG.API_URL}/api/upload`, { ... });
```

**Step 3: Commit**

```bash
git add site/config.example.js site/dashboard.html
git commit -m "feat: make API URL configurable via CONFIG.API_URL"
```

---

### Task 7: End-to-end test

**Objective:** Verify the entire pipeline works with a real contract file

**Step 1: Start the server**

```bash
cd /Users/justasza/contractlens
python -m uvicorn src.server:app --host 127.0.0.1 --port 8123 &
```

**Step 2: Test health endpoint**

```bash
curl http://127.0.0.1:8123/api/health
```
Expected: `{"status":"ok","version":"0.2.0"}`

**Step 3: Test upload with the sample contract**

```bash
curl -X POST http://127.0.0.1:8123/api/upload \
  -F "file=@samples/independent_contractor_agreement.txt" \
  -F "email=test@example.com"
```

Expected: JSON response with `"success": true`, `"risk": "low|medium|high"`, `"zones": {...}`, `"recommendations": [...]`. Response takes 15-60 seconds.

**Step 4: Verify report was generated**

```bash
ls -la output/report_*.html
```
Expected: HTML file exists.

**Step 5: Kill the server**

```bash
kill %1
```

**Step 6: Commit any fixes from testing**

```bash
git add -A
git commit -m "test: verify end-to-end pipeline with sample contract"
```

---

## How It All Connects

```
User uploads PDF on dashboard
        │
        ▼
POST /api/upload  (FastAPI, server.py)
        │
        ├─► validate_file()          (security.py)  — magic bytes, size, symlink
        ├─► extract_text()           (extract.py)   — PyMuPDF/python-docx
        ├─► sanitize_text()          (security.py)  — strip injection vectors
        ├─► get_contract_metadata()  (extract.py)   — title, parties, date
        │
        ├─► analyze_contract()       (llm_client.py) — NEW
        │       │
        │       ├─► load_prompt()    (analyze.py)   — reads prompts/contract_analysis.md
        │       └─► DeepSeek API     (httpx)        — system prompt + contract text → JSON
        │
        ├─► validate_analysis()      (analyze.py)   — check all 6 zones present
        ├─► generate_html_report()   (report.py)    — self-contained HTML
        ├─► save_report()            (report.py)    — write to output/
        ├─► send_report_email()      (emailer.py)   — SMTP delivery
        └─► _record_scan()           (server.py)    — Supabase scan record
```

The AI agent "soul" is `prompts/contract_analysis.md` — it defines:
- **Personality:** "expert contract analyst for freelancers"
- **Audience:** "freelancers, not lawyers"
- **Framework:** 6 danger zones with specific questions per zone
- **Output format:** JSON with risk levels, summaries, clause quotes, recommendations

---

## File Changes Summary

| File | Action | Purpose |
|------|--------|---------|
| `requirements.txt` | Modify | Add FastAPI, httpx, supabase |
| `src/llm_client.py` | **Create** | DeepSeek API client |
| `src/server.py` | **Create** | FastAPI server with upload endpoint |
| `site/dashboard.html` | Modify | Replace fake upload with real API call |
| `site/config.example.js` | Modify | Add API_URL config |

No changes needed to: `extract.py`, `report.py`, `emailer.py`, `security.py`, `analyze.py`, `prompts/contract_analysis.md` — they already work and are reused as-is.

---

## What Happens To The Old Flow

- `pipeline.py` CLI still works — useful for manual testing and debugging
- The simulated dashboard upload is replaced — no more `Math.random()` risk levels
- Hermes cron is not needed — the LLM call happens synchronously in the API request
- `analyze.py` `build_analysis_prompt()` and `parse_analysis_response()` are partially superseded by `llm_client.py` but kept for CLI/standalone use

---

## Deployment Notes

**Development:**
```bash
python -m uvicorn src.server:app --host 127.0.0.1 --port 8123 --reload
```

**Production (later):**
```bash
python -m uvicorn src.server:app --host 0.0.0.0 --port 8123 --workers 4
```
Put behind nginx with HTTPS. Tighten CORS origins. Add rate limiting.

**Cost estimate:** DeepSeek API is ~$0.27/M input tokens, ~$1.10/M output tokens. A typical 25-page contract (~25K characters, ~6K tokens) with a 4K token analysis output costs roughly $0.01 per scan.
