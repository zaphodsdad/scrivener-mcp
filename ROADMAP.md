# Scrivener MCP Roadmap

## Current Status: v0.1.0 Ready

A read-only MCP server for Claude Desktop that gives AI access to your Scrivener projects.

**Philosophy:** Write in Scrivener. Ask Claude for help.

---

## What It Does

9 read-only tools for Claude Desktop:

| Tool | Description |
|------|-------------|
| `find_projects` | Scan common locations for .scriv projects |
| `open_project` | Load a project by path |
| `list_binder` | Show binder structure |
| `read_document` | Read document content |
| `search_project` | Full-text search |
| `get_word_counts` | Word count statistics |
| `read_manuscript` | Read full manuscript in compile order |
| `get_synopsis` | Read synopsis/index card |
| `get_notes` | Read inspector notes |

---

## Platform Support

| Platform | Client | Status |
|----------|--------|--------|
| macOS | Claude Desktop | Supported |
| Windows | Claude Desktop | Supported |
| Linux | Claude Desktop | Community build available |

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
- Export to markdown

---

## Contributing

See [CLAUDE.md](CLAUDE.md) for technical details.
