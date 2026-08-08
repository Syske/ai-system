# Decision Rules

---

## Before-Editing Questions

| Question | Must be answered before editing |
|---|---|
| Do we understand the bug? | Can we describe the exact symptom, input, and expected output? |
| Do we understand expected behavior? | Is the correct behavior defined by a test, spec, or logic? |
| Do we know the root cause? | Can we point to the exact file and line? |
| Is evidence sufficient? | Can we prove the root cause with a stack trace, test, or log? |
| Can scope be reduced? | Is this the smallest possible fix for this root cause? |
| How will we validate? | Which test or verification confirms the fix? |

**If any answer is NO → do not edit. Return to analysis.**

---

## Stage Decisions

| Stage | Decision | Action |
|---|---|---|
| 2 — Evidence | Insufficient evidence? | Ask user for reproduction steps or more context |
| 5 — Compare | Divergence found? | Proceed to Stage 6. Not found? → Stage 2 (more evidence) |
| 7 — Hypotheses | Only 1 hypothesis? | Generate at least 1 more (confirmation bias guard) |
| 8 — Validate | All hypotheses eliminated? | Return to Stage 2. No hypotheses left? → Ask user |
| 9 — Root cause | Can trace cause → effect? | Proceed. Cannot trace? → Return to Stage 7 |
| 10 — Repair | Repair has side effects? | Check if side effects need additional changes |
| 12 — Validate | Fix passes? | Proceed to Stage 13. Fails? → Return to Stage 9 |
| 13 — Regress | Regression found? | Related to change? → Return to Stage 10. Unrelated? → Document |

---

## Skill Invocation Decisions

| Situation | Action |
|---|---|
| Fix needs compilation | Invoke build skill per config: `idea-build` if `build.backend=idea`, else `java-maven`, smallest scope |
| Fix needs test fixture update | Invoke `mock-test` with change context |
| Fix is complete, needs review | Recommend invoking `review` |
| Fix involves spec change | Recommend invoking `spec` |
| Complex root cause | None — handle within this Skill's analysis |

---

## Stopping Conditions

| Condition | Action |
|---|---|
| Root cause cannot be determined | Stop, report "Unable to determine root cause" |
| Fix introduces new bug | Stop, revert, return to Stage 10 |
| Validation fails 3 consecutive times | Stop, report unresolved |
| Regression cannot be avoided | Stop, document trade-off |
| User cancels | Stop |
| Fix verified, no regressions | Stop, report completion |
