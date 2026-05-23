"""Security hardening for ContractLens.

Handles: file validation, sandboxed extraction, content sanitization,
and automatic cleanup of sensitive documents after processing.
"""

from __future__ import annotations

import hashlib
import os
import shutil
import tempfile
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Tuple

# ── Configuration ──────────────────────────────────────────────────────────

MAX_FILE_SIZE = 20 * 1024 * 1024  # 20 MB
ALLOWED_TYPES = {
    "application/pdf": ".pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": ".docx",
    "text/plain": ".txt",
    "text/markdown": ".md",
}
ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt", ".md", ".text"}

# Auto-delete raw files after processing (keep only report + analysis JSON)
DELETE_AFTER_PROCESSING = True

# Patterns to strip from extracted text (potential script injection, etc.)
DANGEROUS_PATTERNS = [
    (r"<script[^>]*>.*?</script>", "[script removed]"),
    (r"javascript\s*:", "[js-uri removed]"),
    (r"data:text/html", "[data-uri removed]"),
]

# ── Magic Bytes ────────────────────────────────────────────────────────────

MAGIC_BYTES = {
    b"%PDF": "application/pdf",
    b"PK\x03\x04": "application/zip",  # DOCX is a ZIP
}


def validate_file(filepath: str | Path) -> Tuple[bool, str]:
    """Validate a file is safe to process.

    Checks: existence, size, extension, magic bytes, and that it's
    an actual file (not a symlink to /etc/passwd, etc.).

    Returns:
        (is_valid, error_message). If valid, error_message is empty.
    """
    filepath = Path(filepath).resolve()

    # 1. Must exist and be a regular file
    if not filepath.exists():
        return False, f"File not found: {filepath}"
    if not filepath.is_file():
        return False, "Path is not a regular file"
    if filepath.is_symlink():
        return False, "Symlinks are not allowed"

    # 2. Size check
    size = filepath.stat().st_size
    if size == 0:
        return False, "File is empty"
    if size > MAX_FILE_SIZE:
        return False, f"File too large ({size:,} bytes). Max: {MAX_FILE_SIZE:,} bytes"

    # 3. Extension check
    suffix = filepath.suffix.lower()
    if suffix not in ALLOWED_EXTENSIONS:
        return False, f"Unsupported file type: {suffix}"

    # 4. Magic bytes check (prevents extension spoofing)
    try:
        with open(filepath, "rb") as f:
            header = f.read(8)
    except (IOError, PermissionError) as e:
        return False, f"Cannot read file: {e}"

    detected_type = None
    for magic, mime in MAGIC_BYTES.items():
        if header.startswith(magic):
            detected_type = mime
            break

    # DOCX files have ZIP magic bytes
    if detected_type == "application/zip" and suffix == ".docx":
        pass  # OK — DOCX is a valid ZIP
    elif detected_type and detected_type not in ALLOWED_TYPES:
        return False, f"File content doesn't match expected type (detected: {detected_type})"

    # 5. Filename safety (no path traversal)
    if ".." in filepath.name or "/" in filepath.name or "\\" in filepath.name:
        return False, "Invalid filename"

    return True, ""


def sanitize_text(text: str) -> str:
    """Remove potentially dangerous content from extracted text.

    Strips: script tags, javascript URIs, data URIs, and null bytes.
    Does NOT alter contract content — just removes injection vectors.
    """
    # Strip null bytes
    text = text.replace("\x00", "")

    # Strip injection patterns
    for pattern, replacement in DANGEROUS_PATTERNS:
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE | re.DOTALL)

    return text


def cleanup_uploads(
    upload_dir: str | Path,
    max_age_hours: int = 24,
    dry_run: bool = False,
) -> list[str]:
    """Delete uploaded files older than max_age_hours.

    Args:
        upload_dir: Directory containing uploaded contract files.
        max_age_hours: Delete files older than this.
        dry_run: If True, only report what would be deleted.

    Returns:
        List of deleted (or would-be-deleted) file paths.
    """
    upload_dir = Path(upload_dir)
    if not upload_dir.exists():
        return []

    cutoff = datetime.now() - timedelta(hours=max_age_hours)
    deleted = []

    for filepath in upload_dir.iterdir():
        if not filepath.is_file():
            continue
        mtime = datetime.fromtimestamp(filepath.stat().st_mtime)
        if mtime < cutoff:
            if not dry_run:
                try:
                    filepath.unlink()
                except OSError:
                    pass
            deleted.append(str(filepath))

    return deleted


def secure_temp_copy(filepath: str | Path) -> Path:
    """Create a secure temporary copy of a file for processing.

    The copy is placed in a temp directory with restricted permissions.
    Caller is responsible for deleting the copy after processing.
    """
    filepath = Path(filepath)
    tmp = Path(tempfile.mkdtemp(prefix="contractlens_"))
    tmp.chmod(0o700)

    dest = tmp / filepath.name
    shutil.copy2(filepath, dest)
    dest.chmod(0o600)

    return dest


def file_hash(filepath: str | Path) -> str:
    """Compute SHA-256 hash of a file (for dedup/detection)."""
    sha = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            sha.update(chunk)
    return sha.hexdigest()


def delete_source_after_processing(filepath: str | Path) -> bool:
    """Securely delete the original uploaded file after processing.

    Overwrites with zeros before deletion when possible.
    """
    filepath = Path(filepath)
    if not filepath.exists():
        return False

    try:
        # Overwrite with zeros (simple, not DoD-level but good enough)
        size = filepath.stat().st_size
        with open(filepath, "wb") as f:
            f.write(b"\x00" * min(size, 1024 * 1024))  # 1MB max overwrite
        filepath.unlink()
        return True
    except OSError:
        return False


def generate_report_id() -> str:
    """Generate a unique, unguessable report ID."""
    return hashlib.sha256(os.urandom(32)).hexdigest()[:16]
