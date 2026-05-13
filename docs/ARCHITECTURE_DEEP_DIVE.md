# SimpCode Architecture Deep Dive

This document explains the internal architecture and design decisions in SimpCode.

**For Users**: Start with the [Comprehensive Guide](COMPREHENSIVE_GUIDE.md)  
**For Developers**: This document explains the system design

---

## Design Principles

### 1. Wiki-First Semantic Navigation

**Problem**: Traditional tools grep files randomly (semantic amnesia)

**Solution**: Maintain a semantic knowledge graph (the Wiki) with hash-validated sources

**Implementation**:
- Every Wiki page references actual code via SHA-256 hash
- Before using a page, verify hash matches current code
- If hash differs: exclude page (content is stale)
- This prevents using outdated information about your codebase

**Benefit**: LLM always works with fresh, accurate understanding

### 2. Tiered Context Assembly

**Problem**: Context windows are expensive and limited

**Solution**: Assemble context in tiers (mandatory > semantic > targeted)

```
Tier 1: MANDATORY (never drop)
├─ SPEC.md (user requirements)
├─ SIMP.md (current system state)
└─ Wiki index (strategic map)

Tier 2: SEMANTIC (drop if budget exceeded)
├─ Module responsibility pages
├─ Architectural decision pages
└─ Risk and pattern pages

Tier 3: TARGETED (drop first)
├─ Specific code ranges
└─ Function implementations
```

**Token Budget Enforcement**:
- Default: 100k tokens
- Fill Tier 1 (mandatory)
- Fill Tier 2 with remaining budget
- Fill Tier 3 with what's left
- If Tier 2 doesn't fit: drop with warning
- Tier 1 is NEVER dropped

**Benefit**: Always has architectural context, scales to large projects

### 3. Read-Before-Write Execution

**Problem**: LLM could make wrong assumptions about current state

**Solution**: Every step reads affected files before modifying

**Implementation**:
```python
# For each plan step:
1. Read file(s) mentioned in target
2. LLM reasons about current state
3. LLM generates modification
4. Apply modification
5. Verify with test or lint
6. Continue until verified
```

**Benefit**: Catches state drift, prevents cascading failures

### 4. High-Integrity Tool Harness

**Problem**: Need to prevent accidental writes outside scope

**Solution**: Every file operation goes through gated harness

**Implementation**:
```python
ToolHarness(root, allowed_files)
  ├─ Path normalization (prevent ../../../ tricks)
  ├─ Scope validation (is file in allowed_files?)
  ├─ Exclusion check (is file in .gitignore or .simpignore?)
  └─ Permission enforcement (read-only vs read-write)
```

**Benefit**: Cannot modify files outside plan scope

### 5. Continuous Learning

**Problem**: Each task is independent; system doesn't grow

**Solution**: Extract patterns and risks from each execution

**Implementation**:
```python
GetBetter(root, llm).run(task, execution_trace)
  ├─ Analyze: What patterns emerged?
  ├─ Analyze: What risks occurred?
  ├─ Analyze: What new invariants exist?
  └─ Update: Wiki with findings
```

**Benefit**: System becomes smarter with each task

---

## Component Interactions

### 1. Initialization Flow (simp init)

```
User runs: simp init
│
├─→ ProjectAnalyzer(root)
│   └─ collect_metadata()
│       ├─ Walk filesystem → file_tree
│       ├─ Extract manifests (pyproject.toml, package.json, etc.)
│       └─ Extract entry point samples (first 2000 chars of main.py, etc.)
│
├─→ IntelligenceSynthesizer(llm)
│   └─ synthesize(metadata)
│       └─ LLM reads: file_tree + manifests + samples
│           └─ Generates: SIMP.md + SPEC.md
│
├─→ DocumentGenerator(root)
│   └─ write_docs(simp_md, spec_md)
│       └─ Writes: SIMP.md and SPEC.md to disk
│
└─→ WikiBootstrap(llm, root)
    └─ run(metadata)
        ├─ LLM reads: file_tree + manifests + samples
        └─ Generates: Initial Wiki pages (modules, symbols, decisions)
            └─ Writes to: .simp/wiki/

Result: Project is initialized with understanding
```

**Key**: Each phase builds on previous outputs

### 2. Task Execution Flow (User enters task)

```
User: "Add comprehensive logging to auth module"
│
├─→ ScanScene(root, llm).run(task)
│   ├─ Load mandatory: SIMP.md, index.md (never dropped). Include `SPEC.md` only if present.
│   ├─ WikiNavigator(llm).navigate(task, index)
│   │   └─ LLM reads: Task + index
│   │       └─ Decides: Which semantic pages needed?
│   ├─ Load selected pages (multi-pass if needed)
│   ├─ For each page, extract: targeted code ranges
│   └─ ContextBudgeter: assemble within token limit
│       └─ Returns: ~80-120k tokens of context
│
├─→ PlanGenerator(llm, scanner).generate(task, context)
│   ├─ Prepend SPEC.md (user requirements)
│   ├─ Multi-turn dialogue:
│   │   ├─ Turn 1: "Given context, generate plan OR request more context?"
│   │   ├─ If requesting: Load additional pages, retry
│   │   └─ Turn N: Generate final plan
│   └─ Returns: Plan with atomic steps
│
├─→ TakeAction(root, llm).execute(plan, context, scanner, task)
│   └─ For each step:
│       ├─ Refresh context: ScanScene.run(task) again
│       ├─ ReAct loop (repeat until step complete):
│       │   ├─ LLM reasoning: "What's current state? Next action?"
│       │   ├─ LLM decision: Call tool (read, write, patch, shell)
│       │   ├─ Tool execution via ToolHarness:
│       │   │   ├─ Validate scope
│       │   │   ├─ Execute operation
│       │   │   └─ Update Wiki hashes
│       │   ├─ Trace logging
│       │   └─ LLM verification: "Is this step complete?"
│       └─ Move to next step
│
└─→ GetBetter(root, llm).run(task, execution_trace)
    ├─ Analyze: What patterns emerged?
    ├─ Analyze: What risks occurred?
    ├─ Analyze: What new invariants exist?
    └─ Update Wiki: changes.md + new cognitive pages

Result: Task completed, Wiki evolved, ready for next task
```

**Key**: Each phase gets fresh context, no assumptions

### 3. Context Assembly Details (ScanScene)

```
ScanScene.run(task)
│
├─ Step 1: Load Mandatory Items
│   ├─ SPEC.md (from disk)
│   ├─ SIMP.md (from disk)
│   ├─ index.md (from wiki)
│   └─ Selected skills (from .simp/skills/)
│
├─ Step 2: Strategic Navigation (Multi-pass)
│   Pass 1:
│   ├─ WikiNavigator.navigate(task, index)
│   ├─ LLM decides: Which semantic pages needed?
│   │   └─ "To add logging to auth, I need: patterns/logging, modules/auth, decisions/error_handling"
│   ├─ Load selected pages from wiki
│   └─ Check staleness: Hash matches? Include : Exclude + warn
│
│   Pass 2 (if needed):
│   ├─ Analyze: Do loaded pages reference other pages?
│   ├─ Load supplemental pages
│   └─ Repeat until no new references
│
├─ Step 3: Extract Targeted Code Ranges
│   For each loaded Wiki page:
│   ├─ Extract source references (file, lines, hash)
│   ├─ Read that range from actual file
│   └─ Add to context with label "CODE: src/auth.py (50-100)"
│
└─ Step 4: Assemble with Budget Enforcement
    ├─ ContextBudgeter(total_budget=100k)
    ├─ Add all mandatory items (usually ~15k tokens)
    ├─ Add semantic items until budget runs low (~35k)
    ├─ Add targeted code ranges to fill remainder (~50k)
    └─ If budget exceeded: drop optional items with warning

Result: Assembled context string ready for LLM
```

**Key**: Multi-pass navigation catches dependencies

### 4. Planning with Context Request

```
PlanGenerator.generate(task, context)
│
├─ Max 3 turns:
│
│   Turn 1:
│   ├─ Prompt: "Given context + task, generate plan OR request more context"
│   ├─ Response: ArchitectResponse (is_plan=true/false)
│   ├─ If is_plan=true: Return plan ✓
│   └─ If is_plan=false: Extract request.pages_to_load
│   │
│   ├─ Requested pages not in context?
│   ├─ Load them from wiki
│   └─ Add to context
│   │
│   Turn 2: Retry with expanded context
│   │
│   Turn 3: Final attempt (force plan with current context)
│
└─ Return: Structured Plan with steps
   ├─ step.id: Step number
   ├─ step.target: Which file
   ├─ step.action: What to do
   ├─ step.rationale: Why it matters
   └─ step.verification: How to verify

Plan structure enables verification and tracing
```

**Key**: Multi-turn dialogue ensures sufficient context

### 5. Execution with Verification

```
TakeAction.execute(plan, context)
│
For each plan step:
│
├─ Context Refresh (Production Readiness Fix #1)
│   └─ Call ScanScene.run(task) again
│       └─ Ensures: Latest code state loaded
│
├─ ReAct Loop (repeat until step.verified):
│   ├─ LLM Reasoning:
│   │   ├─ Analyze: current_context
│   │   ├─ Analyze: execution_history
│   │   ├─ Decide: Next action (tool call)
│   │   └─ Output: ToolCall(tool, args, thought, complete)
│   │
│   ├─ Tool Execution via ToolHarness:
│   │   ├─ read_file(path)
│   │   │   ├─ Check: Is path excluded? → Block
│   │   │   ├─ Read from disk
│   │   │   └─ Return content
│   │   │
│   │   ├─ write_file(path, content)
│   │   │   ├─ Check: Is path in scope? → Block
│   │   │   ├─ Write to disk
│   │   │   ├─ Update Wiki hashes (Production Readiness Fix #4)
│   │   │   └─ Return success
│   │   │
│   │   ├─ patch_file(path, old, new)
│   │   │   ├─ Whitespace-tolerant matching (Fix #2)
│   │   │   ├─ Apply patch
│   │   │   ├─ Verify file is valid
│   │   │   └─ Update Wiki hashes
│   │   │
│   │   └─ run_shell(command)
│   │       ├─ Unrestricted shell (Fix #3)
│   │       └─ Run in project root
│   │
│   ├─ Trace Logging:
│   │   └─ Record: thought, tool, args, result
│   │
│   └─ Continue loop until: tool_call.complete = true
│
└─ Move to next step

Result: Modified files + complete execution trace
```

**Key**: Every step reads current state, verifies before moving on

### 6. Learning Phase (GetBetter)

```
GetBetter.run(task, execution_trace)
│
├─ Analyze execution:
│   ├─ What did the LLM do?
│   ├─ What patterns did it use repeatedly?
│   ├─ What went wrong (retries)?
│   └─ What was learned about the codebase?
│
├─ Extract three types of knowledge:
│   ├─ new_patterns: "We use dependency injection for services"
│   ├─ new_risks: "Token validation must happen first to avoid side effects"
│   └─ new_invariants: "All endpoints must have error handling"
│
├─ Generate change log entry:
│   └─ Semantic summary of architectural impact
│
└─ Update Wiki:
    ├─ Append to changes.md
    ├─ Create new cognitive pages if needed
    └─ Update patterns.md
        └─ Next task can use learned patterns

Result: Wiki becomes smarter, ready for next task
```

**Key**: Learning is automatic, based on execution traces

---

## Data Structures

### ProjectMetadata

```python
class ProjectMetadata(BaseModel):
    name: str                          # Project name
    root: str                          # Root directory
    file_tree: List[str]               # All files (hierarchical if large)
    manifests: Dict[str, str]          # Manifest contents
    entry_point_samples: Dict[str, str] # Entry point snippets
```

### Plan

```python
class Plan(BaseModel):
    task_id: str                   # Unique task ID
    rationale: str                 # Overall architectural reasoning
    steps: List[PlanStep]          # Atomic execution steps
    scope_exclusions: List[str]    # Files NOT to modify
    risk_level: str                # "low", "medium", "high"

class PlanStep(BaseModel):
    id: int                        # Step sequence
    target: str                    # File to modify
    action: str                    # What to do
    rationale: str                 # Why it matters
    verification: str              # How to verify completion
```

### WikiPage

```python
class WikiPageMetadata(BaseModel):
    id: str                        # Page identifier
    type: str                      # "module", "symbol", "decision", "cognitive"
    last_updated: float            # Timestamp
    sources: List[SourceReference] # Hash-validated code references

class SourceReference(BaseModel):
    file_path: str                 # Path relative to project root
    start_line: Optional[int]      # Line number or None for whole file
    end_line: Optional[int]        # Line number or None for whole file
    hash: str                      # SHA-256 hash for integrity

class WikiPage(BaseModel):
    metadata: WikiPageMetadata
    content: str                   # Markdown content
```

### ContextItem

```python
class ContextItem(BaseModel):
    id: str                        # Page or code identifier
    content: str                   # Content to include
    priority: int                  # Tier: 0=mandatory, 1=semantic, 2+=targeted
```

---

## Error Recovery

### Planning Failures

**Scenario**: PlanGenerator can't generate plan after 3 turns

**Recovery**:
1. Log error with partial context
2. Ask user to clarify task
3. Retry with expanded SPEC.md or breaking into smaller tasks

### Execution Failures

**Scenario**: ToolHarness blocks a file write (scope violation)

**Recovery**:
1. Halt execution
2. Log which file was attempted
3. Suggest: "File not in plan scope. Mention it in task description?"

**Scenario**: LLM verification never completes (infinite loop)

**Recovery**:
1. After 30 ReAct turns per step, mark as "incomplete"
2. Log partial progress
3. Ask user: "Manual verification needed?"

### Wiki Staleness

**Scenario**: Wiki page is stale (hash mismatch)

**Recovery**:
1. Exclude stale page from context
2. Warn user: "[Scan] Wiki page X is stale"
3. Next task focused on that module will refresh it

---

## Performance Characteristics

### Token Usage (Per Task)

Typical task execution:

```
Context Assembly:    20-30k tokens (reading, navigation)
Planning:           10-15k tokens (generating plan)
Execution:          40-60k tokens (multi-turn reasoning + verification)
Learning:            5-10k tokens (analysis)
───────────────────
Total per task:     75-115k tokens
```

**Optimization**: Use cheaper LLM for planning (Groq), quality for execution (Anthropic)

### Time Complexity

- **Initialization**: O(n) where n = number of project files
  - Small project (<100 files): ~2 seconds
  - Medium project (<1000 files): ~5-10 seconds
  - Large project (>1000 files): hierarchical compression used

- **Task Execution**: O(s × r) where s = plan steps, r = ReAct rounds per step
  - Simple task (1 step, 2 rounds): ~30 seconds
  - Medium task (3 steps, 3-4 rounds each): ~90 seconds
  - Complex task (5+ steps, 5+ rounds each): ~200+ seconds

### Memory Usage

- **Loaded Wiki**: O(p × c) where p = pages, c = avg page content
  - Small project: ~50MB
  - Medium project: ~200MB
  - Large project: ~1GB (streaming recommended)

---

## Safety Guarantees

### Scope Enforcement

Every ToolHarness operation validates:

```python
def _check_scope(file_path: str):
    # 1. Normalize path (prevent ../../ tricks)
    full_path = (self.root / file_path).resolve()
    
    # 2. Check against allowed list
    for allowed in self.allowed_paths:
        if full_path == allowed or full_path.is_relative_to(allowed):
            return  # OK
    
    # 3. If not allowed: BLOCK
    raise PermissionError(f"Out of scope: {file_path}")
```

**Guarantee**: Cannot write outside plan scope

### Semantic Integrity

Every Wiki page reference is validated:

```python
def check_staleness(page: WikiPage) -> List[Tuple[SourceReference, str]]:
    stale = []
    for source in page.metadata.sources:
        actual_hash = calculate_range_hash(source.file_path)
        if actual_hash != source.hash:
            stale.append((source, actual_hash))
    return stale
```

**Guarantee**: Wiki pages are excluded if sources changed

### Context Budget Enforcement

Every context assembly respects budget:

```python
def assemble(mandatory, semantic, targeted) -> str:
    assembled = []
    current_tokens = 0
    
    # Add all mandatory (never drop)
    for item in mandatory:
        tokens = count_tokens(item.content)
        assembled.append(item.content)
        current_tokens += tokens
    
    # Add optional until budget
    for item in semantic + targeted:
        tokens = count_tokens(item.content)
        if current_tokens + tokens <= budget:
            assembled.append(item.content)
            current_tokens += tokens
        else:
            assembled.append(f"[DROPPED: {item.id}]")
    
    return "".join(assembled)
```

**Guarantee**: Never exceeds token budget

---

## Extension Points

### 1. Custom Roles

Create new system prompts in `src/simpcode/core/prompts/`:

```markdown
# my_custom_role.md
# IDENTITY
ROLE: My Custom Role
...

# my_custom_role_task.md
# PROMPT TEMPLATE
Given context: {current_context}
...
```

Register in `__init__.py`:
```python
registry.register("my_custom_role", "...")
```

### 2. Custom Tools

Extend ToolHarness:

```python
class CustomToolHarness(ToolHarness):
    def my_custom_tool(self, arg):
        # Implement custom operation
        # Must validate scope
        # Must log to trace
        pass
```

### 3. Custom LLM Providers

Implement `LLMProvider` base class:

```python
class CustomProvider(LLMProvider):
    def complete(self, prompt, system) -> str:
        # Implement API call
        pass
    
    def structured_output(self, prompt, schema, system):
        # Implement structured output
        pass
```

---

## Known Limitations & Future Work

### Current Limitations

1. **Python-centric**: Works best with Python projects
2. **Single-task workflow**: Queues multiple tasks (batch execution coming)
3. **Manual SPEC.md**: Requires user to write/maintain
4. **Context truncation**: Very large repos may exceed even compressed form
5. **No dry-run**: Can't preview changes before execution

### Roadmap

1. **Multi-language support**: Golang, Rust, JavaScript, TypeScript
2. **Batch task execution**: Queue and process multiple tasks
3. **Dry-run mode**: Preview changes before execution
4. **Web UI**: Visual dashboard for Wiki, execution history
5. **Custom backends**: Deploy with private LLM infrastructure
6. **Team collaboration**: Shared Wiki, role-based access
7. **Git integration**: Automatic commits with semantic messages
8. **Performance profiling**: Analyze slow tasks, optimize

---

## Summary

SimpCode's architecture achieves high-integrity agentic engineering through:

1. **Wiki-First**: Semantic knowledge guides all decisions
2. **Tiered Context**: Efficient use of limited token budgets
3. **Read-Before-Write**: Continuous state verification
4. **Safe Execution**: Strict scope and permission enforcement
5. **Continuous Learning**: System improves after each task

This design enables **safe, verifiable, improving software engineering at scale**.

---

**See Also**: 
- [Comprehensive User Guide](COMPREHENSIVE_GUIDE.md)
- [Troubleshooting Guide](TROUBLESHOOTING.md)
- [Example Workflows](EXAMPLES.md)
