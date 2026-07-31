# Examples

Complete workflow examples demonstrating the full reasoning chain.

---

## Example 1: Modify One Java Class

**Scenario:** Developer changes `XxxService.java` in the `service` module.
Wants to verify it compiles and tests pass.

**Reasoning chain:**

```
Stage 1 — Discover repository:
  Root: /workspace/project/
  Wrapper: mvnw found
  JAVA_HOME: /usr/lib/jvm/java-17

Stage 2 — Discover modules:
  Type: multi-module (aggregator)
  Modules: [core, service, web, api]
  Changed file: service/src/main/java/com/x/XxxService.java
  Current module: service
  Affected module: service

Stage 3 — Determine goal:
  User: "check if it compiles and tests pass"
  Goal: compile + run service module tests

Stage 4 — Select scope:
  Smallest scope: mvnw -f /workspace/project/pom.xml -pl service -am test
  No clean needed (no dependency change)

Stage 5 — Generate command:
  mvnw -f pom.xml -pl service -am test --batch-mode

Stage 6 — Execute:
  BUILD SUCCESS — 15 tests passed, 0 failures

Stage 8 — Done (no failures to diagnose)
```

**Output:**
```
Command:  mvnw -pl service -am test
Result:   BUILD SUCCESS (15 tests, 0 failures, 12s)
```

---

## Example 2: Modify pom.xml

**Scenario:** Developer adds a new dependency to the `service` module's
`pom.xml`. Wants to verify the whole project still works.

**Reasoning chain:**

```
Stage 1 — Discover:
  Root: /workspace/project/
  Wrapper: mvnw

Stage 2 — Modules:
  Changed: service/pom.xml (dependency added)
  Affected: service + modules depending on service
  Dependents: web depends on service

Stage 3 — Goal: "verify the project still works"

Stage 4 — Scope selection:
  Dependency change → clean needed (classpath may differ)
  Smallest scope: clean compile first, then test
  -pl service,web -am clean test (service + dependents)
  Not full repository (api and core unaffected)

Stage 5 — Command:
  mvnw -f pom.xml -pl service,web -am clean test --batch-mode

Stage 6 — Execute:
  BUILD SUCCESS

Stage 8 — Done
```

---

## Example 3: Compilation Error — cannot find symbol

**Scenario:** Running compile. Build fails with `cannot find symbol`.

**Reasoning chain:**

```
Stage 6 — Execute:
  mvnw -pl service -am compile
  Result: BUILD FAILURE

Stage 7 — Diagnose:
  Symptom: cannot find symbol: method findByEmail(String)
  File: XxxRepository.java:42
  Module: service

  Root cause:
  git diff shows findByEmail(String) was renamed to findUserByEmail(String)
  in core module. service module references old method name.

  Smallest retry scope: mvn -pl core -am compile (core needs fixing first)

Stage 8 — Retry:
  Fix: Update call in XxxRepository.java from
  findByEmail → findUserByEmail

  Retry 1: mvnw -pl service -am compile
  Result: BUILD SUCCESS

  Expand: mvnw -pl service -am test
  Result: BUILD SUCCESS (all tests pass)

Stage 8 — Done
```

---

## Example 4: Surefire Test Failure — Spring Context

**Scenario:** Running module tests. Spring context fails to load.

**Reasoning chain:**

```
Stage 6 — Execute:
  mvnw -pl service -am test
  Result: BUILD FAILURE

Stage 7 — Diagnose:
  Symptom: Failed to load ApplicationContext
  Caused by: Field 'kafkaTopic' in LiveService required a bean of type
  'java.lang.String' that could not be found

  Root cause:
  @Value("${wecom.live.topic}") String kafkaTopic was added to LiveService
  Test doesn't set this property.

  Smallest retry scope: mvn -pl service -am test -Dtest=LiveServiceTest

Stage 8 — Retry:
  Fix: Add @TestPropertySource(properties = {"wecom.live.topic=test"})
  to LiveServiceTest

  Retry 1: mvnw -pl service -am test -Dtest=LiveServiceTest
  Result: BUILD SUCCESS

  Expand: mvnw -pl service -am test
  Result: BUILD SUCCESS (all service tests pass)

Stage 8 — Done
```
