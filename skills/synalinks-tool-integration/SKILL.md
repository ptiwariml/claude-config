---
name: synalinks-tool-integration
description: |
  Integrate Python functions as Synalinks Tools for composable pipelines. Use when:
  (1) ValueError about Literal types not converting to JSON schema, (2) Tool call
  returns JsonDataModel instead of expected dict, (3) "missing required argument"
  errors despite having defaults, (4) wrapping existing sync functions for
  Synalinks. Covers async conversion, type hint constraints, result extraction
  with .get_json(), and proper docstring formatting.
author: Claude Code (Claudeception)
version: 1.0.0
date: 2026-01-28
---

# Synalinks Tool Integration

## Problem

Wrapping existing Python functions as `synalinks.Tool` instances fails with cryptic
errors due to undocumented constraints in Synalinks' function introspection.

## Context / Trigger Conditions

Use this skill when:
- `ValueError: Cannot convert typing.Literal to JSON schema` when creating a Tool
- Tool call returns `JsonDataModel` object instead of expected dict
- `TypeError: missing required argument` despite having default values
- Integrating existing synchronous functions into a Synalinks pipeline
- Building deterministic (non-LLM) transformation pipelines with Synalinks

## Solution

### 1. Function Signature Requirements

**NO `typing.Literal` types** - Synalinks cannot convert Literal to JSON schema:

```python
# WRONG - Will throw ValueError
from typing import Literal
async def my_func(scale: Literal["a", "b", "c"]) -> dict:
    ...

# CORRECT - Use basic str type
async def my_func(scale: str) -> dict:
    ...
```

**NO default parameters** - All parameters must be required:

```python
# WRONG - Defaults not allowed
async def my_func(value: int, scale: str = "auto") -> dict:
    ...

# CORRECT - All params required (document defaults in docstring)
async def my_func(value: int, scale: str) -> dict:
    """
    Args:
        value (int): The input value.
        scale (str): Scale type - 'discrete', 'continuous', or 'auto'.
    """
    ...
```

**Functions MUST be async**:

```python
# WRONG - Sync function
def my_func(value: int) -> dict:
    ...

# CORRECT - Async function
async def my_func(value: int) -> dict:
    ...
```

### 2. Complete Docstring with Args Section

Synalinks parses docstrings for schema generation:

```python
async def map_severity(crowdstrike_severity: int, scale: str) -> dict:
    """Map CrowdStrike severity to OCSF severity_id.

    Args:
        crowdstrike_severity (int): Severity value (0-5 or 0-100).
        scale (str): Scale type - 'discrete', 'continuous', or 'auto'.

    Returns:
        dict: Contains severity_id, severity label, and error field.
    """
    ...
```

### 3. Result Extraction with `.get_json()`

Tool calls return `JsonDataModel`, not raw dict:

```python
import synalinks

# Create the tool
my_tool = synalinks.Tool(my_async_function)

# WRONG - Returns JsonDataModel, not dict
result = await my_tool(value=5, scale="auto")
print(result["key"])  # TypeError: JsonDataModel not subscriptable

# CORRECT - Extract dict with .get_json()
result = await my_tool(value=5, scale="auto")
output = result.get_json()  # Now it's a dict
print(output["key"])  # Works!
```

### 4. Wrapping Sync Functions

If you have existing sync functions, create async wrappers:

```python
# Existing sync function
def execute_sync(value: int, scale: str) -> dict:
    ...

# Async wrapper for Synalinks
async def execute(value: int, scale: str) -> dict:
    """[Full docstring with Args section]"""
    # If CPU-bound, use to_thread; if IO-bound or fast, call directly
    return execute_sync(value, scale)

# Create tool from async wrapper
my_tool = synalinks.Tool(execute)
```

### 5. Tool Creation at Module Level

Create Tool instances at module level (not lazy/deferred):

```python
# In tools/my_tool.py
import synalinks
from skills.my_skill import execute as skill_async

async def my_function(param1: str, param2: int) -> dict:
    """[Full docstring]"""
    return await skill_async(param1, param2)

# Create at module level - NOT in a getter function
my_tool = synalinks.Tool(my_function)
```

## Verification

Test your tool integration:

```python
import asyncio
import synalinks

async def test():
    # 1. Verify tool is created
    assert isinstance(my_tool, synalinks.Tool)

    # 2. Call the tool
    result = await my_tool(param1="test", param2=42)

    # 3. Extract and verify result
    output = result.get_json()
    assert isinstance(output, dict)
    print(f"Success: {output}")

asyncio.run(test())
```

## Example

Complete tool wrapper pattern:

```python
"""Synalinks Tool wrapper for map_severity skill."""

import synalinks
from skills.map_severity import execute as severity_async


async def map_severity(crowdstrike_severity: int, scale: str) -> dict:
    """Map CrowdStrike severity to OCSF severity_id.

    Args:
        crowdstrike_severity (int): CrowdStrike severity value (0-5 or 0-100).
        scale (str): Scale type - 'discrete', 'continuous', or 'auto'.

    Returns:
        dict: Contains severity_id, severity label, original value, and error.
    """
    result = await severity_async(crowdstrike_severity, scale)
    return result


# Create Synalinks Tool instance at module level
map_severity_tool = synalinks.Tool(map_severity)
```

Usage in pipeline:

```python
import asyncio

async def transform(event):
    # Call tool (returns JsonDataModel)
    severity_raw = await map_severity_tool(
        crowdstrike_severity=event["severity"],
        scale="auto"
    )
    # Extract dict
    severity_result = severity_raw.get_json()

    return severity_result
```

## Notes

- **No LLM Dependency**: `synalinks.Tool` is purely deterministic - no LLM calls involved
- **Parallel Execution**: Use `asyncio.gather()` for independent tools
- **Type Hints**: Use basic types (`str`, `int`, `bool`, `dict`, `list`) - avoid complex types
- **Optional Values**: Use `Optional[str]` for nullable params, but caller must still provide them
- **pytest-asyncio**: Add `asyncio_mode = "auto"` to pyproject.toml for async tests

## References

- Synalinks GitHub: https://github.com/synalinks/synalinks
- This skill was derived from integrating 5 CrowdStrike-OCSF transformation skills as Synalinks Tools
