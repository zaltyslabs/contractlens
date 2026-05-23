"""Email delivery for ContractLens reports."""

from __future__ import annotations

import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path
from typing import Optional

from .config import SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASS, FROM_EMAIL


def send_report_email(
    to_email: str,
    report_html: str,
    metadata: dict,
    subject: Optional[str] = None,
) -> bool:
    """Send the contract analysis report via email.

    Args:
        to_email: Recipient email address.
        report_html: Full HTML report content.
        metadata: Contract metadata dict.
        subject: Optional custom subject line.

    Returns:
        True if sent successfully.

    Raises:
        ValueError: If SMTP credentials are not configured.
    """
    if not SMTP_USER or not SMTP_PASS:
        raise ValueError(
            "SMTP credentials not configured. Set SMTP_USER and SMTP_PASS "
            "in environment or .env file."
        )

    title = metadata.get("title", "your contract")
    if subject is None:
        subject = f"📋 ContractLens: Analysis for {title[:50]}"

    # Plain text fallback
    plain_text = f"""ContractLens Analysis Complete

Document: {title}
Overall Risk: See attached report
---
Your contract analysis is ready. View the attached HTML report for full details.

⚠️ This is AI-generated analysis, not legal advice. Consult a lawyer before signing.

— ContractLens
"""

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = FROM_EMAIL
    msg["To"] = to_email

    msg.attach(MIMEText(plain_text, "plain"))
    msg.attach(MIMEText(report_html, "html"))

    try:
        context = ssl.create_default_context()
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls(context=context)
            server.login(SMTP_USER, SMTP_PASS)
            server.sendmail(FROM_EMAIL, to_email, msg.as_string())
        return True
    except smtplib.SMTPAuthenticationError:
        raise ValueError(
            "Gmail SMTP authentication failed. If using Gmail, you need an "
            "App Password (not your regular password). "
            "Go to: https://myaccount.google.com/apppasswords"
        )
    except Exception as e:
        raise RuntimeError(f"Failed to send email: {e}")


def send_report_via_hermes(
    report_html: str,
    metadata: dict,
    output_path: Optional[Path] = None,
) -> Path:
    """Save report and return path for Hermes to deliver.

    This is the preferred delivery method when running inside Hermes —
    Hermes can send files natively via Telegram, Discord, etc.
    """
    if output_path is None:
        from .config import OUTPUT_DIR
        ts = __import__("datetime").datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = OUTPUT_DIR / f"contractlens_report_{ts}.html"

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(report_html, encoding="utf-8")
    return output_path
