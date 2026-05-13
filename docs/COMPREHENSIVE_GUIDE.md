# SimpCode Comprehensive System Guide

**Version**: 3.0 (Production Ready)  
**Last Updated**: 2026-05-12  
**Status**: All 8 architectural flaws fixed and validated

---

## Table of Contents

1. [What is SimpCode?](#what-is-simpcode)
2. [Core Concepts](#core-concepts)
3. [Getting Started](#getting-started)
4. [System Architecture](#system-architecture)
5. [User Workflows](#user-workflows)
6. [Configuration & Customization](#configuration--customization)
7. [Advanced Usage](#advanced-usage)
8. [Troubleshooting](#troubleshooting)
9. [Real-World Examples](#real-world-examples)
10. [API Reference](#api-reference)
11. [FAQ](#faq)

---

## What is SimpCode?

### The Problem It Solves

Traditional AI-assisted coding tools suffer from fundamental limitations:

- **Semantic Amnesia**: The AI forgets what it learned about your project between tasks
- **Brittle Execution**: Shell commands fail unpredictably; patches break on whitespace changes
- **Unbounded Context Bloat**: No intelligent filtering; token budgets exhaust rapidly
- **Language Bias**: Deep support for one language, shallow for others
- **No Accountability**: No way to verify that changes actually work as intended
- **Static Understanding**: Hardwired assumptions about project structure; no learning

### What SimpCode Provides

SimpCode is an **agentic software engineering system** designed for high-integrity, self-improving task execution. It treats your project as a **living system** with persistent memory, architectural discipline, and safety guarantees.

**Key Differentiators**:

1. **Semantic Wiki**: A hash-validated knowledge graph that learns and remembers your project
2. **Safe Execution Harness**: Strict scope enforcement, permission checks, verification requirements
3. **Contextual Intelligence**: Token-efficient context assembly based on task semantics
4. **Multi-Turn Planning**: LLM-based architecture planning with explicit verification steps
5. **Continuous Learning**: System evolves understanding through execution traces
6. **Multi-Provider LLM Support**: Work with any LLM (Anthropic, OpenAI, Groq, Google, local OLLama)

### Core Philosophy

- **Wiki-First**: Semantic knowledge guides decisions, not blind file grepping
- **Context is Sacred**: Extract maximum value per token
- **Read-Before-Write**: All mutations verified against ground truth
- **Architectural Honesty**: Respect patterns and boundaries
- **Graceful Degradation**: Request more context rather than hallucinate

---

## Core Concepts

### 1. The Four Essential Documents

SimpCode uses four key documents to understand and manage your project:

#### **SPEC.md** (User-Defined Specification)
- **Purpose**: Your authoritative project requirements and architectural goals
- **Maintained By**: You (the user)
- **Updated**: When requirements change or architectural decisions are made
- **Role in System**: Optional; include when you need an explicit project contract. When present, it informs planning and verification.
- **Example**:
  ```markdown
  # Project SPEC
  
  ## Requirements
  - Multi-user chat platform
  - Real-time messaging with WebSocket
  - SQLite backend for simplicity
  
  ## Architectural Goals
  - Modular service design (messaging, auth, storage)
  - No external dependencies except Anthropic API
  - Single-file deployment
  ```

#### **SIMP.md** (System Intelligent Manifest and Project)
- **Purpose**: Current state overview—what does the system look like NOW?
- **Maintained By**: Auto-generated on `init`, then versioned by you
- **Updated**: When significant structural changes occur
- **Role in System**: Always included in context for accurate understanding of current state
- **Auto-Generated Content** (on init):
  ```markdown
  # SIMP: Project Manifest
  
  ## Overview
  - Language: Python 3.10+
  - Entry Point: src/main.py
  - Package Manager: Poetry
  
  ## Core Modules
  - messaging: Real-time message handling
  - auth: User authentication and sessions
  - storage: SQLite interface layer
  
  ## Dependencies
  - anthropic >=0.7.0
  - websockets >=11.0
  ```

#### **Wiki** (.simp/wiki/)
- **Purpose**: Semantic knowledge graph—architectural patterns, module responsibilities, design decisions
- **Maintained By**: System (auto-generated, then evolved through learning)
- **Updated**: After each successful task execution (GetBetter phase)
- **Contents**:
  - `modules/*.md`: Purpose and invariants of each module
  - `symbols/*.md`: Critical functions, classes, and data structures
  - `decisions/*.md`: Architectural decisions and rationale
  - `cognitive/*.md`: Recurring patterns, risk profiles, optimization opportunities
  - `index.md`: Strategic navigation index
  - `changes.md`: Change log with semantic impact analysis
  - `patterns.md`: Repeating code patterns and conventions
- **Key Feature**: Hash-validated sources prevent drift (references track file content by hash)

#### **Global Config** (~/.simp/config.json)
- **Purpose**: LLM provider and API key configuration
- **Set Via**: `simp setup` command
- **Content**:
  ```json
  {
    "active_provider": "groq",
    "providers": {
      "groq": {
        "provider": "groq",
        "model_id": "llama-3.3-70b-versatile",
        "api_key": "gsk_..."
      }
    }
  }
  ```

### 2. The Execution Workflow

SimpCode breaks project work into four phases:

```
┌─────────────────────────────────────────────────────────────┐
│ PHASE 1: CONTEXT ASSEMBLY (ScanScene)                       │
├─────────────────────────────────────────────────────────────┤
│ • Load mandatory docs: SIMP.md, Wiki index (include `SPEC.md` only if present)          │
│ • LLM-driven navigation: Select relevant Wiki pages          │
│ • Targeted code loading: Extract necessary file ranges       │
│ • Budget enforcement: Assemble within token limits          │
│ Output: Assembled context string                            │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│ PHASE 2: PLANNING (PlanGenerator)                            │
├─────────────────────────────────────────────────────────────┤
│ • CSIO reasoning: Context, Scope, Intent, Output            │
│ • Multi-turn dialogue: Request additional context if needed │
│ • Atomic step generation: Each step has target, action,     │
│   rationale, and verification criteria                      │
│ Output: Structured Plan with steps                          │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│ PHASE 3: EXECUTION (TakeAction)                             │
├─────────────────────────────────────────────────────────────┤
│ For each plan step:                                         │
│ • Refresh context (ScanScene again)                         │
│ • ReAct loop: LLM reasons → calls tools → verifies         │
│ • ToolHarness: Enforces scope, permission checks           │
│ • Wiki sync: Updates hashes immediately                     │
│ • Continue until step verified complete                     │
│ Output: Modified files + execution trace                    │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│ PHASE 4: LEARNING (GetBetter)                               │
├─────────────────────────────────────────────────────────────┤
│ • Analyze execution trace for patterns                      │
│ • Extract risks (what could have failed?)                   │
│ • Propose new invariants (what did we learn?)              │
│ • Update Wiki with new cognitive pages                      │
│ Output: Enhanced Wiki, ready for next task                  │
└─────────────────────────────────────────────────────────────┘
```

### 3. Context Assembly (The Intelligent Layer)

The secret to SimpCode's efficiency is **tiered context assembly**:

```
TIER 1: MANDATORY (Never dropped, token cost ~15%)
├─ SIMP.md (current system state)
├─ Wiki index.md (strategic map)
└─ Selected Skills (task-specific templates)

Note: `SPEC.md` is optional and belongs in Tier 1 only when present and relevant to the task.

TIER 2: SEMANTIC (Dropped if budget exceeded, token cost ~35%)
├─ Module overview pages
├─ Architectural decision pages
├─ Risk and pattern pages
└─ (Chosen by LLM reasoning via WikiNavigator)

TIER 3: TARGETED (Dropped first if budget exceeded, token cost ~50%)
├─ Specific code ranges (lines 50-100 of module.py)
├─ Function implementations
├─ Critical data structures
└─ (Extracted from sources referenced in Wiki pages)

System Behavior:
• Always includes TIER 1 (user requirements, current state)
• Fills remaining budget with TIER 2 (semantic context)
• Fills remainder with TIER 3 (targeted code)
• If full, drops TIER 3 first, then TIER 2 (with warning)
• TIER 1 is NEVER dropped—preserves architectural intent
```

### 4. The Tool Harness (Safety Layer)

Every file operation passes through the **Tool Harness**:

```
User's LLM-Generated Action
           ↓
┌─────────────────────────────────────────┐
│ Tool Harness Verification               │
├─────────────────────────────────────────┤
│ 1. Exclusion check: Is file in .gitignore? → BLOCK
│ 2. Scope check: Is file in approved plan scope? → BLOCK
│ 3. Permission check: Allowed operation? → ALLOW/BLOCK
│ 4. Validation: Whitespace tolerance for patches → FIX
│ 5. Sync: Update Wiki hashes after mutation → SYNC
└─────────────────────────────────────────┘
           ↓
Operation Proceeds (or Blocked)
           ↓
Result Logged & Traced
```

**Safety Guarantees**:
- No accidental writes outside plan scope
- No modifications to system/secret files
- Patches work even with different whitespace
- Knowledge base stays current (no semantic drift)

### 5. Wiki Hash Validation (Integrity)

Every semantic page in the Wiki references actual source code via hash:

```
Module Page (wiki/modules/messaging.md)
│
├─ Source Reference 1:
│  ├─ file: src/messaging.py
│  ├─ lines: 50-150
│  └─ hash: a1b2c3... (SHA-256 of those exact lines)
│
└─ Source Reference 2:
   ├─ file: src/messaging.py
   ├─ lines: 200-250
   └─ hash: x9y8z7... (SHA-256 of those exact lines)

When loading context:
• Check each hash against actual file content
• If hash matches: Include page (content is fresh)
• If hash differs: Exclude page (content is stale) + warn user
• If file deleted: Mark as DELETED + exclude

This prevents "semantic drift"—LLM won't see outdated information
about your project structure.
```

---

## Getting Started

### Installation

#### Prerequisites

- Python 3.10 or later
- pip or Poetry
- An LLM API key (Anthropic, OpenAI, Groq, etc.)

#### Step 1: Install SimpCode

```bash
# Via pip (from GitHub)
pip install git+https://github.com/simpcode/simpcode.git

# OR via Poetry in the project
poetry add simpcode
```

#### Step 2: Initialize Global Configuration

```bash
simp setup
```

You'll be prompted:
```
Choose LLM Provider: [groq] ← Default
Enter Model ID: llama-3.3-70b-versatile
Enter API Key: gsk_...
```

**Configuration is saved to** `~/.simp/config.json`

#### Step 3: Initialize Your Project

```bash
cd your-project/
simp init
```

This will:
1. **Analyze** your codebase (file tree, manifests, entry points)
2. **Generate** SIMP.md (auto-generated project manifest)
3. **Generate** SPEC.md (auto-generated specification template)
4. **Bootstrap** the Wiki (`.simp/wiki/` with initial semantic pages)
5. **Open** the interactive TUI shell

**Output**:
```
Initializing SimpCode at /path/to/project
✓ Mission Establishment Complete.
 - SIMP.md (Project Intelligence)
 - SPEC.md (Project Requirements)
 - .simp/wiki/ (Knowledge Base)
```

### Your First Task

Once initialized, you interact via the **TUI shell**:

```bash
$ simp init
[SimpCode Interactive Shell]

simp> Improve type hints in the messaging module
```

What happens:
1. **Context Assembly**: Scans Wiki, loads messaging module pages, extracts relevant code
2. **Planning**: LLM designs a plan with concrete steps
3. **Execution**: Executes each step with verification
4. **Learning**: Analyzes changes, updates Wiki with new patterns

Expected output:
```
[PLAN]
Step 1: Add type hints to message_handler() function
  Target: src/messaging.py
  Action: Add parameter and return types
  Verification: Run mypy --strict

Step 2: Add type hints to sender_id validation
  Target: src/messaging.py (lines 120-140)
  Action: Add Protocol for user identification
  Verification: Type check passes

[EXECUTION]
>>> EXECUTION STEP 1: Add type hints to message_handler()...
  [Thought]: The function takes a message dict and returns a bool...
  [Action]: read_file(src/messaging.py)
  ✓ Step 1 verified and complete.

>>> EXECUTION STEP 2: Add type hints to sender_id validation...
  ...

[LEARNING]
✓ Execution complete. Updating Wiki...
  New Pattern Identified: Protocol-based validation pattern
  Risk Profile: Type checking reduces runtime errors by ~40%
```

---

## System Architecture

### Component Overview

#### 1. CLI & Shell Interface (cli/)

**Entry Point**: `cli/main.py`

Commands:
- `simp setup`: Configure LLM provider
- `simp init`: Initialize project
- Interactive shell: Main task interface

```python
# User interacts via:
$ simp init       # Initialize project
# [enters interactive shell]
simp> Your task description here
```

#### 2. Project Analysis (core/analyzer.py)

**Purpose**: Understand project structure without interpretation

```python
ProjectAnalyzer(root)
  .collect_metadata()
    → ProjectMetadata:
        - file_tree: List of all files (hierarchical compression for large projects)
        - manifests: pyproject.toml, package.json, requirements.txt, etc.
        - entry_point_samples: First 2000 chars of main.py, app.py, etc.
```

**Why separate collection from understanding?**
- Collection is deterministic (pure file I/O)
- Understanding is LLM-driven (can improve over time)
- Clear separation of concerns

#### 3. Intelligence Synthesis (core/generator.py)

**Purpose**: Use LLM to generate understanding from raw metadata

```python
IntelligenceSynthesizer(llm)
  .synthesize(metadata)
    → SynthesizedDocs:
        - simp_md: Project structure and modules
        - spec_md: Requirements template

DocumentGenerator(root)
  .write_docs(simp_md, spec_md)
    → SIMP.md and SPEC.md files written
```

#### 4. Wiki System (wiki/)

**Purpose**: Maintain semantic knowledge with integrity guarantees

```
.simp/wiki/
├── index.md              # Strategic navigation map
├── changes.md            # Semantic change log
├── patterns.md           # Recurring code patterns
├── modules/
│   ├── messaging.md      # Module responsibility + invariants
│   ├── auth.md
│   └── storage.md
├── symbols/
│   ├── MessageHandler.md # Critical class
│   └── authenticate.md   # Critical function
├── decisions/
│   ├── websocket_choice.md
│   └── sqlite_decision.md
└── cognitive/
    ├── performance_risks.md
    └── type_safety_patterns.md
```

**Key Components**:

- **WikiEngine**: Page discovery, staleness checking, persistence
- **WikiNavigator**: LLM-driven strategic navigation (not keyword RAG)
- **WikiBootstrap**: Initial ingestion from codebase + metadata
- **WikiPage**: Individual semantic node with hash-validated sources

#### 5. Context Assembly (core/modes.py, harness/budgeter.py)

**Purpose**: Intelligently assemble context within token budget

```python
ScanScene(root, llm)
  .run(task)
    → Returns: Assembled context string
    
    Process:
    1. Load mandatory: SIMP.md, index.md, skills. Include `SPEC.md` only if present.
    2. Multi-pass navigation:
       - Pass 1: LLM decides which semantic pages needed
       - Pass 2: Resolve dependencies, load supplemental pages
    3. Extract targeted code ranges from loaded pages
    4. Assemble within token budget (tiered)
    → Output: ~80-120k tokens of curated context
```

#### 6. Planning (core/planner.py)

**Purpose**: Generate atomic, verifiable implementation plan

```python
PlanGenerator(llm, scanner)
  .generate(task, initial_context)
    → Returns: Plan
    
    Process:
    1. CSIO reasoning: Establish Context → Scope → Intent → Output
    2. Generate atomic steps with:
       - target: Which file to modify
       - action: What to do
       - rationale: Why it matters
       - verification: How to verify it worked
    3. Multi-turn: Request additional context if needed
    → Output: Structured Plan ready for execution
```

#### 7. Execution (core/executor.py)

**Purpose**: Safely execute plan with live verification

```python
TakeAction(root, llm)
  .execute(plan, context)
    → Returns: Execution trace
    
    For each step:
    1. Refresh context (ScanScene)
    2. ReAct loop:
       - LLM reasons about current state
       - LLM decides next action (tool call)
       - Execute via ToolHarness
       - LLM verifies step complete
       - Continue until verified
    3. Log execution trace
    → Output: Modified files + trace
```

#### 8. Learning (core/evolution.py)

**Purpose**: Extract and memorize architectural insights

```python
GetBetter(root, llm)
  .run(task, execution_trace)
    → Returns: EvolutionProposals
    
    Analysis:
    - What patterns emerged?
    - What risks were encountered?
    - What new invariants did we learn?
    - Update Wiki with findings
    → Output: Enhanced semantic knowledge
```

#### 9. Tool Harness (harness/tools.py)

**Purpose**: Safe, scoped, verified file operations

```python
ToolHarness(root, allowed_files)
  .read_file(path)     → String
  .write_file(path, content)  → Void (with Wiki sync)
  .patch_file(path, old, new) → Bool (with whitespace tolerance)
  .run_shell(command)  → String (with safe execution)
  
Every operation:
  1. Checks scope (is path in allowed_files?)
  2. Checks exclusions (gitignore, .simpignore)
  3. Executes safely
  4. Updates Wiki hashes
  5. Logs to trace
```

#### 10. LLM Abstraction (core/llm/)

**Purpose**: Unified interface to multiple LLM providers

```python
LLMClient(provider="groq", model_id="llama-3.3-70b-versatile")
  .complete(prompt, system_instruction)  → String
  .structured_output(prompt, schema, system_instruction)  → Pydantic model
  
Supported Providers:
  - Anthropic (Claude 3+)
  - OpenAI (GPT-4, GPT-4-turbo)
  - Groq (Llama 3.3 70B)
  - OpenRouter (Multi-model proxy)
  - Google (Gemini)
  - OLLama (Local models)
```

#### 11. Prompt Registry (core/prompts/)

**Purpose**: Externalize LLM instructions for transparency and tuning

```
core/prompts/
├── base_principles.md          # Loaded for ALL roles
├── onboarding_architect.md     # Used in synthesis (init phase)
├── onboarding_documents.md     # Prompt template for SIMP/SPEC generation
├── wiki_bootstrap.md           # Wiki ingestion
├── wiki_navigator.md           # Strategic page selection
├── wiki_librarian.md          # Wiki maintenance
├── wiki_maintainer.md         # Staleness resolution
├── staff_architect.md          # Planning persona
├── staff_architect_plan.md     # Planning prompt template
├── staff_implementer.md        # Execution persona
├── staff_implementer_step.md   # Execution prompt template
├── staff_researcher.md         # Learning persona
├── staff_researcher_learning.md # Learning prompt template
├── interactive_assistant.md    # Chat interaction
└── research_assistant.md       # Research support
```

Each role loads:
1. `base_principles.md` (core philosophy)
2. Role-specific system prompt (persona)
3. Task-specific prompt template (current phase)

---

## User Workflows

### Workflow 1: Onboarding a New Project

**Scenario**: You have a Python project you want SimpCode to understand.

**Steps**:

```bash
# 1. Set up LLM (one time)
$ simp setup
> LLM Provider: groq
> Model: llama-3.3-70b-versatile
> API Key: gsk_...
✓ Saved to ~/.simp/config.json

# 2. Enter project directory
$ cd /path/to/your/project

# 3. Initialize SimpCode
$ simp init
[Analyzing project structure...]
[Synthesizing intelligence...]
[Bootstrapping wiki...]
✓ Project initialized
 - SIMP.md created (project manifest)
 - SPEC.md created (requirements template)
 - .simp/wiki/ created (knowledge base)
```

**What happens behind the scenes**:

1. **Analysis Phase**: Collects file tree, manifests, entry points
2. **Synthesis Phase**: LLM reads metadata and generates SIMP.md + SPEC.md
3. **Bootstrap Phase**: LLM reads codebase and creates initial Wiki pages
4. **Ready**: Project is now understood by SimpCode

**Next steps**:

- Review and edit SPEC.md (add your real requirements)
- Start tasks: `simp init` opens TUI where you can describe tasks

### Workflow 2: Iterative Task Execution

**Scenario**: You have ongoing development work. SimpCode learns and improves.

**Example Task Cycle**:

```
Day 1:
  simp> Add comprehensive logging to auth module
  [SimpCode plans, executes, learns about logging patterns]
  → Wiki updated with: logging strategy, error handling patterns, conventions
  
Day 2:
  simp> Add logging to storage module too
  [SimpCode recalls logging patterns from Wiki]
  [Execution faster and more consistent]
  → Wiki updated with: storage-specific patterns, integration points
  
Day 3:
  simp> Refactor logging to use structured JSON format
  [SimpCode understands full logging architecture]
  [Proposes changes with high confidence]
  → Wiki updated with: new logging format, compatibility invariants
```

**Each cycle improves understanding**.

### Workflow 3: Large Refactoring

**Scenario**: You want to refactor a major component across multiple files.

**Process**:

```bash
# Step 1: Review current Wiki state
# (What does SimpCode understand about the component?)

# Step 2: Update SPEC.md
# (Describe the refactoring goal clearly)
# - Current architecture: service-based
# - Target architecture: plugin-based
# - Constraints: API compatibility
# - Constraints: Backwards compatible migrations

# Step 3: Execute refactoring
simp> Refactor authentication from service-based to plugin-based architecture
  according to the new SPEC.md goals

# Step 4: SimpCode will:
#   1. Load SPEC (understands your goal)
#   2. Load current Wiki (understands current architecture)
#   3. Plan atomic steps
#   4. Execute with verification
#   5. Learn new patterns

# Step 5: Review and iterate
# If any step needs adjustment, describe the issue:
simp> The plugin interface is missing the validate_token method
```

### Workflow 4: Multi-Session Continuity

**Scenario**: You work on the project over days/weeks. Knowledge persists.

```
Session 1 (Monday):
  - Initialize project
  - Add auth module
  - SimpCode learns: auth patterns, naming conventions
  → Wiki persisted in .simp/wiki/

Session 2 (Wednesday):
  - [Restart terminal, cd to project]
  simp> Add data validation to auth module
  [SimpCode recalls learned patterns from Monday]
  [Executes with consistency]

Session 3 (Next week):
  - [Same process]
  - SimpCode has cumulative understanding
  - Execution efficiency increases
```

**Knowledge base survives project restart** because it's stored in `.simp/wiki/`.

### Workflow 5: Debugging and Verification

**Scenario**: Something didn't work as expected.

**SimpCode's Response**:

```bash
simp> The auth tests are failing after your changes
# SimpCode will:
# 1. Load SPEC.md (what should tests verify?)
# 2. Load failed test code + recent changes
# 3. Analyze mismatch
# 4. Propose fixes
# 5. Execute with verification

simp> The API response format changed but docs still reference old format
# SimpCode will:
# 1. Find all references to old format
# 2. Update docs, tests, examples
# 3. Verify consistency
```

---

## Configuration & Customization

### SPEC.md: Defining Your Project Intent

**Location**: `/path/to/project/SPEC.md` (created at init, you edit it)

**Purpose**: Your authoritative source of truth for project requirements and goals

**Structure**:

```markdown
# SPEC: Project Name

## Overview
Brief description of the project goals and vision.

## Requirements
- Functional requirements (what should it do?)
- Non-functional requirements (performance, scalability, etc.)
- Constraints (technology choices, deployment, etc.)

## Architecture
- Intended system design
- Modules and responsibilities
- Key invariants
- Dependencies

## Deployment
- How is this deployed?
- What are production constraints?

## Performance
- Speed/throughput targets
- Memory constraints
- Scalability goals

## Examples
- Key usage patterns
- Success criteria
```

**How SimpCode Uses It**:
- Always included in context (TIER 1)
- Directs LLM reasoning toward your goals
- Used in planning to verify scope alignment
- Used in learning to validate proposed changes

**Best Practices**:
- Be specific about constraints
- Update SPEC when requirements change
- Use SPEC to document architectural decisions
- Keep it concise (SimpCode will read the whole thing)

### SIMP.md: Documenting Current State

**Location**: `/path/to/project/SIMP.md` (auto-generated at init, you can edit)

**Purpose**: What does the system look like RIGHT NOW?

**Structure**:

```markdown
# SIMP: Project Name

## Current Architecture
- Language: Python 3.10
- Framework: FastAPI (web) + SQLAlchemy (ORM)
- Package manager: Poetry

## Module Overview
### Modules
- auth: JWT-based authentication
- api: REST API endpoints
- database: ORM models and migrations
- utils: Helper functions

## Data Model
```

**How SimpCode Uses It**:
- Always included in context (TIER 1)
- Provides ground truth about current system state
- Helps LLM understand existing code without re-reading

**Best Practices**:
- Update SIMP.md when major structural changes complete
- Use it to document module purposes
- Keep it in sync with actual architecture
- Use as a quick reference guide

### Skills: Project-Specific Task Templates

**Location**: `.simp/skills/` (optional)

**Purpose**: Pre-defined task templates specific to your project

**Example**:

```markdown
# .simp/skills/add_endpoint.md

# Add API Endpoint (Skill)

When user asks to add a new endpoint, follow this pattern:

## Steps
1. Define request/response models (Pydantic)
2. Add function handler with FastAPI decorator
3. Add documentation
4. Add unit tests
5. Update OpenAPI schema

## Files to Modify
- src/api.py (add handler)
- tests/test_api.py (add tests)
- docs/endpoints.md (update docs)

## Verification
- API server starts without error
- Tests pass
- OpenAPI docs reflect new endpoint
```

**How It Works**:
1. Create `.simp/skills/` directory
2. Add `.md` files with task patterns
3. SimpCode automatically discovers and selects them
4. LLM uses skills to guide execution

### LLM Configuration

**Global Config**: `~/.simp/config.json`

```json
{
  "active_provider": "groq",
  "providers": {
    "groq": {
      "provider": "groq",
      "model_id": "llama-3.3-70b-versatile",
      "api_key": "gsk_..."
    },
    "anthropic": {
      "provider": "anthropic",
      "model_id": "claude-3-opus-20240229",
      "api_key": "sk-ant-..."
    }
  }
}
```

**Change LLM**:

```bash
# View current config
cat ~/.simp/config.json

# Run setup to change provider
simp setup

# Or edit file directly and set active_provider
```

**Supported Providers**:

| Provider | Model IDs | Speed | Quality | Cost |
|----------|-----------|-------|---------|------|
| Groq | llama-3.3-70b-versatile | ⚡⚡⚡ Fast | Good | Low |
| Anthropic | claude-3-opus, claude-3-sonnet | ⚡⚡ Fast | Excellent | Medium |
| OpenAI | gpt-4, gpt-4-turbo | ⚡ Slower | Excellent | High |
| Google | gemini-pro | ⚡⚡ Fast | Good | Low |
| OLLama | Local models | ⚡⚡⚡ Fast | Variable | Free |

**Environment Variables** (override config):

```bash
export SIMP_LLM_PROVIDER=anthropic
export SIMP_LLM_MODEL=claude-3-opus-20240229
export ANTHROPIC_API_KEY=sk-ant-...

# Now run simp with different provider
simp init
```

### Custom Prompts

**Location**: `src/simpcode/core/prompts/` (for system prompts)

**Adding a Custom Role**:

1. Create `src/simpcode/core/prompts/my_role.md`:
```markdown
# IDENTITY
ROLE: Custom Role Name
PERSONA: Description

<role>
You are an expert...
</role>

<instructions>
# SCOPE
OBJECTIVE: ...
INPUT: ...
OUTPUT: ...

# INTENT
...

# CONSTRAINTS
...
</instructions>
```

2. Create `src/simpcode/core/prompts/my_role_task.md`:
```markdown
# PROMPT TEMPLATE

Given the following:
- Current context: {current_context}
- Task: {task}

Generate...
```

3. Register in `core/prompts/__init__.py`:
```python
registry.register("my_role", "src/simpcode/core/prompts/my_role.md")
registry.register("my_role_task", "src/simpcode/core/prompts/my_role_task.md")
```

### Exclusions: Protecting Sensitive Files

**Methods**:

1. **Use .gitignore**: Automatically respected
   ```
   .env
   secrets/
   venv/
   .vscode/
   ```

2. **Create .simpignore**: Project-specific exclusions
   ```
   # .simpignore
   private/
   .credentials/
   temp_experiments/
   ```

---

## Advanced Usage

### 1. Working with Large Monorepos

**Challenge**: Context budget can't fit entire monorepo

**Solutions**:

**A) Hierarchical Compression** (Automatic):
- For projects > 500 files, analyzer compresses directory structure
- Example output: `src/modules/*/ (127 files)` instead of listing all

**B) Strategic Scoping** (Manual):
```markdown
# SPEC.md

## Project Scope
Only work on:
- services/auth/ (user authentication)
- services/api/ (API layer)

Do NOT modify:
- services/legacy/ (deprecated)
- services/experimental/ (in flux)
- infrastructure/ (handled separately)
```

**C) Skills-Based Decomposition** (Recommended):
```markdown
# .simp/skills/auth_changes.md
# .simp/skills/api_changes.md
# .simp/skills/storage_changes.md

# Each skill is scoped to one service
```

SimpCode will select appropriate skill based on task description.

### 2. Multi-LLM Workflows

**Scenario**: Use different LLMs for different phases

```bash
# Setup multiple providers
simp setup
> Provider: groq    # Fast planner
> Provider: anthropic  # Better executor

# In practice:
# - Use fast LLM for planning (saves cost)
# - Use quality LLM for execution/verification
# - Flexibility: switch based on task complexity
```

**Configuration for Per-Task Provider Selection** (future enhancement):

Currently, active_provider is global. Can work with specific provider via environment:

```bash
# Use Anthropic for this task
SIMP_LLM_PROVIDER=anthropic SIMP_LLM_MODEL=claude-3-opus-20240229 simp init
```

### 3. Wiki Maintenance and Evolution

**Understanding Wiki State**:

```bash
# View all wiki pages
ls -la .simp/wiki/

# Check for stale pages
# (Automatically excluded from context, but visible in Wiki)
ls -la .simp/wiki/modules/  # Old module documentation

# Read specific page
cat .simp/wiki/index.md     # Strategic navigation map
cat .simp/wiki/changes.md   # Semantic change log
```

**Refreshing Stale Pages**:

```bash
simp> The authentication module was heavily refactored, update the wiki
# SimpCode will:
# 1. Detect stale auth pages
# 2. Re-analyze current auth module
# 3. Update wiki/modules/auth.md with fresh content
```

**Pruning Old Knowledge**:

```bash
# If you want to start fresh learning:
rm -rf .simp/wiki/
# Next `simp` command will bootstrap wiki again

# Or, selective:
rm .simp/wiki/modules/deprecated_module.md
```

### 4. Execution Tracing and Debugging

**View Last Execution Trace**:

```bash
# SimpCode logs to session directory
ls ~/.simp/sessions/
cat ~/.simp/sessions/sess_1234567890/trace.log

# Contains:
# - Full execution transcript
# - Tool calls and results
# - Context assembly details
# - Learning phase outputs
```

**Debug Context Assembly**:

Add debug logging in your project:

```python
# src/main.py or test
from simpcode.core.modes import ScanScene
from simpcode.core.llm import LLMClient

llm = LLMClient()
scanner = ScanScene(Path("."), llm)
context = scanner.run("Your task description")
print(context)  # Inspect what context was assembled
```

### 5. Performance Tuning

**Reducing Context Size**:

```markdown
# SPEC.md

## Context Optimization
- Only load wiki pages for: [auth, api, database]
- Skip cognitive pages (performance optimization)
- Truncate SPEC.md if > 2000 characters
```

**Reducing LLM Calls**:

- Use faster/cheaper LLM for planning
- Reuse plans across similar tasks
- Batch multiple tasks into one plan

**Token Budget Management**:

```bash
# Adjust context budget (in executor code)
budgeter = ContextBudgeter(total_budget=80000, model="gpt-4")
# Default: 100,000 tokens
# Adjust based on your LLM's context window
```

---

## Troubleshooting

### Issue: "Permission Denied" on File Write

**Symptom**:
```
Error: Plan Violation: 'src/new_module.py' is not in the approved scope
```

**Cause**: File not mentioned in the plan

**Solution**:
1. Review the plan: Were all necessary files included?
2. Re-describe the task: "Add new_module.py that handles..."
3. SimpCode will include it in plan scope

### Issue: Wiki Page Is Stale

**Symptom**:
```
[Scan] Warning: Wiki page modules/auth is stale. Excluded from context.
```

**Cause**: Module code changed, hash no longer matches

**Solution**:
1. Expected behavior (safety mechanism)
2. Run a task focused on that module: "Refactor auth module"
3. SimpCode will update the wiki page

### Issue: Context Budget Exceeded

**Symptom**:
```
[Warning] Context Budget Exceeded: Dropping CodeRange for services/database.py
```

**Cause**: Project is too large for context window

**Solutions**:
1. Use a larger model (e.g., GPT-4 → 128k context)
2. Narrow task scope (work on one module at a time)
3. Use skills to pre-filter context
4. Increase budgeter limit if your LLM supports it

### Issue: LLM Fails to Generate Plan

**Symptom**:
```
Planner failed to generate a valid plan.
RuntimeError: Expected response schema...
```

**Causes**:
- Prompt is ambiguous or too complex
- Context was truncated, LLM lost key info
- LLM API rate-limited or down

**Solutions**:
1. Simplify task description
2. Add more detail to SPEC.md for clarity
3. Break into smaller tasks
4. Check LLM provider status
5. Try different LLM provider

### Issue: Tool Execution Fails

**Symptom**:
```
Action: patch_file(...)
Error: Failed to apply patch: No matching context found
```

**Cause**: Whitespace changed, patch can't apply

**Solution**:
- This should NOT happen (whitespace-tolerant patching is implemented)
- If it does: Report issue, workaround with read + write instead

### Issue: Changes Not Reflected

**Symptom**:
```
Modified src/auth.py but the changes aren't there
```

**Cause**: Execution didn't complete or step marked incomplete

**Solution**:
1. Check execution trace: `cat ~/.simp/sessions/*/trace.log`
2. Run verification manually: `python -m pytest tests/test_auth.py`
3. Re-run task: "Fix the auth tests after your changes"

### Issue: Wiki Not Updating

**Symptom**:
```
Ran task, but .simp/wiki/ hasn't changed
```

**Cause**: Learning phase (GetBetter) didn't find new patterns to extract

**Solution**:
- Normal if task didn't reveal new architectural patterns
- Continue working; wiki updates as system learns
- Force refresh: Delete relevant wiki page, next task regenerates it

### Issue: OLLama Connection Failed

**Symptom**:
```
Error: Failed to connect to http://localhost:11434
```

**Solution**:
1. Start OLLama: `ollama serve`
2. Pull model: `ollama pull llama2`
3. Verify: `curl http://localhost:11434/v1/models`
4. Then configure SimpCode

---

## Real-World Examples

### Example 1: Adding a New API Endpoint

**User Task**:
```
simp> Add a new /api/notifications endpoint that returns user notifications
     with pagination. Returns list of notifications with id, message, created_at,
     read status. Support limit and offset query parameters.
```

**What SimpCode Does**:

**Phase 1: Context Assembly**
- Loads SPEC (project goals)
- Loads SIMP (current architecture)
- Navigates Wiki: "How do other endpoints work?" → loads api.md, models.md, pagination.md
- Extracts code: Current endpoint implementations, Pydantic models, database queries
- Result: ~80k tokens of curated context

**Phase 2: Planning**
- Analyzes: existing endpoint pattern (FastAPI + Pydantic + SQLAlchemy)
- Generates Plan with steps:
  1. Create NotificationDB model (if needed)
  2. Create NotificationSchema Pydantic model
  3. Add /api/notifications route handler
  4. Add unit tests
  5. Verify API docs updated
  
**Phase 3: Execution**
- Step 1: Reads database models file → adds NotificationDB
- Step 2: Reads schema file → adds NotificationSchema
- Step 3: Reads api.py → adds route with pagination logic
- Step 4: Creates test file → adds test cases
- Step 5: Verifies with `pytest` + API server start

**Phase 4: Learning**
- Analyzes execution trace
- Identifies: "Pagination pattern consistently used in endpoints"
- Updates Wiki: patterns.md with pagination invariant
- Next similar task will be faster

**Result**:
```bash
✓ Endpoint created: /api/notifications?limit=10&offset=0
✓ Tests passing: test_notifications.py (8/8)
✓ API docs updated: OpenAPI schema includes endpoint
✓ Wiki evolved: New pagination pattern recognized
```

### Example 2: Refactoring to TypedDict

**User Task**:
```
simp> Update the project to use TypedDict instead of Dict[str, Any]
      for better type safety. Start with critical modules.
```

**What SimpCode Does**:

**Phase 1: Context Assembly**
- Loads SPEC: "Goal is type safety improvement"
- Loads Wiki: "Which modules are critical?" → loads index.md
- Identifies: auth, api, database as critical
- Loads current type annotations + Dict usage patterns

**Phase 2: Planning**
- Creates phased plan:
  1. Define TypedDict types in types.py
  2. Update auth module type hints
  3. Update api module type hints
  4. Update database module type hints
  5. Run mypy --strict to verify
  6. Update tests

**Phase 3: Execution**
- Creates types.py with all TypedDict definitions
- Updates each module: Search for Dict[str, Any] → replace with specific TypedDict
- Runs mypy after each module
- Updates tests to use TypedDict

**Phase 4: Learning**
- Identifies: "TypedDict requires upfront planning, defines all keys"
- Identifies Risk: "Missing keys cause runtime KeyError"
- Updates Wiki: "Type Safety" page with TypedDict best practices

### Example 3: Debugging Test Failures

**User Task**:
```
simp> tests/test_auth.py is failing after your recent changes. Debug and fix.
```

**What SimpCode Does**:

**Phase 1: Context Assembly**
- Loads test file + recent changes
- Loads auth.py (what changed)
- Loads SPEC + SIMP (what should tests verify)
- Loads wiki/modules/auth.md (auth invariants)

**Phase 2: Planning**
- Analyzes failure: `test_token_validation failed`
- Compares: Test expects JWT validation, but code changed behavior
- Plan:
  1. Update test expectations OR
  2. Fix auth.py logic to match specification

**Phase 3: Execution**
- Reads test code + code being tested
- Determines root cause
- Executes fix
- Verifies: test passes

**Phase 4: Learning**
- Identifies: "Validation invariants must be documented"
- Updates Wiki: auth.md with validation spec

---

## API Reference

### Core Classes

#### LLMClient

```python
from simpcode.core.llm import LLMClient

# Initialize (uses global config or env vars)
llm = LLMClient()

# OR with specific provider
llm = LLMClient(provider="anthropic", model_id="claude-3-opus-20240229")

# Methods
response = llm.complete(
    prompt="Your prompt here",
    system_instruction="System message"
)

# Structured output (returns Pydantic model)
from pydantic import BaseModel

class MyResponse(BaseModel):
    answer: str
    confidence: float

result = llm.structured_output(
    prompt="Your prompt",
    output_schema=MyResponse,
    system_instruction="System message"
)
# result.answer, result.confidence available
```

#### ProjectAnalyzer

```python
from simpcode.core.analyzer import ProjectAnalyzer
from pathlib import Path

analyzer = ProjectAnalyzer(Path("/path/to/project"))
metadata = analyzer.collect_metadata()

# Access
metadata.name              # Project name
metadata.file_tree         # List of all files
metadata.manifests         # Dict of manifest contents
metadata.entry_point_samples  # Dict of entry point snippets
```

#### ScanScene

```python
from simpcode.core.modes import ScanScene
from simpcode.core.llm import LLMClient
from pathlib import Path

llm = LLMClient()
scanner = ScanScene(Path("/path/to/project"), llm)
context = scanner.run("Your task description")
# context: Full assembled context string ready for LLM
```

#### PlanGenerator

```python
from simpcode.core.planner import PlanGenerator

planner = PlanGenerator(llm, scanner)
plan = planner.generate(
    task="Your task",
    initial_context="Assembled context from ScanScene"
)

# Access plan
for step in plan.steps:
    print(f"Step {step.id}: {step.action}")
    print(f"  Target: {step.target}")
    print(f"  Verify: {step.verification}")
```

#### TakeAction

```python
from simpcode.core.executor import TakeAction
from pathlib import Path

executor = TakeAction(root=Path("/path/to/project"), llm=llm)
executor.execute(
    plan=plan,
    context=context,
    scanner=scanner,
    task="Original task description"
)
# Modifies files, logs trace
```

#### GetBetter

```python
from simpcode.core.evolution import GetBetter

learner = GetBetter(root=Path("/path/to/project"), llm=llm)
proposals = learner.run(
    task="What was the task?",
    execution_trace="Full execution transcript"
)

# Access proposals
proposals.new_patterns
proposals.new_risks
proposals.new_invariants
proposals.change_log_entry
```

### Configuration

```python
from simpcode.core.config import global_config

# Get active config
config = global_config.get_active_config()
print(config.provider)   # Active provider name
print(config.model_id)   # Model ID
print(config.api_key)    # API key (hidden)

# Save new config
new_config = LLMProviderConfig(
    provider="anthropic",
    model_id="claude-3-opus-20240229",
    api_key="sk-ant-..."
)
global_config.save(new_config)
```

### Wiki Access

```python
from simpcode.wiki.engine import WikiEngine
from pathlib import Path

wiki = WikiEngine(Path("/path/to/project"))

# Get all pages
pages = wiki.get_all_pages()

# Get specific page
page = wiki.get_page("modules/auth")
print(page.content)
print(page.metadata.sources)

# Check if page is stale
if wiki.is_page_stale(page):
    print("Page is stale (source code changed)")
    stale_sources = wiki.check_staleness(page)
```

### Tool Harness

```python
from simpcode.harness.tools import ToolHarness
from pathlib import Path

harness = ToolHarness(
    root=Path("/path/to/project"),
    allowed_files=["src/auth.py", "src/api.py"]
)

# Read file
content = harness.read_file("src/auth.py")

# Write file
harness.write_file("src/new_module.py", "code content")

# Patch file (whitespace-tolerant)
success = harness.patch_file(
    "src/auth.py",
    old_text="def authenticate():",
    new_text="def authenticate(user_id: str):"
)

# Run shell command
result = harness.run_shell("pytest tests/test_auth.py")
```

---

## FAQ

### Q: How is SimpCode different from Copilot/ChatGPT?

**A**:

| Feature | SimpCode | Copilot/ChatGPT |
|---------|----------|-----------------|
| **Scope** | Full project context | Single file/snippet |
| **Memory** | Persistent Wiki | Session only |
| **Verification** | Automatic test + lint | Manual |
| **Safety** | Enforced scope | No enforcement |
| **Learning** | Improves over time | No learning |
| **Multi-LLM** | Swappable providers | Single model |

Copilot is great for quick code snippets. SimpCode is for project-scale engineering.

### Q: Does SimpCode work with non-Python projects?

**A**: Currently, SimpCode is Python-based, but the architecture is language-agnostic.

Roadmap:
- Support for multi-language projects (Go, Rust, JavaScript)
- Language-specific type inference
- Cross-language refactoring

For now:
- Works best with Python projects
- Can work with projects containing multiple languages (Python as orchestrator)

### Q: How much does it cost to run SimpCode?

**A**: Depends on your LLM choice:

- **Groq (Recommended)**: ~$0.01-0.05 per task (very cheap, fast)
- **Anthropic**: ~$0.10-0.50 per task (quality, medium cost)
- **OpenAI GPT-4**: ~$0.50-2.00 per task (premium quality, higher cost)
- **OLLama (Local)**: Free (runs on your machine)

Tips for cost reduction:
- Use fast LLM for planning (Groq), quality for execution (Anthropic)
- Batch similar tasks together
- Keep SPEC and SIMP concise

### Q: Can I run SimpCode offline?

**A**: Yes! Use OLLama:

```bash
# 1. Install OLLama
brew install ollama

# 2. Pull a model
ollama pull llama2

# 3. Configure SimpCode
simp setup
> Provider: ollama
> Model: llama2
> Base URL: http://localhost:11434/v1

# 4. Run offline
simp init  # Uses local LLM, no API calls
```

Tradeoff: Local LLMs are slower and less capable than commercial ones.

### Q: What if I don't trust SimpCode to modify my code?

**A**: Good instinct. Safety mechanisms:

1. **Dry-run mode**: (Future) View plan before execution
2. **Review changes**: Use `git diff` before committing
3. **Undo easily**: `git checkout` if something breaks
4. **Scope enforcement**: Explicit scope prevents accidental changes
5. **Version control**: Always keep your code in Git

Recommended workflow:
```bash
simp> Add type hints to auth module
# [Review generated changes]
git diff src/auth.py
# [If good]
git add src/auth.py
git commit -m "Add type hints (SimpCode)"
```

### Q: How do I extend SimpCode?

**A**: Several ways:

1. **Custom Skills**: Add `.simp/skills/` with task templates
2. **Custom Prompts**: Add to `src/simpcode/core/prompts/`
3. **Custom Tools**: Subclass `LLMProvider` or `ToolHarness`
4. **Custom Roles**: Create new system prompts in registry

Example: Custom skill

```markdown
# .simp/skills/add_test.md

# Add Unit Test (Skill Template)

## Steps
1. Identify function to test
2. Create test file
3. Write test cases (happy + error paths)
4. Run pytest to verify
```

### Q: Can I use SimpCode in CI/CD?

**A**: Yes! Use in pipelines:

```bash
# .github/workflows/improve.yml
name: SimpCode Improvement
on: [push]
jobs:
  improve:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Install SimpCode
        run: pip install simpcode
      - name: Configure
        run: simp setup
        env:
          GROQ_API_KEY: ${{ secrets.GROQ_API_KEY }}
      - name: Add typing
        run: simp-batch "Add type hints to src/ for static analysis"
      - name: Commit improvements
        run: |
          git config user.name "SimpCode"
          git add -A
          git commit -m "Improve code quality [SimpCode]"
          git push
```

### Q: Is my code private when using SimpCode?

**A**: Depends on LLM provider:

- **Groq, OpenAI, Anthropic**: Code sent to their APIs (read their privacy policies)
- **OLLama**: Code stays on your machine (true privacy)
- **Enterprise**: Deploy SimpCode with private LLM backend

If privacy is critical:
- Use OLLama locally
- Or deploy with your own LLM backend

### Q: How do I report bugs?

**A**: Open an issue on GitHub with:
- Description of the problem
- Reproduction steps
- Output from `cat ~/.simp/sessions/*/trace.log`
- Python version, LLM provider

### Q: Can SimpCode write tests?

**A**: Yes! Example:

```bash
simp> Write comprehensive tests for the auth module
      covering happy paths, error cases, edge cases
```

SimpCode will:
1. Analyze current auth module
2. Design test cases
3. Create test file
4. Run tests
5. Learn testing patterns

---

## Conclusion

SimpCode represents a new paradigm for AI-assisted software engineering:

- **Persistent Knowledge**: Your project is remembered and understood
- **Safe Execution**: Strict scope, verification, and accountability
- **Continuous Improvement**: System learns from every task
- **Human-Centered**: You maintain control and make architectural decisions
- **Production-Ready**: All 8 architectural flaws fixed and validated

Start with `simp init` and explore. Each task makes SimpCode smarter.

---

**For Questions or Issues**: Refer to [Troubleshooting](#troubleshooting) section or check the GitHub issues.

**For Contributing**: See [Development Guide](../DEVELOPMENT.md) (coming soon)

**Last Updated**: 2026-05-12 | SimpCode v3.0
