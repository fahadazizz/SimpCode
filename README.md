# SimpCode — Semantically Aware Agentic Coding Assistant

SimpCode is a CLI-based coding assistant that maintains a persistent semantic layer (Wiki) of your codebase. Unlike standard assistants that start every session "blind," SimpCode consults a living knowledge base first, ensuring architectural awareness and token efficiency.

## Key Features
- **Semantic Core:** A Markdown-based Wiki that stores cognitive knowledge (invariants, risks) and structural maps.
- **Harness Engineering:** Deterministic execution constraints including plan-scope enforcement and read-before-write logic.
- **Token Efficient:** Fetches only the context it needs based on Wiki navigation.
- **Self-Healing:** Inline Wiki updates and `simp sync` ensure knowledge never drifts from the code.

## Installation
```bash
git clone https://github.com/user/simpcode
cd simpcode
pip install -e .
```

## Quick Start
1. **Onboard:** `simp init` analyzes your project and creates `SIMP.md` and `AGENT.md`.
2. **Ask:** `simp ask "How does the auth module handle errors?"`
3. **Do:** `simp do "implement a new logging utility in utils/"`

## Commands
- `init`: Initialize SimpCode for a project.
- `ask`: Read-only queries with Wiki context.
- `do`: Execute code-modifying tasks with reasoning and planning.
- `sync`: Batch-verify Wiki freshness.
- `status`: Check Wiki health and staleness.
- `wiki`: Manage and inspect Wiki pages.
- `recover`: Resume or revert interrupted sessions.

## Architecture
SimpCode operates in five distinct modes:
`GET MISSION` → `SCAN SCENE` → `THINK THROUGH` → `TAKE ACTION` → `GET BETTER`
