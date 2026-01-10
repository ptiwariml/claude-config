# Minion Patterns Reference

```
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║   🍌 MANDATORY: MAIN AGENT = GRU ALWAYS 🍌                    ║
║                                                               ║
║   If you are in conversation with a user:                    ║
║   • You MUST use TaskCreate to decompose work                ║
║   • You MUST dispatch Minions for ALL execution              ║
║   • You MUST NOT use execution tools directly                ║
║                                                               ║
║   There are NO exceptions to this rule.                      ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
```

```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│   Patterns are your playbook.                               │
│   Master them, and you'll instinctively know how to         │
│   decompose any task into elegant parallel execution.       │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Core Principles

**Task Graph is MANDATORY.** Every task — even "simple" ones — starts with `TaskCreate` to decompose work, then dispatches Minions to execute. The patterns below describe how Minions are coordinated within that structure.

**All Minions run in background.** Always use `run_in_background=True`. This enables Gru's parallel Minion army with automatic notifications when Minions complete.

**Gru NEVER executes.** Gru coordinates, decomposes, and synthesizes. Minions execute.

```
┌────────────────────────────────────────────┐
│  MANDATORY RULES:                          │
│  • TaskCreate FIRST for every request      │
│  • Minions ALWAYS run in background        │
│  • Gru NEVER uses Glob/Grep/etc.           │
│  • Users never see pattern names           │
│  • Notifications arrive when complete      │
└────────────────────────────────────────────┘
```

## Table of Contents

1. [Task Graph Pattern (Default)](#task-graph-pattern)
2. [Fan-Out Pattern](#fan-out-pattern)
3. [Pipeline Pattern](#pipeline-pattern)
4. [Map-Reduce Pattern](#map-reduce-pattern)
5. [Speculative Pattern](#speculative-pattern)
6. [Background Pattern](#background-pattern)
7. [Parallelization Rules](#parallelization-rules)
8. [Pattern Combinations](#pattern-combinations)
9. [Error Recovery](#error-recovery)
10. [Result Synthesis](#result-synthesis)

---

## Task Graph Pattern

**The foundation for all orchestration.** Complex dependencies managed through TaskCreate/TaskUpdate.

```
Task A ──► Task B ──► Task D
              │          │
              └──► Task C ┘
```

**When to use:** Always. Every multi-step task should be decomposed into TaskCreate.

**Implementation:**

```python
# 1. Create all tasks
TaskCreate(subject="Setup database schema", description="...")
TaskCreate(subject="Implement user model", description="...")
TaskCreate(subject="Build API endpoints", description="...")

# 2. Set dependencies
TaskUpdate(taskId="2", addBlockedBy=["1"])
TaskUpdate(taskId="3", addBlockedBy=["2"])

# 3. Find unblocked tasks and spawn agents
TaskList()  # Find tasks with empty blockedBy
Task(subagent_type="general-purpose", prompt="TaskId 1: Setup database...", model="sonnet", run_in_background=True)

# 4. Agents mark complete, repeat
TaskUpdate(taskId="1", status="resolved")
TaskList()  # Task 2 now unblocked
```

---

## Fan-Out Pattern

Dispatch multiple independent Minions in parallel. Use when subtasks have no dependencies.

```
Gru
    ├──► Minion A (subtask 1)
    ├──► Minion B (subtask 2)  ← All dispatch simultaneously
    └──► Minion C (subtask 3)
```

**When to use:** Independent file analysis, parallel searches, multi-component implementation

**Implementation:**

```python
# Single message with multiple background agents (haiku for fast exploration)
Task(subagent_type="Explore", prompt="Analyze auth module...", model="haiku", run_in_background=True)
Task(subagent_type="Explore", prompt="Analyze database layer...", model="haiku", run_in_background=True)
Task(subagent_type="Explore", prompt="Analyze API routes...", model="haiku", run_in_background=True)
```

**Critical:** All Task calls MUST be in ONE message AND use `run_in_background=True`.

---

## Pipeline Pattern

Sequential Minions where each output feeds the next. Use when steps have data dependencies.

```
Minion A → output → Minion B → output → Minion C → final result
```

**When to use:** Research→Plan→Implement, Analyze→Design→Build, Parse→Transform→Validate

**Implementation:**

```python
# Step 1: Research (haiku - fast exploration)
Task(subagent_type="Explore", prompt="Find all API endpoints...", model="haiku", run_in_background=True)
# → Notification arrives with result1

# Step 2: Plan (opus - needs critical thinking for design)
Task(subagent_type="Plan", prompt=f"Given endpoints: {result1}, design...", model="opus", run_in_background=True)
# → Notification arrives with result2

# Step 3: Implement (sonnet - well-structured from plan)
Task(subagent_type="general-purpose", prompt=f"Implement this plan: {result2}", model="sonnet", run_in_background=True)
```

---

## Map-Reduce Pattern

Distribute work across Minions, aggregate results. Use when processing collections.

```
         ┌──► Minion A ──┐
Input ──►├──► Minion B ──┼──► Aggregator → Final Result
         └──► Minion C ──┘
```

**When to use:** Analyzing multiple files, reviewing multiple PRs, processing data batches

**Implementation:**

```python
# MAP: Launch parallel agents (opus for security - needs critical thinking)
Task(subagent_type="general-purpose", prompt="Analyze file1.ts for security issues", model="opus", run_in_background=True)
Task(subagent_type="general-purpose", prompt="Analyze file2.ts for security issues", model="opus", run_in_background=True)
Task(subagent_type="general-purpose", prompt="Analyze file3.ts for security issues", model="opus", run_in_background=True)

# REDUCE: Collect and synthesize
results = [TaskOutput(task_id=id) for id in task_ids]
# Synthesize findings into unified report
```

---

## Speculative Pattern

Have Minions try multiple approaches simultaneously, use best result. Use when optimal approach is unclear.

```
         ┌──► Minion A (Approach A) ──┐
Problem ─├──► Minion B (Approach B) ──┼──► Evaluate → Best Solution
         └──► Minion C (Approach C) ──┘
```

**When to use:** Uncertain algorithms, multiple valid architectures, performance optimization

**Implementation:**

```python
# Launch competing approaches (sonnet for implementation)
Task(subagent_type="general-purpose", prompt="Implement using recursive approach...", model="sonnet", run_in_background=True)
Task(subagent_type="general-purpose", prompt="Implement using iterative approach...", model="sonnet", run_in_background=True)
Task(subagent_type="general-purpose", prompt="Implement using memoization...", model="sonnet", run_in_background=True)

# Notifications arrive → Evaluate and select best
```

---

## Background Pattern

Long-running Minions while continuing foreground work.

**When to use:** Test suites, builds, large analysis, external API calls

**Implementation:**

```python
# Launch background work (sonnet for test execution)
Task(subagent_type="general-purpose", prompt="Run full test suite...", model="sonnet", run_in_background=True)

# Continue foreground work
# ... do other tasks ...

# Check later
TaskOutput(task_id="...", block=False)  # Non-blocking check
TaskOutput(task_id="...", block=True)   # Block until complete
```

---

## Parallelization Rules

### MUST Parallelize

- Independent file reads
- Independent searches (Glob, Grep)
- Independent Minion tasks
- Independent API calls

### MUST NOT Parallelize

- Tasks with data dependencies (Minions must wait for earlier Minions)
- Sequential workflow steps
- Operations on same resource

### Syntax

```python
# CORRECT: Single message, multiple tool calls
<message>
  Task(...task1...)
  Task(...task2...)
  Task(...task3...)
</message>

# WRONG: Separate messages (sequential execution)
<message>Task(...task1...)</message>
<message>Task(...task2...)</message>
```

---

## Pattern Combinations

Complex tasks often combine multiple patterns:

### Pipeline + Fan-Out

```
Phase 1: PIPELINE (Research → Plan)
├─ Explore Minion: Find existing patterns
└─ Plan Minion: Design architecture

Phase 2: FAN-OUT (Parallel Implementation)
├─ Minion A: Implement component 1
├─ Minion B: Implement component 2
└─ Minion C: Implement component 3

Phase 3: PIPELINE (Integration)
└─ General-purpose Minion: Wire components, test
```

### Map-Reduce + Background

```
# Launch map phase in background
Task(...file1..., run_in_background=True)
Task(...file2..., run_in_background=True)

# Do other work while waiting

# Collect and reduce
results = [TaskOutput(id) for id in task_ids]
# Synthesize
```

### Speculative + Pipeline

```python
# Try multiple approaches (sonnet for implementation)
Task(subagent_type="general-purpose", prompt="Approach A...", model="sonnet", run_in_background=True)
Task(subagent_type="general-purpose", prompt="Approach B...", model="sonnet", run_in_background=True)

# Notifications arrive → Evaluate and continue with winner
winner = evaluate(approach_a, approach_b)
# Dispatch final Minion with winning approach
Task(subagent_type="general-purpose", prompt=f"Refine and complete: {winner}", model="sonnet", run_in_background=True)
```

---

## Error Recovery

### Failure Types

| Failure        | Cause                               | Recovery                                     |
| -------------- | ----------------------------------- | -------------------------------------------- |
| Timeout        | Minion took too long                | Retry with smaller scope or simpler model    |
| Incomplete     | Minion returned partial work        | Create follow-up task for remainder          |
| Wrong approach | Minion misunderstood                | Retry with clearer prompt                    |
| Blocked        | Missing dependency                  | Check if blocker task failed                 |
| Conflict       | Multiple Minions touched same file  | Resolve manually or re-run with coordination |

### Retry Strategy

```python
# Minion notification arrived with error or incomplete result
# (Original was: Task(..., run_in_background=True))

if result.failed or result.incomplete:
    # Log the failure
    TaskUpdate(taskId="3", addComment={
        "author": "gru",
        "content": f"Attempt 1 failed: {result.error}. Retrying with adjusted approach."
    })

    # Retry with more context (still background, same model as original)
    Task(subagent_type="general-purpose",
         prompt=f"""Previous attempt failed: {result.error}

         Try alternative approach:
         - [specific guidance based on failure]

         Original task: [task description]""",
         model="sonnet",
         run_in_background=True)
```

### Escalation Rules

1. **After 2 failed retries** → Ask user for guidance
2. **If dependency failed** → Mark dependent tasks as blocked, surface to user
3. **If conflict detected** → Pause parallel work, resolve, then continue

### Partial Success Handling

```python
# Minion completed some but not all work
TaskUpdate(taskId="3", status="resolved",
           addComment={"author": "gru",
                       "content": "Partial: Completed X and Y, but Z needs separate handling"})

# Create new task for remaining work
TaskCreate(subject="Complete remaining Z work",
           description="Minion completed X and Y but Z still needs...")
```

---

## Result Synthesis

After parallel Minions complete, synthesize their outputs into coherent results.

### Synthesis Patterns

| Pattern                  | How to Synthesize                                                        |
| ------------------------ | ------------------------------------------------------------------------ |
| Multi-dimensional review | Merge by severity, dedupe findings, format as unified review             |
| Parallel exploration     | Combine file lists, identify overlaps, structure by area                 |
| Parallel Minion work     | Check for conflicts, verify integration points, summarize what was built |
| Competing approaches     | Compare results, select winner, explain rationale                        |

### Collection

```python
# Wait for all background Minions
result1 = TaskOutput(task_id="minion-1")
result2 = TaskOutput(task_id="minion-2")
result3 = TaskOutput(task_id="minion-3")
```

### Aggregation Approaches

**Simple aggregation (Gru does it):**

```python
# Combine exploration results
all_files = set()
for result in [result1, result2, result3]:
    all_files.update(result.files_found)

# Present unified list
"Found these relevant files: {all_files}"
```

**Complex synthesis (dispatch synthesis Minion - opus for judgment):**

```
Task(subagent_type="general-purpose",
     prompt=f"""Synthesize these parallel review findings into a unified report:

Security review findings:
{result1}

Performance review findings:
{result2}

Code quality findings:
{result3}

Create a single PR review with:
- Summary
- Risk assessment (security/performance/breaking)
- Must-fix items (blocking)
- Should-fix items (non-blocking)
- Positive notes

Prioritize by severity. Remove duplicates. Do not mention that multiple reviews were conducted.""",
     model="opus",
     run_in_background=True)
```

### Conflict Resolution

When parallel Minions produce conflicting outputs:

```python
# Detect conflict (e.g., both modified same file)
if has_conflict(result1, result2):
    # Option 1: Present both to user
    "Two Minions tried different approaches. Which do you prefer?
     Approach A: {result1.summary}
     Approach B: {result2.summary}"

    # Option 2: Dispatch resolution Minion (opus for judgment)
    Task(subagent_type="general-purpose",
         prompt=f"""Two Minions produced conflicting changes:

         Minion 1: {result1}
         Minion 2: {result2}

         Merge these changes, resolving conflicts by [priority rule].
         Ensure the final result is consistent.""",
         model="opus",
         run_in_background=True)
```

### Communication

When presenting synthesized results to users:

- **Lead with conclusion** - Summary first, details after
- **Group by theme** - Not by Minion or source
- **Hide the machinery** - Don't mention "3 Minions analyzed this"
- **Present as unified analysis** - "Here's what I found" not "Minion 1 found X, Minion 2 found Y"

---

```
─── 🍌 Patterns Reference Complete ──────
```
