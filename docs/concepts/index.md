# Concepts & Architecture

Explore the engineering philosophy and technical components that make SimpCode a high-integrity coding assistant.

---

## The Semantic Wiki

The most significant problem with standard AI assistants is **Context Fragmentation**. As a project scales, the AI cannot "see" the whole codebase, leading to hallucinations about nonexistent functions or conflicting architectural patterns.

SimpCode solves this with the **Semantic Wiki**, plus a clear separation between `SPEC.md` (requirements), `SIMP.md` (project overview), and the internal prompt layer.

### What is it?
The Semantic Wiki is a repository-local long-term memory stored in `.simp/wiki/`. It treats your codebase as a structured database of knowledge rather than a raw collection of text files.

### Core Mechanics:
1.  **Distillation**: Instead of reading a 2,000-line file every time, SimpCode reads a "Wiki Node" that summarizes the file's exports, dependencies, and purpose.
2.  **Referential Integrity**: Every piece of knowledge is linked to specific file paths and line ranges.
3.  **Cryptographic Syncing**: SimpCode hashes your source files. If a file changes manually, the Wiki node is marked as **STALE**, prompting a re-sync before the next task.
4.  **Tiered Discovery**: When you ask a question, SimpCode searches the Wiki *first* to find the "Impact Surface," then zooms in on the necessary source code.

---

## The Engineering Lifecycle (The ReAct Loop)

SimpCode does not operate on simple prompt-response cycles. Every "Mission" follows a industrial-grade engineering lifecycle.

### Phase 1: Planning (Architectural Review)
The AI generates a **Multi-Step Implementation Plan**. This plan identifies:
- **Prerequisites**: What needs to be researched first.
- **Modifications**: Exactly which files/lines will be changed.
- **Verification**: How the success of the task will be measured (e.g., specific test runs).

### Phase 2: Approval
A task never proceeds without human sign-off. This "Human-in-the-Loop" stage ensures you maintain total control over the architectural direction.

### Phase 3: Execution (The Harness)
SimpCode interacts with your system through a **Hardened Execution Harness**.
- **Tool Isolation**: The AI cannot run arbitrary commands; it uses a specific set of verified Python methods.
- **Policy Enforcement**: Every action is checked against the repository context, the generated plan, and the project requirements in `SPEC.md` before it is committed.
- **Safety**: Shell commands are escaped and validated to prevent RCE (Remote Code Execution) vulnerabilities.

### Phase 4: Reflection & Sync
After the task is finished, SimpCode updates the Semantic Wiki to reflect the new state of the world. It "learns" from the change it just made.

---

## Component Breakdown

| Component | Responsibility | Relevant Files |
| :--- | :--- | :--- |
| **Core** | Orchestrates the planning and execution state machine. | `src/simpcode/core/` |
| **Wiki** | Manages the indexing and retrieval of project knowledge. | `src/simpcode/wiki/` |
| **Harness** | Provides secure tools for file I/O and shell operations. | `src/simpcode/harness/` |
| **LLM Interface** | Decouples the system from specific AI providers. | `src/simpcode/core/llm/` |
| **CLI** | Provides the user interface (Rich TUI and shell commands). | `src/simpcode/cli/` |

---

## Security & Privacy

SimpCode is built with a **Privacy-First** architecture:
- **Local Everything**: Your Wiki, configuration, and source analysis stay on your machine.
- **Minimal Transmission**: Only necessary code snippets and Wiki nodes are sent to the LLM provider for reasoning.
- **No Background Training**: By using API-based providers (like Anthropic or OpenAI), your code is typically not used for training secondary models.
- **Audit Trails**: Every action taken by SimpCode is logged locally, allowing you to trace exactly what happened during a mission.
