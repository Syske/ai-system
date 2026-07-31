# Fixture Synchronization

This document defines precise rules for synchronizing test fixtures with
production code changes. Use during Stage 4 of the workflow.

---

## Constructor Injection

If production changes a constructor's parameters:

| Production change | Test action |
|---|---|
| Parameter added | Add `@Mock` for the new type. If using `@InjectMocks`, no further action. If manual construction, update `new XxxService(...)`. |
| Parameter removed | Remove `@Mock` for the removed type (if no other test uses it). Update constructor call. |
| Parameter reordered | Update constructor call to match new order. |
| Parameter type changed | Replace `@Mock OldType` with `@Mock NewType`. Update constructor call. |
| No-arg constructor removed | Add `@InjectMocks` or switch to explicit constructor call. |

**Examples:**

```java
// Production: XxxService(A a, B b) → XxxService(A a, B b, C c)
// Test update:
@Mock A a;
@Mock B b;
@Mock C c;                  // ← NEW
@InjectMocks XxxService service;  // ← Mockito handles C automatically
```

```java
// Manual construction (no @InjectMocks):
// Before:
// private XxxService createService() { return new XxxService(a, b); }
// After:
private XxxService createService() {
    return new XxxService(a, b, c);   // ← updated constructor call
}
```

---

## Field Injection (@Autowired, @Resource, @Inject)

If production adds a field-injected dependency:

| Annotation | Test action |
|---|---|
| `@Autowired` | Add `@Mock` field + `ReflectionTestUtils.setField()` |
| `@Resource(name="x")` | Add `@Mock` with matching field name |
| `@Inject` | Same as `@Autowired` |
| `Optional<X>` | Set field to `Optional.of(mockX)` or `Optional.empty()` |

**Example:**

```java
// Production added:
// @Autowired
// private D d;
// Test update:
@Mock D d;
@InjectMocks XxxService service;  // if using @InjectMocks, Mockito handles @Autowired

// If @InjectMocks not used:
// @BeforeEach
// void setUp() {
//     service = new XxxService(a, b);
//     ReflectionTestUtils.setField(service, "d", mockD);
// }
```

---

## @Value Field Injection

**Mandatory rule:** Every new `@Value` field must be initialized in every test
that constructs the class. Never leave `@Value` fields null.

| Production | Test action |
|---|---|
| `@Value("${key}")` | `ReflectionTestUtils.setField(service, "fieldName", "test-value")` |
| `@Value("${key:default}")` | Optional — works with default. But prefer explicit initialization. |
| `@Value("#{systemProperties['key']}")` | Set system property in `@BeforeEach` or use `ReflectionTestUtils`. |

**Example:**

```java
// Production added:
// @Value("${wecom.live.topic}")
// private String liveTopic;
//
// @Value("${wecom.live.group}")
// private String liveGroup;

// Test @BeforeEach:
@BeforeEach
void setUp() {
    service = new XxxService(a, b);
    ReflectionTestUtils.setField(service, "liveTopic", "test-live-topic");
    ReflectionTestUtils.setField(service, "liveGroup", "test-live-group");
}
```

---

## @MockBean / @SpyBean (Spring Boot Test)

| Production change | Test action |
|---|---|
| New bean dependency | Add `@MockBean` to test |
| Removed bean dependency | Remove `@MockBean` (if no other test method needs it) |
| Bean type changed | Replace `@MockBean OldType` with `@MockBean NewType` |
| Bean replaced with primary | Add `@MockBean` with `@Primary` |

**Example:**

```java
@WebMvcTest(XxxController.class)
class XxxControllerTest {

    @MockBean
    private XxxService xxxService;    // existing

    @MockBean
    private NewDependency newDep;     // ← NEW (bean introduced in production)
}
```

---

## Builder / Factory Methods

If a builder or factory constructs a class whose constructor changed:

```java
// Before: return new XxxService(a, b);
// After:  return new XxxService(a, b, c, d);
```

Update every call site:

```java
// Shared test helper:
private XxxService createService(A a, B b, C c, D d) {
    return new XxxService(a, b, c, d);
}

// Or use builder pattern:
private XxxService createService() {
    return XxxService.builder()
        .a(mockA)
        .b(mockB)
        .c(mockC)       // ← NEW
        .d(mockD)       // ← NEW
        .build();
}
```

---

## Configuration Properties

If production introduces `@ConfigurationProperties`:

**Option A — @TestPropertySource (preferred for Spring Boot tests):**

```java
@TestPropertySource(properties = {
    "app.property.key1=value1",
    "app.property.key2=value2"
})
```

**Option B — ReflectionTestUtils (for unit tests without Spring context):**

```java
AppProperties props = new AppProperties();
ReflectionTestUtils.setField(props, "key1", "value1");
ReflectionTestUtils.setField(props, "key2", "value2");
ReflectionTestUtils.setField(service, "properties", props);
```

---

## Removed Dependencies

Before removing a `@Mock` or `@MockBean` field, verify:

1. No other test method in the class references the field
2. No `@InjectMocks` targets need it for constructor resolution
3. No `when()` or `verify()` blocks reference it

If any condition fails, keep the field but mark it as lenient.
