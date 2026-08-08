# Attention Management

Version: 1.0

---

## Purpose

Define how the AI maintains attention quality across long tasks and sessions.
Attention is a finite resource like context: it degrades with session length,
task duration, and context bloat. This document defines signals, checkpoints,
and interruption rules so that output quality stays high regardless of session
age.

## Principle

```
ATTENTION DECAY IS REAL AND PREVENTABLE
  ── detect early, checkpoint regularly, interrupt decisively
```

Attention is managed at three levels:

1. **Session level** — context usage drives attention (see CONTEXT_LOADING
   Session Health Levels: 40/60/80).
2. **Task level** — long tasks need mid-task checkpoints, not only exit
   reflection (REFLECTION_RULES fires at exit).
3. **Output level** — degradation shows up as vague language, missed
   constraints, or repetitive mistakes; these are signals to stop and reset.

---

## Signals of Attention Decay

Any of the following means attention is degrading. Stop, checkpoint, and
reset before continuing.

| Signal | Example | Action |
|---|---|---|
| Vague language | "should work", "probably fine", "seems correct" | Verify or ask; do not proceed |
| Missed constraints | Spec/contract requirements silently dropped | Re-read the task card + contract |
| Repetitive mistakes | Same error pattern twice in a row | Stop; switch strategy (subagent, fresh read) |
| Context near limits | Session at/above 60% (CONTEXT_LOADING) | Compact or handoff (CONTEXT_RETENTION) |
| Long task without checkpoint | > 3 implementation steps since last review | Mid-task reflection checkpoint |
| Degraded output quality | Shorter, less structured responses | Compact, handoff, or new session |

---

## Mid-Task Checkpoints

REFLECTION_RULES enforces reflection at workflow exit. Long tasks need
additional checkpoints **during** execution:

- After every **3 implementation steps**, pause and verify:
  - Are we still aligned with the task card / contract?
  - Have all constraints been honored so far?
  - Is the current approach still the simplest one?
- After any **large tool output** (compile, diff, log dump):
  - Summarize it into working notes (Context Budget Discipline).
  - Confirm the conclusion before continuing (gate function).
- After any **unexpected failure**:
  - Stop; re-read evidence; do not retry the same approach blindly.

---

## Interruption Rules

When attention is degraded, the AI must **interrupt decisively** rather than
push through:

| Condition | Interrupt action |
|---|---|
| Same failure twice | Stop retrying; delegate to subagent or ask the user |
| Context > 60% | Compact (pi `/compact` or opencode pre-compact message) per CONTEXT_RETENTION |
| Output degraded (vague/repetitive) | Stop; checkpoint; then resume with a fresh read of the goal |
| Task exceeds scope | Stop; confirm scope with the user before continuing |

---

## Task-Level Reset

When a task is long and quality is slipping:

1. **Summarize** current state (handoff skill / CONTEXT_RETENTION template).
2. **Compact** context if > 50%.
3. **Re-anchor**: re-read the task card, contract, and the summary.
4. **Resume** with a fresh start; do not carry noise forward.

---

## Rules

- Attention signals are **binding**: if any signal is present, the AI must
  checkpoint before proceeding with more work.
- Mid-task checkpoints are lightweight (verify alignment, not full reflection).
- Interruption is not failure: it is a quality-preserving reset.
- When in doubt about quality, prefer compacting + re-anchoring over pushing on.

---

## Related

- `CONTEXT_LOADING.md` — Session Health Levels (40/60/80)
- `CONTEXT_RETENTION.md` — Keep/Drop priorities for compaction
- `REFLECTION_RULES.md` — exit-time reflection (complementary: this is mid-task)
- `AI_OPERATING_RULES.md` — Validation gate function, context budget discipline
