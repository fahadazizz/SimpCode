# Architectural Overview

SimpCode is designed to solve the "context blindness" problem of traditional coding assistants. It achieves this by introducing a **Semantic Layer** and a **Deterministic Agentic Loop**.

## The Semantic Layer (Wiki)

Most AI assistants start every session with zero knowledge of your project's history, architectural rules, or business logic. SimpCode maintains this knowledge in a **Wiki** (stored in `.simp/wiki/`).

- **Persistence:** Knowledge survives between sessions.
- **Semantic Navigation:** Instead of dumping the whole codebase into context, SimpCode "navigates" the Wiki to find relevant pages.
- **Staleness Detection:** Every Wiki page is pinned to specific file hashes. If the code changes, SimpCode detects the drift and triggers a sync.

## The Deterministic Agentic Loop

SimpCode does not just "generate and pray." It follows a strict 5-mode lifecycle for every task:

1.  **GET MISSION:** Define the user's objective.
2.  **SCAN SCENE:** Research the codebase using the Wiki and local files.
3.  **THINK THROUGH:** Decompose the task into a concrete, step-by-step plan.
4.  **TAKE ACTION:** Execute the plan through a restricted tool harness.
5.  **GET BETTER:** Update the Wiki and verify the results.

## Key Layers

- **CLI Layer:** Handles user interaction and command dispatching.
- **Semantic Layer:** Manages the Wiki, navigation, and freshness.
- **Reasoning Layer:** Analyzes the project, generates plans, and makes tool-call decisions.
- **Harness Layer:** Enforces safety, budget, and scope constraints.
