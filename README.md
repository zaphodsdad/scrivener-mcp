# Scrivener MCP

An MCP server that connects AI assistants to your Scrivener writing projects.

**Status:** MVP Complete (read-only)

## What is this?

[Scrivener](https://www.literatureandlatte.com/scrivener/overview) is a beloved writing app for novelists, screenwriters, and long-form writers. This MCP server lets AI assistants (like Claude) read and understand your Scrivener projects.

Point Claude at your novel and ask:
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

### With Claude Code

Add to your Claude Code MCP configuration (`~/.claude/claude_desktop_config.json`):

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

### Available Tools

| Tool | Description |
|------|-------------|
| `open_project` | Open a Scrivener project by path |
| `list_binder` | Show the binder structure (folders and documents) |
| `read_document` | Read a document by title, path, or UUID |
| `search_project` | Full-text search across all documents |
| `get_word_counts` | Word count statistics by chapter/folder |
| `read_manuscript` | Read the full manuscript in compile order |

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
