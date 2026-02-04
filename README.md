# Scrivener MCP

An MCP server that connects AI assistants to your Scrivener writing projects.

**Status:** MVP Complete (read-only) | [See Roadmap](ROADMAP.md)

## Supported Platforms

| Platform | Client | Status |
|----------|--------|--------|
| macOS | Claude Desktop | Supported |
| macOS | LibreChat | Supported |
| Windows | Claude Desktop | Supported |
| Windows | LibreChat (Docker/WSL) | Supported |
| Linux | LibreChat | Supported |
| Linux | Claude Desktop | [Community build](https://github.com/aaddrick/claude-desktop-debian) |

> **Note:** ChatGPT is *not* an MCP client and does not support MCP servers.

## What is this?

[Scrivener](https://www.literatureandlatte.com/scrivener/overview) is a beloved writing app for novelists, screenwriters, and long-form writers. This MCP server lets AI assistants read and understand your Scrivener projects.

Point your AI assistant at your novel and ask:
- "Find inconsistencies in my character descriptions"
- "What plot threads are unresolved?"
- "Help me write the next scene"
- "Where do I mention the lighthouse?"

## Requirements

- Python 3.10+
- Scrivener 3 project (.scriv folder)
- **Important:** Close your project in Scrivener before using this tool

## Installation

```bash
# Clone the repo
git clone https://github.com/zaphodsdad/scrivener-mcp.git
cd scrivener-mcp

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install
pip install -e .
```

## Usage

### With Claude Desktop (Mac/Windows)

Add to your config file:
- **Mac:** `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows:** `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "scrivener": {
      "command": "/path/to/scrivener-mcp/.venv/bin/scrivener-mcp",
      "env": {
        "SCRIVENER_PROJECT": "/path/to/your/Novel.scriv"
      }
    }
  }
}
```

Restart Claude Desktop. The `SCRIVENER_PROJECT` env var is optional - you can use `find_projects` or `open_project` tools instead.

### With LibreChat

LibreChat supports MCP via SSE transport. You need to run the server in HTTP mode.

**Step 1: Start the MCP server**
```bash
cd scrivener-mcp
source .venv/bin/activate
export SCRIVENER_PROJECT="/path/to/your/Novel.scriv"

# Run with SSE transport
python -c "
import uvicorn
from scrivener_mcp.server import mcp
app = mcp.sse_app()
uvicorn.run(app, host='0.0.0.0', port=8000)
"
```

**Step 2: Configure LibreChat**

Add to `librechat.yaml`:
```yaml
version: 1.2.1

mcpSettings:
  allowedDomains:
    - 'host.docker.internal'  # For Docker on Mac/Windows
    - 'localhost'

mcpServers:
  scrivener:
    type: sse
    url: http://host.docker.internal:8000/sse  # Docker
    # url: http://localhost:8000/sse           # Native install
```

Restart LibreChat and the MCP tools will be available.

### Available Tools

| Tool | Description |
|------|-------------|
| `find_projects` | Scan common locations for Scrivener projects |
| `open_project` | Open a Scrivener project by path |
| `list_binder` | Show the binder structure (folders and documents) |
| `read_document` | Read a document by title, path, or UUID |
| `search_project` | Full-text search across all documents |
| `get_word_counts` | Word count statistics by chapter/folder |
| `read_manuscript` | Read the full manuscript in compile order |
| `get_synopsis` | Read the synopsis (index card text) for a document |
| `get_notes` | Read the inspector notes for a document |

### Example Prompts

Once connected, you can ask things like:

- "List the chapters in my novel"
- "Read Chapter 1"
- "Search for mentions of 'red door'"
- "What's my word count by chapter?"
- "Show me the synopsis for Chapter 3"

## How It Works

Scrivener projects are actually folders containing:
- A `.scrivx` XML file (the binder structure)
- RTF files for each document (`Files/Data/{UUID}/content.rtf`)

This server parses the XML to understand your project structure, then reads and converts the RTF files to plain text for the AI to analyze.

**Safety:** The server detects if Scrivener has the project open (via `user.lock` file) and warns you to avoid conflicts.

## Roadmap

See [ROADMAP.md](ROADMAP.md) for planned features including:
- Write operations (edit scenes, update synopses)
- Grammar checking (LanguageTool integration)
- Character extraction and profiling
- Export to markdown

## Limitations

- **Read-only for now** - write operations coming soon (see roadmap)
- Scrivener 3 format only (Scrivener 1/2 not tested)
- Some RTF formatting may not convert perfectly

## Related Projects

- [Prometheus](https://github.com/zaphodsdad/prose-pipeline) - AI-powered prose generation for storytellers

## License

MIT
