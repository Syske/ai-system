---
name: memory-capture
description: Capture verified engineering experience from the current session into Coding Memory. Use at session end, after a significant debugging/fix/refactor, or when the user says "记一下" / "record this" / "capture a lesson". Follows MEMORY_GUIDELINES; drives the knowledge workflow collect/update operations.
---

# Memory Capture

## Purpose

Turn verified session experience into Coding Memory entries per
`governance/memory/MEMORY_GUIDELINES.md`. Memory is an experience
repository — NOT rules, NOT task state, NOT reports.

## When to Use

- Session end (after handoff summary, see `handoff` skill)
- After a difficult debugging / fix / refactor with a verified lesson
- User explicitly asks to record ("记一下", "record this", "capture a lesson")
- After a release or retrospective (knowledge workflow `collect` trigger)

## What Qualifies (must meet ALL)

| Criterion | Explanation |
|---|---|
| **Verified** | Root cause proven + solution confirmed working (not hypothesis) |
| **Reusable** | Would help a future session; not a one-off |
| **Experience** | A lesson, not a rule (rules → governance/) and not task state (→ handoff) |
| **Non-duplicate** | No existing entry covers it (check index first) |

## What Does NOT Qualify

- Rules / standards → `governance/` (not memory)
- In-progress task state, decisions, todos → `handoff` skill, NOT memory
- One-off incidents without a reusable lesson
- Content duplicating an existing memory entry (update the old one instead)

## Steps

### 1. Screen the session

Scan the session for candidate lessons (debugging findings, root causes,
verified solutions, tricky integration facts). List candidates with a
one-line "lesson" each.

### 2. Check the index (dedupe)

Read `governance/memory/coding-memory.md` (and the scope index, e.g.
`governance/memory/java/coding-memory.md`). For each candidate:

- **Existing entry covers it** → skip, or `update` the existing entry with
  new examples/scope (knowledge workflow `update` operation)
- **New lesson** → `collect` (add new entry)

### 3. Choose the category

`governance/memory/<category>/` — existing: `ai-system/`, `java/`
(reserved: `python/`, `integration/`). Match by domain, not by repo.

### 4. Write the entry

Follow the entry format in **`entry-format.md`** (same directory) — all
sections required except Related; Lesson mandatory; English per
LANGUAGE_CONVENTION.

### 5. Update the index

Append the new entry title to the scope index
(`governance/memory/<category>/coding-memory.md`).

### 6. Report

Summarize: what was captured (or updated / skipped as duplicate), and why.

## Validation

- Lesson field present on every entry (memory.py gate)
- No duplicate Lesson across files (memory.py warns)
- English (memory.py enforces for ai-system scope)
- Index updated to match new entries
- Rules, reports, and in-progress task tracking NOT written into memory (boundary check)
