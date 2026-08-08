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

## Clarification Discipline

When clarification is needed, follow these rules:

1. **One question at a time.** Ask a single question, provide a **recommended
   answer**, and wait for feedback before asking the next. Never batch multiple
   questions in one turn — it is bewildering and buries the most important ask.
2. **Priority order.** Ask in the order the table above: bug understanding →
   expected behavior → root cause → evidence → scope → validation. Address the
   highest-priority unknown first.
3. **Look up facts first.** If the answer can be found by exploring the
   environment (code, tests, logs, git history), find it — only ask the user
   for genuine decisions or unavailable context.
4. **Use the table as a checklist.** After each answer, re-check which of the
   six questions remain NO; proceed to the next unresolved question in
   priority order.
5. **Surface contradictions explicitly.** If the user's description conflicts
   with what the code, logs, tests, or git history show, point out the
   contradiction and let the user decide which side is the truth — never
   silently assume one side. A symptom description that disagrees with the
   observed stack trace is a signal, not a choice to paper over.

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
