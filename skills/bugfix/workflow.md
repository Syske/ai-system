# Workflow

## Stage 1: Observe

**Goal:** Capture the initial symptom without interpretation.

**Steps:**

1.1 Record the exact error message or incorrect behavior verbatim.

1.2 Capture the environment: input data, system state, test case, configuration.

1.3 Determine if the bug is reproducible:
- If reproducible, document the exact reproduction steps
- If not reproducible, document the circumstances (time, data, load)

**Output:** `{symptom, environment, reproducible: true|false}`

---

## Stage 2: Collect Evidence

**Goal:** Gather all available data about the defect.

**Steps:**

2.1 If exception/stack trace: capture the full trace. Identify the first
line in application code (not framework/library code).

2.2 If test failure: capture the full test output, including expected vs
actual values.

2.3 If compilation error: capture the full error with file, line, and symbol.

2.4 If log message: capture surrounding log context (10 lines before/after).

2.4a Log analysis discipline (when investigating from logs):
- Detect the log format first (plain-text / JSON / structured) before parsing.
- Redact PII/secrets before quoting logs in the report.
- Distinguish the **first error** from the **root cause** — they are usually
  different; trace upstream to the originating component.
- Separate noise from signal with a rough count/time-window: N identical
  errors in 1 hour vs 1 hour apart are different signals.
- Correlate across services using `trace_id` / `request_id` when logs span
  multiple components.
- End with a prioritised list of hypotheses + which evidence supports each.

2.5 Run `git diff` and `git log --oneline -10` to check recent changes.

2.6 Check if the bug was introduced by a specific commit:
```
git log --all --full-history -- <affected-file>
git blame <affected-file> -L<line>,+10
```

2.7 Reproducibility discipline: can the bug be triggered reliably? If it
cannot be reproduced consistently, do not guess a fix — gather more data
(extra logging, more context, ask the user for exact reproduction steps)
until it is reproducible or the cause is otherwise proven.

**Evidence sufficiency check (from `decision.md`):**
- Is there a stack trace pointing to application code? → Sufficient
- Is there a failing test with expected/actual? → Sufficient
- Is there a compilation error with file+line? → Sufficient
- Is there only a user description? → Ask for reproduction steps

**Output:** `{evidenceType, detail, sufficiency: sufficient|insufficient}`

---

## Stage 3: Understand Expected Behavior

**Goal:** Determine what should happen.

**Steps:**

3.1 Check if the behavior is defined by:
- A unit test (the test's expected value is the specification)
- A specification document or API contract
- A previous working version (git checkout to verify)
- An obvious correctness rule (null check, bounds check)

3.2 If the expected behavior cannot be determined from any source, ask the
user to clarify — **one question at a time**, highest-priority first, each
with a recommended answer (see Clarification Discipline in `decision.md`).
Never batch multiple questions in one turn.

**Output:** `{expectedBehavior, source: test|spec|git|obvious|askUser}`

---

## Stage 4: Understand Actual Behavior

**Goal:** Determine what actually happens.

**Steps:**

4.1 Trace the execution path that produces the incorrect result.

4.2 If available, use the stack trace to map the execution path.

4.3 If no stack trace, identify the code path through logic analysis.

4.4 For conditional bugs, determine which branch was taken.

**Output:** `{actualBehavior, executionPath: [file:line...]}`

---

## Stage 5: Compare Differences

**Goal:** Identify the exact divergence between expected and actual.

**Steps:**

5.1 Pinpoint the first line where expected and actual behavior diverge.

5.2 Determine the type of divergence:

| Divergence type | Signal |
|---|---|
| Wrong value | Return/response has incorrect value |
| Wrong type | Return type mismatch |
| Missing call | Expected call didn't happen |
| Extra call | Unexpected call happened |
| Wrong path | Wrong conditional branch taken |
| Missing check | Guard clause absent |
| Wrong state | Object/DB in wrong state |

**Output:** `{divergencePoint: file:line, divergenceType, expectedValue, actualValue}`

---

## Stage 6: Identify Affected Code

**Goal:** Determine all code locations related to the divergence.

**Steps:**

6.1 Identify the direct location (where the divergence occurs).

6.2 Trace backward to find the code that produced the incorrect value or state.

6.3 Identify all callers and data sources involved.

6.4 Use `analysis.md` to map the dependency chain if needed.

**Output:** `{directLocation, contributingLocations[], dataSources[]}`

---

## Stage 7: Generate Hypotheses

**Goal:** Form hypotheses about the root cause without jumping to conclusions.

**Steps:**

7.1 Generate at least 2 hypotheses (never stop at 1).

7.2 For each hypothesis, predict what evidence would confirm or refute it.

| Hypothesis | Would confirm | Would refute |
|---|---|---|
| Null value passed | Stack trace shows NPE at line | Value is never null |
| Wrong conditional branch | Condition evaluates opposite | Log shows correct condition |
| Missing edge case | Input falls outside handled range | Input is within range |
| Stale cached value | Cache not invalidated | Cache returns fresh value |
| Incorrect mock behavior | Mock returns wrong value | Mock is not involved |

7.3 Rank hypotheses by likelihood (based on evidence, not guessing).

**Output:** `{hypotheses: [{explanation, confirmEvidence, refuteEvidence, rank}]}`

---

## Stage 8: Validate Hypotheses

**Goal:** Eliminate impossible hypotheses, confirm the likely one.

**Steps:**

8.1 For each hypothesis, test using the cheapest available validation:

| Validation method | Cost | When to use |
|---|---|---|
| Read code logic | Free | Always — validate against source |
| Add log/trace | Low | Complex conditionals |
| Write isolated test | Medium | When logic is non-obvious |
| Run existing test | Low | When test covers the path |
| Check git blame | Free | When change history exists |

8.2 Eliminate hypotheses that fail validation.

8.3 If all hypotheses fail, return to Stage 7 (generate new hypotheses).

**Output:** `{validatedHypothesis, eliminatedHypotheses[]}`

---

## Stage 9: Identify Root Cause

**Goal:** Identify the exact root cause with evidence.

**Steps:**

9.1 Map the root cause to a specific file and line.

9.2 Determine the root cause category:

| Category | Example |
|---|---|
| Logic error | Wrong operator, missing condition |
| Null/empty handling | Missing null check, empty collection not handled |
| Boundary condition | Off-by-one, edge case not covered |
| State management | Cache not invalidated, stale reference |
| Concurrency | Race condition, deadlock, thread safety |
| Configuration | Wrong property, missing config |
| API misuse | Wrong method called, wrong arguments |
| Dependency | Wrong version, missing dependency, API change |

9.3 Verify the root cause by tracing from cause to symptom:
```
Root cause → intermediate effect → immediate cause → symptom
```

**Output:** `{rootCause: {file, line, category, explanation}, verificationPath: []}`

---

## Stage 10: Design Smallest Repair

**Goal:** Design the minimal change that fixes the root cause.

**Steps:**

10.1 Define the repair in terms of changes:

| Change type | Examples |
|---|---|
| Add | null check, guard clause, boundary validation, configuration |
| Modify | operator, conditional expression, variable assignment |
| Remove | dead code, redundant check, incorrect guard |
| Move | statement to correct block, reorder operations |

10.2 Check if the repair introduces any side effects.

10.3 Check if the repair needs other Skills:
- Needs compilation? → Mark for build-backend invocation:
  `build.backend=idea` (environments config) → `idea-build` skill;
  otherwise (default) → `java-maven` skill
- Needs test fixture update? → Mark for `mock-test` invocation
- Needs code review? → Mark for `review` invocation

**Output:** `{repairPlan: {changeType, file, line, oldCode, newCode}, sideEffects, skillDeps}`

---

## Stage 11: Implement Repair

**Goal:** Apply the repair with minimal scope.

**Steps:**

11.1 Apply the single change designed in Stage 10.

11.2 Do NOT make any additional changes. No refactoring, no formatting,
no unrelated fixes.

11.3 If compilation needed, invoke the configured build skill with smallest
    scope: `idea-build` (when `build.backend=idea`) or `java-maven` (default).

11.4 If test fixtures need updating, invoke `mock-test` with context.

**Output:** Applied change. Compilation result (if applicable).

---

## Stage 12: Validate Fix

**Goal:** Verify the repair resolves the bug.

**Steps:**

12.1 Run the test or reproduction case that demonstrated the bug.

12.2 If compilation needed, use `java-maven`:
```
mvn -pl <mod> -am test -Dtest=AffectedTest
```

12.3 If the fix passes, proceed to Stage 13.

12.4 If the fix fails, return to Stage 9 (root cause analysis may be wrong):

```
Validate failed → Hypothesis wrong?
  ├─ Yes → Return to Stage 7 (new hypotheses)
  └─ No  → Return to Stage 10 (fix was wrong) → redesign repair
```

**Output:** `{validationResult: pass|fail, evidence}`

---

## Stage 13: Check Regressions

**Goal:** Ensure the repair doesn't break existing functionality.

**Steps:**

13.1 Run all tests in the affected module:
```
mvn -pl <mod> -am test
```

13.2 Run all tests in modules that depend on the affected module:
```
mvn -pl <mod> -amd test
```

13.3 If any test fails, determine:
- Is the failure caused by my change? → Return to Stage 10 (redesign)
- Is the failure pre-existing? → Document, proceed

**Output:** `{regressionResult: clean|regression, details}`

---

## Stage 14: Finish

**Goal:** Document the fix and report completion.

**Steps:**

14.1 Summarize the fix:

```
Root cause: <category> at <file:line>
Repair:     <change type> — <one line description>
Evidence:   <how root cause was determined>
Validation: <which test confirms the fix>
Scope:      <files changed>
```

14.2 Report completion to the user.

**Output:** Completion report.
