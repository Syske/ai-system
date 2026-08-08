# Anti-Patterns

---

## 1. Editing Before Understanding

**Pattern:** See a compilation error → immediately open the file and start
editing.

**Why it fails:** The fix may be in a different file. The root cause may be
a dependency change, not a code error. Editing without understanding increases
the chance of introducing new bugs.

**Instead:** Follow the workflow: collect evidence, understand, analyze,
then edit.

---

## 2. Multiple Unrelated Changes

**Pattern:** While fixing a bug, also refactor the method, rename variables,
add comments, reformat the file.

**Why it fails:** Each change is a potential source of new bugs. If the fix
introduces a regression, the other changes mask which one caused it.

**Instead:** Change exactly what's needed for the fix. Nothing else.

---

## 3. Guessing the Root Cause

**Pattern:** "This looks like a null pointer, I'll add a null check" without
verifying which variable is null and why.

**Why it fails:** Adding a null check at the wrong location hides the real
issue. The null may come from a different path than expected.

**Instead:** Trace the exact null variable from the stack trace. Verify the
path that produced it.

---

## 4. Ignoring Existing Tests

**Pattern:** Fix the bug, then only verify the symptom is gone — don't run
existing tests.

**Why it fails:** The fix may break assumptions that existing tests verify.
Those tests may catch regressions that manual verification misses.

**Instead:** Always run existing tests in the affected module (Stage 13).

---

## 5. Full Build Without Reason

**Pattern:** Running a full `clean install` build after every fix.

**Why it fails:** Takes 10x longer than incremental build. May introduce
unrelated failures that confuse diagnosis.

**Instead:** Delegate the run to `java-maven` — smallest scope that
exercises the failing test. Expand scope only when necessary.

---

## 6. Refactoring While Fixing

**Pattern:** "I'll clean up this method while I'm here" during a bug fix.

**Why it fails:** Refactoring changes code structure without changing behavior.
If the fix has a bug, the refactoring makes it harder to identify.
Refactoring may also introduce new bugs.

**Instead:** Fix in one commit, refactor in a separate commit (if at all).

---

## 7. Weakening Assertions

**Pattern:** Replace `eq("expected")` with `anyString()` to make a failing
test pass.

**Why it fails:** The test is asserting something important. Weakening the
assertion hides incorrect behavior. The real fix is to update the expected
value or fix the production code.

**Instead:** Fix the root cause. Update the expected value to match
production, or fix production to match the expected value.

---

## 8. Suppressing Exceptions

**Pattern:** Wrap suspicious code in `try-catch(Exception)` and swallow.

**Why it fails:** The exception is a signal that something is wrong.
Swallowing it hides the defect. Users may encounter silent failures.

**Instead:** Handle the exception properly: log, recover, or rethrow with
context.

---

## 9. Ignoring Regression Risks

**Pattern:** Fix passes the failing test → done. Skip dependent module tests.

**Why it fails:** The fix may change a public method that other modules
depend on. Those modules may break silently.

**Instead:** Check dependent modules (Stage 13). At minimum, compile them.

---

## 10. Overcomplicating the Fix

**Pattern:** Instead of a one-line null check, restructure the entire method
to use Optional, streams, and functional interfaces.

**Why it fails:** High risk of introducing new bugs. Harder to review.
Harder to revert if needed.

**Instead:** The simplest fix that addresses the root cause. One line change
is preferred over ten lines of restructuring.
