"""ContractLens API server.

Endpoints:
  POST /api/upload  — receive contract file, run full analysis pipeline
  GET  /api/health  — liveness check

Run with:
  uvicorn src.server:app --host 127.0.0.1 --port 8123 --reload
"""

from __future__ import annotations

import os
import traceback
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from .analyze import validate_analysis
from .config import MAX_CONTRACT_CHARS, OUTPUT_DIR, UPLOAD_DIR
from .emailer import send_report_email
from .extract import extract_text, get_contract_metadata
from .llm_client import analyze_contract
from .report import _compute_overall_risk, generate_html_report, save_report
from .security import file_hash, sanitize_text, validate_file


app = FastAPI(
    title="ContractLens API",
    description="AI-powered contract analysis for freelancers",
    version="0.2.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten in production with specific origins
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)


# ── Supabase (lazy init — optional) ────────────────────────────────────────

_supabase = None


def _get_supabase():
    global _supabase
    if _supabase is None:
        url = os.getenv("SUPABASE_URL", "")
        key = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")
        if url and key:
            from supabase import create_client
            _supabase = create_client(url, key)
    return _supabase


async def _record_scan(
    user_id: str,
    filename: str,
    fhash: str,
    status: str,
    overall_risk: Optional[str] = None,
    report_url: Optional[str] = None,
    char_count: int = 0,
) -> Optional[str]:
    """Insert a scan record into Supabase. Returns scan ID or None if not configured."""
    supabase = _get_supabase()
    if not supabase:
        return None

    row: dict = {
        "user_id": user_id,
        "filename": filename,
        "file_hash": fhash,
        "status": status,
        "char_count": char_count,
    }
    if overall_risk:
        row["overall_risk"] = overall_risk
    if report_url:
        row["report_url"] = report_url

    try:
        result = supabase.table("scans").insert(row).execute()
        return result.data[0]["id"] if result.data else None
    except Exception as e:
        print(f"Supabase record_scan failed: {e}")
        return None


# ── Endpoints ───────────────────────────────────────────────────────────────

@app.get("/api/health")
async def health():
    return {"status": "ok", "version": "0.2.0"}


@app.post("/api/upload")
async def upload_contract(
    file: UploadFile = File(...),
    email: str = Form(...),
    user_id: Optional[str] = Form(None),
):
    """Upload a contract for analysis.

    Full pipeline: validate → extract → sanitize → LLM analysis
    → HTML report → email delivery → Supabase scan record.

    Returns JSON with risk, zones, recommendations.
    """
    allowed = {".pdf", ".docx", ".txt", ".md", ".text"}
    suffix = Path(file.filename or "unknown").suffix.lower()
    if suffix not in allowed:
        raise HTTPException(
            400,
            f"Unsupported file type: {suffix}. Accepted: {', '.join(sorted(allowed))}",
        )

    content = await file.read()
    if len(content) == 0:
        raise HTTPException(400, "File is empty")
    if len(content) > 20 * 1024 * 1024:
        raise HTTPException(400, "File too large (max 20 MB)")

    UPLOAD_DIR.mkdir(exist_ok=True)
    tmp_path = UPLOAD_DIR / f"{os.urandom(8).hex()}_{file.filename}"
    tmp_path.write_bytes(content)

    try:
        return await _process_upload(tmp_path, email, file.filename or "unknown", user_id)
    except ValueError as e:
        raise HTTPException(400, str(e))
    except RuntimeError as e:
        raise HTTPException(500, str(e))
    except Exception:
        traceback.print_exc()
        raise HTTPException(500, "Internal server error")
    finally:
        try:
            tmp_path.unlink()
        except OSError:
            pass


async def _process_upload(
    filepath: Path,
    email: str,
    original_filename: str,
    user_id: Optional[str],
) -> dict:
    # 1. Security validation (magic bytes, size, symlink check)
    valid, err = validate_file(filepath)
    if not valid:
        raise ValueError(f"Security check failed: {err}")

    # 2. Extract text
    raw_text = extract_text(filepath)

    # 3. Sanitize (strip injection vectors)
    text = sanitize_text(raw_text)

    # 4. Truncate if needed
    if len(text) > MAX_CONTRACT_CHARS:
        text = text[:MAX_CONTRACT_CHARS]

    # 5. Contract metadata
    metadata = get_contract_metadata(text)

    # 6. LLM analysis
    analysis = await analyze_contract(text)

    # 7. Validate completeness (warn but don't fail on partial)
    warnings = validate_analysis(analysis)
    if warnings:
        print(f"Analysis warnings: {warnings}")

    # 8. Generate and save HTML report
    html = generate_html_report(analysis, metadata)
    report_path = save_report(html, OUTPUT_DIR)
    print(f"Report saved: {report_path}")

    # 9. Email delivery (non-fatal failure)
    emailed = False
    try:
        send_report_email(email, html, metadata)
        emailed = True
    except Exception as e:
        print(f"Email failed (non-fatal): {e}")

    # 10. Compute overall risk
    overall_risk = _compute_overall_risk(analysis)

    # 11. Record scan in Supabase (if user is authenticated and Supabase configured)
    if user_id:
        fhash = file_hash(filepath) if filepath.exists() else ""
        await _record_scan(
            user_id=user_id,
            filename=original_filename,
            fhash=fhash,
            status="done",
            overall_risk=overall_risk,
            report_url=str(report_path),
            char_count=len(text),
        )

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
