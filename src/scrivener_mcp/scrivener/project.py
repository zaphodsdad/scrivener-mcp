"""Main ScrivenerProject class for interacting with .scriv projects."""

from __future__ import annotations

import re
import shutil
import uuid
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path
from typing import Iterator

from .binder import BinderItem, parse_binder, parse_binder_item
from .rtf import count_words, read_rtf, text_to_rtf


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

    # ========== Write Operations ==========

    def get_snapshots_path(self, item: BinderItem) -> Path:
        """Get the path to the snapshots folder for a binder item."""
        return self.path / "Snapshots" / "Data" / item.uuid

    def create_snapshot(self, item: BinderItem, title: str | None = None) -> str:
        """Create a snapshot of a document's current state.

        Args:
            item: The binder item to snapshot
            title: Optional title for the snapshot (defaults to timestamp)

        Returns:
            The snapshot filename
        """
        if not item.is_text:
            raise ValueError(f"Cannot snapshot non-text item: {item.title}")

        # Create snapshots directory if needed
        snapshots_dir = self.get_snapshots_path(item)
        snapshots_dir.mkdir(parents=True, exist_ok=True)

        # Generate snapshot filename with timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        snapshot_title = title or f"Snapshot {timestamp}"
        safe_title = re.sub(r'[^\w\s-]', '', snapshot_title).strip()
        snapshot_filename = f"{timestamp} {safe_title}.rtf"

        # Copy current content to snapshot
        content_path = self.get_content_path(item)
        snapshot_path = snapshots_dir / snapshot_filename

        if content_path.exists():
            shutil.copy2(content_path, snapshot_path)
        else:
            # Create empty snapshot if no content exists
            snapshot_path.write_text(text_to_rtf(""), encoding="utf-8")

        return snapshot_filename

    def write_document(self, item: BinderItem, content: str, create_snapshot: bool = True) -> None:
        """Write content to a document.

        Args:
            item: The binder item to write to
            content: The plain text content to write
            create_snapshot: Whether to create a snapshot before writing (default: True)
        """
        if self.is_locked:
            raise RuntimeError(
                "Project is open in Scrivener. Close Scrivener before writing."
            )

        if not item.is_text:
            raise ValueError(f"Cannot write to non-text item: {item.title}")

        # Create snapshot first (safety measure)
        if create_snapshot:
            content_path = self.get_content_path(item)
            if content_path.exists():
                self.create_snapshot(item, "Auto-snapshot before edit")

        # Ensure the data directory exists
        data_dir = self.path / "Files" / "Data" / item.uuid
        data_dir.mkdir(parents=True, exist_ok=True)

        # Write the RTF content
        content_path = self.get_content_path(item)
        rtf_content = text_to_rtf(content)
        content_path.write_text(rtf_content, encoding="utf-8")

    def write_synopsis(self, item: BinderItem, synopsis: str) -> None:
        """Write the synopsis for a document.

        Args:
            item: The binder item to update
            synopsis: The synopsis text
        """
        if self.is_locked:
            raise RuntimeError(
                "Project is open in Scrivener. Close Scrivener before writing."
            )

        # Ensure the data directory exists
        data_dir = self.path / "Files" / "Data" / item.uuid
        data_dir.mkdir(parents=True, exist_ok=True)

        synopsis_path = self.get_synopsis_path(item)
        synopsis_path.write_text(synopsis.strip(), encoding="utf-8")

    def write_notes(self, item: BinderItem, notes: str, create_snapshot: bool = True) -> None:
        """Write notes for a document.

        Args:
            item: The binder item to update
            notes: The notes text
            create_snapshot: Whether to snapshot existing notes first
        """
        if self.is_locked:
            raise RuntimeError(
                "Project is open in Scrivener. Close Scrivener before writing."
            )

        # Ensure the data directory exists
        data_dir = self.path / "Files" / "Data" / item.uuid
        data_dir.mkdir(parents=True, exist_ok=True)

        notes_path = self.get_notes_path(item)

        # Snapshot existing notes if they exist
        if create_snapshot and notes_path.exists():
            snapshots_dir = self.get_snapshots_path(item)
            snapshots_dir.mkdir(parents=True, exist_ok=True)
            timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
            snapshot_path = snapshots_dir / f"{timestamp} notes-backup.rtf"
            shutil.copy2(notes_path, snapshot_path)

        # Write the notes
        rtf_content = text_to_rtf(notes)
        notes_path.write_text(rtf_content, encoding="utf-8")

    def create_document(
        self,
        title: str,
        parent: BinderItem,
        content: str = "",
        synopsis: str = "",
        include_in_compile: bool = True,
        position: int | None = None,
    ) -> BinderItem:
        """Create a new document in the binder.

        Args:
            title: Title for the new document
            parent: Parent folder to create the document in
            content: Initial content (optional)
            synopsis: Initial synopsis (optional)
            include_in_compile: Whether to include in compile (default: True)
            position: Position among siblings (None = append at end)

        Returns:
            The newly created BinderItem
        """
        if self.is_locked:
            raise RuntimeError(
                "Project is open in Scrivener. Close Scrivener before writing."
            )

        if not parent.is_folder:
            raise ValueError(f"Parent must be a folder: {parent.title}")

        # Generate a new UUID
        new_uuid = str(uuid.uuid4()).upper()

        # Create timestamp in Scrivener's format
        now = datetime.now()
        timestamp = now.strftime("%Y-%m-%d %H:%M:%S -0600")

        # Create the data directory
        data_dir = self.path / "Files" / "Data" / new_uuid
        data_dir.mkdir(parents=True, exist_ok=True)

        # Write initial content if provided
        if content:
            content_path = data_dir / "content.rtf"
            content_path.write_text(text_to_rtf(content), encoding="utf-8")

        # Write synopsis if provided
        if synopsis:
            synopsis_path = data_dir / "synopsis.txt"
            synopsis_path.write_text(synopsis, encoding="utf-8")

        # Now modify the .scrivx XML
        tree = ET.parse(self._scrivx_path)
        root = tree.getroot()

        # Find the parent element in the XML
        parent_elem = self._find_binder_item_element(root, parent.uuid)
        if parent_elem is None:
            raise ValueError(f"Could not find parent in XML: {parent.uuid}")

        # Get or create Children element
        children_elem = parent_elem.find("Children")
        if children_elem is None:
            children_elem = ET.SubElement(parent_elem, "Children")

        # Create the new BinderItem element
        new_elem = ET.Element("BinderItem")
        new_elem.set("UUID", new_uuid)
        new_elem.set("Type", "Text")
        new_elem.set("Created", timestamp)
        new_elem.set("Modified", timestamp)

        # Add Title
        title_elem = ET.SubElement(new_elem, "Title")
        title_elem.text = title

        # Add MetaData
        metadata_elem = ET.SubElement(new_elem, "MetaData")
        compile_elem = ET.SubElement(metadata_elem, "IncludeInCompile")
        compile_elem.text = "Yes" if include_in_compile else "No"

        # Add TextSettings
        text_settings = ET.SubElement(new_elem, "TextSettings")
        text_selection = ET.SubElement(text_settings, "TextSelection")
        text_selection.text = "0,0"

        # Insert at position or append
        if position is not None and position < len(children_elem):
            children_elem.insert(position, new_elem)
        else:
            children_elem.append(new_elem)

        # Update the project's Modified timestamp
        root.set("Modified", timestamp)
        root.set("ModID", str(uuid.uuid4()).upper())

        # Write the XML back (preserve formatting as much as possible)
        self._write_scrivx(tree)

        # Reload the binder to get the new item
        self._binder_items = parse_binder(self._scrivx_path)

        # Return the new item
        new_item = self.find_by_uuid(new_uuid)
        return new_item

    def _find_binder_item_element(self, root: ET.Element, target_uuid: str) -> ET.Element | None:
        """Find a BinderItem element by UUID in the XML tree."""
        for elem in root.iter("BinderItem"):
            if elem.get("UUID") == target_uuid:
                return elem
        return None

    def _write_scrivx(self, tree: ET.ElementTree) -> None:
        """Write the .scrivx XML file with proper formatting."""
        # Add XML declaration and write
        root = tree.getroot()

        # Indent for readability
        self._indent_xml(root)

        # Write with XML declaration
        tree.write(
            self._scrivx_path,
            encoding="UTF-8",
            xml_declaration=True,
        )

    def _indent_xml(self, elem: ET.Element, level: int = 0) -> None:
        """Add indentation to XML elements for readability."""
        indent = "\n" + "    " * level
        if len(elem):
            if not elem.text or not elem.text.strip():
                elem.text = indent + "    "
            if not elem.tail or not elem.tail.strip():
                elem.tail = indent
            for child in elem:
                self._indent_xml(child, level + 1)
            if not child.tail or not child.tail.strip():
                child.tail = indent
        else:
            if level and (not elem.tail or not elem.tail.strip()):
                elem.tail = indent
