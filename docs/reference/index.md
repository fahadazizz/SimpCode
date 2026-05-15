# SimpCode Reference

This reference describes the current implementation behavior and interfaces.

## 1. CLI Commands

### `simp`

Run with no subcommand to launch the interactive TUI shell.

Options available at root invocation:

- `--provider <name>`: override provider for this launch.
- `--model <model-id>`: override model for this launch.
- `--session <session-id>`: load a specific session.
- `--new`: force a new session ID.

### `simp setup`

Interactive global provider setup.

Prompts for:

- provider name (`groq`, `anthropic`, `openai`, `openrouter`, `google`, `ollama`)
- model ID
- API key (except for `ollama`)
- base URL for `ollama`

Writes configuration via ConfigManager writable path resolution.

### `simp init`

Initializes project onboarding artifacts when needed, then enters TUI.

### `simp ask <query>`

Non-mutating research question execution through workflow ask mode.

### `simp do <task> [--yes] [--dry-run]`

Plan-driven task execution.

- `--dry-run`: generate/review plan only, no execution.
- `--yes`: skip approval prompt.

### `simp sync`

Synchronizes stale wiki pages against source hashes.

### `simp status`

Displays project and wiki freshness summary.

### `simp wiki <args>`

Delegates to wiki command handler used in TUI.

### `simp recover`

Attempts recovery by loading most recent saved plan artifact.

## 2. TUI Slash Commands

- `/ask <query>`
- `/do <task> [--yes] [--dry-run]`
- `/sync`
- `/status`
- `/recover`
- `/init`
- `/wiki list`
- `/wiki show <page-id>`
- `/wiki search <keyword>` (placeholder, not fully implemented)

 - `/wiki search <keyword>` — command handler may be incomplete; verify availability with `simp --help` or in the CLI source.
- `/config`
- `/config --provider <name>`
- `/config --model <model-id>`
- `/sessions`
- `/sessions --switch <session-id>`
- `/simp show`
- `/simp update <instruction>`
- `/clear`
- `/help`
- `/exit`

## 3. Session Data Model

Persisted session fields include:

- `session_id`
- `project_root`
- `history[]` (role/content/timestamp)
- `current_provider`
- `current_model`
- `started_at`
- `ended_at`
- `tasks_performed[]`
- `plans_produced[]`
- `files_modified[]`
- `errors_encountered[]`
- `final_summary`
- `status`
- `last_updated`

Location:

- `.simp/sessions/<session_id>.json`

## 4. Plan Schema

Plan fields:

- `task_id`
- `rationale`
- `steps[]`
- `scope_exclusions[]`
- `risk_level`

Each step includes:

- `id`
- `target`
- `action`
- `rationale`
- `verification`

Plan persistence:

- `.simp/plans/plan_<task_id>.json`

## 5. Tool Harness Constraints

Available tools in executor loop:

- `read_file`
- `write_file`
- `patch_file`
- `run_shell`

### Scope and safety

- Reads: allowed project-wide except excluded patterns.
- Writes: limited to approved plan targets.
- Path traversal outside project root blocked.

### `run_shell` restrictions

- rejects shell operators like `;`, `&`, `|`, `>`, `<`, `$`, `` ` ``,
- only allows conservative command allowlist,
- runs with `shell=False`.

## 6. Wiki File Format

Each page is markdown with YAML frontmatter.

Metadata keys:

- `id`
- `type`
- `sources[]`
- `last_updated`
- optional `title`

Source reference keys:

- `file_path`
- `hash`
- optional `start_line`
- optional `end_line`

## 7. Wiki Runtime Operations

### Registry

- path: `.simp/wiki/registry.json`
- maps source file path -> list of page IDs
- used by `get_pages_for_file` for O(1) lookup

### Freshness

- page stale if any tracked source hash differs or source missing.

### Sync

- stale pages can be regenerated with `wiki_maintainer` prompt.

### Changes log

- append-only style page: `.simp/wiki/changes.md`
- entries include task, rationale, and modified files.

### Index hotspots

- index manager updates hotspot list with recent modified files.

## 8. Configuration Resolution

ConfigManager writable target for config/history follows:

1. global: `~/.simpcode/<filename>`
2. fallback: `<project>/.simp/<filename>`

Primary config file:

- `config.json`

Expected config shape:

- `active_provider`
- `providers.<provider>.provider`
- `providers.<provider>.model_id`
- `providers.<provider>.api_key`
- optional `providers.<provider>.base_url`

## 9. On-Disk Artifact Layout

Common generated artifacts:

- `SIMP.md`
- `SPEC.md`
- `.simp/wiki/**/*.md`
- `.simp/wiki/registry.json`
- `.simp/sessions/*.json`
- `.simp/plans/*.json`
- `.simp/logs/exec_*.jsonl`
- `.simp/tokens.log`
- `.simp/registry.json` (hash registry used by HashRegistry)

## 10. Implementation Notes Worth Knowing

- Onboarding check is based on `SIMP.md` and `.simp/wiki/index.md` existence.
- `ask` and `do` both auto-trigger onboarding if needed.
- `sync` currently uses default LLM construction without explicit session override arguments.
- `wiki search` command path is currently placeholder text in shell handler.

## 11. Exit Codes and Error Surfaces

SimpCode surfaces most command/runtime failures as console messages in the TUI/CLI.

Common error channels:

- provider setup and LLM errors,
- plan generation or structured-output errors,
- tool harness security violations,
- verification command failures,
- stale wiki regeneration failures.

Use [Troubleshooting](../TROUBLESHOOTING.md) for practical recovery procedures.
