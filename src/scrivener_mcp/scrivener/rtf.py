"""RTF parsing utilities for Scrivener documents."""

from pathlib import Path

from striprtf.striprtf import rtf_to_text


def read_rtf(path: Path) -> str:
    """Read an RTF file and return plain text content."""
    if not path.exists():
        return ""

    rtf_content = path.read_text(encoding="utf-8", errors="ignore")

    # Handle empty files
    if not rtf_content.strip():
        return ""

    try:
        text = rtf_to_text(rtf_content)
        return text.strip()
    except Exception:
        # If RTF parsing fails, try to extract raw text
        # This handles edge cases with malformed RTF
        return ""


def count_words(text: str) -> int:
    """Count words in a text string."""
    if not text:
        return 0
    return len(text.split())
