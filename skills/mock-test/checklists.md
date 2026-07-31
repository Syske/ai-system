# Checklists

---

## Dependency Checklist

Use during Stage 4 (fixture changes).

- [ ] All new constructor params have matching `@Mock` fields
- [ ] All new `@Autowired` / `@Resource` / `@Inject` fields have mocks
- [ ] All new `@Value` fields initialized via `ReflectionTestUtils.setField()`
- [ ] All removed dependency mocks cleaned up (no other test uses them)
- [ ] `@InjectMocks` handles constructor injection correctly
- [ ] Manual construction calls updated with new params
- [ ] Builder/factory methods updated
- [ ] `@MockBean` / `@SpyBean` added for new Spring beans

---

## Configuration Checklist

Use during Stage 5 (configuration changes).

- [ ] Every `@Value("${...}")` field has an initialization
- [ ] Every `@ConfigurationProperties` prefix has test properties
- [ ] `Environment.getProperty()` calls have mock responses
- [ ] MQ topic/queue constants are consistent with production
- [ ] Redis key prefix constants are consistent
- [ ] Cache name constants are consistent
- [ ] HTTP URL constants are consistent

---

## Mockito Checklist

Use during Stage 6 (mock changes).

- [ ] Stubbed methods exist in current production code
- [ ] Stubbed method return types match production
- [ ] Stubbed method parameter types match production
- [ ] Removed methods have their stubbings removed
- [ ] Renamed methods have updated stubbing targets
- [ ] Void/nonvoid transitions handled correctly
- [ ] Matchers are the narrowest safe choice
- [ ] No `lenient()` used without justification comment

---

## Verification Checklist

Use during Stage 7 (verification changes).

- [ ] Verified methods exist in current production code
- [ ] `times(n)` matches production call count
- [ ] `never()` used for methods not called in this path
- [ ] `InOrder` blocks match production call order
- [ ] `timeout(n)` matches production timing
- [ ] `ArgumentCaptor` generic types match production parameter types
- [ ] No orphaned `verify()` blocks for removed methods

---

## Failure Diagnosis Checklist

Use during Stage 9 (when tests fail after fix).

| Exception | Check this first |
|---|---|
| `ArgumentsAreDifferent` | Did the production argument change? |
| `WantedButNotInvoked` | Was the production call removed or conditional? |
| `TooManyActualInvocations` | Was a loop added? A new call site? |
| `UnnecessaryStubbingException` | Was the production call removed? |
| `PotentialStubbingProblem` | Do different test paths use different args? |
| `NullPointerException` | Which field/param is null (from stack trace)? |
| `AssertionError` | Did production logic or return type change? |
| `Spring context failure` | Is a `@MockBean` or `@TestPropertySource` missing? |

---

## Validation Checklist

Use during Stage 8 (validate before applying).

- [ ] Rule 1 pass: production-test structure synchronized
- [ ] Rule 2 pass: fixtures correct (no null `@Value`, all mocks exist)
- [ ] Rule 3 pass: mocks updated to match production signatures
- [ ] Rule 4 pass: verifications updated to match production calls
- [ ] Rule 5 only if 1-4 confirmed: matcher relaxation justified
- [ ] No fix violates priority order

---

## Retry Checklist

Use during Stage 9 (incremental retry).

- [ ] First blocking issue identified
- [ ] Single fix applied (not a batch)
- [ ] Smallest test scope: `-Dtest=TestClass#testMethod`
- [ ] If passes: expand scope to full test class
- [ ] If fails: diagnose, apply targeted fix, retry
- [ ] Cycle limit: max 3 retries
