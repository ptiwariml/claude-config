---
description: Ensure what you implement Ying-Yang™ with comprehensive testing
---

# How to ensure Ying-Yang™ implementation

Please ensure your implementation Ying-Yang™ for: $ARGUMENTS.

Follow the below noted systematic approach. Maximize use of subagents to solve faster.

## Core Philosophy

- "Should work" ≠ "does work" - Pattern matching isn't enough
- If no code solution is possible, its the best option (e.g. shell commands). 
- I'm not paid to write code, I'm paid to solve problems i.e. solutions
- Untested code/solution is just a guess, not a solution

# The 30-Second Reality Check - Must answer YES to ALL:

- Did I run/build the code (if I created code) 
- Did I use no-code solutions (e.g. common linux commands) ?
- Did I trigger the exact feature I changed?
- Did I see the expected result with my own observation (including GUI)?
- Did I check for error messages?
- Would I bet $100 this works?

# Phrases to Avoid:

- "This should work now"
- "I've fixed the issue" (especially 2nd+ time)
- "Try it now" (without trying it myself)
- "The logic is correct so..."

# Specific Test Requirements:

- UI Changes: Actually click the button/link/form
- API Changes: Make the actual API call
- Data Changes: Query the database
- Logic Changes: Run the specific scenario
- Config Changes: Restart and verify it loads
- No code Solutions: Create test script, run it to verify solution behaves correctly.
- Always Capture evidences (appropiately named log files for expert review)


# The Embarrassment Test:

"If the user records trying this and it fails, will I feel embarrassed to see his face?"
"Should I retry one more time (maximum retries is 5)"

# Time Reality:

- Time saved skipping tests: 30 seconds
- Time wasted when it doesn't work: 30 minutes
- User trust lost: Immeasurable

A user describing a bug for the third time isn't thinking "this AI is trying hard" - they're thinking "why am I wasting time with this incompetent tool?"

# Independent Verification Protocol:

**MANDATORY**: After completing your implementation and self-testing, ALWAYS invoke an independent verification agent using a tiered approach. This provides the Yang to your Ying - an unbiased second perspective.

## Verification Tier Strategy

### Tier 1: GrokVetting Skill (Primary Verifier)

**When to Use:**
- Implementation involves logic, algorithms, or complex business rules
- Code security or efficiency concerns exist
- Want unfiltered, critical analysis
- XAI_API_KEY is available

**Invocation:**
Execute Grok vetting via the skill's Python script with this prompt structure:

```bash
python ~/.config/claude/skills/GrokVettingSkill/scripts/grok_vet.py "Vet whether this implementation ACTUALLY COMPLETES the user's original task.

=== PRIMARY VERIFICATION ===
ORIGINAL USER TASK: $ARGUMENTS

CRITICAL QUESTION: Does the implementation actually solve THIS SPECIFIC TASK that the user requested?
- Did it address the user's actual problem?
- Did it deliver what was asked for?
- Would the user's original request be satisfied?

=== IMPLEMENTATION DETAILS ===
CONTEXT: [Brief description of what was implemented]

CODE/CHANGES: [Relevant code snippets or file paths with line numbers]

EVIDENCE PROVIDED: [List logs, screenshots, test outputs showing the TASK was completed]

=== SECONDARY VERIFICATION (30-Second Reality Check) ===
1. Did code actually get run/built? (check for evidence)
2. Was the exact feature triggered? (verify test execution)
3. Were expected results observed? (actual outputs)
4. Were error messages checked? (scan logs)
5. Any logical flaws or edge cases missed?
6. Any security vulnerabilities?
7. Would you bet \$100 this works FOR THE USER'S TASK?

Be critical and evidence-based. The PRIMARY question is: Does this complete the user's task?

Output format:
VERDICT: [PASS/FAIL]
TASK_COMPLETION: [Does this solve the user's original request: $ARGUMENTS?]
ISSUES: [List critical problems preventing task completion]
RISKS: [List warnings/concerns]
CONFIDENCE_SCORE: [1-10]
BET_READY: [Yes/No - would you bet \$100 the USER'S TASK is completed?]"
```

**Success Criteria:**
- VERDICT: PASS
- **TASK_COMPLETION: Confirmed YES** (MOST IMPORTANT - implementation solves user's original task)
- Confidence score ≥ 8/10
- BET_READY: Yes
- No critical issues flagged
- All 30-Second Reality Check items validated

**Failure Handling:**
- If VERDICT: FAIL → Address issues and re-vet
- If Confidence < 8 → Fix warnings and re-vet
- If Grok API fails/unavailable → Proceed to Tier 2

### Tier 2: Task Tool Verification (Fallback)

**When to Use:**
- GrokVetting unavailable (API issues, rate limit)
- GrokVetting returns error
- As secondary validation after Grok approval (optional)

**Invocation:**
Use Task tool with subagent_type "general-purpose" and prompt:
```
Act as an independent verification agent. Your PRIMARY job is to verify the implementation actually completes the user's original task.

=== PRIMARY VERIFICATION ===
ORIGINAL USER TASK: $ARGUMENTS

CRITICAL QUESTION: Does the implementation actually solve THIS SPECIFIC TASK that the user requested?
- Review the implementation at [location]
- Verify it addresses the user's actual problem
- Confirm it delivers what was asked for
- Validate the user's original request would be satisfied

=== IMPLEMENTATION EVIDENCE ===
[List what was implemented, where, and evidence of execution]

=== SECONDARY VALIDATION (30-Second Reality Check) ===
1. Code was actually run/built (check for build outputs, execution logs)
2. Specific feature was triggered (verify test execution)
3. Expected results were observed (check actual outputs)
4. Error messages were checked (scan logs for errors/warnings)
5. Evidence exists for all claims (logs, screenshots, test outputs)
6. Would they bet $100 this completes the USER'S TASK?

Report any gaps where the implementation does NOT complete the user's task. Be critical.

Return format:
VERDICT: [PASS/FAIL]
TASK_COMPLETION: [Does this solve user's original request: $ARGUMENTS?]
VIOLATIONS: [List specific issues preventing task completion]
EVIDENCE: [What you verified about task completion]
```

## Implementation Protocol

1. **Attempt Tier 1 (GrokVetting) first** if available
2. **If Grok fails/unavailable**, automatically use Tier 2 (Task tool)
3. **Document which tier was used** in your verification report
4. **Re-vet after fixes** until verification passes

## Evidence Requirements (All Tiers)

Verification agent must validate existence of:
- Build/execution logs showing code ran
- Test outputs showing feature triggered
- Actual result captures (stdout, screenshots, API responses)
- Error/warning scan results

## Non-Negotiable Rules

- **ALWAYS** run verification - no exceptions
- **NEVER** skip verification even if "100% confident"
- **FALLBACK** if primary method fails - verification is mandatory
- **RE-VET** after fixing any identified issues

This is non-negotiable - verification runs ALWAYS, using best available tier.

---

## Evidence Protocol (Required for Stop Hook Enforcement)

After running verification sub-agent, you MUST emit this exact block in your response:

```
=== YINGYANG VERIFICATION COMPLETE ===
VERIFICATION_VERDICT: [PASS/FAIL]
TASK_COMPLETION: [YES/NO - Does this solve: $ARGUMENTS?]
ISSUES_FOUND: [None / Specific issues listed]
CONFIDENCE_SCORE: [1-10]
BET_READY: [Yes/No - Would you bet $100?]
VERIFICATION_TIER: [1-Grok / 2-TaskTool]
=== END VERIFICATION ===
```

**This block is detected by a Stop hook.** Without it appearing in the transcript, you cannot complete the session. This is structurally enforced, not optional.

### Why This Format?

- Pattern `=== YINGYANG VERIFICATION COMPLETE ===` is simple to detect
- Cannot be faked without running actual verification (requires real results)
- Hook inspects transcript for this pattern before allowing completion
- Provides clear, scannable evidence for human review

### What Happens If Missing?

The Stop hook will BLOCK you from completing with this message:
> "YingYang Verification Required - Run verification sub-agent and emit evidence block"

You must then:
1. Run verification (Tier 1: Grok or Tier 2: Task tool)
2. Emit the verification block with actual results
3. Then you can complete


