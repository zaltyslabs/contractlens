# ContractLens 📋

**AI-powered contract analysis for freelancers.** Upload a contract, get a plain-English summary of what you're actually signing — in minutes, not hours. No lawyer required.

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-green.svg)](https://www.python.org/)

---

## 🎯 The Problem

Freelancers, consultants, and small business owners sign contracts every week. But:

- **Nobody reads them.** Too long, too dense, too much legalese.
- **Lawyers charge $200–800 per review.** Out of budget for a $2k freelance gig.
- **The scary parts are buried.** Indemnification, IP assignment, non-competes — hidden in section 14.3(b)(ii).

**ContractLens fixes this.** Upload → analyze → understand. Plain English, color-coded risks, actionable recommendations.

---

## ⚡ How It Works

```
PDF → Extract Text → AI Analysis → HTML Report → Email Delivery
```

1. **Upload** — PDF, DOCX, or TXT. Text is extracted locally.
2. **Analyze** — AI reads every clause across 6 danger zones.
3. **Report** — A beautiful, color-coded HTML report with 🟢🟡🔴 risk ratings.
4. **Deliver** — Lands in your inbox. Ready in minutes.

---

## 🔍 What We Check

| Zone | What It Covers |
|------|---------------|
| 💰 **Payment Terms** | When, how much, late fees, holdbacks |
| 🔒 **IP & Ownership** | Who owns your work? Portfolio rights? |
| 🚫 **Non-Compete** | Restrictions, duration, scope |
| ⏰ **Termination** | Exit clauses, notice periods, auto-renewal |
| 🛡️ **Indemnification** | Who's liable? Is it mutual? |
| ⚖️ **Liability Caps** | Damage limits, uncapped liabilities |

---

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- Hermes Agent (for LLM-powered analysis)
- PyMuPDF (for PDF extraction)

### Installation

```bash
git clone https://github.com/zaltyslabs/contractlens.git
cd contractlens
pip install -r requirements.txt
```

### Extract Text (First Step)

```bash
python -m src.pipeline samples/independent_contractor_agreement.txt
```

This extracts the contract text and prints metadata. The actual AI analysis runs through Hermes.

### Full Pipeline (with Hermes)

The analysis step is designed to run as a Hermes cron job:

1. User uploads a contract via the landing page
2. Hermes cron job picks up the file
3. `extract.py` pulls the text
4. The LLM (via the prompt in `prompts/contract_analysis.md`) analyzes it
5. `report.py` generates the HTML report
6. `emailer.py` delivers it

### Run Analysis Manually

```bash
# Extract text first
python -m src.pipeline path/to/contract.pdf

# Then use Hermes to analyze the extracted text with the prompt
# from prompts/contract_analysis.md
```

---

## 📁 Project Structure

```
contractlens/
├── landing/
│   └── index.html           # Landing page
├── src/
│   ├── __init__.py
│   ├── config.py            # Configuration
│   ├── extract.py           # PDF/DOCX text extraction
│   ├── analyze.py           # LLM analysis + prompt building
│   ├── report.py            # HTML report generation
│   ├── emailer.py           # Email delivery
│   └── pipeline.py          # Main orchestrator
├── prompts/
│   └── contract_analysis.md # The analysis prompt for the LLM
├── samples/
│   └── independent_contractor_agreement.txt  # Test contract
├── requirements.txt
└── README.md
```

---

## 💰 Business Model

| Tier | Price | Scans/Month |
|------|-------|:-----------:|
| **Free** | $0 | 1 |
| **Side Hustler** | $12/mo | 5 |
| **Power Freelancer** | $25/mo | 20 |
| **Agency** | $49/mo | 50 |

---

## ⚠️ Disclaimer

**ContractLens provides AI-generated analysis for informational purposes only. It is NOT legal advice.** Always consult a qualified attorney before signing important contracts. The AI can miss nuances, misinterpret clauses, or miss context that a human lawyer would catch.

---

## 🛠️ Tech Stack

- **Text extraction:** PyMuPDF (PDF), python-docx (DOCX)
- **Analysis:** LLM (via Hermes Agent)
- **Reports:** Custom HTML/CSS (dark theme)
- **Email:** SMTP (Gmail, Resend, or any provider)
- **Payments:** Stripe (coming soon)
- **Frontend:** Vanilla HTML/CSS

---

## 📝 License

MIT — see [LICENSE](LICENSE) for details.

---

Built for freelancers who want to know what they're signing. 🚀
