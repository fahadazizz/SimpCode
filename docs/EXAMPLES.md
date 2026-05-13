# SimpCode Examples & Real-World Workflows

Practical examples showing how to use SimpCode for common development tasks.

---

## Example 1: Onboarding a New Project

**Scenario**: You have an existing Python project. You want SimpCode to understand it and start improving it.

**Project**: A FastAPI REST API with authentication

```
my_api/
├── src/
│   ├── main.py
│   ├── auth.py
│   ├── api.py
│   ├── models.py
│   └── utils.py
├── tests/
│   ├── test_auth.py
│   └── test_api.py
├── pyproject.toml
└── README.md
```

### Step 1: Configure LLM (First Time Only)

```bash
$ simp setup
Choose LLM Provider: groq
Enter Model ID: llama-3.3-70b-versatile
Enter API Key: gsk_...

✓ Configuration saved to ~/.simp/config.json
```

### Step 2: Initialize SimpCode

```bash
$ cd my_api
$ simp init

Initializing SimpCode at /Users/dev/my_api
Collecting codebase metadata...
Synthesizing Project Intelligence...
Compiling Initial Wiki...

✓ Mission Establishment Complete.
 - SIMP.md (Project Intelligence)
 - SPEC.md (Project Requirements)
 - .simp/wiki/ (Knowledge Base)
```

### Step 3: Review Generated Documents

**SIMP.md** (auto-generated project manifest):
```markdown
# SIMP: My API

## Overview
FastAPI-based REST API with JWT authentication.

## Architecture
- Framework: FastAPI
- Database: SQLite (simple)
- Authentication: JWT tokens
- Language: Python 3.10+

## Core Modules
- auth.py: User authentication (JWT tokens)
- api.py: REST endpoints (users, posts)
- models.py: Pydantic schemas
- utils.py: Helper functions (logging, validation)

## Dependencies
- fastapi >=0.95
- sqlalchemy >=2.0
- pydantic >=2.0
```

**SPEC.md** (auto-generated requirements template):
```markdown
# SPEC: My API

## Overview
A secure REST API for managing users and posts.

## Requirements
- Users can register and login
- JWT token-based authentication
- Endpoints for CRUD operations
- Rate limiting (future)
- Comprehensive error handling

## Constraints
- Single SQLite database (no migration service)
- No external dependencies except LLM API
- Single-server deployment

## Acceptance Criteria
- All tests pass
- API docs updated
- Type hints in all functions
```

### Step 4: Customize SPEC.md

Edit `SPEC.md` to match your actual requirements:

```markdown
# SPEC: My API

## Additional Constraints
- Must support concurrent requests (async)
- All errors logged with correlation IDs
- Response time < 200ms

## Performance Goals
- Support 1000 concurrent users
- 99.9% uptime
- Database queries < 50ms
```

### Step 5: Start Working

Now you can describe tasks, and SimpCode understands your project:

```bash
$ # (TUI shell opens)
simp> Add comprehensive type hints to the auth module
     to improve IDE support and catch bugs early

[Context Assembly]
Loaded: SPEC.md, SIMP.md, wiki/modules/auth, wiki/patterns
Context: ~85k tokens

[Planning]
Step 1: Add type hints to authenticate() function
Step 2: Add type hints to token validation functions
Step 3: Add type hints to user lookup functions
Step 4: Run mypy --strict to verify

[Execution]
>>> EXECUTION STEP 1: Add type hints to authenticate()
  [Thought]: Function takes username and password (str), returns JWT token
  [Action]: read_file(src/auth.py)
  ...✓ Step 1 complete

...

[Learning]
Updated Wiki: patterns.md with type hint patterns
Updated Wiki: modules/auth.md with current implementation
```

Result: Project now understood, typed, documented, learned.

---

## Example 2: Feature Development

**Scenario**: Add a new feature with high confidence that SimpCode understands current architecture.

**Task**: Add rate limiting to API endpoints

### Description with Context

```bash
simp> Add rate limiting to API endpoints:

- Create RateLimiter class in utils.py
- Track requests per IP address
- Limit: 100 requests/minute per IP
- Return 429 Too Many Requests when exceeded
- Add rate limit headers to all responses
- Update tests to verify rate limiting works
- Update API documentation

Constraints:
- Don't require external database
- Use in-memory storage (Redis-compatible interface)
- Graceful degradation if limits not available
```

### What SimpCode Does

**Phase 1: Context Assembly**
- Loads SPEC: "Rate limiting is mentioned in future requirements"
- Loads SIMP: "Current architecture and dependencies"
- Navigates Wiki: "How is error handling done? How are utilities structured?"
- Loads code: Current utils.py, api.py implementation

**Phase 2: Planning**
```
[Plan Generated]

Step 1: Create RateLimiter class in utils.py
  Target: src/utils.py
  Action: Add RateLimiter class with in-memory IP tracking
  Verification: RateLimiter(limit=100, window=60) instantiates

Step 2: Add rate_limit_check() function
  Target: src/utils.py
  Action: Check if IP exceeded rate limit
  Verification: Function returns bool correctly

Step 3: Add middleware to FastAPI
  Target: src/main.py
  Action: Wrap endpoints with rate limit middleware
  Verification: Middleware applies rate limit headers

Step 4: Add error response
  Target: src/api.py
  Action: Return 429 response when limit exceeded
  Verification: HTTP 429 response generated

Step 5: Add tests
  Target: tests/test_api.py
  Action: Test rate limiting with multiple requests
  Verification: pytest passes

Step 6: Update docs
  Target: README.md
  Action: Document rate limiting behavior
  Verification: Documentation is clear
```

**Phase 3: Execution**
- Execute each step with verification
- All tests pass
- Middleware correctly applied

**Phase 4: Learning**
- Extract pattern: "Rate limiting via IP tracking"
- Extract invariant: "All error responses must include rate limit headers"
- Update Wiki with new patterns

### Result

```bash
✓ Rate limiting implemented
✓ Tests passing (test_api.py: 8/8)
✓ Documentation updated
✓ Wiki evolved with new patterns
```

---

## Example 3: Debugging and Fixing

**Scenario**: Tests are failing after recent changes. SimpCode debugs and fixes.

**Initial Problem**:
```bash
$ pytest tests/test_auth.py
FAILED tests/test_auth.py::test_token_validation - AssertionError

tests/test_auth.py:42:
  assert validate_token(expired_token) == False
  ↳ AssertionError: Expected False, got True
```

### Task Description

```bash
simp> The token validation test is failing.
     
Recent changes modified how JWT tokens are validated.
The test expects expired tokens to return False,
but the function is returning True.

Fix the validation logic to correctly reject expired tokens.

Constraints:
- Don't change test expectations (they're correct)
- Must handle both malformed and expired tokens
- Must log validation failures for debugging
```

### What SimpCode Does

**Phase 1: Context Assembly**
- Loads failing test: test_auth.py
- Loads current implementation: auth.py validate_token()
- Loads SPEC: "What should JWT validation do?"
- Loads Wiki: "Previous JWT implementation patterns"
- Checks git diff: What changed recently?

**Phase 2: Planning**
```
[Analysis]
- Test expects expired tokens to fail
- Current implementation returns True (incorrectly)
- Root cause: Missing expiration check

[Plan]
Step 1: Read validate_token() function
  Verify: Check current implementation

Step 2: Fix validation logic
  Add: expiration time check
  Return: False if expired

Step 3: Add logging
  Log: Which validation checks fail

Step 4: Run tests
  Verify: test_auth.py passes

Step 5: Run full test suite
  Verify: No regressions
```

**Phase 3: Execution**
```
>>> EXECUTION STEP 1: Read validate_token()
  [Result]: Current implementation missing expiration check
  
>>> EXECUTION STEP 2: Fix validation logic
  [Change]: Add timedelta check for token expiration
  [Code]: if datetime.utcnow() > token_expiry: return False
  
>>> EXECUTION STEP 3: Add logging
  [Added]: Log when token expired
  
>>> EXECUTION STEP 4: Run tests
  [Result]: test_auth.py passes (5/5)
  
>>> EXECUTION STEP 5: Run full suite
  [Result]: All tests pass (13/13)
```

**Phase 4: Learning**
- Extract invariant: "Token validation must check both signature AND expiration"
- Extract risk: "Missing expiration check can allow token replay attacks"
- Update Wiki with validation invariant

### Result

```bash
✓ Tests fixed (test_auth.py: 5/5)
✓ Full test suite passing (13/13)
✓ Logging added for debugging
✓ Wiki updated with validation invariant
```

---

## Example 4: Refactoring for Type Safety

**Scenario**: Incrementally improve type hints across the codebase.

### Task 1: Core Data Models

```bash
simp> Add TypedDict type hints to all Pydantic models
     in models.py to improve type safety.
     
Goals:
- Replace Dict[str, Any] with specific TypedDicts
- Enable IDE autocomplete for model fields
- Catch type errors during linting

Verification: mypy --strict passes
```

**Result**: Models typed, IDE support improved.

### Task 2: Utility Functions

```bash
simp> Add type hints to all functions in utils.py

Goals:
- Add parameter type hints
- Add return type hints
- Use appropriate types (not just Any)

Verification: mypy --strict passes for utils.py
```

**Result**: Utilities typed, consistency improved.

### Task 3: Route Handlers

```bash
simp> Add type hints to all FastAPI route handlers in api.py

Goals:
- Type all route parameters
- Type all return values
- Use Pydantic models for request/response bodies

Verification: 
- mypy --strict passes for api.py
- API docs still work (OpenAPI generation correct)
```

**Result**: Routes typed, API contracts clear.

### Cumulative Effect

Each task:
- ✓ Improves specific module
- ✓ Teaches SimpCode type safety patterns
- ✓ Updates Wiki with typing patterns

After 3 tasks:
- ✓ Entire codebase typed
- ✓ SimpCode is expert in project's typing patterns
- ✓ Next task automatically uses same patterns

---

## Example 5: Large Refactoring

**Scenario**: Restructure authentication from function-based to class-based.

### Background

Current architecture:
```
auth.py:
  - authenticate(user, pwd) → token
  - validate_token(token) → bool
  - refresh_token(token) → new_token
```

Goal: Class-based, encapsulated, testable:
```
auth.py:
  - class JWTAuthenticator:
      __init__(secret_key)
      authenticate() → token
      validate() → bool
      refresh() → new_token
```

### Multi-Part Task

**Part 1: Analysis**
```bash
simp> Analyze the current authentication architecture.
     
Describe:
- Current auth flow
- Current data structures
- Current error handling
- What invariants must be preserved
- What will change

Goal: Understand current design before refactoring
```

SimpCode documents current architecture → Wiki updated.

**Part 2: Design the New Architecture**
```bash
simp> Design a class-based authentication system that:
     - Encapsulates JWT logic in JWTAuthenticator class
     - Maintains backward compatibility (same interface)
     - Improves testability
     - Improves type safety

Constraints:
- All current tests must pass unchanged
- API endpoint interface must not change
- Performance must not degrade
```

SimpCode generates design proposal → You review and approve.

**Part 3: Implement New Class**
```bash
simp> Implement JWTAuthenticator class in auth.py
     
Based on:
- Current authentication logic
- New class design
- Type hints

Verification:
- Class instantiates correctly
- Methods have correct signatures
- All unit tests pass
```

SimpCode implements new class.

**Part 4: Migrate Endpoints**
```bash
simp> Update api.py route handlers to use JWTAuthenticator

Current: token = authenticate(username, password)
New: token = authenticator.authenticate(username, password)

Verification:
- API endpoints still work
- Tests pass
- Type hints are correct
```

SimpCode updates endpoints.

**Part 5: Deprecate Old Functions**
```bash
simp> Remove old authenticate, validate_token, refresh_token
     functions from auth.py (now replaced by class methods)

Verification:
- No code references old functions
- All tests pass
- Full test suite passes
```

SimpCode cleans up.

**Part 6: Document Changes**
```bash
simp> Update README.md and code comments to document
     the new JWTAuthenticator class and how to use it

Include:
- Usage examples
- Method documentation
- Breaking changes (none, since interface unchanged)
```

SimpCode documents.

### Result

```
✓ Refactoring complete (6 focused tasks)
✓ All tests pass (15/15)
✓ Code is more maintainable
✓ Wiki evolved with new patterns
✓ No downtime during refactoring
✓ Each step was reversible
```

**Key insight**: Large refactoring broken into focused, verifiable steps.

---

## Example 6: Performance Optimization

**Scenario**: Profile slow endpoints and optimize.

### Task 1: Profile Current Performance

```bash
simp> Add performance profiling to the API.
     
Setup:
- Import cProfile
- Wrap slow endpoints with profiler
- Generate performance reports

Goal: Identify bottlenecks
```

**Result**: Profile data collected.

### Task 2: Optimize Database Queries

```bash
simp> Optimize database queries based on profiling results.

Identified bottleneck: User lookup queries in /api/users

Optimization:
- Add database index on username column
- Cache frequently accessed users (LRU cache)
- Batch queries where possible

Verification:
- Query execution < 10ms
- Tests still pass
- No data correctness issues
```

**Result**: Queries 5x faster.

### Task 3: Add Caching Layer

```bash
simp> Add in-memory caching for frequently accessed endpoints.
     
Cache strategy:
- Cache GET endpoints for 5 minutes
- Invalidate on POST/PUT/DELETE
- Use functools.lru_cache decorator

Endpoints to cache:
- GET /api/users (all users)
- GET /api/users/{id} (specific user)

Verification:
- Response time < 50ms (cached)
- Cache invalidates correctly
- Tests pass
```

**Result**: 10x faster response for cached endpoints.

### Task 4: Async Improvements

```bash
simp> Convert blocking database operations to async.
     
Current: SQLite with blocking queries
Target: Async SQLite queries

Changes:
- Use aiosqlite for async database access
- Convert functions to async/await
- Update tests

Verification:
- API handles concurrent requests
- Performance improves for concurrent load
- Tests pass
```

**Result**: Better concurrent performance.

### Cumulative Result

```
✓ Profiling added (debugging capability)
✓ Database queries optimized
✓ Caching added
✓ Async operations implemented
✓ Performance: 50ms → 5ms average response
✓ Concurrent capacity: 100 → 1000 users
```

---

## Example 7: Documentation Generation

**Scenario**: Auto-generate comprehensive documentation.

### Task 1: API Documentation

```bash
simp> Generate API documentation from code.
     
From:
- Route definitions in api.py
- Request/response Pydantic models
- Docstrings

Generate:
- OpenAPI schema
- API endpoints guide
- Example curl commands

Verification:
- OpenAPI schema is valid
- /docs endpoint works
```

**Result**: Interactive API docs ready.

### Task 2: Installation Guide

```bash
simp> Generate installation guide.
     
Include:
- System requirements (Python 3.10+)
- Installation steps (pip, poetry)
- Configuration (setup LLM)
- Quick start (init project, first task)
- Troubleshooting (common issues)

Verification:
- Instructions are complete
- New user can follow step-by-step
```

**Result**: Installation guide ready.

### Task 3: Architecture Guide

```bash
simp> Generate architecture documentation.
     
Document:
- Module structure
- Data flow
- Authentication flow
- Error handling
- Performance characteristics

Generate from:
- Current SIMP.md
- Wiki pages
- Code structure
- Tests

Verification:
- Guide is clear and accurate
- Diagrams work (mermaid)
```

**Result**: Architecture guide ready.

---

## Example 8: Testing Improvements

**Scenario**: Increase test coverage and quality.

### Task 1: Identify Missing Tests

```bash
simp> Run coverage analysis and identify missing tests.
     
Current coverage: 65%

Identify:
- Untested functions
- Untested error paths
- Untested edge cases

Generate list of missing tests.
```

**Result**: Missing coverage identified.

### Task 2: Add Tests

```bash
simp> Add tests for identified gaps.
     
For each missing test:
- Test happy path
- Test error case
- Test edge case
- Add assertion

Target coverage: 85%+

Verification: pytest passes, coverage > 85%
```

**Result**: Coverage improved to 87%.

### Task 3: Test Documentation

```bash
simp> Document testing approach and patterns.
     
Document:
- How to run tests
- How to add new tests
- Test organization
- Mocking patterns
- Assertion patterns

Generate: tests/README.md
```

**Result**: Testing guide ready.

---

## Example 9: Multi-Task Workflow (Weekly Development)

**Monday**: Feature work
```bash
simp> Add user profile endpoint
```

**Tuesday**: Bug fixes
```bash
simp> Fix token expiration test failures
```

**Wednesday**: Optimization
```bash
simp> Add caching to frequently used queries
```

**Thursday**: Documentation
```bash
simp> Generate API documentation
```

**Friday**: Polish
```bash
simp> Add comprehensive error messages
```

**Result**:
- ✓ 5 focused tasks, each verifiable
- ✓ Wiki grows with each task
- ✓ System becomes more capable
- ✓ New developer can onboard by reviewing Wiki

---

## Example 10: Handling Uncertainty

**Scenario**: Unsure how to implement something. Use SimpCode to explore.

### Task: Research Best Practice

```bash
simp> Research best practices for implementing rate limiting
     in Python FastAPI applications.

What should I know about:
- Different rate limiting algorithms (token bucket, sliding window)
- Libraries available (slowapi, etc.)
- Performance implications
- How other projects do it

Generate: Document with findings and recommendation
```

**Result**: SimpCode generates research document.

### Task: Implement Recommended Approach

```bash
simp> Implement rate limiting using the recommended approach
     from the research document.

Constraints:
- Use in-memory storage (no Redis required)
- Limit 100 requests per minute per IP
- Return proper HTTP 429 responses
- Include rate limit headers

Verification:
- Implementation works
- Tests pass
```

**Result**: Feature implemented with confidence.

---

## Anti-Patterns (What NOT to Do)

### Anti-Pattern 1: Vague Task Descriptions

❌ **Bad**:
```bash
simp> Make the auth module better
```

✅ **Good**:
```bash
simp> Add comprehensive type hints to src/auth.py
     and ensure mypy --strict passes
```

### Anti-Pattern 2: Huge Tasks

❌ **Bad**:
```bash
simp> Refactor entire project to async
```

✅ **Good**:
```bash
simp> Convert database query layer to async
     (specific, focused, verifiable)

# Then later:
simp> Convert HTTP request handlers to async

# Then later:
simp> Convert utility functions to async
```

### Anti-Pattern 3: Unrealistic Constraints

❌ **Bad**:
```bash
simp> Add rate limiting without modifying any code
```

✅ **Good**:
```bash
simp> Add rate limiting to API
     implementing in middleware layer
```

### Anti-Pattern 4: Ignoring Test Failures

❌ **Bad**:
```bash
simp> Add feature X
# Tests fail, ignore and move on
simp> Add feature Y
```

✅ **Good**:
```bash
simp> Add feature X
# Tests fail, fix them
simp> Verify all tests pass before continuing
simp> Add feature Y
```

---

## Performance Tips

### Tip 1: Task Granularity

```
Too vague:      "Improve authentication"
Too fine:       "Add parameter type hint to line 42"
Just right:     "Add type hints to auth.py"
```

### Tip 2: Context Efficiency

```
Inefficient:    "Improve the entire codebase"
               (context budget exceeded)

Efficient:      "Improve error handling in auth module"
               (focused, fits context)
```

### Tip 3: Verification Clarity

```
Weak:           "Does it look good?"
Strong:         "pytest tests/test_auth.py passes"
```

### Tip 4: Learning from Patterns

```
First task:     "Add type hints to auth module"
Second task:    "Add type hints to api module"
(SimpCode learns pattern, faster)

Third task:     "Add type hints to utils module"
(Even faster, consistent patterns)
```

---

## Summary

SimpCode excels at:

1. ✅ **Understanding** existing codebases
2. ✅ **Implementing** features with verification
3. ✅ **Debugging** with context and history
4. ✅ **Refactoring** incrementally
5. ✅ **Learning** from each task
6. ✅ **Scaling** to larger projects over time

**Key principle**: Break large work into focused, verifiable tasks.

Each task:
- ✓ Has clear success criteria
- ✓ Can be verified independently
- ✓ Teaches the system new patterns
- ✓ Makes next task faster

---

**See Also**:
- [Comprehensive Guide](COMPREHENSIVE_GUIDE.md)
- [Architecture Deep Dive](ARCHITECTURE_DEEP_DIVE.md)
- [Troubleshooting](TROUBLESHOOTING.md)
