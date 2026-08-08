# Failure Diagnosis

Diagnose test failures deterministically. Each entry follows:
symptom → root cause → fix priority → safest fix → retry scope.

---

## ArgumentsAreDifferent

**Symptom:** `Argument(s) are different! Wanted: foo("x"), Actual: foo("y")`

**Root causes:**
- Production now passes a different argument value
- Production computes the argument differently (new variable, new expression)

**Fix priority:**
1. Check if the production value changed intentionally → update expected value
2. Check if the test input changed → align test data with production scenario
3. Never replace `eq("y")` with `anyString()` without verifying fixture

**Safest fix:** Update matcher in both `when()` and `verify()` to match new production value.

**Retry scope:** Delegate to java-maven: run the single test method

---

## WantedButNotInvoked

**Symptom:** `Wanted but not invoked: mock.method() — zero interactions`

**Root causes:**
1. Production removed the call → remove `verify()`
2. Production made the call conditional → update test input to trigger condition
3. Production replaced `method()` with `newMethod()` → update verify target
4. Production moved the call to a different service → verify the new service

**Fix priority:**
1. Check git diff — was the call removed, wrapped in condition, or replaced?
2. Trace the production code path for the affected method
3. Determine which of the 4 scenarios applies

**Safest fix:** Based on scenario. Never add `verifyNoMoreInteractions()` as workaround.

**Retry scope:** Delegate to java-maven: run the single test method

---

## TooManyActualInvocations

**Symptom:** `Wanted 1 time, but was 2 times`

**Root causes:**
1. Production now calls the method in a loop
2. Production calls the method from an additional code path
3. An event listener fires twice

**Fix priority:**
1. Check if the extra call is intentional → update `times(n)`
2. Check if the extra call is a bug → keep verify as-is (test catches the bug)
3. Use `InOrder` if call sequence matters across multiple verifications

**Safest fix:** Update `times(n)` to match new call count, or use `atLeast(n)`.

**Retry scope:** Delegate to java-maven: run the single test method

---

## UnnecessaryStubbingException

**Symptom:** `Unnecessary stubbings detected in test class`

**Root causes:**
1. Production removed the call → remove stubbing
2. Production made the call conditional → `lenient()` + comment
3. Test exercises a different code path → move stubbing to specific test

**Fix priority:**
1. Check git diff — was the production call removed?
2. If removed → delete `when()` block entirely
3. If conditional → wrap in `lenient()` with explanatory comment

**Safest fix:** Delete orphaned stubbings. Only use `lenient()` when the stubbing
is genuinely optional (called from setup but not by every test method).

**Retry scope:** Delegate to java-maven: run the single test class

---

## PotentialStubbingProblem

**Symptom:** `Strict stubbing argument mismatch: stubbed with "a", invoked with "b"`

**Root causes:**
- Test stubs method with specific argument (`eq("a")`)
- Different test path invokes the same method with different argument (`"b"`)
- This triggers Mockito 3+ strict mode

**Fix priority:**
1. Check if the stubbed value matters for the test → use `anyString()` if not
2. Check if the test should cover both scenarios → split into separate tests
3. Never add `lenient()` blindly — understand the mismatch first

**Safest fix:** Use broader matcher (`anyString()` → `eq("a")`) or split test.

**Retry scope:** Delegate to java-maven: run the single test class

---

## NullPointerException

**Symptom:** `NullPointerException at XxxService.java:42`

**Root causes:**
1. New `@Value` field not initialized → `ReflectionTestUtils.setField()`
2. New `@Autowired` field not mocked → add `@Mock` + injection
3. New constructor parameter not provided → update constructor call
4. `Environment.getProperty()` returns null → mock Environment

**Fix priority:**
1. Check the NPE line number in production code
2. Identify the null field/parameter from the stack trace
3. Use `fixture.md` to find the correct initialization mechanism

**Safest fix:** Initialize the null field using the appropriate mechanism
(constructor → add mock; `@Value` → `ReflectionTestUtils`; Spring → `@MockBean`).

**Retry scope:** Delegate to java-maven: run the single test class

---

## AssertionError (AssertJ / Hamcrest)

**Symptom:** `expected: "x" but was: "y"`

**Root causes:**
1. Production logic changed (new computation, different output)
2. Mock return value changed (different stub data)
3. Test fixture input changed
4. Production return type changed (e.g., `List` → `Set`)

**Fix priority:**
1. Check if the production return value changed → update expected value
2. Check if the mock stub changed → update stub and assertion together
3. Check if return type changed → update assertion style

**Safest fix:** Update the expected value to match production. Never remove
the assertion — that deletes the test, it doesn't fix it.

**Retry scope:** Delegate to java-maven: run the single test method

---

## Spring Context Failure

**Symptom:** `Failed to load ApplicationContext`

**Root causes:**
1. New bean dependency needs `@MockBean`
2. New configuration property needs `@TestPropertySource`
3. Bean constructor changed — Spring cannot auto-wire
4. Circular dependency introduced
5. Profile-specific bean not available

**Fix priority:**
1. Check the nested exception message for the specific failure
2. Check for missing `@MockBean` annotations
3. Check for missing `@TestPropertySource` properties

**Safest fix:** Add missing `@MockBean` or `@TestPropertySource` entries.
If circular dependency, check production code design.

**Retry scope:** Single test class via java-maven
