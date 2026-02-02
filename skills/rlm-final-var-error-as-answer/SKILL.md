---
name: rlm-final-var-error-as-answer
description: |
  Fix the official alexzhang13/rlm FINAL_VAR bug where error strings terminate the RLM loop
  prematurely. Use when: (1) RLM completion returns "Error: Variable 'X' not found. Available
  variables: [...]" as the actual response, (2) the RLM loop terminates after one iteration
  despite the model not finding a real answer, (3) FINAL_VAR is called with a variable name
  that doesn't exist in the REPL locals. Root cause: _final_var() returns error strings instead
  of raising exceptions, and find_final_answer() treats any non-empty output as the final answer.
author: Claude Code
version: 1.0.0
date: 2026-02-01
---

# RLM FINAL_VAR Error-as-Answer Bug

## Problem
When using the official alexzhang13/rlm library, if the model calls `FINAL_VAR('variable_name')`
with a variable that doesn't exist in the REPL environment, the error message is returned as
the "final answer" and the RLM loop terminates prematurely. The model never gets a chance to
self-correct.

## Context / Trigger Conditions
- Using `alexzhang13/rlm` (any version as of Feb 2026)
- RLM completion returns a response like:
  `Error: Variable 'final_answer' not found. Available variables: ['summary', 'result', ...].
  You must create and assign a variable BEFORE calling FINAL_VAR on it.`
- The RLM loop runs only 1 iteration despite `max_iterations` being set higher
- The model created variables with names like `summary`, `result`, etc. but called
  `FINAL_VAR('final_answer')` — a name that doesn't exist
- Common with Claude models that tend to default to `final_answer` as the variable name

## Root Cause (3 layers deep)

### Layer 1: `rlm/environments/local_repl.py:_final_var()`
Returns error **strings** instead of raising exceptions when variable not found:
```python
def _final_var(self, variable_name):
    if variable_name in self.locals:
        return str(self.locals[variable_name])
    # BUG: Returns error string instead of raising
    return f"Error: Variable '{variable_name}' not found. ..."
```

### Layer 2: `rlm/utils/parsing.py:find_final_answer()`
Treats ANY non-empty stdout from FINAL_VAR execution as the final answer:
```python
result = environment.execute_code(f"print(FINAL_VAR({variable_name!r}))")
final_answer = result.stdout.strip()
if final_answer == "":
    final_answer = result.stderr.strip() or ""
return final_answer  # Returns error string as "answer"
```

### Layer 3: `rlm/core/rlm.py` completion loop
Terminates when `find_final_answer` returns non-None:
```python
final_answer = find_final_answer(iteration.response, environment=environment)
if final_answer is not None:  # Error string is not None!
    return RLMChatCompletion(response=final_answer, ...)  # Returns error as response
```

## Solution

Monkey-patch `find_final_answer` in the RLM module's namespace to return `None` when
it detects a FINAL_VAR error, allowing the loop to continue.

```python
import rlm.core.rlm as _rlm_core

_original_find_final_answer = _rlm_core.find_final_answer

def _resilient_find_final_answer(text, environment=None):
    result = _original_find_final_answer(text, environment)
    if result and "Error:" in result and "not found" in result:
        return None  # Let the loop continue
    return result

_rlm_core.find_final_answer = _resilient_find_final_answer
```

### Critical: Patch the importing module, not the source

Python's `from X import Y` creates a local binding. The RLM core does:
```python
from rlm.utils.parsing import find_final_answer
```
So you must patch `rlm.core.rlm.find_final_answer`, NOT `rlm.utils.parsing.find_final_answer`.
Patching the source module won't affect the already-imported binding.

### Also: Enhance the system prompt

Add explicit FINAL_VAR naming guidance to reduce the error frequency:
```python
_FINAL_VAR_SUPPLEMENT = (
    "\n\nCRITICAL FINAL_VAR RULE: Always assign your final result to a variable "
    "named `final_answer` in a ```repl``` block FIRST, then call FINAL_VAR(final_answer) "
    "in your NEXT response. Before calling FINAL_VAR, run SHOW_VARS() to confirm the "
    "variable exists. Do NOT guess variable names."
)
```

### Also: Don't replace the system prompt

If you use `custom_system_prompt` on the RLM class, it **replaces** the entire default
`RLM_SYSTEM_PROMPT`, stripping all REPL environment instructions. Always append to the
default prompt instead:
```python
from rlm.utils.prompts import RLM_SYSTEM_PROMPT
custom_prompt = RLM_SYSTEM_PROMPT + your_additions
```

## What happens after the patch

When `find_final_answer` returns `None` for a FINAL_VAR error:
1. The RLM loop continues to the next iteration
2. The model sees its previous response in the message history
3. The model may self-correct and call FINAL_VAR with the right name
4. Or it may use `FINAL(direct text answer)` instead
5. Or it exhausts `max_iterations` and `_default_answer()` kicks in — which asks
   the model to summarize without FINAL_VAR, always producing a usable response

## Verification
```python
from rlm.environments.local_repl import LocalREPL
import rlm.core.rlm as rlm_mod

repl = LocalREPL()
repl.execute_code("summary = 'the actual answer'")

# With patch: returns None (loop continues)
result = rlm_mod.find_final_answer("FINAL_VAR(final_answer)", environment=repl)
assert result is None

# Correct variable name still works
result = rlm_mod.find_final_answer("FINAL_VAR(summary)", environment=repl)
assert result == "the actual answer"
```

## Notes
- This is a design issue in the official repo, not a Claude-specific problem
- Any LLM backend (OpenAI, Anthropic, etc.) can trigger this if the model picks
  the wrong variable name for FINAL_VAR
- Claude models particularly tend to use `final_answer` as a default name even
  when the actual variable has a different name
- The `_default_answer` fallback (reached at max_iterations) is actually a good
  safety net — it asks the model to just answer in text without FINAL_VAR
- Related skill: `anthropic-sdk-max-tokens-timeout` (another RLM-Claude gotcha)
- Related skill: `sqlite-timestamp-ordering-pitfall` (discovered in same project)
