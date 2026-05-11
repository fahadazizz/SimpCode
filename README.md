# SimpCode — High-Integrity Agentic Engineering Assistant

I am SimpCode. I am not a chatbot, a code generator, or a probabilistic search tool. I am a **Senior Staff AI Engineer** built to manage the complexity of production software systems through **Semantic Navigation** and **Harness Engineering**.

Standard coding assistants start every session blind—they grep files, guess context, and dump token soup into an LLM. This is expensive, architecturally ignorant, and fundamentally unreliable. 

I work differently. I maintain a living knowledge base of your project called the **Wiki**. I consult the Wiki first, reason about your architecture second, and fetch code only when I have a confirmed implementation target. 

## My Core Philosophy

### 1. Wiki-First, Always
I never read your codebase directly as my first action. I navigate your semantic map to identify **Invariants**, **Patterns**, and **Risks**. Code is fetched only to resolve pointers identified by my reasoning layer.

### 2. Understand Before Acting
I do not write code the moment you ask. I perform a multi-pass **Scan Scene** to build situational awareness, followed by a **Think Through** phase where I produce a concrete, surgical implementation plan for your approval.

### 3. Harness Engineering over Prompt Engineering
My reliability comes from structural constraints. I use a multi-turn **ReAct Loop** that enforces a **Read-Before-Write** invariant. I physically cannot write to files outside of my approved plan, and I mandate inline verification (tests/linting) for every logical unit of change.

## High-Integrity Features
*   **Universal LLM Engine:** Native SDK support for Google Gemini, Anthropic, OpenAI, Groq, OpenRouter, and Ollama.
*   **Semantic Wiki:** A dual-layer Markdown graph (.simp/wiki/) that stores cognitive intelligence and structural maps.
*   **Zero-Stub Architecture:** No placeholders. Every component—from AST-aware symbol parsing to bit-perfect token budgeting—is built for production use.
*   **Simp-Shell TUI:** A high-fidelity interactive environment for real-time collaborative engineering.
*   **Deterministic Recovery:** Persisted Plan Artifacts allow me to resume failed or interrupted tasks from the exact point of failure.

## Installation

```bash
git clone https://github.com/user/simpcode
cd simpcode
pip install -e .
```

## Global Setup

Initialize your global configuration (stored in `~/.simpcode/config.json`):

```bash
simp setup
```

## The Engineering Lifecycle

1.  **Get Mission:** `simp init` — I analyze your repository and synthesize your project model (`SIMP.md`) and behavioral rules (`AGENT.md`).
2.  **Scan Scene:** `simp ask "How is state managed?"` — I navigate the Wiki to answer forensic queries with cited file:line ranges.
3.  **Take Action:** `simp chat` or `simp do "task"` — I architect a plan, obtain your approval, and execute surgical edits with inline verification.
4.  **Get Better:** `simp sync` — I perform self-healing regeneration of my knowledge base to ensure I never drift from the source truth.

---
*SimpCode is designed for developers who value architectural honesty and surgical precision.*
