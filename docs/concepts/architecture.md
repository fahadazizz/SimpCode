# Architecture Concept

This document explains the runtime architecture of SimpCode in user terms while staying faithful to implementation.

## 1. High-Level Pipeline

At a high level, SimpCode runs this loop:

1. Gather context from repository and wiki.
2. Use role-specific prompts to produce structured outputs.
3. Ask user approval for plans.
4. Execute via constrained tool harness.
5. Verify results at each step.
6. Persist all state and evolve knowledge artifacts.

## 2. Main Runtime Components

### CLI and TUI Entry

- `src/simpcode/cli/main.py` defines command entrypoints.
- `src/simpcode/cli/shell.py` defines interactive shell behavior.

### Workflow Orchestration

- `src/simpcode/core/workflows.py` is shared orchestration for both CLI and TUI commands.

### Context Assembly

- `src/simpcode/core/modes.py` (`ScanScene`) builds task context with mandatory and optional tiers.

### Planning

- `src/simpcode/core/planner.py` (`PlanGenerator`) creates structured plans with steps and verification.

### Execution

- `src/simpcode/core/executor.py` (`TakeAction`) runs the plan through an iterative tool-call loop.

### Wiki Engine

- `src/simpcode/wiki/engine.py` manages wiki pages, staleness checks, regeneration, and source registry.

### State and Persistence

- `src/simpcode/core/state.py` persists sessions and execution logs.
- `src/simpcode/core/paths.py` manages `.simp` artifact directories.

## 3. Context Architecture

SimpCode uses tiered context with budget control.

### Mandatory tier

Always attempted first:

- `SIMP.md` if present
- `SPEC.md` if present
- wiki `index`
- wiki `invariants`
- selected skills

### Semantic tier

Wiki pages selected by navigator based on task and index map.

### Targeted tier

Specific code ranges referenced by wiki source spans.

### Budgeting

ContextBudgeter preserves mandatory content and drops optional content when over budget with explicit warnings.

## 4. Planning Architecture

Planner returns an `ArchitectResponse` that can either:

- provide a full `Plan`, or
- request additional context pages first.

This enables multi-turn planning where insufficient context is corrected before forcing a final plan.

If `SPEC.md` exists, planner prepends it prominently in planning context.

## 5. Execution Architecture

Execution is step-based and loop-bounded.

Per plan step:

1. model reasons and emits a `ToolCall`
2. harness executes allowed tool
3. result is logged and fed back to model
4. step ends only when tool call signals `complete=true`

Safety controls include:

- repeated identical tool call detection,
- plan-scope write enforcement,
- shell command restrictions,
- bounded failure counts.

## 6. Wiki Architecture

Wiki pages are markdown with YAML frontmatter metadata.

Freshness is source hash based:

- file-level hash or range hash
- stale sources detected per page

Registry maps source file -> page IDs and supports O(1) retrieval.

Page discovery uses directory mtime caching for fast repeated reads.

## 7. Recovery Architecture

- Plans are persisted to `.simp/plans/`.
- Sessions are persisted to `.simp/sessions/`.
- Execution traces are appended to `.simp/logs/`.

`/recover` loads the latest plan artifact and reruns execution after approval.

## 8. Configuration Architecture

Provider config is loaded from persisted config first, then environment fallback.

Writable path preference:

1. `~/.simpcode/`
2. `<project>/.simp/`

This pattern applies to config and history storage.

## 9. What This Means for Users

You can trust SimpCode behavior more when you:

- keep project manifests (`SIMP.md`, `SPEC.md`) current,
- review plans before approval,
- constrain task scope explicitly,
- inspect `.simp` artifacts during debugging.

Architecture is not hidden. It is reflected in files you can open and inspect.
