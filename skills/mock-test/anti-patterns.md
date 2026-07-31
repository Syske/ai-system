# Anti-Patterns

---

## 1. Blind Matcher Relaxation

**Pattern:** Replace `eq("x")` with `anyString()` when `ArgumentsAreDifferent` appears.

**Why it fails:** Weakens the test. The test no longer verifies what argument
production passes. The real issue is usually a changed test input or production
value — fix that instead.

**Instead:** Update the expected value to match the actual production call.

---

## 2. Disabling Assertions

**Pattern:** Comment out `assertThat(...)` or `Assert.assertEquals(...)` lines
when a test fails.

**Why it fails:** Removes test coverage silently. The assertion exists for a
reason — it verifies a behavior that changed.

**Instead:** Update the expected value. If the test logic changed, rewrite the
assertion to cover the new behavior.

---

## 3. Weakening Verification

**Pattern:** Replace `verify(mock, times(1))` with `verify(mock, never())` when
a production call is removed.

**Why it fails:** `never()` verifies the method is NOT called — but the real
issue is that the method used to be called and isn't anymore. If the call was
removed intentionally, remove the entire `verify()` block.

**Instead:** Remove `verify()` entirely, or update to verify the new behavior.

---

## 4. Lenient() as First Fix

**Pattern:** Add `Mockito.lenient()` to suppress `UnnecessaryStubbingException`
without investigating why the stubbing is unused.

**Why it fails:** Masks real drift between production and test. A stubbing that
is never called means the production path that used it has changed.

**Instead:** Check if the production call was removed (delete stubbing) or made
conditional (use `lenient()` only then, with a comment).

---

## 5. Ignoring Production Changes

**Pattern:** Only look at the test file, not the production diff.

**Why it fails:** The root cause is always in the production change. A
test-only view leads to symptom-fixing instead of root-cause fixing.

**Instead:** Always start with `git diff src/main/java/`. Understand the
production change first, then fix the test.

---

## 6. Running Every Test

**Pattern:** `mvn clean test` or `mvn test` without specifying the affected test.

**Why it fails:** Takes 10x longer. Masks which tests are actually affected.
May introduce unrelated failures that confuse diagnosis.

**Instead:** `mvn test -Dtest=AffectedTest` — smallest possible scope.
Expand only after the affected test passes.

---

## 7. Duplicate Fixture Initialization

**Pattern:** The same `ReflectionTestUtils.setField()` or mock setup appears
in every test method instead of in `@BeforeEach`.

**Why it fails:** 10 test methods = 10 copies of the same initialization.
Changes require editing every test method.

**Instead:** Extract shared initialization to `@BeforeEach`. Keep per-test
customization in individual test methods.

---

## 8. Skipping Validation

**Pattern:** Apply all Stage 4-7 fixes at once, then run tests, without
checking priority order.

**Why it fails:** A fixture error gets masked by a matcher relaxation.
The test passes but the underlying issue is hidden.

**Instead:** Use Stage 8 (Validate) to check every fix against the priority
rules. Fix in order: sync → fixture → mock → verify → relax.
