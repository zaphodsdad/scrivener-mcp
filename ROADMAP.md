# Scrivener MCP Roadmap

## Current Status: Phase 1 Complete

**Two interfaces to Scrivener projects:**

1. **MCP Server** - For AI clients with tool-calling (Claude Desktop, LibreChat + capable models)
2. **Web App** - For any LLM via API (OpenRouter, Anthropic, OpenAI, etc.) - *In Development*

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   scrivener/ (core library)             │
│         project.py, binder.py, rtf.py                   │
│     The actual Scrivener reading/writing logic          │
└───────────────────┬─────────────────────┬───────────────┘
                    │                     │
        ┌───────────▼───────┐   ┌─────────▼──────────┐
        │   MCP Server      │   │   Web App          │
        │   (server.py)     │   │   (app/)           │
        │                   │   │                    │
        │ Protocol-based    │   │ Browser-based UI   │
        │ Requires tool-    │   │ Works with ANY LLM │
        │ capable models    │   │ No tool-calling    │
        │                   │   │ required           │
        └───────────────────┘   └────────────────────┘
```

**Why two interfaces?**

MCP requires the LLM to understand tool-calling. Testing shows only certain models work:
- ✅ Claude Sonnet 4, GPT-5.1 (via OpenRouter)
- ❌ Claude 3.7, Opus 3, local LLMs (Ollama)

The Web App bypasses this limitation - the app handles all Scrivener operations directly, and the LLM just generates/analyzes text.

---

## MCP Server (Complete)

14 tools for Claude Desktop and tool-capable models.

### Read Tools (9)
| Tool | Description | Status |
|------|-------------|--------|
| `find_projects` | Scan common locations for .scriv projects | ✅ Done |
| `open_project` | Load a project by path | ✅ Done |
| `list_binder` | Show binder structure | ✅ Done |
| `read_document` | Read document content | ✅ Done |
| `search_project` | Full-text search | ✅ Done |
| `get_word_counts` | Word count statistics | ✅ Done |
| `read_manuscript` | Read full manuscript in compile order | ✅ Done |
| `get_synopsis` | Read synopsis/index card | ✅ Done |
| `get_notes` | Read inspector notes | ✅ Done |

### Write Tools (5)
| Tool | Description | Status |
|------|-------------|--------|
| `create_snapshot` | Backup before changes | ✅ Done |
| `write_document` | Update document content | ✅ Done |
| `set_synopsis` | Update synopsis | ✅ Done |
| `set_notes` | Update inspector notes | ✅ Done |
| `create_document` | Create new document in binder | ✅ Done |

### Safety Features
- ✅ Lock detection (refuses writes if Scrivener is open)
- ✅ Auto-snapshot before every write
- ✅ User approval prompts in tool descriptions
- ✅ RTF format preservation

---

## Web App (In Development)

Browser-based interface that works with any LLM.

### MVP Features
| Feature | Description | Status |
|---------|-------------|--------|
| Project browser | Find and open .scriv projects | Planned |
| Binder sidebar | Navigate folders and documents | Planned |
| Document viewer | Read document content | Planned |
| Document editor | Edit with auto-snapshot | Planned |
| AI chat panel | Send context to LLM, get responses | Planned |
| LLM configuration | API key, model selection | Planned |

### How It Works

1. **User navigates** - Click folders/documents in binder sidebar
2. **App fetches** - Calls `ScrivenerProject` methods directly
3. **AI assists** - Selected text + user prompt sent to LLM API
4. **User approves** - Review AI suggestions before applying
5. **App writes** - Changes saved to Scrivener project

The LLM never needs to "call tools" - it just receives text and generates text.

### Supported LLM Providers
- OpenRouter (access to Claude, GPT, Llama, etc.)
- Anthropic API (direct)
- OpenAI API (direct)
- Any OpenAI-compatible API

---

## Future Phases

### Phase 2: Analysis Tools
| Tool | Description |
|------|-------------|
| `check_grammar` | LanguageTool integration |
| `analyze_pov` | Detect POV shifts |
| `consistency_check` | Character description consistency |
| `pacing_analysis` | Scene length, action vs dialogue |

### Phase 3: Character & World Building
| Tool | Description |
|------|-------------|
| `extract_characters` | Build character list from manuscript |
| `get_character_profile` | Read from Research folder |
| `relationship_map` | Who interacts with whom |

### Phase 4: Export & Integration
| Tool | Description |
|------|-------------|
| `export_markdown` | Clean markdown export |
| `export_outline` | Binder as outline |
| `sync_obsidian` | Two-way Obsidian sync |

---

## Platform Support

### MCP Server
| Platform | Client | Status |
|----------|--------|--------|
| macOS | Claude Desktop | ✅ Supported |
| macOS | LibreChat | ✅ Supported (Sonnet 4, GPT-5.1) |
| Windows | Claude Desktop | ✅ Supported |
| Linux | LibreChat | ✅ Supported |

### Web App
| Platform | Status |
|----------|--------|
| Any browser | Planned |

---

## Contributing

See [CLAUDE.md](CLAUDE.md) for technical details on the codebase.
