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

## [Java] Standalone Maven Modules Must Inline Inherited Build Config

Date: 2026-09-18

Priority: P1

Context:

Service repos commonly publish a `*-facade` contract module that sibling services consume as a Maven dependency from the internal Nexus. A repo root POM may declare build config once so every child module inherits it — `distributionManagement` (publish target) and `<repositories>`/`<pluginRepositories>` (dependency resolution). Modules that set `<parent>` inherit it; standalone (parent-less) modules inherit nothing. Some repos deliver the service as a container image and host a few standalone library modules instead.

Problem:

Two symptoms on the same newly added standalone facade module (same day), both from the missing inheritance:

1. `mvn deploy` failed:

`Failed to execute goal ... maven-deploy-plugin:deploy (default-deploy) on project <facade>: Deployment failed: repository element was not specified in the POM inside distributionManagement element or in -DaltDeploymentRepository=id::url parameter`

2. The pipeline build failed while resolving dependencies: `Could not resolve dependencies for project ...: Could not find artifact net.coolcollege.platform.service:platform-util:jar:<version> in alimaven (http://maven.aliyun.com/nexus/content/groups/public/)` — the module depends on an internal artifact, but in CI `central` is mirrored to a public mirror, so internal artifacts cannot be found. Local builds did not reproduce it (the local settings mirror `central` to the company Nexus).

Both commands worked for a sibling repo's facades, which made it look like a Nexus connectivity or permission problem.

Root Cause:

The module POM has no `<parent>`, so it inherits **nothing** from the repo root POM — neither `distributionManagement` nor `<repositories>`/`<pluginRepositories>`. The repo root POM itself declares no `distributionManagement` (that service ships as a container image, so it never needed Maven publishing), while it does declare the internal repository. Sibling-repo facades worked only because their root POM declares the config and all their modules set `<parent>`. Because the standalone module is published to consumers, adding a `<parent>` is NOT the fix: the parent POM would then also have to be published for consumers to resolve it.

Solution:

- Inline every piece of build config the module actually needs — publish target (`distributionManagement`) and dependency/plugin repositories (`<repositories>`/`<pluginRepositories>`) — mirroring an existing precedent in the same repo (a library module that already deploys) or the repo root POM.
- Do NOT try to fix it by adding `<parent>` when the parent POM declares no `distributionManagement`: nothing would be inherited, and the parent BOM would be pulled in, changing the module build.
- Verify offline first: `mvn -o install -pl <module> -DskipTests` (exit 0, artifact lands in the local repo). Then confirm the distribution id matches a `<server><id>` entry in the Maven `settings.xml`, and probe the remote repository (an unauthenticated HTTP 401 means it is reachable and only needs credentials).
- Keep the two goals apart: `install` fills only the local repository (enough when the consumer builds on the same agent); `deploy` publishes to the remote repository (required for cross-agent / cross-pipeline consumption).
- To reproduce a CI resolution failure locally, run from a directory whose POM declares no repositories (an empty dir) and point `central` at a public mirror with an empty local repository: internal artifacts then fail to resolve. Running in the repo root masks it, because the root POM supplies the repository.

Lesson:

A standalone (parent-less) Maven module inherits nothing from the repo root POM, so it must inline every build config it needs — `distributionManagement` (else `mvn deploy` fails with "repository element was not specified") and `<repositories>`/`<pluginRepositories>` (else internal dependencies fail to resolve in CI, where `central` is mirrored to a public repository).

Scope:

- Standalone (parent-less) Maven modules in multi-module service repos — e.g. facade / common library artifacts
- Repos whose root POM declares no `distributionManagement` because the service is delivered as a container image
- Check with: `mvn help:effective-pom -pl <module> | grep -A6 distributionManagement` and `... | grep -A6 '<repositories>'`
- Symptom fingerprints: "repository element was not specified in the POM inside distributionManagement element"; "Could not find artifact <internal groupId> in alimaven"

Related:

- No governance standard for Maven publishing yet (candidate: a company-standard Maven conventions doc); incident record: `ai-system/logs/env-maven-distmgmt-deploy-20260918-110006.md`

## Cross-branch merge conflict resolution discipline (2026-09 evidence)

- **Resolve conflicts against the upstream's own unit-test assertions as the contract baseline**, never by semantic intuition "take the union". Counter-example: when two upstream fixes touch the same method, a union-introduced fallback branch breaks the other fix's own test (`DynamicDataSource#getDbServerByDbName`: `getCurrentDbName(false)` default-DB fallback vs the test-required "blank delegates as null and does not write back").
- **Immediately run that file's unit test after resolving** (`mvn -o -pl <module> -am test -Dtest=<Case>`) as the verdict evidence; compilation alone does not prove semantic correctness.
- **Two branches resolving the same core method differently will conflict again on the next merge**; converge on a "single version" (prefer the upstream owner's version), not both sides keeping their own.
- **Test sources that fail to compile cannot be skipped with `@Ignore`** (`@Ignore` only affects execution, not compilation): exclude them at the **test compile phase** (`maven-compiler-plugin` `testExcludes`); if the project disables surefire ignore-test-failures, prefer compile-phase exclusion and document the removal condition.
- **Do not commit tool artifacts**: `git rm --cached <artifact-dir>` + append `.gitignore`, otherwise every cross-branch merge drags them in (e.g. CodeGraph index 170MB).

## MyBatis: when `resultType` is an entity you MUST alias columns to camelCase explicitly (2026-09, verified)

- This project does **not** enable `mapUnderscoreToCamelCase` at runtime (existing in-repo comment: `StudyDurationMigrateTaskMapper.xml:45`). So a `<select resultType="...Entity">` that directly maps raw underscore columns (`batch_id`/`exec_status`) leaves **every entity field except `id` null**.
- The failure mode is **silent logic drift**, not an error: e.g. a reconciliation segment decided by `batchId`/`execStatus` hits null and just `continue`s — appearing as "there were candidates but nothing happened".
- Avoidance: hand-written `<select>` must always `column as camelCaseAlias` (or use a `resultMap`); `resultType=int/long/map` is unaffected (in the map case column names are the keys and need aliasing yourself).
- Guard: lock the convention with a static test before merging (this project's `MapperXmlColumnAliasGuardTest`: entity statements whose column fragments contain underscore columns must carry camelCase aliases).
- Lesson: **unit tests with mocked mappers can never catch this class of runtime mapping issue** — you need runtime verification or a static guard.

## Never anchor a field insertion on the field-declaration line (it strips the annotation above)

- **Symptom**: a script anchored on `private X y;` and inserted a new field carrying its own
  comment/annotation; the original field's `@Autowired` was "inherited" by the new field —
  producing a **duplicate `@Autowired`** while the original field **lost its annotation** →
  runtime injection failure (NPE), with the compiler and syntax checks staying silent
  (the most dangerous class of defect).
- **Rule**: when inserting a member, the anchor must include the annotation/comment above it
  (e.g. use the whole `@Autowired\n    private X y;` as oldText), or insert *before* the
  annotation line; after inserting, always re-inspect the three adjacent lines.
- **Verification**: `awk '/@Autowired/{if(p=="Autowired") print FILENAME": "NR; p="Autowired"; next} {p=""}' <file>`
  — detects consecutive duplicate annotations; additionally confirm every newly injected field
  still carries its annotation.
- **Instance**: adding `OssClientService` to `MigrationJobServiceImpl` stripped `@Autowired`
  from `PrivateOssClientService` (fixed in `fedf58884`).
