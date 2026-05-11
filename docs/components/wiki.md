# The Semantic Wiki

The Wiki is my "brain." It lives in your repository at `.simp/wiki/`. It is not just documentation; it is my **Intermediate Representation** of your codebase.

## 1. Dual-Layer Knowledge Graph
I organize knowledge into two distinct tiers:

### Cognitive Layer (The Architecture)
*   **`invariants.md`**: The technical laws of your system. If I am told "No logic in controllers," this is where it lives. I check this before every plan.
*   **`patterns.md`**: Repeated implementation styles (e.g., naming conventions, API response shapes). I follow these to ensure my code "fits in."
*   **`risks.md`**: Known fragile areas or complex dependencies. I consult this to estimate the impact of a change.

### Structural Layer (The Map)
*   **`index.md`**: My primary entry point. A high-level map of modules and symbols. It is always loaded but kept under a strict token budget.
*   **`modules/`**: Detailed semantic descriptions of every major package.
*   **`symbols/`**: Precise technical contracts for key classes and functions.

## 2. Technical Integrity (Staleness Detection)
I use SHA-256 hashes to ensure my knowledge never drifts. 
*   **Pointers:** Every Wiki page contains frontmatter with `sources` (file paths and line ranges).
*   **Verification:** Before I read a Wiki page, my **Wiki Engine** compares its recorded hash against the current state of the source file.
*   **Self-Healing:** If a hash mismatches, I mark the page as **STALE**. You can use `simp sync` to have me re-compile the page based on the new code reality.

## 3. Navigation vs. Search
I don't use embeddings or vector search. I use **Intentional Navigation**. My **Wiki Navigator** reads the index, reasons about your task, and decides which pages to load. This eliminates the "retrieval error" common in standard coding assistants.
