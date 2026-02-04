# Scrivener MCP

A read-only MCP server that connects AI assistants to your Scrivener writing projects.

Work in Scrivener, ask Claude for help. Claude can see your entire project - structure, content, notes, synopses - but all writing happens in Scrivener where it belongs.

## What can it do?

Point your AI assistant at your novel and ask:
- "Find inconsistencies in my character descriptions"
- "What plot threads are unresolved?"
- "Where do I mention the lighthouse?"
- "What's my word count by chapter?"
- "Read the synopsis for Chapter 3"

## Supported Platforms

| Platform | Client | Status |
|----------|--------|--------|
| macOS | Claude Desktop | Supported |
| Windows | Claude Desktop | Supported |
| Linux | Claude Desktop | [Community build](https://github.com/aaddrick/claude-desktop-debian) |

> **Note:** This is designed for Claude Desktop. Other MCP clients may work but are untested.

## Requirements

- Python 3.10+
- Scrivener 3 project (.scriv folder)
- Claude Desktop

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

## Setup with Claude Desktop

Add to your config file:
- **Mac:** `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows:** `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "scrivener": {
      "command": "/path/to/scrivener-mcp/.venv/bin/scrivener-mcp"
    }
  }
}
```

Restart Claude Desktop. That's it.

## Available Tools (9)

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

## Example Prompts

Once connected, try:

- "Find my Scrivener projects"
- "Open [your project name]"
- "List the chapters in my novel"
- "Read Chapter 1"
- "Search for mentions of 'red door'"
- "What's my word count by chapter?"
- "Show me the synopsis for Chapter 3"
- "Read the manuscript and find plot holes"

## How It Works

Scrivener projects are actually folders containing:
- A `.scrivx` XML file (the binder structure)
- RTF files for each document (`Files/Data/{UUID}/content.rtf`)

This server parses the XML to understand your project structure, then reads and converts the RTF files to plain text for the AI to analyze.

## Why Read-Only?

Scrivener is excellent software. Write in Scrivener. Use this MCP to give Claude context about your work so it can help you think through problems, find inconsistencies, and answer questions about your manuscript.

All writing stays in Scrivener where it belongs.

## Limitations

- Scrivener 3 format only (Scrivener 1/2 not tested)
- Some RTF formatting may not convert perfectly
- Read-only by design

## Related Projects

- [prose-pipeline](https://github.com/zaphodsdad/prose-pipeline) - AI-powered prose generation

## License

MIT
