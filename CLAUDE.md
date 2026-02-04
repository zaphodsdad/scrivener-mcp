# Scrivener MCP Server

An MCP (Model Context Protocol) server that gives AI assistants access to Scrivener writing projects.

## Project Vision

Allow writers to point Claude (or other AI assistants) at their Scrivener project and:
- "Read my novel, find plot holes"
- "Check character consistency across chapters"
- "Help me write the next scene in my voice"
- "What's my word count by chapter?"
- "Search for everywhere I mention the red door"

## Key Finding: External Access Works

**Scrivener projects can be opened outside of Scrivener.** ProWritingAid proves this:
- Reads the `.scrivx` XML to reconstruct binder structure
- Directly accesses RTF files at `Files/Data/{UUID}/content.rtf`
- Changes sync back when Scrivener reopens

**Constraint:** Project must be closed in Scrivener. A `user.lock` file inside the `.scriv` package indicates an open project. We detect this and handle it.

## Technical Decisions

- **Language:** Python
- **MCP SDK:** Official Python SDK with FastMCP interface
- **RTF Handling:** `striprtf` library (91K weekly downloads, actively maintained)
- **XML Parsing:** Built-in `xml.etree.ElementTree`
- **Scope:** Full CRUD with snapshot safety measures

## Scrivener File Format

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
├── user.lock                  # Present when open in Scrivener
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

## Implemented MCP Tools (14 total)

### Read Tools (9)

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

### Write Tools (5)

| Tool | Description |
|------|-------------|
| `create_snapshot` | Create a backup snapshot before making changes |
| `write_document` | Update document content (auto-snapshot first) |
| `set_synopsis` | Update a document's synopsis (index card text) |
| `set_notes` | Update a document's inspector notes |
| `create_document` | Create a new document in a folder |

## Planned Tools (See ROADMAP.md)

| Tool | Description |
|------|-------------|
| `check_grammar` | LanguageTool integration for grammar/style checking |
| `get_characters` | Extract character sheets from Research folder |
| `analyze_pov` | Detect POV shifts and inconsistencies |
| `export_markdown` | Export project to markdown files |

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

## Safety Measures

- **Lock detection:** Checks for `user.lock` and refuses writes if project is open in Scrivener
- **Auto-snapshot:** Creates backup snapshot before every write operation
- **User approval:** Write tools instruct AI to show content and get user approval before writing
- **RTF preservation:** Converts plain text to proper RTF format for Scrivener compatibility

## Dependencies

```
mcp                 # Official MCP SDK
striprtf            # RTF to text conversion
```

## Status

**Phase 1 Complete** - 14 tools working (9 read + 5 write). See ROADMAP.md for upcoming features.

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

## Running the Server

### Transport Modes

The server supports two transport modes:

```bash
scrivener-mcp              # stdio mode (default, for Claude Desktop)
scrivener-mcp --http       # HTTP mode on port 8000 (for ChatGPT/remote)
scrivener-mcp --http --port 9000 --host 127.0.0.1  # Custom port/host
```

### Option 1: Environment variable
```bash
export SCRIVENER_PROJECT="/path/to/Your Novel.scriv"
scrivener-mcp
```

### Option 2: No config needed
Just run `scrivener-mcp` and use `find_projects` or `open_project` tools via the AI assistant.

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

Note: `SCRIVENER_PROJECT` env var is optional. Without it, use `find_projects` to discover projects.

Then restart Claude Desktop. You can ask things like:
- "Find my Scrivener projects"
- "Open Neon Syn"
- "List the chapters in my novel"
- "Search for mentions of the red door"
- "Read Chapter 5"
- "What's my word count by chapter?"
- "Show me the synopsis for Chapter 3"

## LibreChat Configuration

LibreChat supports MCP via SSE transport. Run the server in HTTP mode:

### Step 1: Start HTTP server
```bash
source .venv/bin/activate
export SCRIVENER_PROJECT="/path/to/Your Novel.scriv"
python -c "
import uvicorn
from scrivener_mcp.server import mcp
app = mcp.sse_app()
uvicorn.run(app, host='0.0.0.0', port=8000)
"
```

### Step 2: Configure LibreChat
Add to `librechat.yaml`:
```yaml
mcpSettings:
  allowedDomains:
    - 'host.docker.internal'  # For Docker
    - 'localhost'

mcpServers:
  scrivener:
    type: sse
    url: http://host.docker.internal:8000/sse  # Docker
    # url: http://localhost:8000/sse           # Native install
```

> **Note:** ChatGPT is *not* an MCP client and does not support MCP servers.

---

## Future: scrivener-lite (Planned Separate Project)

A lightweight Scrivener editor with AI chat - the GUI counterpart to this MCP server.

### Vision

```
┌─────────────────────────────────────────────────────────────┐
│  scrivener-lite                                    [─][□][×]│
├──────────────┬──────────────────────────────────────────────┤
│ 📁 Neon Syn  │  Chapter 01 - The Dead Don't Die             │
│  📁 Book One │  ─────────────────────────────────────────── │
│    📄 Ch 01  │  I can't remember my name, but I remember    │
│    📄 Ch 02  │  hers. She died screaming mine. Like a       │
│    📄 Ch 03  │  Logos. Like the universe bent to her will   │
│  📁 Book Two │  one last time...                            │
│    📄 Ch 10  │                                              │
│    📄 Ch 11  │                                              │
│              ├──────────────────────────────────────────────┤
│              │ 💬 AI Chat                                   │
│              │ ──────────────────────────────────────────── │
│              │ You: Is this scene consistent with Ch 3?     │
│              │ AI: Yes, the "Logos" reference connects to...│
│              │                                              │
│              │ [____________________________] [Send]        │
└──────────────┴──────────────────────────────────────────────┘
```

### Scope (Keep It Minimal)

**Include:**
- Binder sidebar (read from .scrivx)
- Text editor (read/write RTF)
- AI chat panel (context-aware)
- Lock detection + snapshots

**Exclude (save for prose-pipeline):**
- Generation from scratch
- Critique-revision loop
- Character/world management
- Series system

### Tech Stack

- **Backend:** FastAPI (like prose-pipeline)
- **Frontend:** Vanilla HTML/CSS/JS (like prose-pipeline)
- **Scrivener parsing:** Import from scrivener-mcp or copy module
- **AI:** Claude API via OpenRouter

### Why Separate?

1. Portfolio diversity - shows range
2. Focused scope - one job done well
3. De-risks prose-pipeline - experiment freely
4. Later integration - merge into prose-pipeline when proven

---

## References

- [ProWritingAid Scrivener Integration](https://prowritingaid.com/art/1607/scrivener-and-prowritingaid:-best-practices.aspx)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [striprtf](https://pypi.org/project/striprtf/)
- [Scrivener File Format](https://preservation.tylerthorsted.com/2025/03/21/scrivener/)

## Related Projects

- [Prometheus/prose-pipeline](https://github.com/zaphodsdad/prose-pipeline) - Full AI writing suite
- scrivener-lite (planned) - Lightweight Scrivener editor with AI chat
