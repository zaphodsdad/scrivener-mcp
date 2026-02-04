# Scrivener MCP Server

A read-only MCP server that gives Claude Desktop access to Scrivener writing projects.

## Project Vision

Allow writers to work in Scrivener while Claude reads their project to help with:
- "Scan the project and summarize each chapter"
- "Find plot holes in my novel"
- "Check character consistency across chapters"
- "What's my word count by chapter?"
- "Search for everywhere I mention the red door"

**Philosophy:** Write in Scrivener. Ask Claude for help. All writing stays in Scrivener.

## Implemented MCP Tools (10)

| Tool | Description |
|------|-------------|
| `find_projects` | Scan common locations (Documents, Dropbox, iCloud) for .scriv projects |
| `open_project` | Load a Scrivener project by path |
| `scan_project` | Bird's eye view: chapter titles, word counts, synopses, opening lines |
| `list_binder` | Show project structure (folders, documents) as tree |
| `read_document` | Read a single document by title, path, or UUID |
| `read_chapter` | Read a full chapter with all its scenes |
| `search_project` | Full-text search across all documents |
| `get_word_counts` | Word count stats per document/folder |
| `get_synopsis` | Read the synopsis (index card text) for a document |
| `get_notes` | Read the inspector notes for a document |

## Technical Details

### Scrivener File Format

A `.scriv` file is actually a folder (package on Mac):
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
└── project.scrivx             # XML binder structure
```

### How It Works

1. Parses the `.scrivx` XML to reconstruct binder structure
2. Reads RTF files from `Files/Data/{UUID}/content.rtf`
3. Converts RTF to plain text using `striprtf` library
4. Returns text to Claude for analysis

## Project Structure

```
scrivener-mcp/
├── src/
│   └── scrivener_mcp/
│       ├── __init__.py
│       ├── server.py          # MCP server + all 10 tools
│       └── scrivener/
│           ├── __init__.py
│           ├── project.py     # ScrivenerProject class
│           ├── binder.py      # Binder/BinderItem parsing
│           └── rtf.py         # RTF conversion utilities
├── pyproject.toml
├── README.md
└── CLAUDE.md
```

## Dependencies

```
mcp                 # Official MCP SDK
striprtf            # RTF to text conversion
```

## Quick Start (Mac)

```bash
# Clone and setup
git clone https://github.com/zaphodsdad/scrivener-mcp.git
cd scrivener-mcp
python3 -m venv .venv
source .venv/bin/activate
pip install -e .

# Test it runs
scrivener-mcp  # Ctrl+C to exit
```

## Claude Desktop Configuration

Add to `~/Library/Application Support/Claude/claude_desktop_config.json` (Mac):

```json
{
  "mcpServers": {
    "scrivener": {
      "command": "/path/to/scrivener-mcp/.venv/bin/scrivener-mcp"
    }
  }
}
```

Restart Claude Desktop. Ask things like:
- "Find my Scrivener projects"
- "Open Neon Syn"
- "Scan the project"
- "Read Chapter 5"
- "Search for mentions of the red door"
- "What's my word count by chapter?"

## Recommended Workflow

1. **Open:** "Open my project [name]"
2. **Scan:** "Scan the project" - get overview without loading everything
3. **Dive deep:** "Read Chapter 3" - read specific chapters
4. **Search:** "Search for [term]" - find across all documents
5. **Refresh:** "Re-open the project" - after editing in Scrivener

## References

- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [striprtf](https://pypi.org/project/striprtf/)
- [Scrivener File Format](https://preservation.tylerthorsted.com/2025/03/21/scrivener/)

## Related Projects

- [prose-pipeline](https://github.com/zaphodsdad/prose-pipeline) - AI-powered prose generation
