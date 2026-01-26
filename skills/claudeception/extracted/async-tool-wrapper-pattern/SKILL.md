---
name: async-tool-wrapper-pattern
description: |
  Pattern for wrapping synchronous Python functions as async Tools for Synalinks or similar
  async-first frameworks. Use when: (1) You have existing sync functions/skills that need to
  work with async pipelines, (2) Synalinks Tool class requires async functions, (3) You need
  lazy Tool instantiation to avoid import-time errors. Covers asyncio.to_thread() pattern and
  lazy initialization for framework compatibility.
author: Claude Code (Claudeception)
version: 1.0.0
date: 2026-01-25
---

# Async Tool Wrapper Pattern

## Problem

When integrating existing synchronous Python functions (like CLI-based skills) with async-first
frameworks like Synalinks, you face two challenges:

1. The framework's `Tool` class requires async functions
2. Import-time Tool creation can fail if dependencies aren't ready

## Context / Trigger Conditions

- You have existing sync functions (often from argparse-based CLI scripts)
- Framework requires async functions (e.g., `synalinks.Tool`)
- You get errors like "is not an asynchronous function"
- You need to maintain backward compatibility with sync callers
- Import errors occur when Tool is created at module load time

## Solution

### Step 1: Create Async Wrapper with asyncio.to_thread()

```python
import asyncio
from skills.my_skill import execute as sync_execute

async def my_async_function(param1: str, param2: int) -> dict:
    """Async wrapper for sync skill.

    Args:
        param1 (str): First parameter description.
        param2 (int): Second parameter description.
    """
    result = await asyncio.to_thread(sync_execute, param1, param2)
    return result
```

**Key points:**
- `asyncio.to_thread()` runs sync function in a thread pool (non-blocking)
- Function signature must match what the Tool expects
- Docstring with Args section is REQUIRED for Synalinks Tool

### Step 2: Lazy Tool Instantiation

```python
_tool_instance = None

def get_my_tool():
    """Get or create the Tool instance lazily."""
    global _tool_instance
    if _tool_instance is None:
        try:
            import synalinks
            _tool_instance = synalinks.Tool(my_async_function)
        except ImportError:
            # Framework not available, return raw function
            return my_async_function
    return _tool_instance

# Alias for convenient import
my_tool = get_my_tool
```

**Why lazy?**
- Avoids import-time errors if framework isn't installed
- Allows module to be imported even when Tool creation would fail
- Enables graceful fallback to raw async function

### Step 3: Complete Module Template

```python
"""Async Tool wrapper for [skill_name]."""

import asyncio
import sys
from pathlib import Path

# Add project root to path for skill imports
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from skills.my_skill import execute as sync_execute


async def my_async_skill(param1: str, param2: int) -> dict:
    """Description of what this skill does.

    Args:
        param1 (str): Description of param1.
        param2 (int): Description of param2.
    """
    result = await asyncio.to_thread(sync_execute, param1, param2)
    return result


# Lazy Tool instantiation
_tool_instance = None

def get_tool():
    """Get or create the Tool instance."""
    global _tool_instance
    if _tool_instance is None:
        try:
            import synalinks
            _tool_instance = synalinks.Tool(my_async_skill)
        except ImportError:
            return my_async_skill
    return _tool_instance


# Export both the async function and tool getter
my_skill_tool = get_tool
```

## Verification

1. Import works without framework installed:
   ```python
   from tools.my_tool import my_async_skill  # Works
   ```

2. Async function works standalone:
   ```python
   result = await my_async_skill("test", 42)  # Works
   ```

3. Tool creation works when framework is available:
   ```python
   tool = my_skill_tool()
   result = await tool(param1="test", param2=42)  # Works
   ```

## Example

Real-world example from CrowdStrike OCSF project:

```python
# synalinks_pipeline/tools/parse_tool.py

import asyncio
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from skills.parse_crowdstrike import execute as parse_sync


async def parse_crowdstrike(event_json: str) -> dict:
    """Parse CrowdStrike DetectionSummaryEvent to extract fields.

    Args:
        event_json (str): Raw JSON string of CrowdStrike event.
    """
    result = await asyncio.to_thread(parse_sync, event_json)
    return result


_tool_instance = None

def get_parse_tool():
    global _tool_instance
    if _tool_instance is None:
        try:
            import synalinks
            _tool_instance = synalinks.Tool(parse_crowdstrike)
        except ImportError:
            return parse_crowdstrike
    return _tool_instance

parse_crowdstrike_tool = get_parse_tool
```

## Notes

- **Thread pool:** `asyncio.to_thread()` uses the default thread pool executor. For
  CPU-bound work, consider `ProcessPoolExecutor` instead.

- **Docstrings required:** Synalinks Tool parses the docstring's Args section to build
  JSON schema. Missing or incomplete docstrings will raise ValueError.

- **Return type:** Tool expects the function to return a dict. Non-dict returns are
  wrapped in `{"result": value}`.

- **Error handling:** The sync function's exceptions propagate through the async wrapper.
  Consider adding try/except in the wrapper if you need different error handling.

- **Alternative pattern:** If you control the original function, make it async directly
  rather than wrapping. Only use this pattern for legacy/external code.

## Related Skills

- `minion-task-tool-permissions` - Handling Task tool permissions for background agents
