"""Binder parsing for Scrivener projects."""

from __future__ import annotations

import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterator


@dataclass
class BinderItem:
    """A single item in the Scrivener binder (document or folder)."""

    uuid: str
    title: str
    item_type: str  # "Text", "Folder", "DraftFolder", "ResearchFolder", "TrashFolder"
    created: str | None = None
    modified: str | None = None
    include_in_compile: bool = False
    children: list[BinderItem] = field(default_factory=list)
    parent: BinderItem | None = field(default=None, repr=False)

    @property
    def is_folder(self) -> bool:
        """Check if this item is a folder type."""
        return self.item_type in ("Folder", "DraftFolder", "ResearchFolder", "TrashFolder")

    @property
    def is_text(self) -> bool:
        """Check if this item is a text document."""
        return self.item_type == "Text"

    @property
    def is_draft(self) -> bool:
        """Check if this item is part of the manuscript (Draft folder)."""
        return self.item_type == "DraftFolder"

    @property
    def path(self) -> str:
        """Get the full path from root to this item (e.g., 'Draft/Chapter 1/Scene 1')."""
        parts = []
        current: BinderItem | None = self
        while current is not None:
            parts.append(current.title)
            current = current.parent
        return "/".join(reversed(parts))

    @property
    def depth(self) -> int:
        """Get the depth of this item in the tree (0 = root level)."""
        count = 0
        current = self.parent
        while current is not None:
            count += 1
            current = current.parent
        return count

    def walk(self) -> Iterator[BinderItem]:
        """Iterate over this item and all descendants depth-first."""
        yield self
        for child in self.children:
            yield from child.walk()

    def find_by_title(self, title: str, exact: bool = True) -> list[BinderItem]:
        """Find all items matching the given title."""
        results = []
        for item in self.walk():
            if exact and item.title == title:
                results.append(item)
            elif not exact and title.lower() in item.title.lower():
                results.append(item)
        return results

    def find_by_uuid(self, uuid: str) -> BinderItem | None:
        """Find an item by its UUID."""
        for item in self.walk():
            if item.uuid == uuid:
                return item
        return None

    def to_tree_string(self, indent: str = "  ") -> str:
        """Return a tree representation of this item and its children."""
        lines = []
        for item in self.walk():
            prefix = indent * item.depth
            type_marker = "📁" if item.is_folder else "📄"
            compile_marker = "✓" if item.include_in_compile else " "
            lines.append(f"{prefix}{type_marker} [{compile_marker}] {item.title}")
        return "\n".join(lines)


def parse_binder_item(element: ET.Element, parent: BinderItem | None = None) -> BinderItem:
    """Parse a BinderItem XML element into a BinderItem object."""
    uuid = element.get("UUID", "")
    item_type = element.get("Type", "Text")
    created = element.get("Created")
    modified = element.get("Modified")

    # Get title
    title_elem = element.find("Title")
    title = title_elem.text if title_elem is not None and title_elem.text else "Untitled"

    # Check if included in compile
    include_in_compile = False
    metadata = element.find("MetaData")
    if metadata is not None:
        include_elem = metadata.find("IncludeInCompile")
        if include_elem is not None and include_elem.text:
            include_in_compile = include_elem.text.lower() == "yes"

    item = BinderItem(
        uuid=uuid,
        title=title,
        item_type=item_type,
        created=created,
        modified=modified,
        include_in_compile=include_in_compile,
        parent=parent,
    )

    # Parse children
    children_elem = element.find("Children")
    if children_elem is not None:
        for child_elem in children_elem.findall("BinderItem"):
            child = parse_binder_item(child_elem, parent=item)
            item.children.append(child)

    return item


def parse_binder(scrivx_path: Path) -> list[BinderItem]:
    """Parse the .scrivx file and return the root binder items."""
    tree = ET.parse(scrivx_path)
    root = tree.getroot()

    binder = root.find("Binder")
    if binder is None:
        return []

    items = []
    for item_elem in binder.findall("BinderItem"):
        items.append(parse_binder_item(item_elem))

    return items
