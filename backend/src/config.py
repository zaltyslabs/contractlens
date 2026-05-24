"""ContractLens configuration."""

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent
UPLOAD_DIR = BASE_DIR / "uploads"
OUTPUT_DIR = BASE_DIR / "output"
PROMPTS_DIR = BASE_DIR / "prompts"
SAMPLES_DIR = BASE_DIR / "samples"

# Ensure directories exist
UPLOAD_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

# LLM config — pulled from Hermes environment
LLM_PROVIDER = os.getenv("HERMES_MODEL_PROVIDER", "deepseek")
LLM_MODEL = os.getenv("HERMES_MODEL", "deepseek-v4-pro")

# Email config
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASS = os.getenv("SMTP_PASS", "")
FROM_EMAIL = os.getenv("FROM_EMAIL", SMTP_USER)

# Analysis
DANGER_ZONES = [
    "payment_terms",
    "ip_ownership",
    "non_compete",
    "termination",
    "indemnification",
    "liability_caps",
]

MAX_CONTRACT_CHARS = 40_000  # ~10K tokens; leaves ample output budget for LLM
