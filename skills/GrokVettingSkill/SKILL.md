---
name: GrokVettingSkill
description: Use this skill when you need to vet facts, code logic, or decisions with Grok's real-time reasoning and unfiltered analysis. Invoke for cross-validation to reduce errors.
trigger_phrases: ["vet with Grok", "check via Grok", "Grok validate", "cross-check reasoning"]
permissions: ["api_call", "external_query"]
---

# GrokVetting Skill - Independent Verification Gatekeeper (Tier 2 Fallback)

## Purpose

GrokVetting is an **independent verification agent** that provides unbiased, critical analysis of completed work. It acts as the **Tier 2 fallback gatekeeper** in the YingYang verification flow when GeminiVetting (Tier 1) is unavailable.

**Note:** GeminiVettingSkill is now the primary (Tier 1) verifier. GrokVetting serves as the fallback when the Gemini API is unavailable.

**Philosophy:** Trust but verify. An independent second opinion catches errors that self-assessment misses.

---

## Role: Fallback Independent Gatekeeper (Tier 2)

GrokVetting serves as **Tier 2 verification** (fallback) in the YingYang framework:

| Aspect | Description |
|--------|-------------|
| **Independence** | External API (xAI Grok) - not the same model doing the work |
| **Objectivity** | No context of implementation struggles - judges only results |
| **Unfiltered** | Grok provides direct, unvarnished feedback |
| **Evidence-based** | Requires concrete proof, not claims |

---

## Required Inputs

When invoking GrokVetting, you MUST provide:

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
python3 ~/.claude/skills/GrokVettingSkill/scripts/grok_vet.py "Vet whether this implementation ACTUALLY COMPLETES the user's original task.

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

## What GrokVetting Checks

### Correctness
- Does the output match the specification?
- Are there logical errors?
- Do edge cases work?

### Accuracy
- Are facts/data correct?
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

GrokVetting should return:

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

GrokVetting is **Tier 2** in the YingYang verification hierarchy:

| Tier | Method | When to Use |
|------|--------|-------------|
| **Tier 1** | GeminiVetting | Primary - when GEMINI_API_KEY available |
| **Tier 2** | GrokVetting (this skill) | Fallback - when Gemini unavailable but XAI_API_KEY available |
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
| `XAI_API_KEY` not set | Fall back to Tier 3 (Task tool) |
| API rate limit | Fall back to Tier 3 |
| Network error | Fall back to Tier 3 |
| Timeout | Fall back to Tier 3 |

---

## Configuration

### Environment Variable
```bash
export XAI_API_KEY="your-xai-api-key"
```

### Script Location
```
~/.claude/skills/GrokVettingSkill/scripts/grok_vet.py
```

---

## Examples

### Example 1: Code Implementation
```bash
python3 ~/.claude/skills/GrokVettingSkill/scripts/grok_vet.py "
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
python3 ~/.claude/skills/GrokVettingSkill/scripts/grok_vet.py "
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

> "Should work" ≠ "Does work"

Self-assessment is prone to:
- Confirmation bias
- Overlooking edge cases
- Assuming success without testing
- Missing the actual user intent

GrokVetting provides the **Yang** to your **Ying** - the verification that balances creation.
