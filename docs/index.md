# SimpCode Documentation Portal

SimpCode is a local, TUI-first engineering assistant designed for real repositories and real workflows.

This portal is organized so you can move from first-run setup to daily engineering usage, then into architecture and implementation detail when needed.

## Start Here

- If you are new to SimpCode, begin with [Getting Started Overview](getting-started/overview.md).
- If you want the complete user flow from installation to productive execution, use [User Guide](guide.md).
- If you are trying to solve a specific task quickly, jump to [How-To Guides](how-to/index.md).
- If you need exact command behavior and on-disk artifact details, use [Reference](reference/index.md).
- If something is failing or inconsistent, use [Troubleshooting](TROUBLESHOOTING.md).

## Documentation Map

### Getting Started

- [Overview](getting-started/overview.md)
- [Installation Deep Dive](getting-started/installation-deep-dive.md)
- [Setup and Usage](getting-started/setup-and-usage.md)
- [File Ownership](getting-started/file-ownership.md)

### Concepts

- [Concepts Index](concepts/index.md)
- [Architecture Concept](concepts/architecture.md)

### How-To

- [How-To Index](how-to/index.md)
- [Advanced Capabilities](how-to/advanced-capabilities.md)
- [Writing Rules and Prompting Guidance](how-to/writing-rules.md)

### Reference and Operations

- [Reference](reference/index.md)
- [Troubleshooting](TROUBLESHOOTING.md)

### Deep Technical Material

- [Architecture Deep Dive](ARCHITECTURE_DEEP_DIVE.md)
- [Comprehensive Guide](COMPREHENSIVE_GUIDE.md)

## What Is Accurate in This Documentation

This documentation has been rewritten against the current implementation in:

- CLI and TUI command handlers in `src/simpcode/cli/main.py` and `src/simpcode/cli/shell.py`
- Workflow orchestration in `src/simpcode/core/workflows.py`
- Planner and executor flow in `src/simpcode/core/planner.py` and `src/simpcode/core/executor.py`
- Wiki storage, freshness checks, and registry logic in `src/simpcode/wiki/engine.py`
- Path and persistence behavior in `src/simpcode/core/paths.py`, `src/simpcode/utils/paths.py`, and `src/simpcode/core/state.py`

If behavior changes in code, this documentation should be updated in lockstep.

## Recommended Reading Order

1. [Getting Started Overview](getting-started/overview.md)
2. [Setup and Usage](getting-started/setup-and-usage.md)
3. [User Guide](guide.md)
4. [How-To Index](how-to/index.md)
5. [Reference](reference/index.md)
6. [Architecture Deep Dive](ARCHITECTURE_DEEP_DIVE.md)

## Reader Profiles

### I just want to use SimpCode effectively

Read:

- [Getting Started Overview](getting-started/overview.md)
- [Setup and Usage](getting-started/setup-and-usage.md)
- [User Guide](guide.md)

### I need operational confidence and recovery paths

Read:

- [Reference](reference/index.md)
- [Troubleshooting](TROUBLESHOOTING.md)
- [How-To Advanced Capabilities](how-to/advanced-capabilities.md)

### I need to understand internals before trusting behavior

Read:

- [Concepts Architecture](concepts/architecture.md)
- [Architecture Deep Dive](ARCHITECTURE_DEEP_DIVE.md)
- [Comprehensive Guide](COMPREHENSIVE_GUIDE.md)
