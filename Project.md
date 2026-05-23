# ContractLens — Project Soul

> **Canonical source of truth.** Read this before touching any file. Agents, this is your context injection — don't hallucinate.

---

## What Is This?

**ContractLens** is an AI-powered contract analysis tool for freelancers and small business owners. Upload a contract (PDF, DOCX, TXT) → get a plain-English summary of what you're actually signing in minutes. No lawyer required.

**One-liner:** "Understand every contract you sign."

---

## Who It's For

Freelancers, consultants, indie hackers, small agencies. People who sign contracts regularly but can't afford $200-800 per legal review. They need to know: *will this contract screw me?*

---

## How It Works (Pipeline)

```
PDF/DOCX/TXT → Extract Text (PyMuPDF/python-docx) → Sanitize → LLM Analysis (via Hermes) → HTML Report → Email Delivery
```

Six danger zones analyzed:
1. 💰 **Payment Terms** — when/how you get paid, late fees, holdbacks
2. 🔒 **IP & Ownership** — who owns your work, portfolio rights
3. 🚫 **Non-Compete** — restrictions, duration, scope
4. ⏰ **Termination** — exit clauses, notice periods, auto-renewal
5. 🛡️ **Indemnification** — who's liable, is it mutual
6. ⚖️ **Liability Caps** — damage limits, uncapped liabilities

Each zone gets: risk level (low/medium/high), plain-English summary, key clause quotes, actionable recommendations.

---

## Architecture

**Two halves that talk through the filesystem:**

### Backend (Python, `src/`)
- `pipeline.py` — main orchestrator: validate → extract → sanitize → deliver
- `extract.py` — PDF (PyMuPDF), DOCX (python-docx), TXT extraction
- `analyze.py` — loads prompt template, injects contract text, parses LLM JSON response
- `report.py` — generates self-contained HTML report with CSS custom properties (light/dark)
- `emailer.py` — SMTP delivery (Gmail App Passwords) or Hermes native delivery
- `security.py` — magic byte validation, symlink rejection, sanitization, secure deletion, file hashing
- `config.py` — paths, env vars, LLM config, danger zones list

### Frontend (Vanilla JS, `site/`)
- `index.html` — landing page (Tailwind CDN, Supabase auth, Stripe)
- `dashboard.html` — user dashboard (profile, plan management, report viewer)
- `app.js` — shared client: Supabase client init, auth helpers, Stripe redirect
- `config.js` — **REAL KEYS (Supabase URL, anon key, Stripe PK, Stripe links)** — DO NOT COMMIT
- `config.example.js` — template without secrets
- `tos.html`, `privacy.html` — legal pages

### Infrastructure
- **Supabase** — auth, database, storage, edge functions (Stripe webhook)
- **Stripe** — test-mode subscriptions (3 tiers: Side Hustler $12, Power Freelancer $25, Agency $49)
- **Hermes Agent** — cron-driven contract analysis pipeline

---

## Business Model

| Tier | Price | Scans/Month |
|------|-------|:-----------:|
| Free | $0 | 1 |
| Side Hustler | $12/mo | 5 |
| Power Freelancer | $25/mo | 20 |
| Agency | $49/mo | 50 |

---

## Tech Stack

- **Text extraction:** PyMuPDF, python-docx
- **Analysis:** LLM via Hermes Agent (DeepSeek v4 Pro, configurable)
- **Reports:** Custom HTML/CSS with light+dark mode CSS custom properties
- **Email:** SMTP (Gmail with App Passwords) or Hermes native delivery
- **Payments:** Stripe (test mode)
- **Auth/DB/Storage:** Supabase
- **Frontend:** Vanilla HTML/CSS/JS + Tailwind CDN
- **Python:** 3.10+, type hints, `from __future__ import annotations`

---

## Design System (Current)

- **Primary:** Indigo/Purple gradient (`#6366f1` → `#a855f7` → `#ec4899`)
- **Background:** Dark (`gray-950`), light mode supported via `prefers-color-scheme`
- **Typography:** System font stack (`-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto`)
- **Cards:** Glass effect (`.glass`: blur + low-opacity borders)
- **Reports:** Card-based layout, scoreboard grid, clause blocks with monospace
- **Risk colors:** Green `#22c55e` (low), Amber `#f59e0b` (medium), Red `#ef4444` (high)

---

## Key Design Decisions

1. **Python backend, vanilla JS frontend** — no framework overhead for a simple tool
2. **Filesystem as the API** — pipeline writes files, Hermes cron picks them up. No HTTP server.
3. **Self-contained HTML reports** — no external dependencies, works in any email client
4. **Magic byte validation, not extension trust** — `security.py` reads file headers
5. **Auto-delete uploaded files** — overwrite with zeros, then unlink. Privacy-first.
6. **Tailwind via CDN** in frontend — quick iteration, no build step
7. **Supabase for everything infra** — auth, DB, file storage, edge functions

---

## File Structure

```
contractlens/
├── src/
│   ├── __init__.py
│   ├── config.py         # Paths, env vars, LLM config
│   ├── extract.py        # PDF/DOCX/TXT extraction
│   ├── analyze.py        # Prompt building + JSON parsing
│   ├── report.py         # HTML report generator
│   ├── emailer.py        # SMTP + Hermes delivery
│   ├── security.py       # Validation, sanitization, cleanup
│   └── pipeline.py       # Main orchestrator + CLI
├── site/
│   ├── index.html        # Landing page
│   ├── dashboard.html    # User dashboard
│   ├── app.js            # Shared client logic
│   ├── config.js         # REAL KEYS — gitignored
│   ├── config.example.js # Template without secrets
│   ├── tos.html          # Terms of service
│   └── privacy.html      # Privacy policy
├── supabase/
│   ├── schema.sql        # Database schema
│   └── config.toml       # Supabase CLI config
├── prompts/
│   └── contract_analysis.md  # LLM system prompt
├── samples/
│   └── independent_contractor_agreement.txt
├── output/               # Generated reports (gitignored)
├── uploads/              # Temp uploads (gitignored, auto-cleaned)
├── tests/                # Empty — NEEDS TESTS
├── requirements.txt
├── .env.example
├── .gitignore
├── README.md
└── Project.md            # ← THIS FILE
```

---

## Known Issues & TODO

- [ ] **No tests** — `tests/` directory exists but is empty. Critical gap.
- [ ] **Client-side secrets** — `config.js` contains real Supabase URL, anon key, and Stripe PK. These are "publishable" keys by design but should be documented clearly.
- [ ] **No input validation on frontend** — email, password fields not validated before hitting Supabase
- [ ] **No CSRF protection** — vanilla HTML forms
- [ ] **No rate limiting** on contract uploads
- [ ] **Pipeline is CLI-only** — no web upload endpoint. Relies on Hermes cron to pick up files.
- [ ] **OCR support** — PDFs without extractable text (scanned docs) fail with a clear error but no fallback
- [ ] **Mobile responsiveness** — basic Tailwind responsive classes, not thoroughly tested
- [ ] **Error handling** — some try/except blocks are bare (e.g., `except OSError: pass`)
- [ ] **i18n** — English only, hardcoded strings throughout

---

## Agent Guidelines

When working on this project, agents should:

1. **Read Project.md first.** This is the ground truth. Don't invent architecture.
2. **Never commit `config.js` or `.env`** — they contain real keys.
3. **Python style:** type hints, `from __future__ import annotations`, Google-style docstrings. 4-space indentation.
4. **JS style:** Vanilla ES6+, no framework. Keep it simple. One shared `app.js` for common logic.
5. **HTML reports:** Must be self-contained (inline CSS, no external deps). Must support light AND dark mode via `prefers-color-scheme`.
6. **Security-first:** Validate file types by magic bytes, not extension. Sanitize extracted text. Auto-delete uploads.
7. **Tests required:** Any new feature must include tests. Use pytest.
8. **Design:** Dark-first, indigo/purple brand. No generic SaaS slop (see claude-design skill).
9. **Commits:** Conventional commits (`feat:`, `fix:`, `refactor:`).
10. **The analysis prompt** (`prompts/contract_analysis.md`) is sacred — changes there affect output quality for all users. Test with real contracts before modifying.

---

## Environment Variables

See `.env.example` for the full list. Key ones:
- `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY` — Supabase
- `STRIPE_SECRET_KEY`, `STRIPE_WEBHOOK_SECRET` — Stripe
- `SMTP_HOST/PORT/USER/PASS` — Email (Gmail App Passwords)
- `HERMES_MODEL_PROVIDER`, `HERMES_MODEL` — LLM config
