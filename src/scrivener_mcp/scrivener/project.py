"""Main ScrivenerProject class for interacting with .scriv projects."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Iterator

from .binder import BinderItem, parse_binder
from .rtf import count_words, read_rtf


class ScrivenerProject:
    """A Scrivener project (.scriv folder)."""

    def __init__(self, path: str | Path):
        """Initialize a ScrivenerProject.

        Args:
            path: Path to the .scriv folder
        """
        self.path = Path(path)

        if not self.path.exists():
            raise FileNotFoundError(f"Project not found: {self.path}")

        if not self.path.is_dir():
            raise ValueError(f"Not a directory: {self.path}")

        # Find the .scrivx file
        self._scrivx_path = self._find_scrivx()
        if not self._scrivx_path:
            raise ValueError(f"No .scrivx file found in {self.path}")

        # Parse the binder
        self._binder_items = parse_binder(self._scrivx_path)

    def _find_scrivx(self) -> Path | None:
        """Find the .scrivx binder file in the project."""
        for f in self.path.iterdir():
            if f.suffix == ".scrivx":
                return f
        return None

    @property
    def name(self) -> str:
        """Get the project name (folder name without .scriv)."""
        return self.path.stem

    @property
    def is_locked(self) -> bool:
        """Check if the project is currently open in Scrivener."""
        lock_file = self.path / "user.lock"
        return lock_file.exists()

    @property
    def binder_items(self) -> list[BinderItem]:
        """Get the root-level binder items."""
        return self._binder_items

    def all_items(self) -> Iterator[BinderItem]:
        """Iterate over all binder items (depth-first)."""
        for item in self._binder_items:
            yield from item.walk()

    def find_draft_folder(self) -> BinderItem | None:
        """Find the main Draft/Manuscript folder."""
        for item in self.all_items():
            if item.item_type == "DraftFolder":
                return item
        return None

    def find_by_title(self, title: str, exact: bool = True) -> list[BinderItem]:
        """Find all items matching the given title."""
        results = []
        for item in self._binder_items:
            results.extend(item.find_by_title(title, exact=exact))
        return results

    def find_by_uuid(self, uuid: str) -> BinderItem | None:
        """Find an item by its UUID."""
        for item in self._binder_items:
            result = item.find_by_uuid(uuid)
            if result:
                return result
        return None

    def find_by_path(self, path: str) -> BinderItem | None:
        """Find an item by its full path (e.g., 'Neon Syn/Book One/Chapter 01/01')."""
        for item in self.all_items():
            if item.path == path:
                return item
        return None

    def get_content_path(self, item: BinderItem) -> Path:
        """Get the path to the content.rtf file for a binder item."""
        return self.path / "Files" / "Data" / item.uuid / "content.rtf"

    def get_synopsis_path(self, item: BinderItem) -> Path:
        """Get the path to the synopsis.txt file for a binder item."""
        return self.path / "Files" / "Data" / item.uuid / "synopsis.txt"

    def get_notes_path(self, item: BinderItem) -> Path:
        """Get the path to the notes.rtf file for a binder item."""
        return self.path / "Files" / "Data" / item.uuid / "notes.rtf"

    def read_document(self, item: BinderItem) -> str:
        """Read the text content of a document."""
        content_path = self.get_content_path(item)
        return read_rtf(content_path)

    def read_synopsis(self, item: BinderItem) -> str:
        """Read the synopsis for a document."""
        synopsis_path = self.get_synopsis_path(item)
        if synopsis_path.exists():
            return synopsis_path.read_text(encoding="utf-8", errors="ignore").strip()
        return ""

    def read_notes(self, item: BinderItem) -> str:
        """Read the notes for a document."""
        notes_path = self.get_notes_path(item)
        return read_rtf(notes_path)

    def get_word_count(self, item: BinderItem, recursive: bool = False) -> int:
        """Get the word count for an item (optionally including children)."""
        if recursive:
            total = 0
            for child in item.walk():
                if child.is_text:
                    content = self.read_document(child)
                    total += count_words(content)
            return total
        else:
            content = self.read_document(item)
            return count_words(content)

    def search(self, query: str, case_sensitive: bool = False) -> list[tuple[BinderItem, list[str]]]:
        """Search for text across all documents.

        Returns a list of (item, matching_lines) tuples.
        """
        results = []
        flags = 0 if case_sensitive else re.IGNORECASE

        for item in self.all_items():
            if not item.is_text:
                continue

            content = self.read_document(item)
            if not content:
                continue

            # Find matching lines
            matching_lines = []
            for line in content.split("\n"):
                if re.search(query, line, flags):
                    matching_lines.append(line.strip())

            if matching_lines:
                results.append((item, matching_lines))

        return results

    def get_binder_tree(self) -> str:
        """Get a string representation of the entire binder structure."""
        lines = []
        for item in self._binder_items:
            lines.append(item.to_tree_string())
        return "\n".join(lines)

    def get_manuscript_text(self, include_titles: bool = True) -> str:
        """Get the full manuscript text (all items in the Draft folder marked for compile)."""
        draft = self.find_draft_folder()
        if not draft:
            return ""

        parts = []
        for item in draft.walk():
            if item == draft:
                continue  # Skip the draft folder itself

            if item.is_folder and include_titles:
                # Add folder title as a heading
                parts.append(f"\n{'#' * min(item.depth, 4)} {item.title}\n")
            elif item.is_text and item.include_in_compile:
                content = self.read_document(item)
                if content:
                    if include_titles:
                        parts.append(f"\n### {item.title}\n")
                    parts.append(content)

        return "\n".join(parts)
