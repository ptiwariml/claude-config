---
name: context-aware-claude-code-hooks
description: |
  Pattern for making Claude Code hooks context-aware to prevent infinite loops or unnecessary
  triggers. Use when: (1) a Stop hook fires on every response including simple Q&A, (2) a hook
  creates loops by blocking non-applicable tasks, (3) you need to detect what actually happened
  in a conversation (code changes vs planning vs simple questions). Covers transcript analysis,
  tool_use detection, and conditional hook logic.
author: Claude Code
version: 1.0.0
date: 2025-01-25
---

# Context-Aware Claude Code Hooks

## Problem

Claude Code hooks (especially "Stop" hooks) fire on every response turn, not selectively.
A hook that requires verification for code changes will also block simple greetings,
questions, and planning tasks—causing infinite loops or forcing unnecessary patterns.

## Context / Trigger Conditions

- A Stop hook blocks EVERY response unless a specific pattern is present
- Simple Q&A like "What is X?" triggers the same verification as code implementations
- Users experience infinite loops on non-applicable tasks
- Hook has no awareness of what actually happened in the conversation

## Solution

### 1. Analyze Transcript Entries for Tool Usage

Hook receives transcript via `transcript_path`. Parse JSONL entries and look for tool_use blocks:

```python
def detect_code_modifications(entries: list[dict]) -> bool:
    """Check if any code files were modified using Write/Edit tools."""
    code_extensions = {'.py', '.js', '.ts', '.tsx', '.jsx', '.go', '.java', '.rs',
                       '.cpp', '.c', '.h', '.hpp', '.cs', '.rb', '.php', '.swift',
                       '.kt', '.scala', '.r', '.m', '.mm'}

    for entry in entries:
        if entry.get("type") != "assistant":
            continue
        content = entry.get("message", {}).get("content", [])
        if not isinstance(content, list):
            continue

        for block in content:
            if not isinstance(block, dict) or block.get("type") != "tool_use":
                continue
            tool_name = block.get("name", "")
            if tool_name in ("Write", "Edit"):
                file_path = block.get("input", {}).get("file_path", "")
                ext = Path(file_path).suffix.lower()
                if ext in code_extensions:
                    return True
    return False
```

### 2. Detect Simple Q&A Sessions

```python
def detect_simple_qa(entries: list[dict]) -> bool:
    """Detect simple Q&A without code changes."""
    tool_count = 0
    has_write_edit_bash = False

    for entry in entries:
        if entry.get("type") != "assistant":
            continue
        content = entry.get("message", {}).get("content", [])
        if isinstance(content, list):
            for block in content:
                if isinstance(block, dict) and block.get("type") == "tool_use":
                    tool_count += 1
                    if block.get("name") in ("Write", "Edit", "Bash"):
                        has_write_edit_bash = True

    # Simple if few tools and no modifications
    return tool_count < 3 or not has_write_edit_bash
```

### 3. Detect Planning/Research Context

```python
def detect_planning_context(entries: list[dict]) -> bool:
    """Detect planning or research contexts."""
    indicators = ["PLANNING MINION", "writing-plans", "brainstorm",
                  "superpowers:write-plan", "research"]

    for entry in entries:
        content = entry.get("message", {}).get("content", "")
        if isinstance(content, str):
            if any(ind.lower() in content.lower() for ind in indicators):
                return True
        elif isinstance(content, list):
            for block in content:
                if isinstance(block, dict) and "text" in block:
                    if any(ind.lower() in block["text"].lower() for ind in indicators):
                        return True
    return False
```

### 4. Main Decision Function

```python
def should_require_verification(entries: list[dict]) -> bool:
    """Smart decision about when verification is needed."""
    # Planning always skips
    if detect_planning_context(entries):
        return False

    # Code modified = verification required
    if detect_code_modifications(entries):
        return True

    # Simple Q&A skips
    if detect_simple_qa(entries):
        return False

    # Default: don't require
    return False
```

### 5. Integrate Into Hook Main Logic

```python
def main():
    input_data = read_stdin()
    transcript_path = input_data.get("transcript_path")
    entries = read_transcript(transcript_path)

    # NEW: Check if verification is even needed
    if not should_require_verification(entries):
        print(json.dumps({}))  # Allow stop
        return

    # Original verification logic only runs when applicable
    if check_verification(entries):
        print(json.dumps({}))  # Allow stop
    else:
        print(json.dumps({
            "decision": "block",
            "reason": "Verification required for code changes"
        }))
```

## Verification

Test with scenarios:
1. Simple greeting → Hook should NOT block
2. Code file edited → Hook SHOULD require verification
3. Planning context → Hook should NOT block
4. Non-code file (README.md) → Hook should NOT block

## Example

Before (broken):
```
User: "Hello!"
Claude: "Hi there!"
Hook: "BLOCKED! No verification pattern!"
→ Infinite loop
```

After (context-aware):
```
User: "Hello!"
Claude: "Hi there!"
Hook: (detects simple Q&A, no code changes) → Allows stop

User: "Fix the bug in main.py"
Claude: [Edits main.py]
Hook: (detects code modification) → Requires verification pattern
```

## Notes

- Hook type matters: "Stop" hooks fire on EVERY response turn
- Transcript is JSONL format, each line is a separate JSON object
- Tool usage is in `message.content` array as `{"type": "tool_use", "name": "...", "input": {...}}`
- Be permissive by default (return False) to avoid loops
- Planning contexts should always skip verification

## References

- Claude Code hooks documentation
- Transcript JSONL structure from Claude Code internals
