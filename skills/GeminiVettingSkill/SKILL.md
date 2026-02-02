---
name: GeminiVettingSkill
description: Use this skill when you need to vet facts, code logic, or decisions with Gemini's reasoning and Google Search grounding. Primary (Tier 1) verifier in the YingYang framework.
trigger_phrases: ["vet with Gemini", "check via Gemini", "Gemini validate", "cross-check reasoning", "verify with Gemini"]
permissions: ["api_call", "external_query"]
---

# GeminiVetting Skill - Independent Verification Gatekeeper (Tier 1)

## Purpose

GeminiVetting is the **primary independent verification agent** that provides unbiased, critical analysis of completed work. It acts as the **Tier 1 gatekeeper** in the YingYang verification flow, ensuring implementations actually accomplish what the user requested.

**Philosophy:** Trust but verify. An independent second opinion catches errors that self-assessment misses.

**Advantage over Grok:** Google Search grounding enables real-time fact verification against live web data, making it especially strong for verifying claims about APIs, libraries, and current best practices.

---

## Role: Primary Independent Gatekeeper (Tier 1)

GeminiVetting serves as **Tier 1 verification** in the YingYang framework:

| Aspect | Description |
|--------|-------------|
| **Independence** | External API (Google Gemini) - not the same model doing the work |
| **Objectivity** | No context of implementation struggles - judges only results |
| **Search Grounded** | Google Search grounding for real-time fact verification |
| **Evidence-based** | Requires concrete proof, not claims |
| **Deterministic** | Temperature 0 for consistent verification results |

---

## Required Inputs

When invoking GeminiVetting, you MUST provide:

### 1. Original User Request
The exact task the user asked for. This is the PRIMARY success criteria.

```
ORIGINAL USER TASK: [Exact user request]
```

### 2. Context
Brief description of what was implemented and how.

```
CONTEXT: [What was built/done]
```

### 3. Final Results / Pointers
Evidence that the task was completed:
- File paths created/modified
- Test outputs
- Screenshots
- Commit hashes
- Any artifacts proving completion

```
EVIDENCE:
- [File/artifact 1]
- [File/artifact 2]
- [Test results]
```

---

## Invocation Template

```bash
python3 ~/.claude/skills/GeminiVettingSkill/scripts/gemini_vet.py "Vet whether this implementation ACTUALLY COMPLETES the user's original task.

=== PRIMARY VERIFICATION ===
ORIGINAL USER TASK: [Exact user request here]

CRITICAL QUESTION: Does the implementation actually solve THIS SPECIFIC TASK?
- Did it address the user's actual problem?
- Did it deliver what was asked for?
- Would the user's original request be satisfied?

=== IMPLEMENTATION DETAILS ===
CONTEXT: [Brief description of what was implemented]

FILES/CHANGES: [List of files, paths, artifacts]

EVIDENCE PROVIDED: [Logs, screenshots, test outputs]

=== SECONDARY VERIFICATION (30-Second Reality Check) ===
1. Did code actually get run/built?
2. Was the exact feature triggered?
3. Were expected results observed?
4. Were error messages checked?
5. Any logical flaws or edge cases missed?
6. Would you bet \$100 this works?

Be critical and evidence-based.

Output format:
VERDICT: [PASS/FAIL]
TASK_COMPLETION: [Does this solve the user's original request?]
ISSUES: [List critical problems]
RISKS: [List warnings/concerns]
CONFIDENCE_SCORE: [1-10]
BET_READY: [Yes/No]"
```

---

## What GeminiVetting Checks

### Correctness
- Does the output match the specification?
- Are there logical errors?
- Do edge cases work?

### Accuracy
- Are facts/data correct? (enhanced by Google Search grounding)
- Are calculations right?
- Do file paths/references exist?

### Completeness
- Was the FULL task addressed?
- Are there missing pieces?
- Would the user be satisfied?

### Quality
- Is the solution robust?
- Are there obvious improvements needed?
- Does it follow best practices?

---

## Expected Output Format

GeminiVetting should return:

```
VERDICT: [PASS/FAIL]
TASK_COMPLETION: [YES/NO - Does this solve the user's original request?]
ISSUES: [List of critical problems preventing task completion]
RISKS: [List of warnings or concerns]
CONFIDENCE_SCORE: [1-10]
BET_READY: [Yes/No - Would you bet $100 this works?]
```

---

## Integration with YingYang

GeminiVetting is **Tier 1** in the YingYang verification hierarchy:

| Tier | Method | When to Use |
|------|--------|-------------|
| **Tier 1** | GeminiVetting (this skill) | Primary - when GEMINI_API_KEY available |
| **Tier 2** | GrokVetting | Fallback - when Gemini unavailable but XAI_API_KEY available |
| **Tier 3** | Task tool subagent | Last resort - when both APIs unavailable |

After verification, emit the YingYang evidence block:

```
=== YINGYANG VERIFICATION COMPLETE ===
VERIFICATION_VERDICT: [PASS/FAIL]
TASK_COMPLETION: [YES/NO]
ISSUES_FOUND: [None / List]
CONFIDENCE_SCORE: [1-10]
BET_READY: [Yes/No]
VERIFICATION_TIER: [1-Gemini / 2-Grok / 3-TaskTool]
=== END VERIFICATION ===
```

---

## Error Handling

| Error | Resolution |
|-------|------------|
| `GEMINI_API_KEY` not set | Fall back to Tier 2 (GrokVetting) |
| API rate limit | Fall back to Tier 2 |
| Network error | Fall back to Tier 2 |
| Timeout | Fall back to Tier 2 |

---

## Configuration

### Environment Variable
```bash
export GEMINI_API_KEY="your-gemini-api-key"
```

### Script Location
```
~/.claude/skills/GeminiVettingSkill/scripts/gemini_vet.py
```

### Model
- `gemini-2.5-flash` - Fast, cost-effective, strong reasoning
- Google Search grounding enabled by default

---

## Examples

### Example 1: Code Implementation
```bash
python3 ~/.claude/skills/GeminiVettingSkill/scripts/gemini_vet.py "
ORIGINAL USER TASK: Add a login button to the navbar

CONTEXT: Added LoginButton component to Navbar.tsx

EVIDENCE:
- src/components/Navbar.tsx modified
- src/components/LoginButton.tsx created
- npm run build passed
- Screenshot shows button in navbar

Does this complete the task? VERDICT?"
```

### Example 2: Documentation Task
```bash
python3 ~/.claude/skills/GeminiVettingSkill/scripts/gemini_vet.py "
ORIGINAL USER TASK: Create feature comparison matrix for Ralph implementations

CONTEXT: Created HTML slides with 10 slides, 7 tables comparing 4 implementations

EVIDENCE:
- slides.html (815 lines)
- 11 screenshots captured via Playwright
- All 4 implementations present with Y/N/L/M/H ratings

Does this complete the task? VERDICT?"
```

---

## Why Independent Verification Matters

> "Should work" != "Does work"

Self-assessment is prone to:
- Confirmation bias
- Overlooking edge cases
- Assuming success without testing
- Missing the actual user intent

GeminiVetting provides the **Yang** to your **Ying** - the verification that balances creation.
