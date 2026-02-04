# Scrivener MCP

An MCP server that connects AI assistants to your Scrivener writing projects.

**Status:** MVP Complete (read-only)

**Supported Clients:** Claude Desktop, ChatGPT, LibreChat, and any MCP-compatible assistant

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

### Transport Modes

The server supports two transport modes:

- **stdio** (default): For Claude Desktop and local MCP clients
- **HTTP**: For ChatGPT and remote clients

```bash
scrivener-mcp              # stdio mode (Claude Desktop)
scrivener-mcp --http       # HTTP mode on port 8000
scrivener-mcp --http --port 9000  # HTTP mode on custom port
```

### With Claude Desktop

Add to `~/Library/Application Support/Claude/claude_desktop_config.json` (Mac):

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

Or use the `open_project` tool to set the project path dynamically.

### With ChatGPT

ChatGPT requires an HTTP server accessible from the internet. You'll need to expose your local server using a tunnel (Cloudflare Tunnel, ngrok, etc.).

**Step 1: Start the HTTP server**
```bash
source /path/to/scrivener-mcp/.venv/bin/activate
export SCRIVENER_PROJECT="/path/to/your/Novel.scriv"
scrivener-mcp --http --port 8000
```

**Step 2: Expose via Cloudflare Tunnel** (recommended)
```bash
# Install cloudflared
brew install cloudflared  # or apt install cloudflared

# Quick tunnel (random URL, no account needed)
cloudflared tunnel --url http://localhost:8000

# Or set up a persistent tunnel with your domain
cloudflared tunnel create scrivener
cloudflared tunnel route dns scrivener mcp.yourdomain.com
cloudflared tunnel run scrivener
```

**Step 3: Configure ChatGPT**
1. Open ChatGPT Desktop
2. Go to Settings → Connectors → Advanced → Developer mode
3. Add your MCP server URL (e.g., `https://mcp.yourdomain.com/mcp`)

### With LibreChat

LibreChat has native MCP support. Add to your `librechat.yaml`:

```yaml
mcpServers:
  scrivener:
    command: /path/to/scrivener-mcp/.venv/bin/scrivener-mcp
    env:
      SCRIVENER_PROJECT: /path/to/your/Novel.scriv
```

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

Once connected, you can ask Claude things like:

- "List the chapters in my novel"
- "Read Chapter 1"
- "Search for mentions of 'red door'"
- "What's my word count by chapter?"
- "Read the full manuscript"

## How It Works

Scrivener projects are actually folders containing:
- A `.scrivx` XML file (the binder structure)
- RTF files for each document (`Files/Data/{UUID}/content.rtf`)

This server parses the XML to understand your project structure, then reads and converts the RTF files to plain text for the AI to analyze.

**Safety:** The server detects if Scrivener has the project open (via `user.lock` file) and warns you to avoid conflicts.

## Limitations

- **Read-only for now** - write operations coming soon
- Scrivener 3 format only (Scrivener 1/2 not tested)
- Some RTF formatting may not convert perfectly

## Related Projects

- [Prometheus](https://github.com/zaphodsdad/prose-pipeline) - AI-powered prose generation for storytellers

## License

MIT
