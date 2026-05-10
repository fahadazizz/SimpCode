# SimpCode Documentation

Welcome to the SimpCode documentation. SimpCode is a semantically aware agentic coding assistant that maintains a persistent knowledge layer of your codebase.

## Table of Contents

### [Architecture](architecture/overview.md)
- [Overview](architecture/overview.md)
- [Operational Modes](architecture/modes.md)

### [Components](components/cli.md)
- [CLI Interface](components/cli.md)
- [Core Logic](components/core.md)
- [Wiki System](components/wiki.md)
- [Execution Harness](components/harness.md)

### [Usage](usage/onboarding.md)
- [Onboarding](usage/onboarding.md)
- [Workflows](usage/workflows.md)

## Key Concepts

- **Semantic Layer (Wiki):** A set of Markdown files in `.simp/wiki/` that store cognitive knowledge (invariants, risks) and structural maps of the codebase.
- **Agentic Loop:** A deterministic 5-mode cycle that ensures every action is preceded by research and followed by verification.
- **Execution Harness:** A safety layer that restricts file access and command execution to the scope of an approved plan.
