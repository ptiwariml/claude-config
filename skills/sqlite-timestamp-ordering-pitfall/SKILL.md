---
name: sqlite-timestamp-ordering-pitfall
description: |
  Fix nondeterministic ORDER BY results when using SQLite datetime('now') as sort key.
  Use when: (1) tests intermittently fail on ordering assertions with SQLite,
  (2) multiple rows inserted in rapid succession have identical timestamps,
  (3) ORDER BY created_at DESC returns rows in wrong order within same second.
  Solution: always add autoincrement id as secondary sort key.
author: Claude Code
version: 1.0.0
date: 2026-02-01
---

# SQLite Timestamp Ordering Pitfall

## Problem
When multiple rows are inserted into SQLite within the same second, `datetime('now')` produces
identical timestamps. Using `ORDER BY created_at DESC` alone results in nondeterministic row
ordering, causing intermittent test failures and incorrect "most recent" queries.

## Context / Trigger Conditions
- SQLite table with `DEFAULT (datetime('now'))` timestamp column
- Multiple inserts in rapid succession (batch operations, tests, loops)
- Queries using `ORDER BY created_at DESC` to get "most recent first"
- Tests that assert on ordering (e.g., "most recent entry should be first")
- Symptom: tests pass sometimes, fail sometimes, depending on SQLite's internal ordering

## Solution

Always include the autoincrement `id` as a secondary sort key:

```sql
-- BAD: nondeterministic when timestamps match
SELECT * FROM strategies ORDER BY created_at DESC LIMIT 3;

-- GOOD: deterministic even with identical timestamps
SELECT * FROM strategies ORDER BY created_at DESC, id DESC LIMIT 3;
```

Apply this to all queries that need consistent ordering, including:
- `find_similar()` or "get latest" queries
- `list_all()` or paginated listing queries
- Any query where the caller expects a specific order

Also apply to index definitions:
```sql
CREATE INDEX idx_task_sig ON strategies(task_signature, success, created_at DESC);
-- Consider adding id to the index if performance matters
```

## Verification
Insert 3+ rows in a tight loop (no sleep between inserts), then query with ORDER BY.
The results should consistently return rows in insertion order (newest first).

## Example
```python
# This test would intermittently fail without the fix:
for i in range(3):
    store.save(Strategy(task_signature="test", approach=f"approach_{i}", ...))

results = store.find_similar("test", limit=2)
assert results[0].approach == "approach_2"  # Most recently inserted
```

## Notes
- This affects any database where the timestamp column has second-level granularity
- PostgreSQL `now()` also has this issue within a transaction (returns same value)
- Alternative: use `strftime('%Y-%m-%d %H:%M:%f', 'now')` for millisecond precision
  (but this doesn't fully solve it for sub-millisecond inserts)
- The `ROWID` / autoincrement `id` is always strictly monotonic in SQLite, making it
  the reliable tiebreaker
