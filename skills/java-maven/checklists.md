# Checklists

---

## Repository Discovery Checklist

Use during Stage 1.

- [ ] Repository root found (`.git/` or VCS marker)
- [ ] Root pom.xml located
- [ ] Wrapper script checked: `mvnw`, `mvnw.cmd`, custom
- [ ] `.mvn/jvm.config` checked
- [ ] `.mvn/maven.config` checked
- [ ] `.mvn/extensions.xml` checked
- [ ] JAVA_HOME detected and valid
- [ ] If no wrapper: `mvn --version` succeeds

---

## Module Discovery Checklist

Use during Stage 2.

- [ ] Project type determined: single / multi / child
- [ ] All module pom.xml files read
- [ ] Module dependency graph built
- [ ] Current module identified
- [ ] Affected module(s) identified from change context
- [ ] Change-to-module mapping confirmed (file changed → module)

---

## Build Scope Checklist

Use before every command (Stage 4).

- [ ] Smallest scope that achieves the goal selected
- [ ] Clean build justified? (dep/plugin/generated-source change only)
- [ ] Lifecycle phase minimal: compile → test → package → verify
- [ ] Multi-module: `-pl <mod> -am` used instead of full build
- [ ] Single test: `-Dtest=Class#method` before `-Dtest=Class`
- [ ] `--batch-mode` added for non-interactive execution

---

## Compilation Validation Checklist

Use during Stage 7 (compilation failure).

- [ ] Error category identified: symbol/package/method/constructor/type
- [ ] File path and line number extracted
- [ ] Affected module identified
- [ ] Root cause determined:
  - [ ] Missing dependency
  - [ ] Renamed/moved symbol
  - [ ] Changed method signature
  - [ ] Changed constructor params
  - [ ] Generated source not regenerated
  - [ ] Duplicate class
- [ ] Smallest retry scope determined

---

## Surefire Validation Checklist

Use during Stage 7 (test failure).

- [ ] Failure category: assertion/mockito/spring/timeout/compilation
- [ ] Test class and method extracted
- [ ] Full exception message extracted
- [ ] Root cause determined:
  - [ ] Production logic changed
  - [ ] Production API changed
  - [ ] Test fixture stale
  - [ ] Mock not updated
  - [ ] Configuration missing
  - [ ] Network call not mocked
  - [ ] Timeout too low
- [ ] Smallest retry scope determined

---

## Retry Checklist

Use during Stage 8.

- [ ] Single blocking issue identified (not batch)
- [ ] Fix applied to correct location
- [ ] Smallest retry scope selected
- [ ] If passes: scope expanded
- [ ] If fails: re-diagnosed before next retry
- [ ] Max retries (3/module, 5/project) respected
- [ ] Stopping condition checked before each retry

---

## Execution Checklist

Use before every Maven invocation.

- [ ] Wrapper preferred over raw mvn
- [ ] `-f` flag used when not at pom.xml directory
- [ ] `-pl` flag used for multi-module targeting
- [ ] `-am` flag used when building dependencies needed
- [ ] Clean added only when justified
- [ ] `--batch-mode` added
- [ ] Command explained to user before execution
