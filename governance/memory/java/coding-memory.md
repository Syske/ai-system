# Java Coding Memory

General Java coding experience.


## [Java] Strategy Pattern Over BizType Branching

Date: 2026-07-06

Priority: P1

Context:

LiveInfoFacadeImpl handled live platform differences (DingTalk/WeCom/Polyv) via if (BizTypeEnum.WX_LIVE_COURSE.equals()) branching, duplicating ecosystem-specific logic across deleteByBizId and modifyByBizId.

Problem:

BizType if-else branching scattered ecosystem-specific logic across the Facade layer. Adding a new ecosystem required modifying multiple methods. Bugs occurred when the order of operations differed (e.g., cancel API before vs after DB delete), as the branching logic was error-prone and hard to review.

Solution:

Extract ecosystem-specific logic into a LiveService strategy interface with default no-op methods. Delete and modify operations delegate to LiveService.deleteByBizId() and LiveService.modifyByBizId(), with the Facade layer handling only common operations (local DB update/delete). New ecosystems implement only their specific logic without touching Facade code.

Lesson:

Cross-ecosystem operations should use the Strategy pattern with a shared interface. Ecosystem-agnostic common logic stays in the Facade; ecosystem-specific pre/post operations live in strategy implementations. Avoid if-else on bizType in the dispatch layer.

Scope:

- Multi-platform service design
- SOFA RPC Facade implementations
- All live platform integrations (DingTalk/WeCom/Polyv/HD)


## [Java] Order of Operations in Delete-then-API Pattern

Date: 2026-07-06

Priority: P1

Context:

LiveInfoFacadeImpl.deleteByBizId() required calling WeCom cancel API before deleting the local DB record.

Problem:

The code deleted the local DB record first, then tried to query the same record to get the feedId for the cancel API call. Since the record was already deleted, the query returned null, making the cancel API call dead code. WeCom livings remained active on the WeCom side after local deletion.

Root Cause:

The delete operation (liveInfoService.deleteByBizId()) was called before the ecosystem-specific pre-logic. The subsequent query for the feedId would always return null because the record no longer existed.

Solution:

Reorder: query the record first → extract feedId → call ecosystem pre-logic (cancel API) → delete local DB. Extract the pre-logic into LiveService.deleteByBizId() strategy method to ensure consistent ordering.

Lesson:

When implementing a "delete + call external API" pattern, always query the required data before deletion. The data needed for the external API call must be obtained while the record still exists in the database.

Scope:

- All delete operations that require external API calls before deletion
- Any pattern where record data is needed by strategy logic


## Category Files

Category files, split by topic:

- `java/mq.md` — MQ-related experience
- `java/integration.md` — integration (WeCom, etc.) experience
- `java/spring.md` — Spring experience


## [Java] SOFABoot Offline Test-Environment Workarounds

Date: 2026-09-04

Priority: P1

Context:

The 202610-public-security-storage-no-ai-parse-optimization project (resource-manager, SOFABoot 3.4.6 / Spring Boot 2.1.13) is built offline (Maven 3.x at `<maven-home>`, Dragonwell JDK8 at `<jdk-home>`, local repo at `<local-repo>`) in a Linux-on-Windows setup. Running `mvn test` hits environment-specific blockers that look like code failures.

Problem:

1. `mvn test -o` fails with `MultipleArtifactsNotFoundException: surefire-junit4:jar:2.22.2` — the provider jar pinned by spring-boot-dependencies 2.1.13 is absent from the offline repo (only 2.22.1 present).
2. Re-running `mvn test` without `clean` fails with jacoco 0.8.2 `Cannot process instrumented class ... Please supply original non-instrumented classes` (double instrumentation).
3. Spring-context tests fail at startup because logback cannot write the service's configured log directory (WSL has no such dir).
4. Two existing VodServiceTest classes fail (mock NPE at line 63 + jacoco×PowerMock IllegalClassFormatException) — they fail identically on the pristine baseline.

Root Cause:

Environment/offline-repo gaps, not code defects: surefire provider version mismatch, jacoco instrument leaves classes instrumented, missing log dir, pre-existing broken tests.

Solution:

- Run tests with `-Dmaven-surefire-plugin.version=2.22.1` (provider present in offline repo; do NOT change the pom — 2.22.2 is the project default in CI).
- Always `mvn clean test` (never bare `test` twice) because jacoco 0.8.2 instrument is not idempotent here.
- Ensure the service's configured logback directory (e.g. /data/log/<service>/access + /error) exists and is writable before context-loading tests.
- Accept pre-existing suite failures as such; prove with `git stash push -u` baseline run (include untracked, else new files break compilation) rather than chasing them.
- Full-suite verdict: run targeted `-Dtest=` filters for the changed classes; treat a full-suite failure count as green for the change when the same failures reproduce on baseline.

Lesson:

For SOFABoot repos in this offline setup, run tests with `-Dmaven-surefire-plugin.version=2.22.1` and `clean`, ensure the configured log directory exists, and baseline-prove any pre-existing suite failures before blaming the change.

Scope:

- SOFABoot / spring-boot-dependencies 2.1.13 based repos built offline
- Any `mvn test` run under jacoco 0.8.2 with PowerMock tests

## [Java] javax.annotation.Resource vs domain.Resource Class-Name Collision

Date: 2026-09-04

Priority: P1

Context:

While adding a SOFA RPC implementation in resource-manager (a multi-module SOFABoot repo whose domain package contains an entity class named `Resource`), a new class injected a bean with `@Resource` (javax.annotation). The single import of `javax.annotation.Resource` silently shadowed the domain `Resource` used elsewhere in the same file.

Problem:

Compilation failed with ~80 errors that looked like a broken environment: javac reported the domain `Resource` type unresolvable, and — cascading from the same shadowing — Lombok's `@Slf4j` reported `log` not found on the injected type. The noise made it look like a pre-existing repo problem rather than a change-introduced bug.

Root Cause:

A class-name collision between the annotation `javax.annotation.Resource` and the domain entity `Resource` in the same compilation unit. javac resolved the simple name to the wrong type, and the Lombok log generation failed on the mismatched field type, producing a cascade of misleading errors.

Solution:

Switch the injection to Spring's `@Autowired` (or fully qualify the annotation). The compile error cascade disappears once the ambiguous simple name is removed.

Lesson:

In multi-module Java repos whose domain package contains an entity named `Resource`, never inject with `@Resource` (javax.annotation) in the same file — use `@Autowired`. When a multi-module compile suddenly floods with errors (especially Lombok `log` not found), first check symbol collisions introduced by the change before suspecting the environment.

Scope:

- Any SOFABoot / Spring repo with a domain entity named `Resource`
- Lombok `@Slf4j` usage combined with `@Resource` injection
