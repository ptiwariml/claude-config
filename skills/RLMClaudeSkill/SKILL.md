---
name: RLMClaudeSkill
description: Delegate complex reasoning tasks to RLM-Claude's recursive decomposition engine. Use when a single LLM pass isn't enough — multi-step analysis, code execution, and iterative self-correction across up to 20 reasoning iterations.
trigger_phrases: ["deep analysis", "recursive reasoning", "RLM analyze", "think harder", "decompose this", "use RLM"]
permissions: ["api_call", "external_query"]
---

# RLMClaudeSkill — Recursive Reasoning Delegator

## Purpose

Delegate hard problems to RLM-Claude, a recursive language model that decomposes complex tasks across multiple iterations with code execution and self-correction. This is your **deep thinking backend** — use it when a single LLM pass would give a shallow or unreliable answer.

**How it works:** RLM-Claude recursively breaks down a problem, executes code in a sandbox to verify intermediate results, and iterates up to 20 times before producing a final answer. It also learns from past decomposition strategies via SQLite memory.

---

## When to Use

| Use This Skill | Don't Use This Skill |
|---------------|---------------------|
| Complex multi-step analysis | Simple factual questions |
| Problems requiring code execution to verify | Opinion or creative writing |
| Tasks where a single LLM pass gives weak results | Quick lookups or definitions |
| Mathematical/logical reasoning chains | Conversational responses |
| Data analysis with computation | File operations or refactoring |

**Cost awareness:** The RLM route uses 130-165K tokens per complex query. Direct route uses ~500 tokens. The auto-router picks the right one, but forcing `--route rlm` should be deliberate.

---

## Prerequisites

**Option A: Server running (faster)**
```bash
cd ~/work/projects/rlm-claude
conda activate formal
source ~/keys.fish
python scripts/serve.py
# Server at http://localhost:8000
```

**Option B: No server needed (automatic fallback)**
- Just needs `ANTHROPIC_API_KEY` in environment
- Script imports RLM-Claude directly

The skill uses **Option C hybrid**: checks if server is up, uses HTTP if yes, falls back to direct import if no.

---

## Invocation

### Basic — RLM by default (full recursive decomposition + REPL execution)
```bash
python3 ~/.claude/skills/RLMClaudeSkill/scripts/rlm_query.py "Analyze the time complexity of this algorithm and prove it formally: [code here]"
```

### Override to direct route — only for trivial queries
```bash
python3 ~/.claude/skills/RLMClaudeSkill/scripts/rlm_query.py --route direct "What is the capital of France?"
```

### JSON output — for structured parsing
```bash
python3 ~/.claude/skills/RLMClaudeSkill/scripts/rlm_query.py --json "What are the trade-offs between B-trees and LSM-trees for write-heavy workloads?"
```

### Custom server URL
```bash
python3 ~/.claude/skills/RLMClaudeSkill/scripts/rlm_query.py --server http://localhost:9000 "query"
```

---

## CLI Reference

```
python3 rlm_query.py [OPTIONS] PROMPT

Positional:
  PROMPT                    The prompt to send to RLM-Claude

Options:
  --route {direct,structured,rlm}   Route to use (default: rlm)
  --server URL              Server URL (default: http://localhost:8000)
  --timeout SECONDS         Request timeout (default: 300)
  --json                    Output as JSON
  --api-key KEY             Anthropic API key (default: from env)
  --dry-run                 Show config without executing
```

---

## Output Format

### Text mode (default)
```
=== RLM-Claude Response (via http) ===
Route: rlm
Iterations: 12
Tokens: 145000
Time: 87.3s

[The detailed response here]
```

### JSON mode (`--json`)
```json
{
  "response": "...",
  "route_used": "rlm",
  "iterations": 12,
  "tokens_used": 145000,
  "execution_time": 87.3,
  "via": "http",
  "strategy_hint": null,
  "termination_reason": null
}
```

---

## Routes

| Route | When | Tokens | Time |
|-------|------|--------|------|
| **direct** | Simple prompts | ~500 | ~2s |
| **structured** | CSV/tabular data | ~800 | ~3s |
| **rlm** | Complex analysis | 130-165K | 30-140s |
| **auto** (default) | Classifier picks based on 10 semantic patterns | varies | varies |

---

## Architecture

```
Claude Code (you) ──── rlm_query.py ───┬── HTTP ──→ RLM-Claude server (localhost:8000)
                                       │              └── FastAPI → RLMClaude → Anthropic SDK
                                       │
                                       └── Direct ─→ import RLMClaude → Anthropic SDK
                                                      (fallback if server is down)
```

The RLM-Claude project lives at `~/work/projects/rlm-claude/` and remains fully standalone. This skill is a thin client wrapper — it never modifies the RLM project.

---

## Environment Variables

```bash
ANTHROPIC_API_KEY=...   # Required (for direct mode or by the server)
GEMINI_API_KEY=...      # Optional (enables Layer 4 verification in RLM-Claude)
```

---

## Error Handling

| Error | Cause | Resolution |
|-------|-------|------------|
| Server down + no API key | Neither path works | Set `ANTHROPIC_API_KEY` or start server |
| HTTP timeout | RLM route taking too long | Increase `--timeout` or use `--route direct` |
| Import error on direct fallback | RLM-Claude not installed at expected path | Check `~/work/projects/rlm-claude/` exists |

---

## Examples

### Delegate complex analysis
```bash
python3 ~/.claude/skills/RLMClaudeSkill/scripts/rlm_query.py --route rlm "Given this codebase structure, identify all potential race conditions and prove whether each is exploitable: [paste code]"
```

### Quick classification check
```bash
python3 ~/.claude/skills/RLMClaudeSkill/scripts/rlm_query.py --route direct "Summarize the key points of this paragraph: [text]"
```

### Parse result programmatically
```bash
python3 ~/.claude/skills/RLMClaudeSkill/scripts/rlm_query.py --json "Analyze X" | jq '.response'
```
