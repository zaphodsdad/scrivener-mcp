"""RTF parsing utilities for Scrivener documents."""

from pathlib import Path

from striprtf.striprtf import rtf_to_text


def text_to_rtf(text: str) -> str:
    """Convert plain text to basic RTF format.

    Creates minimal RTF that Scrivener can read. Preserves paragraphs.
    """
    # RTF header with basic formatting
    rtf_header = r"{\rtf1\ansi\ansicpg1252\cocoartf2761\cocoatextscaling0\cocoaplatform0"
    rtf_header += r"{\fonttbl\f0\fswiss\fcharset0 Helvetica;}"
    rtf_header += r"{\colortbl;\red255\green255\blue255;}"
    rtf_header += r"\margl1440\margr1440\vieww11520\viewh8400\viewkind0"
    rtf_header += r"\pard\tx720\tx1440\tx2160\tx2880\tx3600\tx4320\tx5040\tx5760\tx6480\tx7200\tx7920\tx8640\pardirnatural\partightenfactor0"
    rtf_header += "\n"
    rtf_header += r"\f0\fs24 \cf0 "

    # Escape special RTF characters and convert newlines
    escaped = text.replace("\\", "\\\\")
    escaped = escaped.replace("{", "\\{")
    escaped = escaped.replace("}", "\\}")

    # Convert paragraphs (double newlines) to RTF paragraph breaks
    escaped = escaped.replace("\n\n", "\\par\\par\n")
    # Convert single newlines to line breaks
    escaped = escaped.replace("\n", "\\line\n")

    rtf_footer = "}"

    return rtf_header + escaped + rtf_footer


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
