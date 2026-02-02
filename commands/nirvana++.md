---
description: Response-Aware NIRVANA™ implementation with comprehensive testing
---

# Response-Aware NIRVANA™ Implementation

Please ensure your implementation NIRVANA™ for: $ARGUMENTS using the Response-Awareness paradigm for robust, validated solutions.

## Core Orchestration Principles

**CRITICAL**: The orchestrator (main agent) performs ZERO execution tasks:
- No coding, analysis, or verification
- Only coordination, plan management, and clean state transitions
- All execution delegated to specialized sub-agents
- Plan preservation is paramount throughout all phases

## Response-Aware Workflow

### Phase 1: Research & Planning (Sub-Agents Only)

**Research Agent Tasks:**
- Operate on a task basis and store all intermediate context in markdown files under `tasks/<task-id>/`
- Use semantic slugs for each task id
- Always prefer ast-grep over regular grep for structural code searches
- Investigate existing patterns in this codebase before inventing new approaches
- Search the internet when additional context is relevant
- Start by asking follow-up questions to steer the research direction
- Document findings in `tasks/<task-id>/research.md`
- Tag uncertainties: `#PLAN_UNCERTAINTY:`, `#PATH_DECISION:`

**Planning Agent Tasks:**
- Read the `research.md` snapshot for the active `<task-id>`
- Build a plan that reuses tested patterns, components, and code whenever possible
- Ask the user clarifying questions if the task scope is unclear
- Document the full implementation plan in `plan.md`, including all context another engineer would need
- Export critical decisions: `#EXPORT_CRITICAL:`

### Phase 2: Plan Synthesis

**Plan Synthesis Agent:**
- Merge all domain-specific plans
- Resolve tagged uncertainties with `#PATH_RATIONALE:`
- Validate against NIRVANA™ criteria
- Create unified implementation roadmap

### Phase 3: Implementation (Specialized Sub-Agents)

**Implementation Agents** (Backend, Frontend, etc.):
- Read `plan.md`, translate it into a complete TODO list, and execute against that list
- Push for end-to-end implementation; when questions remain, bundle them at the end and present them together
- Tag assumptions: `#COMPLETION_DRIVE:`, `#CARGO_CULT:`
- Identify missing validation: `#SUGGEST_ERROR_HANDLING:`
- **NEVER** proceed without actual testing per 30-Second Reality Check

**MANDATORY Plan Deviation Protocol:**
- Before ANY deviation from plan.md: Create `tasks/<task-id>/deviation-<N>.md` documenting:
  - Specific plan.md section being violated
  - Why deviation is necessary
  - Proposed alternative approach
  - Risk assessment
- **HALT** implementation and notify orchestrator
- Orchestrator triggers Plan Reconciliation Agent to update plan.md
- Resume implementation ONLY after plan.md updated and re-approved
- Zero undocumented deviations tolerated - plan.md is single source of truth

### Per-Task Verification Protocol

**CRITICAL**: Each task in `tasks/<task-id>/` MUST be verified independently before being marked complete.

**Parallel Execution Rules:**
- Independent tasks MAY be executed in parallel by different implementation agents
- Each task MUST complete its own verification (GeminiVetting or GrokVetting) before being marked complete
- Task status: `pending` → `in_progress` → `implemented` → `vetted` → `complete`
- Only tasks with status `complete` (implementation + vetting passed) can be considered done

**Per-Task Verification Invocation:**

For each completed task implementation in `tasks/<task-id>/`:

**Tier 1: GeminiVetting (Primary)**
```bash
GEMINI_PROMPT="Vet this INDIVIDUAL TASK implementation for completion and correctness.

TASK_ID: <task-id>

=== PRIMARY VERIFICATION: TASK-SPECIFIC REQUIREMENTS ===

STEP 1 - READ AND UNDERSTAND THIS TASK'S REQUIREMENTS:
- tasks/<task-id>/research.md (what THIS task needed to solve)
- tasks/<task-id>/plan.md (what THIS task planned to implement)
- tasks/<task-id>/deviation-*.md (any changes to THIS task's plan)

STEP 2 - CRITICAL QUESTION FOR THIS TASK:
Does the implementation ACTUALLY FULFILL this specific task's requirements?
- Does it solve the problem identified in THIS task's research.md?
- Does it implement what was specified in THIS task's plan.md?
- Is THIS TASK complete and working?

STEP 3 - VERIFY THIS TASK'S IMPLEMENTATION:
- Read implementation files for THIS task only
- Compare against THIS task's requirements
- Test THIS task's functionality independently

=== TASK ISOLATION CHECK ===
- Does this task work in isolation (if independent)?
- Does this task properly integrate with dependencies (if dependent)?
- Are this task's outputs/APIs ready for other tasks to consume?

=== NIRVANA™ CORE PHILOSOPHY (for this task) ===
1. THIS TASK 'does work' not just 'should work'
2. THIS TASK was tested and verified
3. Evidence exists for THIS TASK's completion

OUTPUT FORMAT:
VERDICT: [PASS/FAIL]
TASK_REQUIREMENTS_FULFILLED: [Does this complete THIS task's requirements?]
TASK_READY_FOR_INTEGRATION: [Can other tasks depend on this?]
CONFIDENCE_SCORE: [1-10]
CRITICAL_ISSUES: [Problems with THIS task]
WARNINGS: [Concerns about THIS task]
BET_READY: [Would you bet \$100 THIS TASK is complete?]

Be ruthlessly critical about THIS INDIVIDUAL TASK."

python ~/.claude/skills/GeminiVettingSkill/scripts/gemini_vet.py "$GEMINI_PROMPT"
```

**Tier 2: GrokVetting (Fallback if Gemini unavailable)**

```bash
python ~/.claude/skills/GrokVettingSkill/scripts/grok_vet.py "$GEMINI_PROMPT"
```

**Tier 3: Task Tool Fallback (if both Gemini and Grok unavailable)**
```
Use Task tool with subagent_type "general-purpose" and prompt:

"Act as per-task verification agent for tasks/<task-id>/.

PRIMARY VERIFICATION: Does THIS specific task's implementation fulfill its requirements?

STEP 1 - Read and understand THIS task's requirements:
- tasks/<task-id>/research.md
- tasks/<task-id>/plan.md
- tasks/<task-id>/deviation-*.md

STEP 2 - Verify THIS task's implementation:
- Does it solve what THIS task's research.md identified?
- Does it implement what THIS task's plan.md specified?
- Is THIS task complete and working independently?

OUTPUT:
VERDICT: [PASS/FAIL]
TASK_REQUIREMENTS_FULFILLED: [Yes/No for THIS task]
TASK_READY_FOR_INTEGRATION: [Yes/No]
CONFIDENCE_SCORE: [1-10]
CRITICAL_ISSUES: [List]
"
```

**Task Completion Criteria:**
- Implementation complete for this task
- Verification PASS (Tier 1: Gemini, Tier 2: Grok, or Tier 3: Task tool)
- TASK_REQUIREMENTS_FULFILLED: Yes
- Confidence ≥ 8/10
- Update task status to `complete`
- Create `tasks/<task-id>/vetting-result.md` with verification details

**Orchestrator Tracking:**
- Maintain task status for each `tasks/<task-id>/`
- Track: `{task-id: status, vetting-tier: [Tier1|Tier2], vetting-score: N/10}`
- Only proceed to Phase 4 when ALL tasks reach `complete` status

### Phase 4: Two-Phase Final Verification

**CRITICAL**: Phase 4 consists of TWO INDEPENDENT verification checks that must BOTH pass.

## Phase 4.1: Individual Task Verification Status Check

**Purpose:** Verify ALL individual tasks were completed AND vetted successfully.

**Task Status Verification Agent:**
- Review orchestrator's task tracking log
- For each `tasks/<task-id>/`:
  - Verify status = `complete`
  - Verify `vetting-result.md` exists and shows PASS
  - Verify vetting confidence ≥ 8/10
  - Verify no unresolved critical issues in vetting results
- Check for any tasks marked `implemented` but not `complete` (missing vetting)
- Check for any tasks with vetting FAIL status

**Output Required:**
```
PHASE_4.1_VERDICT: [PASS/FAIL]
ALL_TASKS_VETTED: [Yes/No]
TASK_STATUS_SUMMARY:
  - tasks/task-1/: complete, vetted (Tier1, 9/10)
  - tasks/task-2/: complete, vetted (Tier1, 8/10)
  - tasks/task-3/: complete, vetted (Tier2, 8/10)
INCOMPLETE_TASKS: [List any tasks not fully vetted]
FAILED_TASKS: [List any tasks that failed vetting]
```

**Failure Response:**
- If ANY task not vetted: HALT and complete vetting for that task
- If ANY task vetting FAIL: Return to implementation for that task
- Only proceed to Phase 4.2 when ALL tasks show `complete` with vetting PASS

## Phase 4.2: Overall Solution Integration Verification

**Purpose:** Verify the COMBINED solution fulfills the ORIGINAL user request from $ARGUMENTS.

**This is INDEPENDENT of Phase 4.1** - even if all individual tasks passed vetting, the integrated solution might not fulfill the original request.

**Integration Verification Questions:**
- Do all tasks work together correctly?
- Does the complete solution solve the ORIGINAL user request ($ARGUMENTS)?
- Are there integration gaps between tasks?
- Does the end-to-end workflow actually work?

**Code Review Agent:**
- Validate all implementation assumptions across all tasks
- Resolve or document all tags from prior phases
- Ensure compliance with Core Philosophy for complete solution
- Verify that the integrated implementation meets the overall requirements
- Run integration tests, make tool calls and check outputs
- If there are any issues, return to implementation with specific violation details

**Test Validation Agent:**
- **MANDATORY 30-Second Reality Check** (ALL must be YES):
  - Did I run/build the complete solution?
  - Did I use no-code solutions where possible?
  - Did I trigger the exact end-to-end workflow?
  - Did I see expected result with actual observation?
  - Did I check for error messages?
  - Would I bet $100 the complete solution works?

**Overall Solution Verification Agent (Phase 4.2):**
- **MANDATORY**: Launch specialized verification using tiered approach with GeminiVetting as primary, GrokVetting as secondary, Task tool as last resort
- This agent verifies the INTEGRATED solution fulfills the ORIGINAL user request
- **CRITICAL**: Verification agent independently reads:
  - ORIGINAL user request from $ARGUMENTS or initial research
  - ALL task artifacts from ALL `tasks/<task-id>/` directories:
    - Each task's research.md, plan.md, deviation-*.md
    - Each task's vetting-result.md
  - ALL implementation code files across ALL tasks
  - ALL integration points between tasks
  - End-to-end test results showing complete solution works

### Tier 1: GeminiVetting Skill (Primary Verification)

**Advantages for NIRVANA™:**
- Fresh, unbiased perspective (no implementation context bias)
- Google Search grounding for real-time fact verification
- Deterministic output (temperature 0) for consistent verification
- Fast, cost-effective model (gemini-2.5-flash)

**Invocation:**
```bash
# Construct comprehensive vetting prompt for Gemini
GEMINI_PROMPT="You are performing Phase 4.2 Overall Solution Integration Verification. Your PRIMARY job is to verify the COMPLETE INTEGRATED SOLUTION fulfills the ORIGINAL user request.

**CONTEXT**: Phase 4.1 already verified individual tasks were completed and vetted. Your job is DIFFERENT - verify the INTEGRATED solution works end-to-end.

ORIGINAL_USER_REQUEST: $ARGUMENTS

ALL_TASKS: [List of all task-ids]

=== PRIMARY VERIFICATION: OVERALL SOLUTION FULFILLMENT ===

STEP 1 - UNDERSTAND ORIGINAL REQUEST:
- What did the user originally ask for? (from $ARGUMENTS or initial research)
- What was the complete solution supposed to deliver?

STEP 2 - REVIEW ALL INDIVIDUAL TASKS:
For each tasks/<task-id>/:
- Read research.md, plan.md (what this task was supposed to do)
- Read vetting-result.md (confirmation this task passed individual vetting)
- Note: Individual tasks already passed vetting in Phase 3

STEP 3 - VERIFY INTEGRATION:
- Do all tasks integrate correctly?
- Are there gaps between tasks?
- Does the complete workflow work end-to-end?

STEP 4 - CRITICAL QUESTION (PRIMARY):
Does the COMPLETE INTEGRATED SOLUTION fulfill the ORIGINAL user request?
- NOT: "Do individual tasks work?" (already verified in Phase 3)
- YES: "Does the complete solution solve the user's problem?"
- YES: "Does the end-to-end workflow deliver what was requested?"
- YES: "Would the user's ORIGINAL REQUEST be satisfied by this complete solution?"

=== SECONDARY VERIFICATION: NIRVANA™ CORE PHILOSOPHY ===
1. 'Does work' not just 'should work' - verify actual execution
2. No-code solutions considered first - check for over-engineering
3. Problem-solving focus, not code-writing focus
4. All solutions tested - verify evidence exists
5. No fake/hardcoded data - validate data authenticity

=== TERTIARY VERIFICATION: 30-SECOND REALITY CHECK ===
☐ Complete solution was run/built (check logs/outputs)
☐ No-code solutions used where possible
☐ End-to-end workflow triggered (verify complete execution)
☐ Expected results observed (actual evidence)
☐ Error messages checked (scan for warnings)
☐ Bet \$100 this fulfills the ORIGINAL USER'S REQUEST

=== INTEGRATION-SPECIFIC CHECKS ===
- Do tasks interact correctly at integration points?
- Are there missing pieces between tasks?
- Does the complete workflow execute successfully end-to-end?
- Were integration tests run for the complete solution?

=== META-COGNITIVE TAG VALIDATION ===
- Review all tags across all tasks: #COMPLETION_DRIVE, #CARGO_CULT, #SUGGEST_ERROR_HANDLING
- Verify tag resolution or proper documentation
- Flag any unresolved assumptions

OUTPUT FORMAT:
VERDICT: [PASS/FAIL]
ORIGINAL_REQUEST_FULFILLED: [Does COMPLETE solution fulfill ORIGINAL user request: $ARGUMENTS?]
INDIVIDUAL_TASKS_STATUS: [Confirmed all tasks passed vetting in Phase 3]
INTEGRATION_STATUS: [Do tasks integrate correctly?]
END_TO_END_WORKS: [Does complete solution work end-to-end?]
REQUESTED_VS_DELIVERED: [What user originally requested vs what complete solution delivers]
CONFIDENCE_SCORE: [1-10]
CRITICAL_ISSUES: [Problems with INTEGRATED solution or missing pieces]
INTEGRATION_GAPS: [Missing connections between tasks]
EVIDENCE_QUALITY: [End-to-end test results, integration test results]
REASONING: [Why this verdict - focus on OVERALL solution fulfillment]
BET_READY: [Would you bet \$100 the COMPLETE SOLUTION fulfills the ORIGINAL request?]

Be ruthlessly critical. The PRIMARY question is: Does the complete integrated solution fulfill the original user request?"

# Execute Gemini vetting
python ~/.claude/skills/GeminiVettingSkill/scripts/gemini_vet.py "$GEMINI_PROMPT"
```

**Success Criteria for Phase 4.2 PASS:**
- **Phase 4.1 MUST be PASS first** (all individual tasks vetted)
- VERDICT: PASS
- **ORIGINAL_REQUEST_FULFILLED: Confirmed YES** (MOST IMPORTANT - complete solution fulfills original user request)
- **INTEGRATION_STATUS: Working** (tasks integrate correctly)
- **END_TO_END_WORKS: Yes** (complete solution tested end-to-end)
- Confidence score ≥ 8/10
- BET_READY: Yes
- No critical issues or integration gaps
- Evidence of end-to-end testing exists

**Failure Response:**
- If VERDICT: FAIL → Return to implementation with specific violations
- If Confidence < 8 → Address warnings and re-vet
- If Gemini API error → Proceed to Tier 2 (GrokVetting)

### Tier 2: GrokVetting Skill (Fallback Verification)

**When to Use:**
- GeminiVetting unavailable (API issues)
- Gemini API failures (rate limit, network issues, service down)
- XAI_API_KEY is available
- As secondary validation after Gemini PASS (optional dual verification)
- GeminiVetting returns ambiguous results

**Invocation:**
```bash
python ~/.claude/skills/GrokVettingSkill/scripts/grok_vet.py "$GEMINI_PROMPT"
```

**Failure Response:**
- If Grok also fails → Proceed to Tier 3 (Task tool)

### Tier 3: Task Tool Verification (Last Resort)

**When to Use:**
- Both GeminiVetting and GrokVetting unavailable
- All API keys missing or rate limited
- As tertiary validation (optional)

**Invocation:**
- Launch verification sub-agent using Task tool with subagent_type: "general-purpose"
- Use the **Verification Agent Prompt Template (Tier 2 Fallback)** (see below)
- **CRITICAL**: Verification agent's PRIMARY job is to verify requirements from research.md and plan.md are fulfilled
- Verification agent MUST independently read research.md and plan.md to understand what was requested
- Verification agent generates OWN verification checklist from artifacts
- Orchestrator provides ONLY: task-id and file paths
- Zero contextual interpretation from orchestrator allowed
- Verifier must independently reconstruct requirements and validate implementation fulfills them
- Agent must validate implementation against the Core Philosophy checklist
- Agent performs actual testing and verification of all implemented features
- Agent validates compliance with the 30-Second Reality Check criteria

**Final Requirements (All Tiers):**
- **CRITICAL**: Only proceed if verification agent provides explicit approval
- If verification fails, return to implementation step with specific violation details
- Once verification agent approves, update the task status to "verified"
- Independent validation against complete requirements
- Remove resolved tags, document remaining risks
- Apply Embarrassment Test: "If user records this failing, would I be embarrassed?"

## Meta-Cognitive Tag Lifecycle

### Planning Phase Tags:
- `#PATH_DECISION:` Multiple valid approaches identified
- `#PLAN_UNCERTAINTY:` Assumptions needing validation
- `#EXPORT_CRITICAL:` Key decisions for next phase

### Implementation Phase Tags:
- `#COMPLETION_DRIVE:` Any coding assumptions or guesses
- `#CARGO_CULT:` Pattern-driven code without verification
- `#SUGGEST_ERROR_HANDLING:` Missing validation paths identified

### Verification Phase Tags:
- `#VERIFICATION_PASS:` Tag confirmed and resolved
- `#VERIFICATION_FAIL:` Tag requires remediation
- `#ARCHITECTURAL_RISK:` Known limitation documented

## Core Philosophy (Preserved Across All Agents)

- "Should work" ≠ "does work" - Pattern matching isn't enough
- If no code solution is possible, its the best option (e.g. shell commands).
- Focus on solving problems, not writing code
- Untested code/solution is just a guess, not a solution
- No fake or hardcoded data providing semblance of functionality

## The 30-Second Reality Check - Must answer YES to ALL:

- Did I run/build the code (if I created code)
- Did I use no-code solutions (e.g. common linux commands) ?
- Did I trigger the exact feature I changed?
- Did I see the expected result with my own observation (including GUI)?
- Did I check for error messages?
- Would I bet $100 this works?

## Phrases to Avoid:

- "This should work now"
- "I've fixed the issue" (especially 2nd+ time)
- "Try it now" (without trying it myself)
- "The logic is correct so..."

## Specific Test Requirements (Per Agent Type)

**UI Implementation Agents**: Actually click buttons/links/forms
**API Implementation Agents**: Make actual API calls
**Data Implementation Agents**: Query the database
**Logic Implementation Agents**: Run specific scenarios
**Config Implementation Agents**: Restart and verify loading
**No-code Solution Agents**: Create test script, run it to verify solution behaves correctly
**All Agents**: Always capture evidence (appropriately named log files for expert review)

## The Embarrassment Test:

"If the user records trying this and it fails, will I feel embarrassed to see his face?"
"Should I retry one more time (maximum retries is 5)"

## Time Reality:

- Time saved skipping tests: 30 seconds
- Time wasted when it doesn't work: 30 minutes
- User trust lost: Immeasurable

A user describing a bug for the third time isn't thinking "this AI is trying hard" - they're thinking "why am I wasting time with this incompetent tool?"

## Sub-Agent Coordination Protocol

Each sub-agent receives:
- Current task/phase clearly stated
- Only relevant tags and context from prior phases
- Phase-specific meta-cognitive tags to apply
- NIRVANA™ validation criteria for their domain

## Finalization Requirements

**No Tag Left Behind**: Every tag must be:
- Resolved and documented
- Promoted to architectural decision
- Or declared as known risk

**Evidence Capture**: All agents must provide appropriately named log files for expert review

## Model Assignment Strategy

- **Planning/Synthesis**: Highest reasoning model (Claude Opus, "ultra_think")
- **Implementation**: Balanced model (Claude Sonnet, "think_hard")
- **Verification**: Efficient, robust (Sonnet "think")

## Orchestrator Verification Checklist

Before declaring success, orchestrator validates:

**Phase 3 Completion:**
- All tasks in tasks/*/ have status = `complete`
- Each task has vetting-result.md with PASS verdict
- Each task vetting confidence ≥ 8/10
- No tasks have FAIL vetting status

**Phase 4.1 Completion:**
- Task Status Verification Agent confirmed ALL_TASKS_VETTED: Yes
- No incomplete or failed tasks
- PHASE_4.1_VERDICT: PASS

**Phase 4.2 Completion:**
- Overall Solution Verification Agent confirmed:
  - ORIGINAL_REQUEST_FULFILLED: Yes
  - INTEGRATION_STATUS: Working
  - END_TO_END_WORKS: Yes
  - VERDICT: PASS
  - Confidence ≥ 8/10

**Only when ALL three gates pass:**
- Phase 3: All individual tasks complete and vetted ✓
- Phase 4.1: Task status verification PASS ✓
- Phase 4.2: Overall solution integration PASS ✓

Then and ONLY then: Declare success

**Additional Requirements:**
- All tags resolved or documented
- Evidence artifacts created for all test scenarios
- User trust preservation: "Am I solving their problem or wasting their time?"

**On Verification FAIL Protocol:**
- Orchestrator MUST trigger Root Cause Analysis Agent with:
  - All FAIL verdicts and violation history
  - Original research.md and plan.md
  - Deviation logs (if any)
- RCA Agent outputs: `tasks/<task-id>/rca-iteration-<N>.md` with:
  - Root cause classification (flawed plan / incomplete research / wrong approach)
  - Whether current plan.md is salvageable or needs complete redesign
- If 3 consecutive FAILs with same root cause → MANDATORY:
  - Archive current plan.md as plan-failed-<N>.md
  - Return to Phase 1 with explicit constraint: "Previous approach failed because: [root cause]"
  - User notification: "Current approach exhausted, pivoting strategy"
- Maximum 5 iterations total before user escalation: "I need your guidance on: [blocker]"
- No infinite retry loops - each FAIL requires RCA before next attempt

## Verification Agent Prompt Template (Tier 2 Fallback)

When launching the verification sub-agent via Task tool (Tier 2 fallback), use this exact prompt structure:

```
You are an independent verification agent (Tier 2 fallback). Your PRIMARY job is to verify the implementation ACTUALLY FULFILLS the specific requirements documented in research.md and plan.md.

**NOTE**: You are running as fallback verification since GeminiVetting (Tier 1) and GrokVetting (Tier 2) were unavailable. Apply extra thoroughness.

TASK_ID: [task-id]
ARTIFACT_PATHS:
- tasks/<task-id>/research.md
- tasks/<task-id>/plan.md
- tasks/<task-id>/deviation-*.md
- [implementation file paths]

=== PRIMARY VERIFICATION: REQUIREMENTS FULFILLMENT ===

STEP 1 - UNDERSTAND ORIGINAL REQUEST:
1. What did the user originally ask for? (from $ARGUMENTS or initial research)
2. What was the complete solution supposed to deliver?

STEP 2 - REVIEW ALL INDIVIDUAL TASKS:
For each tasks/<task-id>/:
1. Read research.md, plan.md (what this task was supposed to do)
2. Read vetting-result.md (confirmation this task passed individual vetting)
3. Note: Individual tasks already passed vetting in Phase 3

STEP 3 - VERIFY INTEGRATION:
1. Read all implementation files across all tasks
2. Do all tasks integrate correctly?
3. Are there gaps between tasks?
4. Does the complete workflow work end-to-end?

STEP 4 - CRITICAL QUESTION (PRIMARY):
Does the COMPLETE INTEGRATED SOLUTION fulfill the ORIGINAL user request?
- NOT: "Do individual tasks work?" (already verified in Phase 3)
- YES: "Does the complete solution solve the user's problem?"
- YES: "Does the end-to-end workflow deliver what was requested?"

STEP 5 - GENERATE YOUR OWN INTEGRATION CHECKLIST:
Based on the original request and all tasks, create a checklist of what MUST be verified to confirm the complete solution fulfills the request.

MANDATORY VALIDATION CHECKLIST:

1. **Core Philosophy Compliance**:
   - Verify "does work" not just "should work"
   - Confirm no-code solutions were considered first
   - Validate focus on solving problems, not just writing code
   - Ensure all code/solutions are actually tested
   - Ensure no fake or hardcoded data that provides semblance of functionality but isnt real

2. **30-Second Reality Check** (ALL must be YES):
   - Did they run/build the code (if code was created)?
   - Did they use no-code solutions where possible?
   - Did they trigger the exact feature they changed?
   - Did they see the expected result with actual observation?
   - Did they check for error messages?
   - Would they bet $100 this works?

3. **Specific Test Requirements**:
   - UI Changes: Actually clicked buttons/links/forms
   - API Changes: Made actual API calls
   - Data Changes: Queried the database
   - Logic Changes: Ran specific scenarios
   - Config Changes: Restarted and verified loading
   - No-code Solutions: Created test script and verified behavior
   - Evidence captured (appropriately named log files)

4. **Tag Resolution Validation**:
   - All meta-cognitive tags from implementation addressed
   - No unresolved #COMPLETION_DRIVE or #CARGO_CULT tags
   - All #SUGGEST_ERROR_HANDLING items implemented or documented

5. **Embarrassment Test**:
   - If user records trying this and it fails, would implementer feel embarrassed?

INSTRUCTIONS:
- Test the implementation yourself using available tools
- Validate all tags have been properly resolved
- Provide PASS/FAIL verdict with specific violations
- If FAIL, list exact steps needed to achieve compliance
- Only approve if you would personally stake your reputation on it working

**ADDITIONAL FALLBACK VERIFICATION**:
Since primary GrokVetting was unavailable, apply extra scrutiny:
- Double-check all evidence files exist and contain real data
- Verify no assumptions were "pattern-matched" without testing
- Confirm no cargo-cult programming (copying without understanding)
- Validate error handling is comprehensive, not just happy-path

Return your assessment in this format:
VERDICT: [PASS/FAIL]
ORIGINAL_REQUEST_FULFILLED: [Does COMPLETE solution fulfill ORIGINAL user request: $ARGUMENTS?]
INDIVIDUAL_TASKS_STATUS: [Confirmed all tasks passed vetting in Phase 3]
INTEGRATION_STATUS: [Do tasks integrate correctly?]
END_TO_END_WORKS: [Does complete solution work end-to-end?]
REQUESTED_VS_DELIVERED: [What user originally requested vs what complete solution delivers]
VIOLATIONS: [List specific issues preventing overall solution fulfillment or integration gaps]
TAG_STATUS: [Status of all meta-cognitive tags across all tasks]
EVIDENCE: [What you tested about end-to-end integration]
CONFIDENCE: [Why you believe the complete solution fulfills the original request]
FALLBACK_NOTES: [Any concerns due to primary verification unavailability]
```


