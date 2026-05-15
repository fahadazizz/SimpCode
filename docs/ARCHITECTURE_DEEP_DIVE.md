# Architecture Deep Dive

This deep dive documents SimpCode internals from entrypoint to persistence with implementation-level accuracy.

## 1. Entrypoints and Command Surface

### CLI group behavior

The Click group in `src/simpcode/cli/main.py` is invoked with `invoke_without_command=True`.

Implication:

 - running `simp` with no subcommand launches TUI directly,
 - this is the primary user path,
 - interactive chat is available via the TUI; check available subcommands with `simp --help` or inspect `src/simpcode/cli/` for current handlers.

### Root options

The root command supports:

- `--provider`
- `--model`
- `--session`
- `--new`

These values are passed to `SimpShell` and can override loaded session defaults.

## 2. TUI Command Router Details

`SimpShell._route_command` maps slash commands to handlers.

Implemented handlers:

- ask, do, sync, status, recover, init, wiki, config, sessions, simp, clear, help

Chat fallback:

- non-slash input routes to `_handle_chat`, which performs context scan and LLM interactive reply with session history persistence.

## 3. Onboarding and Initialization Path

Onboarding gate in `needs_onboarding` checks:

- `SIMP.md` existence
- `.simp/wiki/index.md` existence

If missing, `_ensure_onboarded` chooses one of two paths:

1. skeleton initialization:
   - static templates and baseline wiki structure
2. legacy synthesis import:
   - project analyzer metadata
   - synthesized docs
   - wiki bootstrap generation
   - fallback to skeleton on synthesis failure

## 4. Context Assembly Pipeline (`ScanScene`)

### Mandatory context

- `SIMP.md`, `SPEC.md` when present
- wiki pages `index` and `invariants`
- selected skill documents from global/project skill directories

### Auto-healing behavior

If mandatory wiki page is stale, SimpCode attempts regeneration before context inclusion.

### Navigation passes

`WikiNavigator` can request additional pages over multiple passes.

For each page loaded:

- stale pages are healed,
- still-stale pages are excluded,
- semantic content is added,
- file range snippets are added to targeted tier.

### Budget enforcement

`ContextBudgeter` keeps mandatory tier and drops optional items as needed with warnings.

## 5. Planner Internals (`PlanGenerator`)

Planner interaction uses structured output with `ArchitectResponse`.

Possible outcomes:

- direct plan
- context request (`pages_to_load`) for another planning turn

Planner performs up to 3 turns before forcing final plan generation.

Important detail:

- if `SPEC.md` exists, planner prepends it to context.

## 6. Executor Internals (`TakeAction`)

### Allowed write scope

Allowed files are derived from plan step targets that look like path/file targets.

### Loop model

For each step, model emits a `ToolCall` containing:

- tool name
- arguments
- thought
- `complete` boolean

### Safety and reliability controls

- loop ceiling per step,
- failure counting per step,
- repeated same tool-call tripwire,
- explicit blocking on plan/security violations.

### Verification policy

After write/patch:

1. `flake8 <file>`
2. step-specific verification command if defined

Failure in either marks step turn as failed and pushes corrective behavior.

### Wiki coupling on mutation

After file write/patch, executor attempts wiki sync for impacted pages using O(1) registry lookup and regeneration path.

After plan execution with modified files:

- append `changes` page log entry
- update index hotspots with modified paths.

## 7. Tool Harness Security Model

`ToolHarness` enforces:

- normalized absolute paths
- root-bound traversal checks
- exclusion filter rules
- plan-approved write scope

`run_shell` is intentionally conservative:

- forbidden shell control tokens rejected
- command allowlist enforced
- subprocess executed with `shell=False`

## 8. Wiki Engine Deep Details

### Data model

Each page has metadata and content.

Metadata includes source references with hashes and optional line spans.

`_previous_sources` is a private, non-serialized field used to optimize registry cleanup.

### Registry behavior

Registry file: `.simp/wiki/registry.json`

- key: source file path
- value: list of wiki page IDs

`get_pages_for_file`:

- dictionary retrieval (`registry.get(file_path, [])`), O(1)

`save_page`:

- removes old mappings using tracked previous sources (O(s))
- fallback O(m) scan only for edge case (loaded page + clearing sources)
- writes new mappings and updates cached registry state

### Page listing cache

`get_all_pages` uses wiki directory mtime cache.

- unchanged mtime + non-empty cache -> O(1) return
- changed mtime -> recursive scan and parse

### Staleness checks

For each source reference:

- if file missing -> stale (`DELETED`)
- if hash mismatch -> stale with current hash

## 9. Session, Logs, and Tokens

Session manager stores serialized state in `.simp/sessions`.

Execution logger writes JSONL traces per session in `.simp/logs`.

Token logger appends usage estimate entries to `.simp/tokens.log`.

## 10. Provider Resolution and Backoff

`LLMClient` resolution order:

1. explicit runtime override
2. persisted config provider entry
3. environment fallback

Retry/backoff wrapper retries retryable API/server conditions with exponential delay.

Structured output includes one extra corrective attempt for schema compliance failures when appropriate.

## 11. Index and Knowledge Topology

`IndexManager` maintains `index.md` under a token budget.

Pruning order when oversized:

1. hotspots
2. decisions
3. modules

Hotspot updates keep newest entries first and cap list length.

## 12. Skills System

Skill locations:

- global: `~/.simpcode/skills/*.md`
- project: `.simp/skills/*.md`

Project skills override global by matching skill ID.

Skill selector uses structured LLM output to choose task-relevant skills for context assembly.

## 13. Operational Guarantees and Non-Guarantees

### Intended guarantees

- explicit plan approval path,
- scoped writes and safer execution primitives,
- persistent artifacts for inspectability,
- wiki/source consistency mechanisms.

### Non-guarantees

- not all command stubs are feature-complete (`/wiki search` placeholder),
- LLM quality still depends on provider/model quality,
- complex shell workflows are intentionally constrained.

## 14. Practical Implication for Teams

SimpCode is strongest when treated as:

- a controlled assistant for scoped implementation work,
- a local knowledge and audit artifact generator,
- a repeatable execution framework with inspectable traces.

It is weakest when asked to behave like unconstrained autonomous shell automation.

## 15. System Diagram (High-level)

The following Mermaid diagram summarizes the primary runtime components and their interactions. It is intended to help engineers quickly map code locations to architectural responsibilities.

```mermaid
flowchart LR
   CLI["CLI / TUI (simp)"] -->|invokes| Shell[SimpShell]
   Shell -->|routes| Planner[PlanGenerator]
   Planner -->|produces plan| Executor[TakeAction / Executor]
   Executor -->|uses| ToolHarness[ToolHarness]
   Executor -->|updates| WikiEngine[Wiki Engine]
   WikiEngine -->|persists| Registry[.simp/wiki/registry.json]
   WikiEngine -->|reads/writes| WikiFS[.simp/wiki/*.md]
   Executor -->|uses| LLM[LLMClient]
   LLM -->|provider| ExternalAPI[Provider (OpenAI/Anthropic/...)]
   Executor -->|logs| ExecLogs[.simp/logs/*.jsonl]
   Shell -->|stores| Sessions[.simp/sessions]
   IndexManager[IndexManager] -.->|reads| WikiFS
   IndexManager -.->|writes| IndexFile[index.md]
   ToolHarness -->|executes sandboxed| Subprocess[Local subprocess]
   subgraph Code
      Planner
      Executor
      WikiEngine
      ToolHarness
      IndexManager
   end
```

Notes:

- `SimpShell` is the user-facing router implemented in `src/simpcode/cli/shell.py`.
- `PlanGenerator` is implemented in `src/simpcode/core/planner.py` and uses structured LLM outputs.
- `Executor` (TakeAction) is in `src/simpcode/core/executor.py` and orchestrates tool calls and verification.
- `WikiEngine` is in `src/simpcode/wiki/engine.py`; the registry is an inverted index mapping source files to wiki pages for O(1) lookups.
- `ToolHarness` enforces path scoping and an allowlist for shell commands in `src/simpcode/harness/tools.py`.

For a deeper walk-through, see the sections above that map behavior to file locations.
