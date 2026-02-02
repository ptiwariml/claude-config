---
name: anthropic-sdk-max-tokens-timeout
description: |
  Fix ValueError or timeout errors when using the Anthropic Python SDK with high max_tokens values.
  Use when: (1) anthropic SDK raises ValueError about timeout exceeding 600 seconds,
  (2) requests fail before any API call is made with max_tokens >= 21334,
  (3) using anthropic SDK v0.70+ with non-streaming completions.
  The SDK calculates non-streaming timeout as (3600 * max_tokens / 128000) and rejects
  if it exceeds 600 seconds.
author: Claude Code
version: 1.0.0
date: 2026-02-01
---

# Anthropic SDK max_tokens Timeout Limit

## Problem
The Anthropic Python SDK (v0.70+) calculates a non-streaming request timeout based on `max_tokens`.
When `max_tokens` is set too high (>= ~21,334), the calculated timeout exceeds the SDK's 600-second
maximum, causing a `ValueError` before any API call is even made.

## Context / Trigger Conditions
- Using `anthropic.Anthropic().messages.create()` with `max_tokens >= 21334`
- Non-streaming mode (streaming has different timeout logic)
- Anthropic SDK version 0.70+ (introduced calculated timeouts)
- Error occurs BEFORE the API call — no network request is made
- Symptom: `ValueError` mentioning timeout exceeds maximum

## Solution

The SDK timeout formula for non-streaming is:
```
timeout = 3600 * max_tokens / 128000
```

The maximum allowed timeout is 600 seconds. Solving: `max_tokens <= 600 * 128000 / 3600 = 21,333`

**Fix:** Set `max_tokens` to 16384 or lower for non-streaming calls.

```python
# BAD — will fail with ValueError
client = AnthropicClient(api_key=key, model_name="claude-sonnet-4-20250514", max_tokens=32768)

# GOOD — stays under timeout limit
client = AnthropicClient(api_key=key, model_name="claude-sonnet-4-20250514", max_tokens=16384)
```

If you need higher output, use streaming mode which has different timeout handling.

## Verification
After reducing `max_tokens`, the API call should succeed without any timeout ValueError.

## Example
This was discovered when building RLM-Claude. The official RLM repo's `AnthropicClient` defaults
to `max_tokens=32768`, which works for streaming but fails for the non-streaming `messages.create()`
calls used in the RLM completion loop.

## Notes
- This limit is SDK-side, not API-side. The Anthropic API itself supports higher max_tokens.
- The formula may change in future SDK versions.
- For streaming calls, the timeout calculation is different and more generous.
- `max_tokens=16384` provides 16K output tokens which is generous for most use cases.
