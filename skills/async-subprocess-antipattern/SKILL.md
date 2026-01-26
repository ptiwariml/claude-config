---
name: async-subprocess-antipattern
description: |
  Debug frozen/unresponsive async Python applications caused by synchronous subprocess.run()
  inside async functions. Use when: (1) UI freezes during async operations, (2) WebSocket
  connections become unresponsive, (3) Function is marked "async def" but contains
  subprocess.run(), (4) Event loop appears blocked for seconds. Root cause: subprocess.run()
  is synchronous and blocks the entire event loop even inside async functions.
author: Claude Code
version: 1.0.0
date: 2026-01-25
---

# Async Subprocess Anti-Pattern

## Problem

Python functions marked as `async def` that internally use `subprocess.run()` block the
entire asyncio event loop, causing:
- UI/WebSocket unresponsiveness
- Timeouts in concurrent tasks
- "Frozen" application during subprocess execution

The code "looks async" but actually blocks because `subprocess.run()` is synchronous.

## Context / Trigger Conditions

- WebSocket connections become unresponsive during certain operations
- FastAPI/Starlette endpoints freeze for several seconds
- UI shows no progress updates during long operations
- `await some_function()` blocks much longer than expected
- Code pattern: `async def` function containing `subprocess.run()`

**Red Flag Code Pattern**:
```python
async def generate_something():
    # This LOOKS async but BLOCKS the event loop!
    result = subprocess.run(["some-cli", "command"], capture_output=True)
    return result.stdout
```

## Solution

### Option 1: asyncio.create_subprocess_exec() (Recommended)

Replace synchronous subprocess with async version:

**Before (Blocking)**:
```python
import subprocess

async def invoke_cli(prompt: str, timeout: int = 60) -> str:
    result = subprocess.run(
        ["cli-tool", "-p", prompt],
        capture_output=True,
        text=True,
        timeout=timeout
    )
    if result.returncode != 0:
        raise RuntimeError(f"CLI error: {result.stderr}")
    return result.stdout
```

**After (Non-blocking)**:
```python
import asyncio

async def invoke_cli(prompt: str, timeout: int = 60) -> str:
    proc = await asyncio.create_subprocess_exec(
        "cli-tool", "-p", prompt,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )

    try:
        stdout, stderr = await asyncio.wait_for(
            proc.communicate(),
            timeout=timeout
        )
    except asyncio.TimeoutError:
        proc.kill()
        await proc.wait()
        raise RuntimeError("CLI invocation timed out")

    if proc.returncode != 0:
        raise RuntimeError(f"CLI error: {stderr.decode()}")

    return stdout.decode()
```

### Option 2: asyncio.to_thread() (Python 3.9+)

For simpler cases where you want to keep the sync code:

```python
import asyncio
import subprocess

def _invoke_cli_sync(prompt: str, timeout: int) -> str:
    result = subprocess.run(
        ["cli-tool", "-p", prompt],
        capture_output=True,
        text=True,
        timeout=timeout
    )
    if result.returncode != 0:
        raise RuntimeError(f"CLI error: {result.stderr}")
    return result.stdout

async def invoke_cli(prompt: str, timeout: int = 60) -> str:
    return await asyncio.to_thread(_invoke_cli_sync, prompt, timeout)
```

### Option 3: concurrent.futures (Pre-Python 3.9)

```python
import asyncio
import subprocess
from concurrent.futures import ThreadPoolExecutor

executor = ThreadPoolExecutor(max_workers=4)

async def invoke_cli(prompt: str, timeout: int = 60) -> str:
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(
        executor,
        lambda: subprocess.run(
            ["cli-tool", "-p", prompt],
            capture_output=True,
            text=True,
            timeout=timeout
        ).stdout
    )
```

## Verification

1. Add logging before and after the subprocess call
2. Verify other async tasks continue during subprocess execution
3. Test WebSocket ping/pong during operation
4. Measure time - should show concurrent execution, not sequential

```python
import asyncio
import time

async def test_non_blocking():
    async def heartbeat():
        for i in range(10):
            print(f"Heartbeat {i}")
            await asyncio.sleep(0.5)

    async def slow_cli():
        return await invoke_cli("test prompt")

    # Both should run concurrently
    start = time.time()
    await asyncio.gather(heartbeat(), slow_cli())
    elapsed = time.time() - start

    # If blocking: elapsed ≈ subprocess_time + 5 seconds
    # If non-blocking: elapsed ≈ max(subprocess_time, 5 seconds)
    print(f"Elapsed: {elapsed}s")
```

## Example

**Real-world scenario from CrowdStrike OCSF project**:

The web app's "Generate with AI" button froze the UI for 6-17 seconds because:

```python
# web/generator.py - PROBLEMATIC CODE
async def generate_crowdstrike_alert():
    # Marked async but internally blocking!
    response = invoke_claude_cli(GENERATOR_PROMPT)  # This calls subprocess.run()
    ...

def invoke_claude_cli(prompt: str, timeout: int = 60) -> str:
    result = subprocess.run(  # BLOCKS EVENT LOOP
        ["claude", "-p", prompt, "--output-format", "text"],
        capture_output=True,
        text=True,
        timeout=timeout
    )
    return result.stdout
```

**Fix**: Convert to `asyncio.create_subprocess_exec()` and add progress callbacks.

## Notes

- `await` only yields control at await points - sync code between awaits blocks
- `subprocess.run()` has no await points - it's pure blocking I/O
- This anti-pattern is common when migrating sync code to async
- Consider adding progress callbacks for long-running subprocesses
- For shell commands, use `asyncio.create_subprocess_shell()` instead

## Anti-patterns to Recognize

```python
# BAD: sync subprocess in async function
async def bad_example():
    return subprocess.run(["cmd"], capture_output=True)

# BAD: sync file I/O in async function
async def also_bad():
    with open("file.txt") as f:
        return f.read()  # Use aiofiles instead

# BAD: sync HTTP in async function
async def another_bad():
    return requests.get("https://api.example.com")  # Use aiohttp/httpx instead
```

## References

- [Python asyncio subprocess documentation](https://docs.python.org/3/library/asyncio-subprocess.html)
- [Real Python: Async IO in Python](https://realpython.com/async-io-python/)
- [asyncio.to_thread() documentation](https://docs.python.org/3/library/asyncio-task.html#asyncio.to_thread)
