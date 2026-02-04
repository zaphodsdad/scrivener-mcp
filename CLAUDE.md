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

## Planned MCP Tools

| Tool | Priority | Description |
|------|----------|-------------|
| `list_binder` | P0 | Show project structure (folders, documents) |
| `read_document` | P0 | Read a specific document by title or path |
| `search_project` | P0 | Full-text search across all documents |
| `get_word_counts` | P1 | Word count stats per document/folder |
| `read_manuscript` | P1 | Read all Draft content in compile order |
| `read_characters` | P2 | Pull character sheets from Research/Characters |
| `write_document` | P2 | Update a document (auto-snapshot first) |
| `create_snapshot` | P2 | Manual snapshot before changes |

## Project Structure

```
scrivener-mcp/
├── src/
│   └── scrivener_mcp/
│       ├── __init__.py
│       ├── server.py          # MCP server entry point
│       ├── scrivener/
│       │   ├── __init__.py
│       │   ├── project.py     # ScrivenerProject class
│       │   ├── binder.py      # Binder/BinderItem parsing
│       │   ├── document.py    # Document reading/writing
│       │   └── rtf.py         # RTF conversion utilities
│       └── tools/
│           ├── __init__.py
│           ├── list_binder.py
│           ├── read_document.py
│           ├── search.py
│           └── ...
├── tests/
│   ├── fixtures/              # Sample .scriv project for testing
│   └── ...
├── pyproject.toml
└── README.md
```

## Implementation Phases

### Phase 1: Core Parsing
1. Parse `.scrivx` XML into Python objects
2. Read RTF content and convert to plain text
3. Build document tree with titles, paths, UUIDs
4. Detect lock files

### Phase 2: MCP Server + Read Tools
1. Set up MCP server with FastMCP
2. Implement `list_binder`, `read_document`, `search_project`
3. Test with Claude Code

### Phase 3: Enhanced Read Features
1. `get_word_counts`
2. `read_manuscript` (compile order)
3. Character/world reading from Research folder

### Phase 4: Write Operations
1. Snapshot creation before any write
2. `write_document` implementation
3. RTF generation/preservation

## Safety Measures

- **Lock detection:** Check for `user.lock` before any operation
- **Auto-snapshot:** Create snapshot before every write
- **RTF preservation:** Keep original formatting when possible
- **Validation:** Verify binder integrity after writes

## Dependencies

```
mcp                 # Official MCP SDK
striprtf            # RTF to text conversion
```

## Status

**MVP Complete** - Core read functionality working.

## Test Project

```
/root/scrivener-mcp/Scrivner Projects/Neon Syn .scriv
```

- 228 total items, 187 text documents
- 64,885 words across 3 books
- Scrivener 3.4 Mac format

## Running the Server

```bash
# Activate venv
source .venv/bin/activate

# Set project path
export SCRIVENER_PROJECT="/root/scrivener-mcp/Scrivner Projects/Neon Syn .scriv"

# Run server
scrivener-mcp
```

Or configure in Claude Code's MCP settings.

## Claude Desktop Configuration

Add to `~/Library/Application Support/Claude/claude_desktop_config.json` (Mac):

```json
{
  "mcpServers": {
    "scrivener": {
      "command": "/path/to/scrivener-mcp/.venv/bin/scrivener-mcp",
      "env": {
        "SCRIVENER_PROJECT": "/path/to/Your Novel.scriv"
      }
    }
  }
}
```

Then restart Claude Desktop. You can ask things like:
- "List the chapters in my novel"
- "Search for mentions of the red door"
- "Read Chapter 5"
- "What's my word count by chapter?"

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
