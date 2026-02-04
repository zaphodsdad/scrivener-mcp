# Scrivener MCP Server

An MCP (Model Context Protocol) server that gives AI assistants access to Scrivener writing projects.

## Project Vision

Allow writers to point Claude (or other AI assistants) at their Scrivener project and:
- "Read my novel, find plot holes"
- "Check character consistency across chapters"
- "Help me write the next scene in my voice"
- "What's my word count by chapter?"
- "Search for everywhere I mention the red door"

## Technical Approach

### Scrivener File Format

A `.scriv` file is actually a folder containing:
```
MyNovel.scriv/
├── Files/
│   └── Data/
│       ├── {UUID}/
│       │   ├── content.rtf    # The actual text
│       │   └── synopsis.txt   # Optional synopsis
│       └── ...
├── Settings/
│   └── ...
├── Snapshots/
│   └── ...
└── project.scrivx            # XML binder structure
```

### Planned MCP Tools

| Tool | Description |
|------|-------------|
| `list_binder` | Show project structure (folders, documents) |
| `read_document` | Read a specific document by title or path |
| `read_characters` | Pull character sheets from Research/Characters |
| `read_world` | Pull world-building notes |
| `search_project` | Full-text search across all documents |
| `get_word_counts` | Word count stats per document/folder |
| `write_document` | Update a document (auto-snapshot first) |
| `create_snapshot` | Manual snapshot before changes |
| `get_compile_contents` | What's marked "include in compile" |

### Constraints

1. **File locking**: Scrivener locks files while open. Options:
   - User closes Scrivener before AI operations
   - Use Scrivener's "Sync with External Folder" feature
   - Read-only mode when Scrivener is open

2. **Platform differences**: Mac and Windows Scrivener are different codebases, but Scrivener 3 unified the .scriv format. Should work cross-platform.

3. **RTF parsing**: Documents are stored as RTF. Need to convert to/from plain text or markdown.

## Tech Stack (Planned)

- **Language**: Python or TypeScript (TBD)
- **MCP SDK**: Official Anthropic MCP SDK
- **RTF handling**: striprtf (Python) or similar
- **XML parsing**: Built-in (ElementTree for Python, xml2js for Node)

## Status

Project scaffolding - not yet functional.

## Related

- [Prometheus](https://github.com/zaphodsdad/prose-pipeline) - AI prose generation tool (same author)
