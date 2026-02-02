---
name: cross-model-fact-checking
description: |
  Cross-validate facts using multiple AI models with awareness of training cutoff limitations.
  Use when: (1) GrokVetting returns FALSE on claims about recent events (past 1-2 months),
  (2) you need to verify facts about newly released or renamed software/projects,
  (3) one model's assessment contradicts your research or user-provided information,
  (4) fact-checking anything that happened after an LLM's training cutoff.
  Covers Grok API, Gemini API with Google Search grounding, and interpreting conflicting results.
author: Claude Code (Claudeception)
version: 1.0.0
date: 2026-01-31
---

# Cross-Model Fact-Checking with Training Cutoff Awareness

## Problem

When using an LLM (e.g., Grok via GrokVetting) to fact-check claims about recent events,
the model may confidently return FALSE for every claim — not because the claims are wrong,
but because the events occurred after the model's training data cutoff. This can cause you
to distrust valid information and waste time re-investigating.

## Context / Trigger Conditions

- GrokVetting returns FALSE or "unverifiable" on ALL claims (not just some)
- The claims involve events from the past 1-2 months
- The model says things like "this project doesn't exist" or "the date is in the future"
- You have corroborating evidence (user knowledge, web search results) that contradicts the model
- Software rebrands, new releases, or recent announcements are involved

## Solution

### Step 1: Recognize the Pattern

If a fact-checking model flags ALL claims as false, especially with language like:
- "No evidence exists"
- "The date is in the future"
- "This project/repo doesn't exist"
- "Likely fabricated/hallucinated"

**This is a training cutoff signal, not a factual assessment.** The model literally cannot
see events past its training data.

### Step 2: Use Gemini with Google Search Grounding

Gemini's API supports a `google_search` tool that gives it real-time web access. This
makes it reliable for verifying recent events.

```python
import requests

resp = requests.post(
    f'https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}',
    headers={'Content-Type': 'application/json'},
    json={
        'contents': [{'parts': [{'text': 'Your fact-checking prompt here'}]}],
        'generationConfig': {'temperature': 0},
        'tools': [{'google_search': {}}]  # THIS IS THE KEY — enables real-time search
    },
    timeout=60
)
data = resp.json()
for part in data['candidates'][0]['content']['parts']:
    if 'text' in part:
        print(part['text'])
```

**Critical detail:** The `'tools': [{'google_search': {}}]` parameter is what enables
grounding. Without it, Gemini also relies on training data only.

### Step 3: Use Grok with search_mode (if available)

Grok's API supports a `search_mode` parameter for web search:

```python
resp = requests.post('https://api.x.ai/v1/chat/completions',
    headers={
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {XAI_API_KEY}'
    },
    json={
        'model': 'grok-3',
        'search_mode': 'auto',  # Enables web search when needed
        'messages': [
            {'role': 'system', 'content': 'Fact-checker with web search.'},
            {'role': 'user', 'content': 'Your prompt'}
        ],
        'temperature': 0
    },
    timeout=60
)
```

**Note:** Even with `search_mode: 'auto'`, Grok may still fail to find very recent events
(within days). Gemini with Google Search grounding is more reliable for bleeding-edge facts.

### Step 4: Interpret Conflicting Results

| Grok Says | Gemini (grounded) Says | Interpretation |
|-----------|----------------------|----------------|
| ALL FALSE | ALL TRUE | Training cutoff — trust Gemini |
| MIXED | MIXED | Genuine uncertainty — investigate further |
| ALL TRUE | ALL TRUE | High confidence — facts are solid |
| ALL TRUE | ALL FALSE | Possible hallucination — investigate further |
| ALL FALSE | ALL FALSE | Facts are likely wrong |

**Rule of thumb:** When Grok says "doesn't exist" but Gemini with grounding confirms with
specific details (URLs, dates, names), trust Gemini. The grounding gives it access to real
search results.

### Step 5: Always Note the Limitation

When reporting results to the user, be transparent:
- State which model said what
- Explain the training cutoff as a possible cause
- Let the user decide how to proceed

## Verification

The approach is verified when:
1. Gemini's grounded response includes specific, checkable details (repo URLs, dates, package names)
2. Those details are internally consistent
3. The user can independently verify at least one claim (e.g., visit a URL, check npm)

## Example

**Scenario:** Verifying if "OpenClaw" (formerly Moltbot) exists as a software project,
rebrand announced Jan 29, 2026.

- **Grok-3 (with search_mode):** "No evidence exists. Project appears fabricated. The date
  Jan 29, 2026 is in the future."
- **Gemini 2.5 Flash (with google_search):** "Yes, confirmed. GitHub at
  github.com/openclaw/openclaw, npm package `openclaw`, rebrand on Jan 29, 2026. Created
  by Peter Steinberger."

**Result:** Grok's training cutoff predates Jan 29, 2026. Gemini's Google Search grounding
accessed real web results. OpenClaw is real.

## Notes

- **GrokVetting script** (`~/.claude/skills/GrokVettingSkill/scripts/grok_vet.py`) uses the
  Grok API without `search_mode`. For recent-event vetting, prefer direct API calls with
  search enabled, or use Gemini as a secondary check.
- **Gemini model selection:** `gemini-2.5-flash` is fast and cheap for fact-checking.
  Use `gemini-2.5-pro` only if flash gives ambiguous results.
- **Cost:** Gemini with grounding is slightly more expensive due to search queries, but
  for fact-checking it's worth it.
- **False confidence warning:** Both models can still hallucinate. Gemini grounding reduces
  but doesn't eliminate this risk. If a claim is critical, verify manually.
- **Environment:** Use `formal` conda env for Python requests:
  `/Users/praveentiwari/opt/anaconda3/envs/formal/bin/python`

## References

- [Gemini API - Grounding with Google Search](https://ai.google.dev/gemini-api/docs/grounding)
- [xAI Grok API Documentation](https://docs.x.ai/docs/guides/search)
