# Scrivener MCP Server

A read-only MCP server that gives AI assistants access to Scrivener writing projects.

## Project Vision

Allow writers to work in Scrivener while Claude Desktop reads their project to help with:
- "Find plot holes in my novel"
- "Check character consistency across chapters"
- "What's my word count by chapter?"
- "Search for everywhere I mention the red door"
- "Read the synopsis for Chapter 3"

**Philosophy:** Write in Scrivener. Ask Claude for help. All writing stays in Scrivener.

## Technical Details

### Key Finding: External Read Access Works

Scrivener projects can be read outside of Scrivener. ProWritingAid proves this:
- Reads the `.scrivx` XML to reconstruct binder structure
- Directly accesses RTF files at `Files/Data/{UUID}/content.rtf`

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

### .scrivx XML Structure

```xml
<ScrivenerProject Version="2.0" ...>
  <Binder>
    <BinderItem UUID="..." Type="DraftFolder" Created="..." Modified="...">
      <Title>Draft</Title>
      <MetaData>
        <IncludeInCompile>Yes</IncludeInCompile>
      </MetaData>
      <Children>
        <BinderItem UUID="..." Type="Text" ...>
          <Title>Chapter 1</Title>
          ...
        </BinderItem>
      </Children>
    </BinderItem>
  </Binder>
</ScrivenerProject>
```

## Implemented MCP Tools (9)

| Tool | Description |
|------|-------------|
| `find_projects` | Scan common locations (Documents, Dropbox, iCloud) for .scriv projects |
| `open_project` | Load a Scrivener project by path |
| `list_binder` | Show project structure (folders, documents) as tree |
| `read_document` | Read a document by title, path, or UUID |
| `search_project` | Full-text search across all documents |
| `get_word_counts` | Word count stats per document/folder |
| `read_manuscript` | Read all Draft content in compile order |
| `get_synopsis` | Read the synopsis (index card text) for a document |
| `get_notes` | Read the inspector notes for a document |

## Project Structure

```
scrivener-mcp/
├── src/
│   └── scrivener_mcp/
│       ├── __init__.py
│       ├── server.py          # MCP server + all tools
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

Restart Claude Desktop. You can ask things like:
- "Find my Scrivener projects"
- "Open Neon Syn"
- "List the chapters in my novel"
- "Search for mentions of the red door"
- "Read Chapter 5"
- "What's my word count by chapter?"
- "Show me the synopsis for Chapter 3"

## References

- [ProWritingAid Scrivener Integration](https://prowritingaid.com/art/1607/scrivener-and-prowritingaid:-best-practices.aspx)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [striprtf](https://pypi.org/project/striprtf/)
- [Scrivener File Format](https://preservation.tylerthorsted.com/2025/03/21/scrivener/)

## Related Projects

- [prose-pipeline](https://github.com/zaphodsdad/prose-pipeline) - AI-powered prose generation
