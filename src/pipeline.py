"""Main ContractLens pipeline — orchestrates extraction, analysis, and delivery.

Usage (standalone):
    python -m src.pipeline path/to/contract.pdf --email user@example.com

Usage (from Hermes cron):
    The cron job calls this via analyze.py + report.py directly.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .extract import extract_text, get_contract_metadata
from .report import generate_html_report, save_report
from .emailer import send_report_email, send_report_via_hermes
from .config import OUTPUT_DIR


def process_contract(
    filepath: str | Path,
    email_to: str | None = None,
    output_dir: str | Path | None = None,
) -> dict:
    """Full pipeline: extract → analyze → report → deliver.

    NOTE: The actual LLM analysis step happens through Hermes.
    This function handles extraction and report generation; the analysis
    JSON is passed in externally (from the Hermes cron job).

    Args:
        filepath: Path to the contract file.
        email_to: Optional email to send the report to.
        output_dir: Directory for output files.

    Returns:
        Dict with keys: metadata, output_path, email_sent
    """
    filepath = Path(filepath)

    # 1. Extract text
    print(f"📄 Extracting text from {filepath.name}...")
    text = extract_text(filepath)
    print(f"   Extracted {len(text):,} characters")

    # 2. Get metadata
    metadata = get_contract_metadata(text)
    print(f"   Title: {metadata['title']}")
    print(f"   Est. pages: {metadata['page_estimate']}")

    return {
        "text": text,
        "metadata": metadata,
        "filepath": filepath,
    }


def deliver_report(
    analysis: dict,
    metadata: dict,
    email_to: str | None = None,
    output_dir: str | Path | None = None,
    via_hermes: bool = False,
) -> Path:
    """Generate HTML report and deliver it.

    Args:
        analysis: The parsed analysis JSON.
        metadata: Contract metadata dict.
        email_to: Email address to send to.
        output_dir: Output directory.
        via_hermes: If True, save for Hermes native delivery instead of SMTP.

    Returns:
        Path to the saved report file.
    """
    output_dir = Path(output_dir) if output_dir else OUTPUT_DIR

    # Generate HTML report
    print("📝 Generating HTML report...")
    html = generate_html_report(analysis, metadata)
    report_path = save_report(html, output_dir)
    print(f"   Saved to: {report_path}")

    # Deliver
    if email_to:
        if via_hermes:
            report_path = send_report_via_hermes(html, metadata, report_path)
            print(f"   Ready for Hermes delivery: {report_path}")
        else:
            print(f"📧 Sending report to {email_to}...")
            send_report_email(email_to, html, metadata)
            print("   Sent!")

    return report_path


def main():
    parser = argparse.ArgumentParser(
        description="ContractLens — AI-powered contract analysis"
    )
    parser.add_argument("filepath", help="Path to contract file (PDF, DOCX, TXT)")
    parser.add_argument("--email", "-e", help="Email to send report to")
    parser.add_argument("--output", "-o", help="Output directory", default=None)
    parser.add_argument(
        "--hermes",
        action="store_true",
        help="Use Hermes native delivery instead of SMTP",
    )
    parser.add_argument(
        "--extract-only",
        action="store_true",
        help="Only extract text, don't analyze",
    )

    args = parser.parse_args()

    try:
        result = process_contract(args.filepath, args.email, args.output)
        print(f"\n✅ Extraction complete. Text ready for analysis.")
        print(f"   Text length: {len(result['text']):,} chars")
        print(f"\n   Run the analysis through Hermes to complete the pipeline.")
        print(f"   Or use: python -m src.pipeline with the full analysis JSON.")

    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
