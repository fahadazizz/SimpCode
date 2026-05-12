# SimpCode Troubleshooting & Solutions

Comprehensive guide to diagnosing and fixing common SimpCode issues.

---

## Quick Reference

| Symptom | Likely Cause | Solution |
|---------|------------|----------|
| `Error: Config file not found` | Not configured | `simp setup` |
| `Permission Denied: out of scope` | File not in plan | Include file in task description |
| `Wiki page is stale` | Code changed | Normal; page excluded (task focused on module will refresh) |
| `Context Budget Exceeded` | Project too large | Use narrow task scope or larger LLM model |
| `Planner failed to generate plan` | Insufficient context | Clarify task or expand SPEC.md |
| `Tool execution failed` | Script error | Check trace log, verify script syntax |
| `No changes were made` | Execution incomplete | Review execution trace |

---

## Installation & Setup

### Issue 1: "SimpCode: command not found"

**Symptom**:
```bash
$ simp init
zsh: command not found: simp
```

**Diagnosis**:
- SimpCode not installed, or
- Wrong Python environment, or
- Installation failed silently

**Solutions**:

**Option A: Install via pip**
```bash
pip install git+https://github.com/fahadazizz/simpcode.git
# Or if released: pip install simpcode
```

**Option C: Install locally (development)**
```bash
git clone https://github.com/fahadazizz/simpcode.git
cd simpcode
pip install -e .
```

**Verify**:
```bash
simp --version
which simp
```

### Issue 2: "Error: Config file not found"

**Symptom**:
```bash
$ simp init
Error: LLM configuration not found
Run 'simp setup' first
```

**Diagnosis**:
- Global config at `~/.simp/config.json` doesn't exist
- First-time setup not completed

**Solution**:
```bash
simp setup
# Choose provider, model, and API key
# Config saved to ~/.simp/config.json
```

**Verify**:
```bash
cat ~/.simp/config.json
```

### Issue 3: "Invalid API Key"

**Symptom**:
```bash
$ simp init
Error: Authentication failed with provider 'groq'
Invalid API key
```

**Diagnosis**:
- API key is incorrect or expired
- Wrong provider selected
- Network connectivity issue

**Solutions**:

**A: Verify API key**
```bash
# Check what's saved
cat ~/.simp/config.json | grep api_key

# Get fresh API key from provider
# Groq: https://console.groq.com/keys
# Anthropic: https://console.anthropic.com/
# OpenAI: https://platform.openai.com/account/api-keys

# Reconfigure
simp setup
```

**B: Test LLM directly**
```bash
# Create test script
python -c "
from simpcode.core.llm import LLMClient
llm = LLMClient()
print('LLM initialized:', llm.provider_name)
print('Model:', llm.model_id)
"
# If this fails: LLM configuration problem
```

**C: Check network**
```bash
# Test connectivity
curl -I https://api.groq.com
curl -I https://api.anthropic.com

# If timeouts: network/firewall issue
```

---

## Initialization Issues

### Issue 4: "Project analysis failed"

**Symptom**:
```bash
$ simp init
Error: Failed to analyze project
[Errno 13] Permission denied
```

**Diagnosis**:
- SimpCode lacks read permissions on project directory
- Project contains protected files
- Filesystem issue

**Solutions**:

**A: Check permissions**
```bash
# Verify SimpCode can read project
ls -la /path/to/project
# Should show your user has read access

# Fix if needed
chmod -R u+r /path/to/project
```

**B: Check excluded files**
```bash
# View .gitignore
cat /path/to/project/.gitignore

# Create .simpignore to exclude additional files
echo "secrets/" >> /path/to/project/.simpignore
echo ".venv/" >> /path/to/project/.simpignore
```

**C: Debug with smaller scope**
```bash
# Try on subdirectory first
cd /path/to/project/src
simp init
```

### Issue 5: "SIMP.md or SPEC.md generation failed"

**Symptom**:
```bash
$ simp init
...
Synthesizing intelligence...
Error: LLM synthesis failed
```

**Diagnosis**:
- LLM returned invalid response
- Network timeout
- Prompt too complex

**Solutions**:

**A: Check LLM availability**
```bash
# Quick LLM test
python -c "
from simpcode.core.llm import LLMClient
llm = LLMClient()
response = llm.complete('Say hello in one word.')
print(response)
"
```

**B: Try different LLM**
```bash
simp setup
# Select different provider (e.g., Anthropic instead of Groq)
# Re-run init
simp init
```

**C: Reduce project complexity**
- Temporarily remove very large files
- Extract a representative subset
- Then initialize

### Issue 6: "Wiki bootstrap failed"

**Symptom**:
```bash
$ simp init
...
Compiling Initial Wiki...
Error: Bootstrap failed
```

**Diagnosis**:
- Same as synthesis failure (LLM issue)
- Wiki directory permissions issue

**Solutions**:

**A: Check wiki directory**
```bash
# Verify .simp directory can be created
ls -la /path/to/project/.simp/
# If missing: mkdir -p .simp/wiki

# Verify permissions
chmod -R u+w /path/to/project/.simp/
```

**B: Manual wiki bootstrap**
```python
# Python script
from simpcode.wiki.bootstrap import WikiBootstrap
from simpcode.core.llm import LLMClient
from simpcode.core.analyzer import ProjectAnalyzer
from pathlib import Path

root = Path("/path/to/project")
llm = LLMClient()
analyzer = ProjectAnalyzer(root)
metadata = analyzer.collect_metadata()

bootstrap = WikiBootstrap(llm, root)
bootstrap.run(metadata)
print("Wiki bootstrapped successfully")
```

---

## Runtime Issues

### Issue 7: "Permission Denied: out of scope"

**Symptom**:
```bash
simp> Add new endpoint to the API

...
[Error] Plan Violation: 'src/new_endpoint.py' is not in the approved scope
```

**Diagnosis**:
- File mentioned in error wasn't in plan scope
- LLM tried to create/modify file outside plan

**Solutions**:

**A: Re-describe task to include file**
```bash
simp> Add new_endpoint.py to handle /users endpoint
     with handler function and tests
```

Now plan includes the new file in scope.

**B: Review generated plan**
```bash
# (Future feature: dry-run mode)
# For now: Check the error message
# "... not in approved scope"
# → This file should be mentioned in task description
```

### Issue 8: "Wiki page is stale"

**Symptom**:
```bash
simp> Refactor auth module

[Scan] Warning: Wiki page modules/auth is stale. Excluded from context.
```

**Diagnosis**:
- `modules/auth.md` references source code
- Source code hash changed (file was modified)
- Wiki is out of sync with codebase

**Solutions**:

**This is expected behavior** (safety mechanism). Wiki pages are excluded if sources changed.

**Recovery**:

**A: Run a focused task on that module**
```bash
simp> Update the auth module documentation in the wiki
     based on current auth.py implementation
```

This task will refresh the wiki page.

**B: Manual wiki refresh**
```bash
# Delete stale page
rm .simp/wiki/modules/auth.md

# Next task will regenerate it
simp> Improve auth module
```

**Prevention**:

Keep wiki fresh by working on modules regularly. Each task updates related wiki pages.

### Issue 9: "Context Budget Exceeded"

**Symptom**:
```bash
[Warning] Context Budget Exceeded: Dropping CodeRange for services/database.py
```

**Diagnosis**:
- Project is too large for context window
- Too many wiki pages loaded
- Code ranges accumulated

**Solutions**:

**A: Narrow task scope**
```bash
# Instead of:
simp> Improve the entire database layer

# Do:
simp> Add connection pooling to the database layer
     (focus only on connection management)

simp> Add query caching to the database layer
     (separate focused task)
```

Multiple focused tasks = more efficient than one huge task.

**B: Use larger LLM model**
```bash
# Current might be:
# Groq: 8k context
# GPT-4: 128k context
# Claude 3 Opus: 200k context

simp setup
# Select model with larger context window
```

**C: Simplify SPEC.md or SIMP.md**
```bash
# Make these documents more concise
# Remove verbose explanations
# Focus on essential info

# Reduce from 5000 words → 500 words
# This frees up budget for code context
```

### Issue 10: "Planner failed to generate plan"

**Symptom**:
```bash
Planner failed to generate a valid plan.
RuntimeError: Expected response schema but got...
```

**Diagnosis**:
- LLM didn't return structured response in expected format
- Task description too ambiguous
- Context was insufficient or truncated

**Solutions**:

**A: Clarify task description**
```bash
# Instead of:
simp> Make the system better

# Do:
simp> Add type hints to all functions in src/auth.py
     using Python typing module. Target: mypy --strict passes.
```

Clear, specific task = easier planning.

**B: Expand SPEC.md with context**
```markdown
# SPEC.md

## Current Challenge
We're adding type safety to the auth module.

## Architecture
- Services: FastAPI + SQLAlchemy
- Auth uses JWT tokens
- All user IDs are UUIDs

## Success Criteria
- mypy --strict passes
- No runtime type errors
```

**C: Break into smaller tasks**
```bash
# Instead of one huge task:
simp> Refactor all 50 functions in auth module

# Do multiple focused tasks:
simp> Add type hints to authentication functions
simp> Add type hints to token validation functions
simp> Add type hints to user lookup functions
# (3 smaller, focused tasks)
```

### Issue 11: "Tool execution failed"

**Symptom**:
```bash
[Action]: run_shell(pytest tests/test_auth.py)
Error: Command failed with exit code 1
```

**Diagnosis**:
- Script/command has an error
- Dependencies not installed
- File path incorrect

**Solutions**:

**A: Review execution trace**
```bash
# Find trace log
ls ~/.simp/sessions/
cat ~/.simp/sessions/sess_XXXX/trace.log

# Look for full command and output
# See exactly what failed
```

**B: Verify command manually**
```bash
# Test command in terminal
cd /path/to/project
pytest tests/test_auth.py

# If fails: Fix the actual issue
# Then retry SimpCode task
```

**C: Install missing dependencies**
```bash
pip install -r requirements.txt
poetry install

# Retry task
```

---

## Execution Issues

### Issue 12: "Execution doesn't complete"

**Symptom**:
```bash
simp> Add logging to auth module
...
>>> EXECUTION STEP 1: ...
  [Thought]: ...
  [Action]: ...
  ... (continues indefinitely)
```

**Diagnosis**:
- ReAct loop stuck (step verification never completes)
- LLM keeps retrying, never satisfies verification
- Step goal is unclear

**Solutions**:

**A: Interrupt and check status**
```bash
# Ctrl+C to stop
# Check last execution:
cat ~/.simp/sessions/sess_XXXX/trace.log

# What was the step trying to verify?
```

**B: Simplify step goal**
```bash
# Task might be too ambitious for one step
# Break it down:

simp> Add logging to auth.py authenticate() function
     (small, focused)
```

**C: Add verification criteria to SPEC.md**
```markdown
# SPEC.md

## Logging Requirements
- Use Python logging module
- Log level: DEBUG for entry, INFO for success
- Include user_id in logs for tracing
- Tests must pass: pytest tests/test_auth.py
```

### Issue 13: "No changes were made"

**Symptom**:
```bash
simp> Add comprehensive error handling to auth module

[Learning]
✓ Execution complete.
(But no files were modified)
```

**Diagnosis**:
- Task description was understood, but plan included no concrete steps
- All steps marked "complete" without modification
- Verification happened but changes not applied

**Solutions**:

**A: Check execution trace**
```bash
cat ~/.simp/sessions/sess_XXXX/trace.log

# Look for what happened:
# - Did planner generate steps?
# - Did steps execute?
# - What was verification?
```

**B: Be more specific in task**
```bash
# Instead of:
simp> Add error handling to auth module

# Do:
simp> Add try/except blocks to auth.py authenticate() function
     catching ValueError for invalid tokens
     and logging errors
```

**C: Verify with next task**
```bash
# If changes aren't visible:
simp> Show me the current state of src/auth.py
     and describe what error handling is in place
```

---

## Context & Wiki Issues

### Issue 14: "Wrong code shown in context"

**Symptom**:
```bash
simp> Fix the auth bug

[Context]
--- CODE: src/auth.py (50-100) ---
def authenticate():  # ← This is OLD version
    ...
```

**Diagnosis**:
- Wiki page hash didn't match (page excluded)
- Code shown is from memory, not current state
- Context was stale

**Solutions**:

**A: Force context refresh**
```bash
# The issue is: Wiki page was stale
# Make it fresh by running focused task:

simp> Update wiki documentation for auth module
     based on current implementation
```

**B: Check file directly**
```bash
# Verify actual content
cat src/auth.py | head -100

# Should match what you expect
```

**C: Clear wiki and reinit**
```bash
# Nuclear option (if wiki is completely wrong):
rm -rf .simp/wiki/

# Next task will bootstrap fresh wiki
simp> Initialize wiki for auth module
```

### Issue 15: "Wiki pages are empty"

**Symptom**:
```bash
$ cat .simp/wiki/modules/auth.md
---
id: modules/auth
type: module
last_updated: 1234567890
---

(No content)
```

**Diagnosis**:
- Bootstrap failed partially
- Wiki page corrupted
- Content not saved properly

**Solutions**:

**A: Regenerate wiki**
```bash
# Delete problematic page
rm .simp/wiki/modules/auth.md

# Run task focused on that module:
simp> Analyze and document the auth module
```

**B: Full wiki reset**
```bash
# If many pages are broken:
rm -rf .simp/wiki/

# Bootstrap wiki again:
simp init
```

---

## LLM & API Issues

### Issue 16: "API Rate Limited"

**Symptom**:
```bash
Error: Rate limit exceeded
Try again in 60 seconds
```

**Diagnosis**:
- LLM provider rate-limited your API key
- Too many requests in short time
- Free tier quota exhausted

**Solutions**:

**A: Wait and retry**
```bash
# Wait for rate limit window
sleep 60

# Retry task
simp> Your task here
```

**B: Use different LLM provider**
```bash
simp setup
# Select different provider with higher rate limits

# Check provider limits:
# - Groq: Generous free tier
# - Anthropic: 5M tokens/month free
# - OpenAI: Pay-as-you-go
```

**C: Upgrade to paid plan**
- Contact your LLM provider
- Increase rate limits
- Or switch to provider with higher limits

### Issue 17: "API Response Timeout"

**Symptom**:
```bash
Error: Request timeout (30s)
Connection timed out
```

**Diagnosis**:
- Network connectivity issue
- LLM provider slow/down
- Firewall blocking

**Solutions**:

**A: Check network**
```bash
# Test connectivity
ping api.groq.com
curl -I https://api.groq.com/

# If fails: Network issue
```

**B: Check LLM provider status**
```bash
# Visit provider status page:
# - Groq: https://status.groq.com
# - Anthropic: https://status.anthropic.com
# - OpenAI: https://status.openai.com

# If down: Wait for recovery
```

**C: Check firewall/VPN**
```bash
# If using VPN:
# - Disable VPN and retry
# - Or whitelist LLM provider IPs

# If using corporate firewall:
# - Ask IT to allow LLM provider IPs
```

**D: Use offline LLM (OLLama)**
```bash
# If internet connectivity problematic:
simp setup
# Select OLLama provider
# Runs locally, no network needed
```

### Issue 18: "Invalid API key format"

**Symptom**:
```bash
Error: Invalid API key format
Expected format: sk-...
```

**Diagnosis**:
- API key format incorrect for provider
- Key corrupted or truncated
- Pasted with extra whitespace

**Solutions**:

**A: Check API key format**
```bash
# Expected formats:
# Groq:      gsk_... (starts with gsk_)
# Anthropic: sk-ant-... (starts with sk-ant-)
# OpenAI:    sk-... (starts with sk-)

# Verify your key:
echo $ANTHROPIC_API_KEY
# Should start with correct prefix
```

**B: Remove whitespace**
```bash
# When pasting key, ensure no whitespace
# Edit ~/.simp/config.json:
# "api_key": "sk-ant-...",  # NO SPACES

# Or reconfigure:
simp setup
# Paste carefully, no extra spaces
```

**C: Generate new API key**
- Go to provider console
- Generate new key (might be corrupted)
- Reconfigure SimpCode

---

## Performance Issues

### Issue 19: "Execution is very slow"

**Symptom**:
```bash
simp> Simple task
...
>>> EXECUTION STEP 1: ...
[5 minutes later, still going...]
```

**Diagnosis**:
- Large context window being processed
- LLM is slow model
- Many ReAct loop iterations
- Tool commands are slow

**Solutions**:

**A: Use faster LLM**
```bash
simp setup
# Switch to: Groq (fastest), or faster model variant
# Re-run task

# Speed ranking:
# 1. Groq (fastest)
# 2. OpenRouter (fast)
# 3. OpenAI GPT-4 (slow)
# 4. Claude (medium)
```

**B: Reduce context size**
- Make SPEC.md more concise
- Use narrower task scope
- Filter out unnecessary wiki pages

**C: Check tool performance**
```bash
# If task includes slow tools (e.g., pytest):
# These run sequentially, no way to speed up
# Accept as normal overhead
```

### Issue 20: "Wiki operations are slow"

**Symptom**:
```bash
[Scan] Loading wiki pages...
[1 minute+ of loading]
```

**Diagnosis**:
- Very large wiki (hundreds of pages)
- Disk I/O bottleneck
- SHA hash calculation expensive

**Solutions**:

**A: Prune old wiki pages**
```bash
# Remove pages not actively used
ls -la .simp/wiki/
# Remove old decision pages, old cognitive pages
rm .simp/wiki/decisions/old_decision.md
```

**B: Archive wiki**
```bash
# Move old pages to archive
mkdir .simp/wiki/archive
mv .simp/wiki/decisions/2024_old_* .simp/wiki/archive/

# SimpCode only scans active wiki/
```

---

## File & Permission Issues

### Issue 21: "Permission denied when writing file"

**Symptom**:
```bash
[Error] PermissionError: Permission denied: src/auth.py
```

**Diagnosis**:
- File or directory not writable by current user
- File is read-only
- Directory permissions issue

**Solutions**:

**A: Fix file permissions**
```bash
# Make file writable
chmod u+w src/auth.py

# Or entire directory
chmod -R u+w src/
```

**B: Check ownership**
```bash
ls -l src/auth.py
# Should be owned by your user

# If not:
chown $USER:$GROUP src/auth.py
```

**C: Disable read-only in git**
```bash
# If file is read-only in git:
git config --local core.fileMode false
chmod u+w src/auth.py
```

### Issue 22: "File conflicts with git"

**Symptom**:
```bash
[Error] Cannot write src/auth.py
Git merge conflict detected
```

**Diagnosis**:
- File has uncommitted changes
- Git merge in progress
- Git rebase in progress

**Solutions**:

**A: Commit pending changes**
```bash
git status  # See uncommitted changes
git add -A
git commit -m "Current state"

# Now retry SimpCode task
```

**B: Resolve merge conflict**
```bash
# If merge/rebase in progress:
git status

# Either complete:
git merge --continue
# Or abort:
git merge --abort

# Then retry
```

**C: Create new branch**
```bash
# If you want to keep current branch clean:
git checkout -b simp-improvements

# Run SimpCode task
# Then merge or discard
```

---

## Debugging Techniques

### Technique 1: Review Execution Trace

**What it shows**:
- Full transcript of planning phase
- All LLM reasoning steps
- All tool calls and results
- Verification steps

**How to access**:
```bash
# Find most recent session
ls -lt ~/.simp/sessions/ | head -1

# View trace
cat ~/.simp/sessions/sess_TIMESTAMP/trace.log

# Search for specific part:
grep "EXECUTION STEP 2" trace.log
grep "Error:" trace.log
```

**Useful for**:
- Understanding why a step failed
- Verifying context was correct
- Debugging LLM reasoning

### Technique 2: Inspect Wiki State

**What it shows**:
- What SimpCode knows about your project
- Which pages are fresh vs stale
- Source references and hashes

**How**:
```bash
# List all pages
ls -R .simp/wiki/

# Check specific page
cat .simp/wiki/modules/auth.md

# Check if page is stale
grep "hash:" .simp/wiki/modules/auth.md
# Compare hash with actual file:
sha256sum src/auth.py | head -c 64
```

### Technique 3: Test LLM Configuration

**What it shows**:
- Whether LLM is accessible
- Whether API key is valid
- Which model is active

**How**:
```python
# Create test_llm.py
from simpcode.core.llm import LLMClient

llm = LLMClient()
print(f"Provider: {llm.provider_name}")
print(f"Model: {llm.model_id}")

# Test completion
response = llm.complete("Say 'Hello' in one word")
print(f"Response: {response}")

# Test structured output
from pydantic import BaseModel
class TestResponse(BaseModel):
    greeting: str

result = llm.structured_output(
    "Greet me with a single word in JSON format",
    TestResponse,
    "You are helpful"
)
print(f"Structured: {result}")
```

**Run**:
```bash
python test_llm.py
```

### Technique 4: Manually Trace Context Assembly

**What it shows**:
- How context is assembled for a task
- Which Wiki pages are loaded
- What context budget is used

**How**:
```python
# Create test_context.py
from simpcode.core.modes import ScanScene
from simpcode.core.llm import LLMClient
from pathlib import Path

root = Path("/path/to/project")
llm = LLMClient()
scanner = ScanScene(root, llm)

task = "Your task description"
print(f"Task: {task}")
print("\n--- Assembling Context ---")

context = scanner.run(task)

print(f"\nContext length: {len(context)} chars")
print(f"First 1000 chars:")
print(context[:1000])
```

**Run**:
```bash
python test_context.py
```

---

## Getting Help

### When to Report Issues

Report to GitHub if:
- Bug affects multiple users
- Workaround doesn't exist
- Consistent reproduction steps

**DO include**:
- Python version: `python --version`
- SimpCode version: `simp --version`
- LLM provider and model
- Reproduction steps
- Error message and stack trace
- Trace log (if possible): `cat ~/.simp/sessions/*/trace.log`

### When to Ask for Help

Ask on GitHub Discussions if:
- Unsure how to use feature
- Can't figure out configuration
- Need architecture advice
- Design question

**DO include**:
- What you're trying to accomplish
- What you've already tried
- Context (project type, scale, etc.)

### Support Channels

- **GitHub Issues**: Bug reports
- **GitHub Discussions**: Questions and ideas
- **Documentation**: This guide and others in /docs/

---

## Summary

Most SimpCode issues fall into categories:

1. **Installation**: Missing dependencies, wrong environment
2. **Configuration**: LLM setup, API keys, credentials
3. **Initialization**: Project analysis, wiki bootstrap
4. **Execution**: Out-of-scope files, stale wiki, context budget
5. **Performance**: Slow LLM or large projects
6. **Permissions**: File/directory access issues

**First debugging step**: Check the execution trace
```bash
cat ~/.simp/sessions/*/trace.log
```

Most issues have clear solutions once you understand what happened.

---

**See Also**:
- [Comprehensive Guide](COMPREHENSIVE_GUIDE.md)
- [Architecture Deep Dive](ARCHITECTURE_DEEP_DIVE.md)
- [Examples & Workflows](EXAMPLES.md)
