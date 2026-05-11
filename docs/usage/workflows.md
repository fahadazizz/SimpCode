# Core Methodology & Workflows

To get the most out of me, you should adopt the **Staff Engineer Workflow**. I am not a "code monkey"; I am a collaborator.

## 1. Establishing the Mission (`init`)
When you run `simp init`, I perform a deep analysis of your repository. I don't just list files—I synthesize a project model:
*   **SIMP.md:** I identify your tech stack, entry points, and architectural constraints.
*   **AGENT.md:** I propose a set of behavioral rules tailored to your project's complexity.
*   **Initial Wiki:** I "compile" your modules into semantic pages.

**Your Role:** Review these documents. They are my "operating instructions." If I miss a pattern or a risk, add it to the Wiki or AGENT.md immediately.

## 2. Querying for Insight (`ask`)
Use `simp ask` for forensic investigations. 
*   *Workflow:* "How does the error handling in the auth module work?"
*   *My Process:* I navigate to `wiki/modules/auth.md`, identify the relevant symbols, fetch the specific code ranges, and explain the implementation based on your invariants.

## 3. Collaborative Building (`chat`)
The Simp-Shell (`simp chat`) is my primary interactive interface. 
*   **Visual Reasoning:** I use rich formatting to show you my thoughts in blue and my actions in cyan.
*   **Contextual Awareness:** You can discuss architectural choices with me, and I will reference your Wiki pages in real-time.

## 4. Autonomous Implementation (`do`)
When you give me a task via `simp do`, I follow a high-integrity execution loop:
1.  **Plan:** I produce a structured implementation plan.
2.  **Approve:** You review the plan in a table format. You can approve, reject, or request changes.
3.  **Act (ReAct):** I execute the plan step-by-step. I read every file before patching it and run verification (lint/tests) after every write.
4.  **Reflect:** Once finished, I reflect on what I learned and update your Wiki with new patterns or risks.

## 5. Self-Healing (`sync`)
If you make changes to the codebase outside of me, I might get confused. Run `simp sync`. I will identify stale knowledge nodes where the code has drifted from my Wiki and regenerate them to ensure my semantic layer remains the source of truth.
