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
clear message and fall back to `java-maven` CLI offline:
`mvnw -s <settings> -pl <mod> -am compile -o`.
