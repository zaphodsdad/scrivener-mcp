# Scrivener MCP Roadmap

## Current Status: v0.1.0 - Ready for Release

A read-only MCP server for Claude Desktop that gives AI access to your Scrivener projects.

**Philosophy:** Write in Scrivener. Ask Claude for help.

---

## What It Does

10 read-only tools for Claude Desktop:

| Tool | Description |
|------|-------------|
| `find_projects` | Scan common locations for .scriv projects |
| `open_project` | Load a project by path |
| `scan_project` | Bird's eye view: titles, word counts, synopses, opening lines |
| `list_binder` | Show binder structure |
| `read_document` | Read a single document |
| `read_chapter` | Read a full chapter with all scenes |
| `search_project` | Full-text search across all documents |
| `get_word_counts` | Word count statistics |
| `get_synopsis` | Read synopsis/index card |
| `get_notes` | Read inspector notes |

---

## Platform Support

| Platform | Client | Status |
|----------|--------|--------|
| macOS | Claude Desktop | Supported |
| Windows | Claude Desktop | Supported |

---

## Related Projects

| Project | Purpose |
|---------|---------|
| **scrivener-mcp** | Read-only AI companion for Scrivener |
| **[prose-pipeline](https://github.com/zaphodsdad/prose-pipeline)** | AI prose generation from outlines |

**Different tools for different jobs:**
- **scrivener-mcp**: "Help me understand my manuscript" (analysis)
- **prose-pipeline**: "Write this for me" (generation)

---

## Future Possibilities

These are ideas, not commitments:

- PyPI package (`pip install scrivener-mcp`)
- Additional metadata tools (labels, status)

---

## Contributing

See [CLAUDE.md](CLAUDE.md) for technical details.
