# Scrivener MCP Roadmap

## Current Status: MVP Complete (Read-Only)

9 tools implemented for reading Scrivener projects.

---

## Phase 1: Write Operations (Priority: High)

Enable AI to modify Scrivener projects safely.

| Tool | Description | Status |
|------|-------------|--------|
| `create_snapshot` | Manual backup before changes | Planned |
| `write_document` | Update scene text (auto-snapshot) | Planned |
| `set_synopsis` | Update index card summary | Planned |
| `set_notes` | Update inspector notes | Planned |
| `create_document` | Add new scene/chapter to binder | Planned |
| `move_document` | Reorganize binder structure | Planned |
| `delete_document` | Remove document (with confirmation) | Planned |

**Safety measures:**
- Auto-snapshot before any write operation
- Lock file detection (warn if Scrivener is open)
- RTF format preservation where possible

---

## Phase 2: Analysis Tools (Priority: High)

Help writers identify issues in their manuscript.

| Tool | Description | Status |
|------|-------------|--------|
| `check_grammar` | LanguageTool integration | Planned |
| `find_adverbs` | Flag -ly words, weak verbs, passive voice | Planned |
| `analyze_pov` | Detect POV shifts within scenes | Planned |
| `consistency_check` | Compare character descriptions across chapters | Planned |
| `timeline_extract` | Pull dates/times, flag contradictions | Planned |
| `pacing_analysis` | Scene length, action vs dialogue ratio | Planned |

**Dependencies:**
- LanguageTool (free, self-hostable Java app or API)

---

## Phase 3: Character & World Building (Priority: Medium)

Automated extraction and management of story elements.

| Tool | Description | Status |
|------|-------------|--------|
| `extract_characters` | Scan manuscript, build character list | Planned |
| `get_character_profile` | Read from Research folder | Planned |
| `create_character_sheet` | Generate profile from scene mentions | Planned |
| `update_character_sheet` | Add new info to existing profile | Planned |
| `extract_locations` | Find all places mentioned | Planned |
| `relationship_map` | Who interacts with whom, where | Planned |
| `extract_timeline` | Build chronological event list | Planned |

---

## Phase 4: Export & Integration (Priority: Medium)

Connect Scrivener to other tools and formats.

| Tool | Description | Status |
|------|-------------|--------|
| `export_markdown` | Scene/chapter as clean markdown | Planned |
| `export_outline` | Binder as markdown outline | Planned |
| `diff_versions` | Compare current to snapshot | Planned |
| `compile_manuscript` | Full export with format options | Planned |
| `sync_obsidian` | Two-way sync with Obsidian vault | Planned |

---

## Phase 5: Advanced Features (Priority: Low)

Nice-to-have features for power users.

| Tool | Description | Status |
|------|-------------|--------|
| `batch_operations` | Apply changes to multiple documents | Planned |
| `template_apply` | Apply scene template to new documents | Planned |
| `word_frequency` | Analyze word/phrase repetition | Planned |
| `reading_level` | Flesch-Kincaid and other metrics | Planned |
| `dialogue_extraction` | Pull all dialogue for a character | Planned |

---

## External Integrations

| Integration | Purpose | Status |
|-------------|---------|--------|
| **LanguageTool** | Grammar/style checking (free) | Planned |
| **ProWritingAid API** | Advanced style analysis | Considering |
| **Obsidian** | World-building notes sync | Considering |
| **Airtable/Notion** | Character/plot databases | Considering |

---

## Platform Support

| Platform | Client | Status |
|----------|--------|--------|
| macOS | Claude Desktop | Supported |
| macOS | LibreChat (Docker) | Supported |
| Windows | Claude Desktop | Supported |
| Windows | LibreChat (Docker/WSL) | Supported |
| Linux | LibreChat | Supported |
| Linux | Claude Desktop | Community build available |

---

## Contributing

Want to help? Pick an item from Phase 1 or 2 and submit a PR!

See [CLAUDE.md](CLAUDE.md) for technical details on the codebase.
