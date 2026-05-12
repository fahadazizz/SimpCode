# SimpCode Underlying Architecture

To master SimpCode for complex projects, it helps to understand how the system physically "thinks", plans, and alters source code. We have eliminated simple stateless chats; SimpCode acts as an embodied intelligence engine.

## High-Level Flow
1. **Interactive TUI (Shell)**: A Rich, asynchronous interface capturing intent.
2. **Context Scanner (ScanScene)**: Assembles multi-tiered architectural layouts dynamically.
3. **Execution Planner (PlanGenerator)**: Evaluates constraints to build verifiable step-by-step missions.
4. **Action Engine (TakeAction)**: A tightly-constrained execution sandbox that performs exact patches, runs CLI validations, and dynamically reads state.
5. **Evolution Loop (GetBetter)**: Continuously logs learned axioms back to the knowledge graph.

---

## 1. Context Assembly (The "ScanScene" Protocol)
Before SimpCode types a single character for the LLM, the `ScanScene` module maps the project graph.
-- **Mandatory Tier:** Injects `SIMP.md` (project manifest) and `index.md` (Wiki map). `SPEC.md` (target-state requirements) is optional and included only when present.
- **Semantic Tier:** Searches the `.simp/wiki` layer for conceptual relationships and components related to the prompt.
- **Targeted Tier:** Extracts raw file strings by resolving source code citations.

### Autonomic Healing
In enterprise projects, contexts grow huge. The `budgeter.py` enforces absolute mathematical token max limits (e.g., 100k limits over Claude or OpenAI). If a file exceeds its budget and is dropped, SimpCode physically injects a `[SYSTEM WARNING: Dropped Code]` directly into the LLM, ensuring it does not hallucinate that a module was deleted.

## 2. The Multi-Turn ReAct Implementation
The core powerhouse of SimpCode is `executor.py` (`TakeAction`). Rather than taking your prompt and spitting out code, the executor enforces an endless REASON -> ACT validation mechanism via Structured JSON.

1. **Think**: "I see the schema lacks an ID..."
2. **Act**: `patch_file` -> adds ID.
3. **Validate**: The execution harness automatically triggers standard linting (e.g., `flake8`) in the shell.
4. **Dynamic Re-Injection**: If a test fails or the patch structurally collapses, the ReAct loop dynamically grabs the newest error output and re-runs the process on Turn 2, constantly realigning to the actual truth of the filesystem.

## 3. The Execution Harness (`harness.py` & `tools.py`)
Safety and strict production rigor define the Harness.
- **Diff Agnosticism:** LLMs naturally mess up leading whitespace or indentation arrays. SimpCode evaluates the exact normalized intent via a sequence matcher, ensuring precise execution without fatal formatting crashes.
- **The Shell**: SimpCode uses `subprocess.run(shell=True, ...)` to perform actual software engineering constraints. It can initialize package managers, compile binaries, and execute end-to-end framework test suites entirely independently.

## 4. The Self-Healing Wiki Engine
A hallmark SimpCode capability is eliminating **Static Context Poisoning**. Normal agents lose track of architecture after 10 edits.
When SimpCode patches a file, the `_update_wiki_integrity` subsystem recalculates the exact AST cryptographic hash of the modified file and immediately hot-reloads it in the `.simp/wiki` index tree. The intelligence graph physically heals alongside your code in real time without drifting.
