# Advanced Capabilities: Mastering SimpCode

Because SimpCode is designed to replicate the agency of a Principal Software Engineer rather than act as a static completion script, adapting your workflows will exponentially increase the power of the framework.

---

## 1. Defining Hard Constraints (`SPEC.md` & `SIMP.md`)

At initialization (`/init`), SimpCode creates or refreshes the project manifest and the project specification in your root tree.
- **`SIMP.md`**: Outlines the core framework boundaries.
- **`SPEC.md`**: Dictates the project's explicit target-state requirements (goals, constraints, quality bars).

### Expanding Capability via Constraints
You can drastically increase code quality by physically writing strict requirements inside `SPEC.md`. E.g.:
```markdown
# My Project Guidelines
- NEVER use standard Python assertions for logic flows.
- Always implement the Rust strategy pattern (Result/Option).
- Execute `npm run format:fix` after every physical web component execution. 
```
Every time you run `/do`, the `executor.py` ingests these files as **Priority 0 Mandatory Context**. The LLM cannot and will not deviate from explicitly typed directives located here.

## 2. Panning Complex Orchestrations

Often, you are not just writing code; you are trying to refactor massive logic systems or migrate database architectures. 

To utilize SimpCode's full power gracefully:
1. Try breaking impossible demands: `/do Migrate the auth layer from Mongo to Postgres` 
2. Into explicitly planned node executions:
`/ask Write a rigorous implementation plan for migrating our Auth to Postgres inside auth_plan.md`
3. Verify the plan yourself as a human observer.
4. Issue the execution:
`/do Execute the tasks explicitly identified in auth_plan.md. Act immediately.`

## 3. Harnessing The "Evolution" Intelligence Loop

Over the lifespan of a project, engineers invent custom abstractions, figure out workarounds for tricky dependencies, or find new deployment patterns natively suited to only that project structure.

SimpCode implements a proprietary intelligence extraction layer called **GetBetter**. After completing an engineering task via `/do`, SimpCode parses its own execution trace. 
- It logically summarizes what it did (maintaining the `changes.md` index).
- It proposes modifications to structural risk boundaries and system behaviors.
- The intelligence layer implicitly **deduplicates** logic to maintain an optimized context payload format (`patterns.md`, `risks.md`).

This means **the more you use SimpCode on your project, the smarter it physically becomes** natively about that code base structure. 

## 4. Bypassing Framework Silos via Skills 
For absolute maximum capabilities covering bespoke, non-standard CLI environments or proprietary private documentation pipelines, you can natively build abstract `Skills` and place them directly in the tree layers. The `ScanScene` router will dynamically evaluate and bind contextual priority payloads matching the bespoke architecture logic cleanly bypassing legacy API limits.
