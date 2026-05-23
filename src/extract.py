"""Extract text from contracts (PDF, DOCX, TXT)."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Optional


def extract_text(filepath: str | Path) -> str:
    """Extract text from a contract file. Supports PDF, DOCX, TXT.

    Args:
        filepath: Path to the contract file.

    Returns:
        Extracted text as a string.

    Raises:
        ValueError: If file format is unsupported or file is empty.
    """
    filepath = Path(filepath)
    if not filepath.exists():
        raise FileNotFoundError(f"File not found: {filepath}")

    suffix = filepath.suffix.lower()

    if suffix == ".pdf":
        return _extract_pdf(filepath)
    elif suffix == ".docx":
        return _extract_docx(filepath)
    elif suffix in (".txt", ".md", ".text"):
        return _extract_text(filepath)
    else:
        raise ValueError(f"Unsupported file format: {suffix}")


def _extract_pdf(filepath: Path) -> str:
    """Extract text from PDF using PyMuPDF."""
    try:
        import fitz  # pymupdf
    except ImportError:
        raise ImportError(
            "PyMuPDF is required for PDF extraction. "
            "Install it with: pip install pymupdf"
        )

    doc = fitz.open(str(filepath))
    pages = []
    for page in doc:
        text = page.get_text("text")
        if text.strip():
            pages.append(text)
    doc.close()

    text = "\n\n".join(pages)
    if not text.strip():
        raise ValueError(
            "No extractable text found in PDF. It may be a scanned document "
            "(OCR required)."
        )
    return text


def _extract_docx(filepath: Path) -> str:
    """Extract text from DOCX using python-docx."""
    try:
        from docx import Document
    except ImportError:
        raise ImportError(
            "python-docx is required for DOCX extraction. "
            "Install it with: pip install python-docx"
        )

    doc = Document(str(filepath))
    paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
    text = "\n\n".join(paragraphs)

    if not text.strip():
        raise ValueError("No text found in DOCX file.")
    return text


def _extract_text(filepath: Path) -> str:
    """Extract text from a plain text file."""
    text = filepath.read_text(encoding="utf-8")
    if not text.strip():
        raise ValueError("File is empty.")
    return text


def get_contract_metadata(text: str) -> dict:
    """Extract basic metadata from contract text.

    Returns dict with keys: title, parties, date, page_count_estimate
    """
    lines = text.strip().split("\n")
    first_line = lines[0].strip() if lines else "Untitled"

    # Rough page count estimate (250 words/page)
    word_count = len(text.split())
    page_estimate = max(1, word_count // 250)

    # Try to find date
    date_pattern = r"(?:dated|effective\s+date|date\s+of)[:\s]+(\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\w+\s+\d{1,2},?\s+\d{4})"
    date_match = re.search(date_pattern, text, re.IGNORECASE)

    # Try to find parties
    party_section = re.search(
        r"(?:between|by\s+and\s+between)\s+(.+?)(?:\s+and\s+)(.+?)(?:\n|,|\.)",
        text[:500],
        re.IGNORECASE,
    )

    return {
        "title": first_line[:100],
        "parties": (
            [party_section.group(1).strip(), party_section.group(2).strip()]
            if party_section
            else []
        ),
        "date": date_match.group(1) if date_match else None,
        "page_estimate": page_estimate,
        "char_count": len(text),
    }
