---
name: java-maven
description: >
  Foundation Maven execution Skill for all Java development workflows.
  Discovers repository structure and multi-module layout, selects the
  smallest execution scope, generates correct commands (including enterprise
  wrapper scripts), diagnoses compilation/Surefire/dependency failures,
  and retries incrementally. Optimizes for cache preservation and build
  speed — never defaults to clean install.
  Trigger when: user says "build", "compile", "run tests", "package",
  "mvn", "fix build", "test failure", "compilation error", or pom.xml
  changes. Does NOT modify production code.
---

# java-maven

## Overview

java-maven is the **shared Maven execution capability** for all Java-related
Skills. Instead of letting every Skill invoke Maven independently, this Skill
provides deterministic discovery, scope selection, command generation, failure
diagnosis, and incremental retry.

**Core philosophy:** Smallest scope first. Preserve the cache. Diagnose before
retrying. Never default to `clean install`.

## Activation

**Activate when:**
- User says "build", "compile", "package", "mvn", "run tests", "test"
- A pom.xml or Maven-related file changed in the working tree
- Test execution or compilation fails
- Another Skill needs Maven execution (referenced in its description)

**DO NOT activate when:**
- User asks about Maven concepts without wanting to execute (use documentation)
- Project does not contain a pom.xml (not a Maven project)
- User explicitly asks for a different build tool (Gradle, Bazel, etc.)

## Workflow (8 Stages)

```
Stage 1 — Discover repository
Stage 2 — Discover modules
Stage 3 — Determine goal
Stage 4 — Select scope
Stage 5 — Generate command
Stage 6 — Execute
Stage 7 — Diagnose failure
Stage 8 — Retry incrementally
```

## Quick Decision Table

| Question | Rule |
|---|---|
| Should Maven run? | pom.xml exists AND user goal is build-related |
| Which settings.xml? | Resolution order below; ALWAYS pass `-s <path>` — never run bare mvn |
| Which JDK / Maven? | From `ai-system/config/environments/{env}.yaml` → build (java_home / maven_home); never assume PATH |
| What scope? | Smallest that achieves the goal |
| Wrapper available? | Use it, not raw mvn |
| Multi-module? | `-pl <mod> -am` for single-module changes |
| Clean build? | Only if dep/plugin/generated-source changed |
| Which phase? | compile → test → package → verify (minimal) |
| Test to run? | `-Dtest=Class#method` before `-Dtest=Class` |
| Build failed? | Diagnose, fix, retry smallest scope |

## Settings Resolution (mandatory)

Resolve settings.xml in this order; stop at the first hit:

1. `AIC_MAVEN_SETTINGS` environment variable (manual session-level override)
2. `repositories/{service_id}.yaml` → `build.settings` (explicit per-service declaration)
3. Environment config `ai-system/config/environments/{env}.yaml` → `build.maven_settings` (shared default)
4. `~/.m2/settings.xml`
5. None found → STOP. Ask the user; never run bare mvn against unknown mirrors.

Rules:

- ALWAYS pass `-s <resolved path>`; never run bare mvn.
- A repo-local `{repo}/.m2/settings.xml` existing on disk does NOT imply it should be used;
  the shared default wins unless the service declares `build.settings` explicitly.
- Write-back: declare `build.settings` in `repositories/{service_id}.yaml` only after the user
  confirms the service genuinely needs non-default settings.

The workspace-root `mvnw.cmd` follows the same priority (env override, shared default otherwise);
it is a human convenience wrapper — agents resolve from metadata.

## Reference Files

| File | Content | Load when |
|---|---|---|
| `decision.md` | Activation, scope, lifecycle, clean build decisions | Stage 3-4 |
| `discovery.md` | Repository/module/wrapper discovery workflows | Stage 1-2 |
| `commands.md` | Command generation, flag selection, templates | Stage 5 |
| `build-speed.md` | Offline/daemon/parallel build speed practices (measured) | Stage 5, slow builds |
| `idea-build.md` | IDEA MCP `build_project` fast compile verification + fallback | Stage 5, compile checks |
| `diagnosis.md` | Compilation/Surefire/dependency/Spring Boot diagnosis | Stage 7 |
| `retry.md` | Incremental retry strategy and stopping conditions | Stage 8 |
| `checklists.md` | 7 reusable checklists | Any stage |
| `examples.md` | 4 complete workflow examples | Reference |
