"""MCP Server for Scrivener projects."""

import os
from pathlib import Path

from mcp.server.fastmcp import FastMCP

from .scrivener import ScrivenerProject

# Initialize the MCP server
mcp = FastMCP("scrivener-mcp")

# Global project reference (set via environment or tool)
_project: ScrivenerProject | None = None


def get_project() -> ScrivenerProject:
    """Get the current project, loading from SCRIVENER_PROJECT env var if needed."""
    global _project

    if _project is None:
        project_path = os.environ.get("SCRIVENER_PROJECT")
        if not project_path:
            raise ValueError(
                "No project loaded. Set SCRIVENER_PROJECT environment variable "
                "to the path of your .scriv folder, or use the open_project tool."
            )
        _project = ScrivenerProject(project_path)

    return _project


@mcp.tool()
def open_project(path: str) -> str:
    """Open a Scrivener project.

    Args:
        path: Path to the .scriv folder

    Returns:
        Confirmation message with project info
    """
    global _project

    project_path = Path(path).expanduser().resolve()
    _project = ScrivenerProject(project_path)

    # Check for lock
    lock_warning = ""
    if _project.is_locked:
        lock_warning = "\n⚠️  WARNING: Project appears to be open in Scrivener. Changes may conflict."

    # Count items
    total_items = sum(1 for _ in _project.all_items())
    text_items = sum(1 for item in _project.all_items() if item.is_text)

    return f"""Opened project: {_project.name}
Path: {_project.path}
Total items: {total_items}
Documents: {text_items}{lock_warning}"""


@mcp.tool()
def list_binder(folder_path: str | None = None) -> str:
    """List the binder structure of the Scrivener project.

    Shows the hierarchical structure of folders and documents, similar to
    Scrivener's binder sidebar.

    Args:
        folder_path: Optional path to a specific folder to list (e.g., "Neon Syn/Book One").
                    If not provided, lists the entire binder.

    Returns:
        Tree representation of the binder structure with:
        - 📁 for folders
        - 📄 for documents
        - ✓ for items marked "Include in Compile"
    """
    project = get_project()

    if folder_path:
        item = project.find_by_path(folder_path)
        if not item:
            # Try partial match
            matches = project.find_by_title(folder_path, exact=False)
            if matches:
                item = matches[0]

        if not item:
            return f"Folder not found: {folder_path}"

        return item.to_tree_string()

    return project.get_binder_tree()


@mcp.tool()
def read_document(identifier: str) -> str:
    """Read the content of a specific document.

    Args:
        identifier: Can be one of:
            - Document title (e.g., "Chapter 1")
            - Full path (e.g., "Neon Syn/Book One/Chapter 01/01")
            - UUID (e.g., "BA3D0D3E-0BC5-4E4F-AEB4-D7203A5215C4")

    Returns:
        The plain text content of the document, with metadata header showing
        title, path, and word count.
    """
    project = get_project()

    # Try to find by UUID first (most specific)
    item = project.find_by_uuid(identifier)

    # Try by exact path
    if not item:
        item = project.find_by_path(identifier)

    # Try by exact title
    if not item:
        matches = project.find_by_title(identifier, exact=True)
        if len(matches) == 1:
            item = matches[0]
        elif len(matches) > 1:
            # Multiple matches - return list
            paths = [f"  - {m.path}" for m in matches]
            return f"Multiple documents found with title '{identifier}':\n" + "\n".join(paths) + "\n\nPlease use the full path to specify which one."

    # Try by partial title
    if not item:
        matches = project.find_by_title(identifier, exact=False)
        if len(matches) == 1:
            item = matches[0]
        elif len(matches) > 1:
            paths = [f"  - {m.path}" for m in matches[:10]]
            more = f"\n  ... and {len(matches) - 10} more" if len(matches) > 10 else ""
            return f"Multiple documents match '{identifier}':\n" + "\n".join(paths) + more + "\n\nPlease use the full path to specify which one."

    if not item:
        return f"Document not found: {identifier}"

    if item.is_folder:
        # For folders, show contents
        child_count = sum(1 for _ in item.walk()) - 1
        text_count = sum(1 for c in item.walk() if c.is_text)
        word_count = project.get_word_count(item, recursive=True)

        return f"""📁 {item.title}
Path: {item.path}
Contains: {child_count} items ({text_count} documents)
Total words: {word_count:,}

Contents:
{item.to_tree_string()}"""

    # Read document content
    content = project.read_document(item)
    word_count = project.get_word_count(item)

    return f"""📄 {item.title}
Path: {item.path}
Words: {word_count:,}
Include in Compile: {"Yes" if item.include_in_compile else "No"}

---

{content}"""


@mcp.tool()
def search_project(query: str, case_sensitive: bool = False) -> str:
    """Search for text across all documents in the project.

    Args:
        query: Text or regex pattern to search for
        case_sensitive: Whether to match case (default: False)

    Returns:
        List of matching documents with excerpts showing the matching lines.
    """
    project = get_project()
    results = project.search(query, case_sensitive=case_sensitive)

    if not results:
        return f"No matches found for: {query}"

    output = [f"Found {len(results)} document(s) matching '{query}':\n"]

    for item, matching_lines in results:
        output.append(f"\n📄 {item.path}")

        # Show up to 3 matching lines
        for line in matching_lines[:3]:
            # Truncate long lines
            if len(line) > 100:
                line = line[:100] + "..."
            output.append(f"   • {line}")

        if len(matching_lines) > 3:
            output.append(f"   ... and {len(matching_lines) - 3} more matches")

    return "\n".join(output)


@mcp.tool()
def get_word_counts(folder_path: str | None = None) -> str:
    """Get word count statistics for the project or a specific folder.

    Args:
        folder_path: Optional path to a specific folder. If not provided,
                    shows stats for the entire manuscript (Draft folder).

    Returns:
        Word count breakdown by folder/chapter.
    """
    project = get_project()

    if folder_path:
        item = project.find_by_path(folder_path)
        if not item:
            matches = project.find_by_title(folder_path, exact=False)
            item = matches[0] if matches else None

        if not item:
            return f"Folder not found: {folder_path}"

        root = item
    else:
        root = project.find_draft_folder()
        if not root:
            return "No Draft folder found in project."

    output = [f"Word counts for: {root.title}\n"]
    total = 0

    for item in root.walk():
        if item == root:
            continue

        if item.is_folder:
            folder_count = project.get_word_count(item, recursive=True)
            indent = "  " * (item.depth - root.depth - 1)
            output.append(f"{indent}📁 {item.title}: {folder_count:,} words")
        elif item.is_text:
            doc_count = project.get_word_count(item)
            indent = "  " * (item.depth - root.depth - 1)
            output.append(f"{indent}  📄 {item.title}: {doc_count:,} words")
            total += doc_count

    output.append(f"\n{'='*40}")
    output.append(f"Total: {total:,} words")

    return "\n".join(output)


@mcp.tool()
def read_manuscript(include_titles: bool = True, chapter: str | None = None) -> str:
    """Read the full manuscript or a specific chapter.

    Reads all documents marked "Include in Compile" from the Draft folder,
    in binder order.

    Args:
        include_titles: Whether to include document/folder titles as headings
        chapter: Optional chapter name/path to read just that chapter

    Returns:
        The compiled manuscript text.
    """
    project = get_project()

    if chapter:
        # Find the specific chapter
        item = project.find_by_path(chapter)
        if not item:
            matches = project.find_by_title(chapter, exact=False)
            item = matches[0] if matches else None

        if not item:
            return f"Chapter not found: {chapter}"

        # Read just this chapter
        parts = []
        for child in item.walk():
            if child == item:
                if include_titles:
                    parts.append(f"# {child.title}\n")
                continue

            if child.is_folder and include_titles:
                parts.append(f"\n{'#' * min(child.depth - item.depth + 1, 4)} {child.title}\n")
            elif child.is_text:
                content = project.read_document(child)
                if content:
                    if include_titles:
                        parts.append(f"\n### {child.title}\n")
                    parts.append(content)

        return "\n".join(parts)

    return project.get_manuscript_text(include_titles=include_titles)


def main():
    """Run the MCP server."""
    mcp.run()


if __name__ == "__main__":
    main()
