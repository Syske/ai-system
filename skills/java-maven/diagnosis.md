# Failure Diagnosis

Diagnose Maven build failures deterministically. Each entry follows:
symptom → root cause → smallest retry scope → recommended repair.

---

## Compilation: cannot find symbol

**Symptom:** `cannot find symbol: symbol variable/class/method`

**Root causes:**
- A dependency was removed from pom.xml but code references it
- A class was renamed/moved without updating references
- Generated sources were not regenerated
- An inter-module dependency is missing

**Smallest retry scope:** `mvn -pl <module> -am compile`

**Recommended repair:**
1. Check if the symbol exists in another module of the same project → add
   `<dependency>` on that module
2. Check if the symbol exists in an external library → check pom.xml
3. Check if the symbol is generated → run `mvn compile` without `clean`
   (annotation processors generate on incremental compile)

---

## Compilation: package does not exist

**Symptom:** `package com.xxx does not exist`

**Root causes:**
- A dependent module has not been compiled → run `compile` or `install` on it
- Dependency scope is `provided` or `test` but used in main sources

**Smallest retry scope:** `mvn -pl <module> -am compile`

**Recommended repair:**
1. Check if the other module's `target/classes` directory exists
2. If not, the dependency module needs to be compiled first (`-am` handles this)
3. If dependency is `provided` scope, change to `compile` or restructure code

---

## Compilation: method not found

**Symptom:** `cannot find symbol: method newMethod()`

**Root causes:**
- A method was renamed or removed from a dependency
- A method signature changed (new parameters, different types)
- A library was upgraded and the API changed

**Smallest retry scope:** `mvn -pl <module> -am compile`

**Recommended repair:**
1. Locate the method declaration in the dependency module or library
2. Compare old vs new signature
3. Update the call site to match

---

## Compilation: constructor mismatch

**Symptom:** `constructor XxxService cannot be applied to given types`

**Root causes:**
- Constructor parameters added, removed, or reordered
- No-arg constructor removed, code uses `new XxxService()` without args
- A builder or factory calls the old constructor

**Smallest retry scope:** `mvn -pl <module> -am compile`

**Recommended repair:**
1. Check the constructor declaration
2. Update all call sites (including in dependent modules if using `-amd`)
3. If `@InjectMocks` is used in tests, update test fixtures (see mock-test Skill)

---

## Surefire: test assertion failure

**Symptom:** `expected: <X> but was: <Y>`

**Root causes:**
- Production logic changed, expected value is different
- Mock return value changed, test assertion on mock result is stale

**Smallest retry scope:** `mvn -pl <module> -am test -Dtest=Class#method`

**Recommended repair:**
1. Check the production diff — did the logic change?
2. If yes, update the expected value to match new production behavior
3. If mock, update stub return value and assertion together

---

## Surefire: Spring context failure

**Symptom:** `Failed to load ApplicationContext`

**Root causes:**
- A new bean dependency is not mocked (`@MockBean` missing)
- A `@Value` property is not set (`@TestPropertySource` missing)
- A bean constructor changed, Spring cannot auto-wire
- Circular dependency introduced

**Smallest retry scope:** `mvn -pl <module> -am test -Dtest=Class`

**Recommended repair:**
1. Read the nested exception — it identifies the missing bean or property
2. Add `@MockBean` for new bean dependencies
3. Add `@TestPropertySource` for new configuration properties
4. If circular dependency, review production design

---

## Surefire: Mockito failure

**Symptom:** `WantedButNotInvoked`, `UnnecessaryStubbingException`, etc.

**Root causes:**
- Production call was removed or renamed → verify/stubbing is stale
- Production call is now conditional → test input needs updating

**Smallest retry scope:** `mvn -pl <module> -am test -Dtest=Class#method`

**Recommended repair:**
1. Check the production diff for the affected method
2. Update or remove the stale verify/stubbing
3. See mock-test Skill for detailed Mockito repair

---

## Surefire: timeout

**Symptom:** `test timed out after N milliseconds`

**Root causes:**
- Test makes a real network call (not mocked)
- Infinite loop or slow operation in production code
- Test waits on a lock or semaphore

**Smallest retry scope:** `mvn -pl <module> -am test -Dtest=Class#method`

**Recommended repair:**
1. Check if the test is hitting a real external service → mock it
2. Check if a slow operation was added → increase timeout or refactor test
3. Check for unintended real calls (no mock provided)

---

## Dependency resolution

**Symptom:** `Could not resolve dependencies`, `Non-resolvable parent POM`

**Root causes:**
- Parent POM is not in local repo (needs `install` on parent)
- A sibling module hasn't been installed
- Repository is unreachable (VPN, network, credentials)
- Dependency version doesn't exist

**Smallest retry scope:**
```
mvn dependency:resolve
mvn -pl <parent> -am install   (if parent needs installing)
```

**Recommended repair:**
1. Check if the missing artifact is a sibling module → `mvn -pl <sibling> install`
2. Check if the repository is accessible → verify network/VPN
3. Check for typos in version numbers

---

## Plugin failure

**Symptom:** `Plugin ... not found`, `Failed to execute goal ... plugin`

**Root causes:**
- Plugin not in any configured repository
- Plugin version doesn't exist
- Plugin requires a specific Maven version

**Smallest retry scope:** `mvn <phase>`

**Recommended repair:**
1. Check if the plugin is in `settings.xml` plugin groups
2. Check if the plugin version is valid
3. Check if the Maven version meets plugin requirements
