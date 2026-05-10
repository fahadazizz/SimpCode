# SimpCode: Semantically Aware Agentic Coding Assistant

SimpCode is a command-line interface (CLI) application designed to facilitate autonomous software engineering tasks through a persistent semantic knowledge layer. By maintaining a structured Wiki of project-specific invariants, architectural patterns, and structural maps, SimpCode ensures that agentic reasoning is grounded in historical context and verified architectural constraints.

## Technical Foundation

The system is built upon three primary pillars:

1. **Semantic Knowledge Layer:** A persistent Markdown-based Wiki stored in `.simp/wiki/`. This layer provides a cognitive map of the codebase, allowing the assistant to understand high-level intent and cross-module dependencies without requiring exhaustive context window saturation.
2. **Deterministic Agentic Loop:** A structured five-mode execution cycle (GET MISSION, SCAN SCENE, THINK THROUGH, TAKE ACTION, GET BETTER) that mandates research and planning before any modification is performed.
3. **Execution Harness:** A security and integrity layer that restricts file system operations and shell execution to the scope of a user-approved plan.

## Core Features

- **Persistent Context:** Knowledge of business logic and architectural invariants survives between sessions via the Wiki engine.
- **Staleness Detection:** Automatic verification of Wiki accuracy through file-hash pinning and synchronization.
- **Plan-Based Execution:** Mandatory step-by-step implementation plans with explicit risk assessment and scope definition.
- **Deterministic Verification:** Integrated support for automated testing and linting as part of the execution lifecycle.

## Installation

Prerequisites:
- Python 3.9 or higher
- Access to a supported Large Language Model (LLM) via environment variables

```bash
git clone https://github.com/user/simpcode
cd simpcode
pip install -e .
```

## Command Reference

### Project Initialization
```bash
simp init
```
Analyzes the project structure, detects the technology stack, and generates the foundational intelligence files (`SIMP.md` and `AGENT.md`).

### Knowledge Retrieval
```bash
simp ask "Description of the query"
```
Performs a read-only analysis of the codebase by navigating the Wiki and assembling relevant local context.

### Task Execution
```bash
simp do "Description of the task"
```
Initiates the full agentic loop: researches the problem space, generates a structured implementation plan, awaits user approval, and executes modifications through the tool harness.

### Wiki Synchronization
```bash
simp sync
```
Performs a batch check of all Wiki references against the current state of the filesystem and updates stale hashes to maintain semantic integrity.

### Health Status
```bash
simp status
```
Displays a summary of the current Wiki health, tracking pages, and staleness reports.

## Architecture and Documentation

Detailed technical documentation regarding the system architecture, component layers, and internal workflows is available in the `docs/` directory:

- **Architecture:** `docs/architecture/overview.md`
- **Component Details:** `docs/components/`
- **Operational Workflows:** `docs/usage/workflows.md`

## License

Refer to the LICENSE file for details on usage and distribution permissions.
