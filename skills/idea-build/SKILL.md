---
name: idea-build
description: >
  Optional Maven build backend backed by IntelliJ IDEA's resident incremental
  compiler via MCP. Compile verification in seconds (vs 62-70s CLI cold
  start) for projects open in IDEA. Selected via environment config
  build.backend=idea; NOT the default. Falls back to java-maven CLI on any
  failure. Trigger when: build.backend is idea and compile verification is
  needed, or user explicitly asks to compile via IDEA.
---

# idea-build

## Overview

Optional compile backend: drives IntelliJ IDEA's built-in MCP Server
(`build_project`) so compile verification uses IDEA's resident incremental
compiler — the same speed advantage IDEA has over CLI. This skill is **not
the default**: the standard path is `java-maven` (CLI). It activates only
when `config/environments/{env}.yaml` sets `build.backend: idea`.

**Why separate from java-maven:** IDEA is a machine-specific, GUI-dependent
tool (per-user install path, MCP server must be enabled, project must be
open). Keeping it in its own skill means the core CLI skill stays portable
and the optional backend can be enabled/disabled purely by config.

## Activation

**Activate when:**
- `build.backend` (environments config) equals `idea`, OR user explicitly
  asks to "compile via IDEA"
- Compile verification needed for a project open in IDEA

**DO NOT activate when:**
- `build.backend` is `maven` (default) — use `java-maven`
- IDEA not installed / MCP server not enabled / headless CI

## Prerequisites (machine-specific, configure in environments yaml)

```
build:
  backend: idea
  idea:
    executable: '<path to idea64.exe>'   # per-user path
    port: 64342                          # IDEA built-in port + 1000
```

One-time GUI on the IDEA side:
- Enable plugin `com.intellij.mcpServer`
- Settings → Tools → MCP Server → check **Enable MCP Server**
- Open the target project (MCP `build_project` only compiles open projects)

## Configuration

- Reads: `build.backend`, `build.java_home`, `build.maven_home`, `build.idea.*`
  from `ai-system/config/environments/{env}.yaml`.
- Resolve (standalone, without the aic wizard):
  `AI_SYSTEM_ROOT` env → walk up from CWD/SKILL.md to the ancestor holding
  `config/environments/`; then
  `cli/services/environment.py::resolve_environment()` returns `build`/`paths`.
  Portable one-liner (run from the ai-system root or with `AI_SYSTEM_ROOT` set):
  ```
  python -c "from cli.services.environment import resolve_environment; \
    print(resolve_environment().get('build'))"
  ```
- **Missing/ambiguous config → ASK the user.** Never guess a JDK/Maven/IDEA
  path (e.g. `C:\Program Files\Java\...`) — machine-specific values come
  from the environment config, not from the skill.

## Commands

```bash
# tools list (sanity check connection)
python <skill>/idea-mcp.py tools <projectPath>

# compile (incremental, fast)
python <skill>/idea-mcp.py build <projectPath>

# full rebuild
python <skill>/idea-mcp.py build --rebuild <projectPath>

# run a terminal command in IDEA
python <skill>/idea-mcp.py exec <projectPath> <cmd> [args...]
```

Environment (injected by the caller from environments config):
- `IJ_MCP_SERVER_PORT` (default 64342)
- `IJ_MCP_SERVER_PROJECT_PATH` (or first arg)
- `IJ_MCP_SERVER_EXECUTABLE` (idea64 path; used when opening a project)

## Open a project (idempotent)

```bash
"$IDEA_EXECUTABLE" <projectPath>   # open/focus; new window if not open
```
Re-opening an already-open project just focuses it (verified). There is no
CLI/MCP way to close a project — close via IDE GUI (File → Close Project).
First open of a Maven project needs time for module sync (modules appear
empty until then).

## Verified facts (2026-08-08, IDEA 2026.2.0.1 Ultimate)

- SSE endpoint `http://127.0.0.1:64342/sse`, header
  `IJ_MCP_SERVER_PROJECT_PATH=<path>`; stdio: `idea64.exe stdioMcpServer`.
- 38 MCP tools; `build_project` returns `{"isSuccess":true,"problems":[...]}`
  (problems are warnings, not errors).
- `build_project` only accepts projects open in IDEA; `filesToRebuild` cannot
  escape the project directory (multi-project workspace limitation).
- Per-project windows compile only their own modules (knowledge-api: 5,
  live-api: 6) — precise, seconds.

## Fallback

Any failure (IDEA not running, MCP unreachable, project not open) → return a
clear message and fall back to the `java-maven` CLI skill, using the JDK and
Maven configured in `ai-system/config/environments/{env}.yaml` (`build.java_home` /
`build.maven_home`), NOT bare `mvn` / `mvnw` (often not on PATH):

```bash
JAVA_HOME="$build.java_home" "$build.maven_home/bin/mvn" -s <settings> -pl <mod> -am compile -o
```

## JDK / Maven compatibility (verified 2026-08-18)

| Project target | JDK | Maven | Notes |
|---|---|---|---|
| `java.version=1.8` (user-center-api etc.) | `{build.java_home}` | `{build.maven_home}` | JDK 8 must be a real JDK 8 (Maven 3.6.3 bundles compiler plugin 2.8.4, which **fails on JDK 17+** — `class com.sun.tools.javac.api.JavacTool` error); concrete paths come from `ai-system/config/environments/{env}.yaml → build.java_home` |
| Newer JDK-17+ projects | JDK 17+ (per project) | same Maven | only if project's compiler plugin version supports it |

Rules:
- Match the JDK to the project's `<java.version>`; Java 8 projects MUST use a
  JDK 8 (or newer JDK only if the project's maven-compiler-plugin is new enough).
- Read the concrete JDK/Maven paths from the environment config
  `ai-system/config/environments/{env}.yaml` (`build.java_home` / `build.maven_home`)—
  never hard-code machine-specific absolute paths in this skill. Those are
  environment configuration, not part of the skill's portable contract.

## Caveats (learned 2026-08-18)

- IDEA `build_project` problems are almost all pre-existing "deprecated API"
  WARNINGs across the whole repo; check only `kind == "ERROR"` and files you
  modified. `isSuccess` + zero ERRORs is a pass even with hundreds of WARNINGs.
- With `backend: idea`, prefer IDEA for compile verification; it is seconds
  vs 60-70s CLI cold start and avoids the JDK/Maven matrix entirely.
