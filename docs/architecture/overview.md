# Architectural Overview

I am built on the principle of **Harness Engineering**. This means that my reliability does not come from clever prompts alone, but from the structural constraints of the environment I run in.

## The Mental Model: Agent = Model + Harness
I treat the LLM as a stateless reasoning engine. The **Harness** is my "body"—it manages my memory, assembly of context, and physical execution of tools.

### 1. The Semantic Layer (The Wiki)
Standard RAG (Retrieval Augmented Generation) uses probabilistic search (embeddings) to find code. I use **Intentional Navigation**. I read your project index and *reason* about which Wiki pages are relevant. My Wiki is a dual-layer Markdown graph:
*   **Cognitive Layer:** Invariants, Patterns, and Risks.
*   **Structural Layer:** Module summaries and Symbol contracts.

### 2. Hierarchical Context Composition
I don't dump everything into context. I follow a strict hierarchy:
1.  **Mandatory:** SIMP.md (Project Model), AGENT.md (Rules), and the Index.
2.  **Cognitive:** Wiki pages describing invariants and risks.
3.  **Targeted:** Precise code snippets referenced by the Wiki.

### 3. State Persistence
I never rely on conversation history. Every action I take is persisted in a **Plan Artifact** or a **Session Log**. This makes me resilient to interruptions and allows you to audit my reasoning at every step.

## The Operational Flow
I operate in five deterministic modes:

`GET MISSION` → `SCAN SCENE` → `THINK THROUGH` → `TAKE ACTION` → `GET BETTER`

*   **GET MISSION:** Systematic onboarding and knowledge ingestion.
*   **SCAN SCENE:** Semantic context assembly based on task intent.
*   **THINK THROUGH:** Multi-pass planning and invariant verification.
*   **TAKE ACTION:** Multi-turn ReAct execution with inline verification.
*   **GET BETTER:** Self-healing knowledge maintenance and pattern extraction.
