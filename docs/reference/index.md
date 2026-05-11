# Technical Reference

Exhaustive documentation of the SimpCode interface, configuration, and environment.

---

## CLI Interface (`simp`)

The `simp` command is the main entry point. All commands support the following global options.

### Global Options

| Option | Flag | Description |
| :--- | :--- | :--- |
| **Provider** | `-p`, `--provider` | Override the saved LLM provider for this session. |
| **Model** | `-m`, `--model` | Override the saved model ID for this session. |
| **Verbose** | `--verbose` | Print raw debug logs, including full LLM prompt/response payloads. |
| **Help** | `--help` | Show usage information for any command. |

### Commands

#### `simp setup`
Initializes or updates your global user configuration.
- Stores credentials in `~/.simpcode/config.json`.
- Validates API keys with a test connection.

#### `simp init`
Transforms a standard directory into a SimpCode-aware workspace.
- Creates `SIMP.md` (Project Manifest).
- Creates `AGENT.md` (Behavioral Policy).
- Bootstraps `.simp/wiki/` (Knowledge Base).

#### `simp ask [QUERY]`
Performs semantic search and architectural research.
- **Input**: Natural language question.
- **Output**: Markdown-rendered analysis based on the Semantic Wiki.

#### `simp do [TASK]`
Begins a full engineering lifecycle mission.
- **Input**: Goal description.
- **Logic**: Research -> Plan -> Approval -> Execution -> Sync.

#### `simp chat`
Launches the interactive Rich TUI.
- Supports multiline input.
- Renders code snippets with syntax highlighting.
- Shortcuts: `/exit`, `/clear`.

#### `simp sync`
Manually triggers a re-index of the repository.
- Compares file hashes to Wiki metadata.
- Updates stale knowledge nodes.

---

## Configuration Schema (`config.json`)

Located at `~/.simpcode/config.json`. **Do not check this into version control.**

```json
{
  "provider": "anthropic",
  "model": "claude-3-5-sonnet-latest",
  "api_key": "sk-ant-...",
  "base_url": null,
  "max_context": 128000,
  "temperature": 0
}
```

### Supported Providers:
- `anthropic`: (Recommended) Claude 3.5 Sonnet, Opus.
- `openai`: GPT-4o, GPT-4 Turbo.
- `groq`: Fast Llama-3, Mixtral.
- `google`: Gemini 1.5 Pro/Flash.
- `ollama`: Local model execution (requires `base_url`).

---

## Environment Variables

| Variable | Default | Purpose |
| :--- | :--- | :--- |
| `SIMP_CONFIG_DIR` | `~/.simpcode` | Directory for global configuration. |
| `SIMP_LOG_LEVEL` | `INFO` | Set to `DEBUG` for exhaustive engine internals. |
| `SIMP_CACHE_DIR` | `~/.cache/simpcode` | Location for temporary files and indexes. |

---

## Repository Manifests

### `SIMP.md`
The "Source of Truth" for the project's identity.
- contains: Tech stack, core logic, and high-level structure.
- Created by `init`.

### `AGENT.md`
The "Rules of Engagement."
- contains: Patterns, formatting rules, and constraints.
- Always injected into the LLM system prompt for every turn.
