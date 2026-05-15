# SIMP.md Findings

## Understanding of the Intended Contract

From your description, SIMP.md is supposed to be a user-owned, root-level template that SimpCode ships at init time and then treats as a stable rules-of-engagement document. It should define the operating framework for SimpCode across domains: execution flow, constraints, production standards, failure protocol, token discipline, and the update rule that SIMP.md changes only when the user explicitly asks for it.

The current implementation does not follow that contract. It treats SIMP.md as generated project intelligence, refreshable onboarding output, and mutable runtime state. That is the core mismatch.

## Finding

### 1. SIMP.md is generated and overwritten by the onboarding pipeline

Severity: High

The init/onboarding flow writes SIMP.md as part of normal project setup instead of preserving it as a user-owned template. `DocumentGenerator.write_docs()` always writes `SIMP.md` whenever synthesized onboarding docs exist, and if the synthesized SIMP content is empty it silently replaces it with boilerplate text instead of stopping or asking for an explicit user decision. `ensure_onboarding_artifacts()` also writes fallback SIMP content when the file is missing or empty.

Evidence: [src/simpcode/core/generator.py](src/simpcode/core/generator.py#L26-L46), [src/simpcode/core/onboarding.py](src/simpcode/core/onboarding.py#L15-L45)

Why this is wrong: your contract says SimpCode may provide the template, but it should not modify SIMP.md unless the user explicitly asks for that change. The current code can replace user-authored content during init and recovery paths.

Impact: silent data loss, broken ownership, and a file that cannot reliably serve as a stable engineering framework.

### 2. The prompt layer trains the model to synthesize SIMP.md as repo-specific project intelligence

Severity: High

The onboarding prompts tell the model to synthesize SIMP.md from repository metadata, file trees, manifests, and entry-point snippets. The architect prompt frames SIMP.md as a generated output describing the project’s identity and architecture, not as a universal rules-of-engagement template.

Evidence: [src/simpcode/core/prompts/onboarding_documents.md](src/simpcode/core/prompts/onboarding_documents.md#L1-L10), [src/simpcode/core/prompts/onboarding_architect.md](src/simpcode/core/prompts/onboarding_architect.md#L1-L30), [src/simpcode/core/generator.py](src/simpcode/core/generator.py#L11-L25)

Why this is wrong: SIMP.md should be the stable SimpCode template that applies across projects, not a per-repo summary generated from local metadata. Synthesizing it from the target repo makes the file drift into project notes instead of framework policy.

Impact: every project gets a different SIMP.md shape, which defeats the goal of having one reusable operating framework.

### 3. The docs and ownership guidance contradict the desired user-owned contract

Severity: High

The repository documentation currently tells users that SIMP.md is shared, user-editable, and often auto-generated or refreshed. That directly conflicts with your intended rule that SIMP.md belongs to the user and should only be changed by explicit command.

Evidence: [docs/getting-started/file-ownership.md](docs/getting-started/file-ownership.md#L10-L40), [docs/getting-started/file-ownership.md](docs/getting-started/file-ownership.md#L41-L60), [docs/guide.md](docs/guide.md#L80-L83), [docs/reference/index.md](docs/reference/index.md#L28-L31)

Why this is wrong: the docs are part of the product contract. If the docs say SimpCode can create or refresh SIMP.md, users and future maintainers will keep building the wrong behavior back in.

Impact: inconsistent expectations, regressions in future edits, and user confusion about who owns the file.

### 4. There is no explicit SIMP.md update gate or user-confirmed write path

Severity: High

The codebase does not implement a dedicated "update SIMP.md only when the user explicitly commands it" mechanism. The file-write harness enforces scope, but it does not distinguish SIMP.md from any other in-scope project file, and the onboarding flow can mutate it without a special confirmation path.

Evidence: [src/simpcode/harness/tools.py](src/simpcode/harness/tools.py#L15-L68), [src/simpcode/harness/permissions.py](src/simpcode/harness/permissions.py#L1-L22), [src/simpcode/core/workflows.py](src/simpcode/core/workflows.py#L34-L84)

Why this is wrong: your desired rule is not just "be careful"; it is "never modify SIMP.md unless the user explicitly asked." That needs a dedicated policy gate, not a general-purpose write tool.

Impact: any normal task flow can mutate the file, which makes the ownership contract unenforceable.

### 5. SIMP.md is loaded as mandatory task context, but the system also treats it as mutable runtime state

Severity: Medium to High

The context loader always pulls SIMP.md into the mandatory tier, alongside the index and optional SPEC.md. That is not inherently wrong given your intent, but the implementation mixes that read path with the same generation pipeline that rewrites SIMP.md, so the file is simultaneously treated as authoritative policy and as disposable onboarding output.

Evidence: [src/simpcode/core/modes.py](src/simpcode/core/modes.py#L17-L28), [src/simpcode/harness/budgeter.py](src/simpcode/harness/budgeter.py#L18-L37)

Why this is wrong: a rules-of-engagement file should be consumed as a stable baseline, not re-authored as part of routine project discovery.

Impact: policy drift, prompt noise, and no clean separation between framework rules and project-specific context.

### 6. Fallback behavior fabricates SIMP.md when synthesis fails or is empty

Severity: High

If synthesized SIMP content is missing, the code injects a fallback title and generic text instead of surfacing the failure. That means the system can silently create a weaker, generic SIMP.md even when the real content generation path failed.

Evidence: [src/simpcode/core/generator.py](src/simpcode/core/generator.py#L33-L46), [src/simpcode/core/onboarding.py](src/simpcode/core/onboarding.py#L23-L45)

Why this is wrong: for a file that is supposed to be the authoritative operating framework, silent fallback is the wrong failure mode. It hides the failure and leaves behind an untrusted substitute that looks valid.

Impact: brittle init behavior and a false sense of correctness after onboarding failures.

### 7. The current SIMP.md content model is still repository-manifest oriented, not a universal engineering framework

Severity: Medium

The surrounding docs and prompts still describe SIMP.md as a project manifest, project overview, or project intelligence document. That framing is too narrow for what you want. The current content model does not clearly define the execution loop, failure protocol, token-efficiency policy, and explicit update boundaries as a first-class user contract.

Evidence: [src/simpcode/core/prompts/onboarding_architect.md](src/simpcode/core/prompts/onboarding_architect.md#L11-L28), [docs/getting-started/file-ownership.md](docs/getting-started/file-ownership.md#L14-L27), [docs/guide.md](docs/guide.md#L195-L201)

Why this is wrong: a manifest/overview is a description of a repo. Your target is a framework contract for how SimpCode should operate across repos.

Impact: the file ends up optimized for summarizing a codebase instead of governing SimpCode’s behavior.

## Bottom Line

The core problem is not one isolated bug. The entire SIMP.md pipeline is built around the wrong ownership model:

- it is synthesized from repo metadata,
- it is auto-written during onboarding,
- it is documented as refreshable/shared,
- it is consumed as mandatory context,
- and it lacks a strict explicit-update gate.

That makes SIMP.md behave like generated state, not like the user-owned universal engineering framework you described.

## What the implementation should do instead

1. Ship a strong SIMP.md template from SimpCode at init time, but treat it as user-owned from then on.
2. Never rewrite SIMP.md automatically during onboarding, sync, or recovery.
3. Add an explicit SIMP.md update command path that only runs when the user asks for it.
4. Update the docs so they describe SIMP.md as a user-controlled contract, not a refreshable manifest.
5. Keep reading SIMP.md as mandatory context if that is part of the product design, but separate read behavior from write behavior completely.
