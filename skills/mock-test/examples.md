# Examples

Complete workflow examples demonstrating the full reasoning chain.

---

## Example 1: New @Value Field

**Production change:**
```java
public class LiveService {

    @Value("${wecom.live.topic}")
    private String liveTopic;

    public void sendMessage(String msg) {
        kafkaProducer.send(liveTopic, msg);  // new call
    }
}
```

**Reasoning chain:**

```
Stage 2 — Analyze:
  Field added: @Value("${wecom.live.topic}") String liveTopic
  External call added: kafkaProducer.send(topic, msg)

Stage 3 — Affected tests:
  src/test/java/com/x/LiveServiceTest.java
  (same-package mirror — 100% confidence)

Stage 4 — Fixture changes:
  ReflectionTestUtils.setField(service, "liveTopic", "test-live-topic")
  @Mock KafkaProducer kafkaProducer (already existed or needs adding)

Stage 5 — Configuration changes:
  liveTopic has default? No (@Value has no ":default" in expression)
  → Mandatory initialization

Stage 6 — Mock changes:
  when(kafkaProducer.send(anyString(), anyString())).thenReturn(...)
  (or doNothing() if void — depends on KafkaProducer.send signature)

Stage 7 — Verification changes:
  verify(kafkaProducer).send(eq("test-live-topic"), anyString())

Stage 8 — Validation:
  Rule 1 ✓: liveTopic field initialized
  Rule 2 ✓: ReflectionTestUtils provides non-null value
  Rule 3 ✓: kafkaProducer stub matches send signature
  Rule 4 ✓: verify captures correct topic
```

**Final test update:**
```java
@BeforeEach
void setUp() {
    service = new LiveService();
    ReflectionTestUtils.setField(service, "liveTopic", "test-live-topic");
}

@Test
void testSendMessage() {
    service.sendMessage("hello");
    verify(kafkaProducer).send(eq("test-live-topic"), eq("hello"));
}
```

---

## Example 2: New Constructor Parameter

**Production change:**
```java
// Before:
public class ReportService {
    public ReportService(DataRepository repo) { ... }
}

// After:
public class ReportService {
    public ReportService(DataRepository repo, AuditLogger logger) { ... }
}
```

**Reasoning chain:**

```
Stage 2 — Analyze:
  Constructor: +AuditLogger logger (new parameter)

Stage 3 — Affected tests:
  ReportServiceTest.java

Stage 4 — Fixture changes:
  @Mock AuditLogger logger (new mock)
  @InjectMocks handles it automatically
  Check: any manual constructor calls? → None found (uses @InjectMocks)

Stage 6 — Mock changes:
  Any stubbing needed for logger? → Check if production uses it in test path
  logger.log(...) called in sendMessage → need when(logger.log(...)).thenReturn(...)
  or doNothing() if void

Stage 8 — Validation:
  Rule 1 ✓: new param has matching @Mock
  Rule 2 ✓: @InjectMocks resolves constructor params
  Rule 3 ✓: logger stubbing matches log method signature
```

**Final test update:**
```java
@Mock DataRepository repo;
@Mock AuditLogger logger;     // ← NEW
@InjectMocks ReportService service;
```

---

## Example 3: ArgumentsAreDifferent — Diagnosis

**Symptom:**
```
Argument(s) are different! Wanted:
  userService.findByEmail(eq("alice@example.com"));
Actual invocation has different arguments:
  userService.findByEmail("bob@example.com");
```

**Reasoning chain:**

```
Stage 9 — Diagnose:
  Pattern: ArgumentsAreDifferent (diagnosis.md Pattern 1)

  Check 1: Did production argument change?
    git diff shows: -userService.findByEmail("alice@example.com")
                    +userService.findByEmail(user.getEmail())
    → Yes, argument is now computed from a variable

  Check 2: What is user.getEmail() in this test?
    Test creates User with email = "bob@example.com"

  Root cause: Test input changed → email comes from User object

  Fix priority:
    1. Synchronization: test data matches production data flow ✓
    2. Fixture: user object email is "bob@example.com" ✓
    3. Mock: userService.findByEmail is stubbed correctly ✓
    4. Verification: update expected email to "bob@example.com"

  Safest fix: Update verify to use eq("bob@example.com")
```

**Fix:**
```java
// Before:
verify(userService).findByEmail(eq("alice@example.com"));

// After:
verify(userService).findByEmail(eq("bob@example.com"));
```

---

## Example 4: Spring Context Failure

**Symptom:**
```
java.lang.IllegalStateException: Failed to load ApplicationContext
Caused by: org.springframework.beans.factory.UnsatisfiedDependencyException:
  Error creating bean with name 'liveService': Unsatisfied dependency expressed
  through field 'liveTopic'; nested exception is org.springframework.beans.factory.
  NoSuchBeanDefinitionException: No qualifying bean of type 'java.lang.String'
```

**Reasoning chain:**

```
Stage 9 — Diagnose:
  Pattern: Spring Context Failure (diagnosis.md Pattern 8)

  Root cause: @Value("${wecom.live.topic}") String liveTopic
  Spring tries to inject a bean of type String named "wecom.live.topic"
  — but the value is from a property source, not a bean definition.

  Wait — this error is misleading. The real issue is:
  The test doesn't have the property "wecom.live.topic" in its
  application.properties or @TestPropertySource.

  Fix: Add property to @TestPropertySource or use @SpringBootTest
  with properties attribute.

  Alternative (unit test): Don't use Spring Boot test at all.
  Construct LiveService directly with ReflectionTestUtils.
```

**Fix (Option A — Spring Boot test):**
```java
@SpringBootTest(properties = {
    "wecom.live.topic=test-topic"
})
class LiveServiceTest { ... }
```

**Fix (Option B — Unit test, no Spring context):**
```java
class LiveServiceTest {
    private LiveService service;

    @BeforeEach
    void setUp() {
        service = new LiveService();
        ReflectionTestUtils.setField(service, "liveTopic", "test-topic");
    }
}
```
