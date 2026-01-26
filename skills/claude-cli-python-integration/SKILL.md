---
name: claude-cli-python-integration
description: |
  Invoke Claude Code CLI from Python using subprocess. Use when: (1) building agent
  systems that need Claude capabilities, (2) creating generators or validators using
  Claude, (3) automating Claude invocations in pipelines. Covers subprocess invocation
  pattern, proper CLI flags (--dangerously-skip-permissions, --output-format, --session-id),
  and robust JSON extraction from Claude's various output formats.
author: Claude Code
version: 1.0.0
date: 2026-01-25
---

# Claude CLI Python Integration

## Problem
You need to invoke Claude Code CLI programmatically from Python for automation,
agent systems, or building tools that leverage Claude's capabilities without
using the Anthropic API directly.

## Context / Trigger Conditions

Use this skill when:
- Building a Python tool that needs to call Claude
- Creating agent systems with Claude as the reasoning engine
- Automating content generation or validation using Claude
- Need session persistence across multiple invocations
- Running in non-interactive contexts (automation, CI/CD)

## Solution

### 1. Basic Invocation Pattern

```python
import subprocess
import json
import re
from typing import Dict, Any

def invoke_claude_cli(prompt: str, session_id: str = None, timeout: int = 120) -> str:
    """Invoke Claude CLI and return response text.

    Args:
        prompt: The prompt to send to Claude
        session_id: Optional session ID for conversation persistence
        timeout: Timeout in seconds (default 120)

    Returns:
        str: Claude's response text

    Raises:
        RuntimeError: If Claude CLI fails
    """
    cmd = [
        "claude",
        "-p", prompt,
        "--output-format", "text",
        "--dangerously-skip-permissions"
    ]

    if session_id:
        cmd.extend(["--session-id", session_id])

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=timeout
    )

    if result.returncode != 0:
        raise RuntimeError(f"Claude CLI error: {result.stderr}")

    return result.stdout
```

### 2. CLI Flags Reference

| Flag | Purpose |
|------|---------|
| `-p` | Pass prompt directly (not stdin) |
| `--output-format text` | Return plain text (no JSON wrapper) |
| `--output-format json` | Return structured JSON response |
| `--session-id ID` | Maintain conversation history |
| `--dangerously-skip-permissions` | Required for non-interactive/automation |
| `--print` | Print output to stdout |

### 3. Robust JSON Extraction

Claude may wrap JSON in markdown blocks. Handle all formats:

```python
def extract_json_from_output(output: str) -> Dict[str, Any]:
    """Extract JSON from Claude output, handling various formats.

    Tries extraction in order:
    1. Direct JSON parse
    2. From ```json ... ``` blocks
    3. From generic ``` ... ``` blocks
    4. From first { to last }
    """
    output = output.strip()

    # 1. Try direct parse
    try:
        return json.loads(output)
    except json.JSONDecodeError:
        pass

    # 2. Try ```json block
    json_match = re.search(r'```json\s*(.*?)\s*```', output, re.DOTALL)
    if json_match:
        try:
            return json.loads(json_match.group(1))
        except json.JSONDecodeError:
            pass

    # 3. Try generic ``` block
    code_match = re.search(r'```\s*(.*?)\s*```', output, re.DOTALL)
    if code_match:
        try:
            return json.loads(code_match.group(1))
        except json.JSONDecodeError:
            pass

    # 4. Try first { to last }
    first_brace = output.find('{')
    last_brace = output.rfind('}')
    if first_brace != -1 and last_brace != -1:
        try:
            return json.loads(output[first_brace:last_brace + 1])
        except json.JSONDecodeError:
            pass

    raise ValueError(f"Could not extract JSON from output: {output[:200]}...")
```

### 4. Complete Working Example

```python
def invoke_claude_and_get_json(
    prompt: str,
    session_id: str = "default",
    timeout: int = 120
) -> Dict[str, Any]:
    """Invoke Claude CLI and return parsed JSON response."""

    response = invoke_claude_cli(prompt, session_id, timeout)
    return extract_json_from_output(response)
```

### 5. Async Wrapper (for FastAPI/async contexts)

```python
import asyncio

async def invoke_claude_cli_async(prompt: str, timeout: int = 60) -> str:
    """Async wrapper for Claude CLI invocation."""

    def _invoke():
        return invoke_claude_cli(prompt, timeout=timeout)

    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _invoke)
```

### 6. With Retry Logic

```python
import time

def invoke_with_retry(
    prompt: str,
    max_retries: int = 3,
    timeout: int = 120
) -> str:
    """Invoke Claude with exponential backoff retry."""

    last_error = None
    for attempt in range(max_retries):
        try:
            return invoke_claude_cli(prompt, timeout=timeout)
        except (RuntimeError, subprocess.TimeoutExpired) as e:
            last_error = e
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt
                time.sleep(wait_time)

    raise RuntimeError(f"Failed after {max_retries} attempts: {last_error}")
```

## Verification

Test the integration:

```python
# Test basic invocation
response = invoke_claude_cli("Say 'Hello from CLI' in exactly 3 words")
assert "Hello" in response

# Test JSON extraction
json_response = invoke_claude_and_get_json(
    "Output a JSON object with keys 'status' (value: 'ok') and 'count' (value: 42)"
)
assert json_response["status"] == "ok"
assert json_response["count"] == 42
```

## Example: Building a Generator

```python
GENERATOR_PROMPT = """You are a security expert.
Generate a realistic security alert JSON.

OUTPUT FORMAT:
SUMMARY: <1-2 sentence description>

JSON:
```json
{"type": "alert", "severity": "high", ...}
```
"""

async def generate_security_alert():
    """Generate a security alert using Claude CLI."""
    response = await invoke_claude_cli_async(GENERATOR_PROMPT)

    # Extract summary
    summary_match = re.search(r'SUMMARY:\s*(.+?)(?=\n\n|JSON:)', response, re.DOTALL)
    summary = summary_match.group(1).strip() if summary_match else "Security alert"

    # Extract JSON
    alert_json = extract_json_from_output(response)

    return summary, alert_json
```

## Notes

- **Permission Flag**: `--dangerously-skip-permissions` is required for automation;
  without it, Claude CLI prompts for user confirmation
- **Session Persistence**: Use `--session-id` to maintain conversation context across
  invocations (useful for multi-turn agent loops)
- **Timeouts**: Default 120 seconds is reasonable; increase for complex generation tasks
- **Error Handling**: Always check `returncode != 0` and handle stderr
- **JSON Extraction**: Claude often wraps JSON in markdown; always use robust extraction

## References

- Pattern source: ~/work/matrix/implementation.md
- Production example: ~/work/projects/rulegenie/src/rulegenie/agent/interface.py
