# Scrivener MCP

A read-only MCP server that connects Claude Desktop to your Scrivener writing projects.

Work in Scrivener, ask Claude for help. Claude can see your entire project - structure, content, notes, synopses - but all writing happens in Scrivener where it belongs.

## What can it do?

Point Claude at your novel and ask:
- "Scan the project and give me an overview"
- "Find inconsistencies in my character descriptions"
- "What plot threads are unresolved?"
- "Where do I mention the lighthouse?"
- "What's my word count by chapter?"
- "Read Chapter 3"

## Supported Platforms

| Platform | Client | Status |
|----------|--------|--------|
| macOS | Claude Desktop | Supported |
| Windows | Claude Desktop | Supported |

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

## Available Tools (10)

| Tool | Description |
|------|-------------|
| `find_projects` | Scan common locations for Scrivener projects |
| `open_project` | Open a Scrivener project by path |
| `scan_project` | Get bird's eye view: chapter titles, word counts, synopses, opening lines |
| `list_binder` | Show the binder structure (folders and documents) |
| `read_document` | Read a single document by title, path, or UUID |
| `read_chapter` | Read a full chapter with all its scenes |
| `search_project` | Full-text search across all documents |
| `get_word_counts` | Word count statistics by chapter/folder |
| `get_synopsis` | Read the synopsis (index card text) for a document |
| `get_notes` | Read the inspector notes for a document |

## Recommended Workflow

1. **Open project:** "Open my Scrivener project Neon Syn"
2. **Scan for overview:** "Scan the project" - gives chapter summaries without loading everything
3. **Dive deeper:** "Read Chapter 3" - read specific chapters as needed
4. **Search:** "Search for mentions of the red door" - searches all documents
5. **If you edit in Scrivener:** "Re-open the project" to refresh

## Example Prompts

- "Find my Scrivener projects"
- "Open [project name]"
- "Scan the project and summarize each chapter"
- "Read Chapter 1"
- "Search for mentions of 'lighthouse'"
- "What's my word count by chapter?"
- "Show me the synopsis for Chapter 3"
- "Find plot holes based on the chapter summaries"

## How It Works

Scrivener projects are folders containing:
- A `.scrivx` XML file (the binder structure)
- RTF files for each document (`Files/Data/{UUID}/content.rtf`)

This server parses the XML to understand your project structure, then reads and converts the RTF files to plain text for Claude to analyze.

## Why Read-Only?

Scrivener is excellent software. Write in Scrivener. Use this MCP to give Claude context about your work so it can help you think through problems, find inconsistencies, and answer questions about your manuscript.

All writing stays in Scrivener where it belongs.

## Limitations

- Scrivener 3 format only (Scrivener 1/2 not tested)
- Some RTF formatting may not convert perfectly
- Read-only by design
- Re-open project to see changes made in Scrivener

## Related Projects

- [prose-pipeline](https://github.com/zaphodsdad/prose-pipeline) - AI-powered prose generation

## License

MIT
