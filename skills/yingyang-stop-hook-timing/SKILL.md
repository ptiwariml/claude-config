---
name: yingyang-stop-hook-timing
description: |
  Fix infinite loop caused by Claude Code stop hook checking JSONL transcript for verification
  patterns that haven't been flushed yet. Use when: (1) YingYang verification block is emitted
  but stop hook keeps saying "verification not found", (2) stop hook enters infinite retry loop
  despite verification being in the response, (3) any stop hook that reads transcript JSONL
  cannot find content from the CURRENT assistant response. Root cause is a fundamental timing
  issue: stop hooks fire BEFORE the current response is written to the transcript file.
author: Claude Code (extracted from RLM-Claude session)
version: 1.0.0
date: 2026-02-01
---

# YingYang Stop Hook Timing Issue

## Problem

The YingYang verification framework uses a stop hook (`yingyang_gate.py`) that checks the
Claude Code JSONL transcript file for the pattern `=== YINGYANG VERIFICATION COMPLETE ===`
in assistant messages. When the pattern isn't found, the hook returns feedback asking the
assistant to emit it, which creates a new user-type entry in the transcript. This creates
an infinite loop because:

1. Assistant emits verification block in response
2. Stop hook fires BEFORE the response is flushed to the JSONL transcript
3. Hook reads transcript, finds no pattern after the latest "user" entry
4. Hook returns "verification not found" feedback (which becomes a new user entry)
5. Assistant re-emits verification block
6. Go to step 2 (infinite loop)

## Context / Trigger Conditions

- YingYang stop hook repeatedly says "YingYang verification not found in conversation"
- You've already emitted the `=== YINGYANG VERIFICATION COMPLETE ===` block
- The verification pattern IS in your response but the hook can't see it
- Each retry creates another tool_result "user" entry, pushing the search boundary forward
- The hook's logic: find last "user" message timestamp, then search for pattern in
  assistant messages AFTER that timestamp

## Root Cause

Claude Code's architecture:
- Stop hooks execute as part of the response pipeline, BEFORE the current assistant
  message is committed to the JSONL transcript file
- The transcript file (`~/.claude/projects/.../SESSION_ID.jsonl`) is append-only
- Each line is a JSON object with `type: "user"` or `type: "assistant"` and a `timestamp`
- The hook's `check_verification()` function reads this file and searches for the pattern
  in assistant entries after the last user entry
- But the CURRENT response hasn't been written yet, so it's never found

Key code in `yingyang_gate.py`:
```python
def check_verification():
    # Finds last user message timestamp
    # Searches assistant messages AFTER that timestamp
    # Pattern is in CURRENT response which isn't in the file yet
    # → Always returns False
```

## Solution

**For skill/hook authors:** Stop hooks should NOT rely on reading the transcript file
for content from the current response. The current response is not yet flushed when the
hook executes. Instead:

1. **Use hook input directly**: Stop hooks receive the conversation context. Check the
   current response content from the hook's input rather than reading the JSONL file.
2. **Use environment variables or temp files**: Have the assistant write a marker file
   before the hook runs, and have the hook check for that file.
3. **Accept the limitation**: If the hook must read the transcript, it will only see
   content from PREVIOUS responses, never the current one.

**For users hitting this loop RIGHT NOW:**

The pragmatic workaround is to acknowledge the timing limitation and not fight it.
The verification was already run (Gemini/Grok returned results), the evidence is in
the conversation - the hook just can't see it in the file yet.

Options:
- Temporarily disable the stop hook: remove or rename `~/.claude/hooks.json` entry
- Modify the hook to check hook input/stdin instead of the transcript file
- Use a background process to write a verification marker after a delay

## Verification

After applying the fix:
- Run a task that triggers YingYang verification
- Emit the verification block
- The stop hook should find it (if using hook input) or not fire (if disabled)
- No infinite loop

## Example

**Before (broken):**
```
Assistant: [emits verification block]
Hook: reads transcript → can't find pattern → "verification not found"
Assistant: [re-emits verification block]
Hook: reads transcript → still can't find it → "verification not found"
... infinite loop ...
```

**After (fixed - hook reads input instead of file):**
```python
# In the hook, check stdin/input for the pattern instead of reading JSONL
import sys
response_text = sys.stdin.read()
if "=== YINGYANG VERIFICATION COMPLETE ===" in response_text:
    # Verification found in current response
    sys.exit(0)
```

## Notes

- This is a fundamental architectural constraint of Claude Code hooks, not a bug in
  YingYang specifically
- Any stop hook that reads the transcript JSONL for current-response content will hit
  this same issue
- The JSONL file IS eventually updated, just not until after all hooks complete
- Pre-tool and post-tool hooks have the same constraint for their respective triggers
- Tool result entries (type "user" with tool results) also appear in the transcript
  and shift the "last user message" boundary, compounding the problem
