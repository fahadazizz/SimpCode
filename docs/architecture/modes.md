# Operational Modes

I operate through five distinct, deterministic modes. Transitions between these modes are governed by my **Execution Harness** to ensure I never act without understanding.

## 1. GET MISSION
**Trigger:** `simp init` or starting a new session in a fresh repo.
**Activity:** Deep codebase analysis. I scan your file tree, manifests, and entry points.
**Output:** Synthesis of `SIMP.md`, `AGENT.md`, and the initial semantic Wiki layer.
**Goal:** Establish the foundation of architectural honesty.

## 2. SCAN SCENE
**Trigger:** Start of any `ask` or `do` task.
**Activity:** Situational awareness. I read your `index.md` and use the **Wiki Navigator** to identify relevant knowledge nodes.
**Harness Check:** I verify the hash of every Wiki page. If it's stale, I regenerate it or warn you.
**Goal:** Assemble the minimal, high-signal context needed for the task.

## 3. THINK THROUGH
**Trigger:** After Scan Scene.
**Activity:** High-integrity planning. I reason about your task against the backdrop of your Wiki's **Invariants** and **Risks**.
**Output:** A structured, ordered **Plan Artifact** (JSON) with specific verification gates for each step.
**Goal:** Architect a solution before touching a single line of code.

## 4. TAKE ACTION
**Trigger:** Upon your approval of the Plan.
**Activity:** Surgical execution. I follow a multi-turn **ReAct (Reason + Act)** loop for every plan step.
**Harness Check:** I enforce **Read-Before-Write**. I run your linter/tests after every change. I physically block any write to a file not in my approved scope.
**Goal:** Safely implement the plan with 100% technical correctness.

## 5. GET BETTER
**Trigger:** Task completion or manual `simp sync`.
**Activity:** Reflection and maintenance. I extract new patterns or risks discovered during execution. I update `changes.md` with semantic rationale.
**Goal:** Ensure my knowledge of your project grows and matures over time.
