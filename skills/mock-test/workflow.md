# Workflow

## Stage 1: Observe

**Goal:** Capture the production code change.

**Steps:**

1.1 Run `git diff --name-only src/main/java/`. If the list is empty, stop and
report: "No production changes detected — this Skill only maintains sync."

1.2 Run `git diff src/main/java/` for detailed per-file changes.

1.3 Categorize each changed file by change type:

| Change type | Signal |
|---|---|
| Constructor | `public ClassName(` line added/changed |
| Field injection | `@Autowired`, `@Resource`, `@Inject`, `@Value` added/removed |
| Method signature | Return type, parameters, throws clause changed |
| External call | `xxxClient.send()`, `xxxTemplate.exchange()` changed |
| Configuration | `@ConfigurationProperties`, `@Value("${...}")` changed |
| MQ destination | Topic/queue string literal changed |
| Cache annotation | `@Cacheable`, `@CacheEvict` key changed |
| Transaction | `@Transactional` attributes changed |

**Output:** `[{file, changeType, detail}]`

---

## Stage 2: Analyze Production Changes

**Goal:** Extract structured change deltas for each category.

**Steps:**

2.1 For each file with constructor changes, extract the parameter delta:

```
Before: XxxService(A a, B b)
After:  XxxService(A a, B b, D d)
Delta:  +D d (new parameter)
```

2.2 For each file with field injection changes, extract the field delta:

```
Before: @Value("${old.key}") String oldField
After:  @Value("${new.key}") String newField
Delta:  -oldField, +newField
```

2.3 For each file with method signature changes, extract the method delta:

```
Before: void process(int id)
After:  String process(int id, String name)
Delta:  +String return, +String name param
```

2.4 For each file with external call changes, extract the call delta:

```
Before: client.send(msg)
After:  client.sendAsync(msg)
Delta:  send → sendAsync
```

**Output:** `{constructorDeltas[], fieldDeltas[], methodDeltas[], callDeltas[]}`

---

## Stage 3: Determine Affected Tests

**Goal:** Map each production change to its corresponding test(s).

**Steps:**

3.1 For each changed file, derive the test file:

| Production file | Test file |
|---|---|
| `src/main/java/com/x/Y.java` | `src/test/java/com/x/YTest.java` |
| `src/main/java/com/x/Y.java` | `src/test/java/com/x/YIT.java` |
| `src/main/java/com/x/Y.java` | `src/test/java/com/x/YTest.java` + any `@Nested` class |

3.2 If the standard path doesn't exist, search `src/test/java/` for files
importing the changed class.

3.3 If the changed class is used as a Spring bean, also check for Spring
Boot test slices: `@WebMvcTest(Y.class)`, `@DataJpaTest`, `@SpringBootTest`.

3.4 Discard candidates with confidence below 70% (heuristic: match on both
package and class name, or explicit import statement).

**Output:** `[{testFile, productionFile, confidence}]`

---

## Stage 4: Determine Fixture Changes

**Goal:** Identify every fixture that must be updated.

**Steps:**

4.1 For each constructor delta, compute the fixture delta:

```
Constructor added parameter D d:
  → test needs @Mock D d (if @InjectMocks used)
  → test needs new XxxService(a, b, mockD) (if manual construction)
```

4.2 For each field injection delta, compute the fixture delta:

```
Field added @Value("${x}") String x:
  → test needs ReflectionTestUtils.setField(service, "x", "test-x")
Field added @Autowired D d:
  → test needs @Mock D d + ReflectionTestUtils.setField(service, "d", mockD)
```

4.3 For each removed dependency, check if the mock can be removed (verify no
other test method references it).

4.4 For Spring Boot test slices, compute `@MockBean` / `@SpyBean` deltas.

**Output:** `[{testFile, action, fixture, detail}]`

See `fixture.md` for detailed fixture synchronization rules.

---

## Stage 5: Determine Configuration Changes

**Goal:** Identify every new configuration value that tests must provide.

**Steps:**

5.1 Scan the production diff for configuration sources:

| Source | Test impact |
|---|---|
| `@Value("${key}")` | Must set via `ReflectionTestUtils` or `@TestPropertySource` |
| `@ConfigurationProperties` | Must provide properties in test context |
| `Environment.getProperty("key")` | Must mock `Environment` |
| Kafka/RocketMQ topic constant | Must use same constant or mock |
| Redis key prefix | Must use same prefix or mock |
| HTTP base URL | Must mock `RestTemplate` or provide test URL |

5.2 For each configuration value, determine:

- Is there a default? (`@Value("${key:default}")`) → safe if default works
- Is it injected via constructor or field? → determine fixture mechanism
- Can it be set via `@TestPropertySource`? → for Spring Boot tests

5.3 **Never** allow null configuration in tests. If a `@Value` field has no
default, the test **must** initialize it.

**Output:** `[{testFile, configKey, mechanism, value}]`

---

## Stage 6: Determine Mock Changes

**Goal:** Identify every stubbing block that must be updated.

**Steps:**

6.1 For each method signature change, check every `when()` and `doReturn()`
/ `doThrow()` / `doAnswer()` block in the test:

```java
// Production changed: void foo(int a) → String foo(int a, int b)
// Test had:
when(dependency.foo(anyInt())).thenReturn(null);  // void → void mock
// Now needs:
when(dependency.foo(anyInt(), anyString())).thenReturn("result");
```

6.2 For each removed method, remove associated stubbing.

6.3 For each renamed method, update stubbing target.

6.4 For void-to-nonvoid transitions: replace `doReturn(x).when(m).method()`
with `when(m.method()).thenReturn(x)`.

6.5 For nonvoid-to-void transitions: replace `when(m.method()).thenReturn(x)`
with `doNothing().when(m).method()` or remove stubbing.

**Output:** `[{testFile, mockField, oldStubbing, newStubbing}]`

See `mockito.md` for matcher selection rules and stubbing patterns.

---

## Stage 7: Determine Verification Changes

**Goal:** Identify every `verify()` block that must be updated.

**Steps:**

7.1 For each method signature change, check every `verify()` block:

```java
// Production changed: foo(int) → foo(int, String)
// verify(mock).foo(anyInt());
// Now needs:
verify(mock).foo(anyInt(), anyString());
```

7.2 For each removed call, remove associated `verify()`.

7.3 For each call count change, update `times(n)`.

7.4 For call order changes, update `InOrder` blocks.

7.5 For async changes, update `timeout(n)`.

**Output:** `[{testFile, mockField, oldVerify, newVerify}]`

---

## Stage 8: Validate Against Decision Rules

**Goal:** Cross-check every finding against the priority rules before applying.

**Steps:**

8.1 For each proposed fix, verify priority order:

```
Rule 1 check: Is the test structurally synchronized with production?
  → All new constructor params have mocks
  → All new @Value fields have initialization
  → All removed deps are cleaned up

Rule 2 check: Are fixtures correct?
  → ReflectionTestUtils values are non-null and correct type
  → @Mock fields are initialized
  → Builders use correct constructor

Rule 3 check: Are mocks correct?
  → Stubbed methods exist in current production
  → Return types match
  → Argument types match

Rule 4 check: Are verifications correct?
  → Verified methods exist in current production
  → Call counts are realistic
  → ArgumentCaptor types match

Rule 5 check: If relaxing matchers, is it justified?
  → Null is a valid production value
  → Test exercises the null path
  → Fixtures and mocks are confirmed correct
```

8.2 Flag any fix that violates the order. Do not apply it.

**Output:** `[{fix, passesRules: true|false, failingRule}]`

---

## Stage 9: Recommend Repair and Retry

**Goal:** Apply fixes and verify through incremental retry.

**Steps:**

9.1 Apply all validated fixes from Stages 4-7.

9.2 Run the smallest possible test scope:

```
mvn -pl <module> -am test -Dtest=<TestClass>
```

9.3 If all tests pass → report success with change summary.

9.4 If failures remain → load `diagnosis.md`, match the failure pattern,
and produce a targeted secondary fix.

**Retry cycle:**

```
Round 1: Apply all validated fixes → run affected tests
  → If pass: done
  → If fail: diagnose → apply targeted fix → Round 2
Round 2: Targeted fix only → run affected tests
  → If pass: done
  → If fail: re-diagnose → apply targeted fix → Round 3
Round 3: Targeted fix only → run affected tests
  → If pass: done
  → If fail: report unresolved, stop
```

Limit to 3 retries. Never apply untargeted blanket fixes.
