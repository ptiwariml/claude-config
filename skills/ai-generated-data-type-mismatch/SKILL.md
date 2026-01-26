---
name: ai-generated-data-type-mismatch
description: |
  Debug type errors when AI-generated data causes downstream parser failures. Use when:
  (1) TypeError with unexpected operand types (dict vs int, str vs list, etc.),
  (2) Error occurs in parser/processor but data comes from AI generation,
  (3) Pre-defined/sample data works but AI-generated data fails,
  (4) Error message like "unsupported operand type(s) for X: 'dict' and 'int'".
  Covers tracing type mismatches back to AI prompt schema definitions.
author: Claude Code
version: 1.0.0
date: 2026-01-25
---

# AI-Generated Data Type Mismatch Debugging

## Problem

When using AI (Claude, GPT, etc.) to generate structured data (JSON, configs, etc.) that
feeds into parsers or processors, type errors can occur because the AI prompt schema
doesn't match what the downstream code expects. The error appears in the parser, but
the root cause is in the AI generation prompt.

## Context / Trigger Conditions

- `TypeError: unsupported operand type(s) for &: 'dict' and 'int'` (or similar)
- Error occurs in a parser/processor function, not the generator
- Pre-defined sample data works correctly
- AI-generated data consistently fails
- The failing field exists in both working samples and AI output, but with different types

## Solution

### Step 1: Identify the Failing Operation
```python
# Example: Bitwise operation expecting int
result = flags_value & (1 << bit_position)  # Fails if flags_value is dict
```

### Step 2: Trace the Data Source
```
Error location (parser) → Data input → Generation source (AI prompt)
```

### Step 3: Compare Working vs Failing Data

**Working (pre-defined sample)**:
```json
{
  "PatternDispositionValue": 2048
  // PatternDispositionFlags is ABSENT
}
```

**Failing (AI-generated)**:
```json
{
  "PatternDispositionValue": 2048,
  "PatternDispositionFlags": {    // AI added this as DICT
    "Indicator": false,
    "Detect": true
  }
}
```

### Step 4: Fix the AI Prompt

**Before** (incorrect schema in prompt):
```
"PatternDispositionFlags": {
  "Indicator": <bool>,
  "Detect": <bool>,
  ...
}
```

**After** (matches real data format):
```
"PatternDispositionValue": <0|16|2048>
// PatternDispositionFlags removed - not in real data
```

### Step 5: Add Defensive Validation (Defense in Depth)

Even after fixing the prompt, add type validation in the parser:
```python
# Before
if flags_value is None:
    return {}

# After (defensive)
if flags_value is None or not isinstance(flags_value, int):
    return {}
```

## Verification

1. Generate new AI data and verify the field has correct type
2. Run the parser/processor - should complete without TypeError
3. Verify output matches expected format
4. Test edge cases (None, empty, missing field)

## Example

**Scenario**: CrowdStrike detection generator creates `PatternDispositionFlags` as dict,
but parser uses bitwise AND operation expecting int.

**Investigation Flow**:
```
1. Error: "unsupported operand type(s) for &: 'dict' and 'int'"
   Location: skills/parse_crowdstrike.py line 57

2. Check what calls this function:
   event.get("PatternDispositionFlags")  # Returns dict from AI data

3. Check AI generation prompt (web/generator.py):
   - Prompt tells AI to generate PatternDispositionFlags as dict
   - Real CrowdStrike data doesn't have this field (or has it as int)

4. Fix prompt: Remove PatternDispositionFlags dict from schema
5. Fix parser: Add isinstance(flags_value, int) check
```

## Anti-Patterns

- **DON'T** just add try/except around the failing line - find root cause
- **DON'T** assume AI will follow your schema exactly - validate types
- **DON'T** only fix the prompt OR the parser - fix both (defense in depth)

## Notes

- AI models may "helpfully" expand abbreviated schemas into full objects
- Compare AI output against REAL sample data, not documentation
- The prompt schema should match actual data format, not logical structure
- Consider using JSON Schema validation for AI-generated data

## Related Patterns

- Schema validation for AI outputs
- Type guards in dynamic data processing
- Contract testing between generators and consumers

## References

- This skill was extracted from debugging a CrowdStrike→OCSF transformation pipeline
- Pattern applies to any AI-generation-to-parser workflow
