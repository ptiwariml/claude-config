---
name: minion-task-tool-permissions
description: |
  Fix for "Permission to use [tool] has been auto-denied (prompts unavailable)" errors
  when dispatching background agents via the Task tool. Use when: (1) Background Minions
  fail to use Glob, Read, Bash, or other tools, (2) Task tool agents can't access files
  outside the working directory, (3) Parallel agent dispatch returns permission errors.
  Solution: Pass `allowed_tools` parameter to explicitly grant tool permissions to subagents.
author: Claude Code (Claudeception)
version: 1.0.0
date: 2026-01-24
---

# Minion Task Tool Permissions

## Problem

When dispatching background agents using the Task tool (especially in the Minion framework),
agents fail with errors like:
- "Permission to use Glob has been auto-denied (prompts unavailable)"
- "Permission to use Read has been auto-denied (prompts unavailable)"
- "Permission to use Bash has been auto-denied (prompts unavailable)"

This happens because background agents run without interactive prompts, so they can't
request permissions dynamically.

## Context / Trigger Conditions

- Using `Task(run_in_background=True)` to dispatch parallel agents
- Agent needs to read files outside the current working directory
- Agent needs to use tools like Glob, Read, Grep, or Bash
- Error appears in agent output file: "Permission to use [tool] has been auto-denied"
- Using Minion framework for parallel exploration tasks

## Solution

Pass the `allowed_tools` parameter to explicitly grant tool permissions:

```python
# WRONG - permissions will fail
Task(
    subagent_type="Explore",
    description="Explore project",
    prompt="Read files in /path/to/project",
    run_in_background=True
)

# CORRECT - explicitly grant tools
Task(
    subagent_type="Explore",
    description="Explore project",
    prompt="Read files in /path/to/project",
    run_in_background=True,
    allowed_tools=["Glob", "Read", "Grep"]  # <-- Grant specific tools
)
```

### Common Tool Grants by Task Type

| Task Type | Recommended `allowed_tools` |
|-----------|----------------------------|
| Exploration/Research | `["Glob", "Read", "Grep"]` |
| Code Modification | `["Glob", "Read", "Grep", "Edit", "Write"]` |
| Command Execution | `["Bash", "Read"]` |
| Full Access | `["Glob", "Read", "Grep", "Bash", "Edit", "Write"]` |

### Pattern-Based Permissions

You can also use glob patterns for Bash:
```python
allowed_tools=["Read", "Bash(git *)"]  # Only allow git commands
```

## Verification

After adding `allowed_tools`:
1. Check the agent output file: `Read(/private/tmp/claude/.../tasks/<agent-id>.output)`
2. Verify tool calls succeeded (no "auto-denied" errors)
3. Verify agent returned actual data, not permission error messages

## Example

### Before (Fails)
```python
Task(
    subagent_type="Explore",
    description="Deep dive Synalinks",
    prompt="Explore /Users/user/work/projects/synalinks - read README, find examples...",
    model="opus",
    run_in_background=True
)
# Result: "Permission to use Glob has been auto-denied (prompts unavailable)"
```

### After (Works)
```python
Task(
    subagent_type="Explore",
    description="Deep dive Synalinks",
    prompt="Explore /Users/user/work/projects/synalinks - read README, find examples...",
    model="opus",
    run_in_background=True,
    allowed_tools=["Glob", "Read", "Grep"]  # <-- Add this
)
# Result: Agent successfully reads files and returns findings
```

## Notes

- This is especially important when exploring paths outside the current working directory
- The `Explore` subagent type doesn't automatically get file access permissions
- When using the Minion framework, always include `allowed_tools` for background agents
- If unsure which tools are needed, start with `["Glob", "Read", "Grep"]` for exploration
- For execution tasks, add `["Edit", "Write", "Bash"]` as needed
- The user will be prompted to approve the permissions if not already allowed

## Related

- Minion framework: `~/.claude/skills/minion/minion.md`
- Task tool documentation in Claude Code
