# IDEA Build via MCP — Compile Verification Strategy

> Solves: CLI Maven cold-start compile is slow (62-70s on SNAPSHOT-heavy
> multi-module services). IntelliJ IDEA's resident incremental compiler is
> the fast path; IDEA 2025.2+ exposes it to external agents via the built-in
> **MCP Server** (`build_project` tool).
>
> **STATUS: VERIFIED 2026-08-07** — end-to-end connection tested against
> IntelliJ IDEA 2026.2.0.1 (Ultimate, `IU`). 38 tools exposed incl.
> `build_project`; real compile executed via MCP and returned JPS build
> results.

## When to Use IDEA Build (fast path)

| Situation | Use |
|---|---|
| IDEA is running with this project open | ✅ `idea_build` (MCP `build_project`) for **compile verification** |
| Compile-only verification after edits | ✅ IDEA build — seconds, incremental, returns structured errors |
| Running tests / packaging / install | ❌ CLI (`mvnw`) — IDEA build_project does not run tests |
| No IDEA / headless / CI | ❌ CLI with offline strategy (see `build-speed.md`) |
| IDEA build errors look stale | ⚠️ Re-verify with CLI once, then fix |

**Golden rule:** use the fast IDEA incremental compiler for *compile* checks;
use CLI only when tests/package are needed or IDEA is unavailable.

## Mechanism (verified facts)

- IntelliJ IDEA **2025.2+** ships the MCP Server plugin, bundled & enabled by
  default. Local IDE is 2026.2 — available.
- Tool: `build_project` — triggers IDE internal build, waits, returns compile
  errors/warnings. Params: `rebuild` (full), `filesToRebuild` (relative paths),
  `timeout`, `projectPath`.
- Tool: `execute_terminal_command` — runs shell in the IDE terminal
  (not needed for compile; useful for ad-hoc mvn).
- Connect: IDEA Settings → enable "MCP Server" → Auto-Configure writes the
  client config, or copy the SSE/Stdio URL manually.

## Verified Connection (2026-08-07, IDEA 2026.2.0.1 Ultimate)

**Enablement (one-time GUI):**

- Plugin `com.intellij.mcpServer` must be enabled (Plugins → Installed).
- Settings → Tools → MCP Server → check **Enable MCP Server**
  (persists to `options/mcpServer.xml` with `enableMcpServer=true`).
- If the settings page does not appear, restart IDEA fully (File → Exit).

**Endpoints (verified):**

```
SSE : http://127.0.0.1:64342/sse      (port = built-in 63342 + 1000)
      Header: IJ_MCP_SERVER_PROJECT_PATH=<project path>
stdio: idea64.exe stdioMcpServer
      env IJ_MCP_SERVER_PORT=64342
      env IJ_MCP_SERVER_PROJECT_PATH=<project path>
```

**Handshake:** standard MCP `initialize` then `tools-list` (slash form) returns 38 tools incl.
`build_project`, `execute_terminal_command`, `get_project_modules`, `read_file`,
`search_symbol`, git tools, xdebug debugger tools.

**Constraints (verified):**

- `build_project` only compiles projects **open in IDEA**; passing an
  unopened project path returns an error listing currently open projects.
- Enabling the server is a GUI action (plugin enable + settings checkbox); the
  headless `appStarter id="mcpServer"` CLI entry exists but is blocked by
  IDEA's single-instance lock when a GUI instance is running.

## pi Integration (extension sketch)

pi extensions can register custom tools via `pi.registerTool()`. Sketch for an
`idea_build` tool that proxies to the IDEA MCP server (SSE/Stdio):

```ts
// extensions/idea-build.ts (illustrative — adapt to your MCP client wiring)
import type { Pi } from "@earendil-works/pi-coding-agent";

export default function (pi: Pi) {
  pi.registerTool({
    name: "idea_build",
    description: "Compile the project with IntelliJ IDEA's resident compiler via MCP (fast incremental). Falls back to CLI message if IDEA unavailable.",
    parameters: {
      type: "object",
      properties: {
        files: { type: "array", items: { type: "string" }, description: "relative paths to compile; empty = whole project" },
        projectPath: { type: "string" },
      },
    },
    async execute(toolCallId, params) {
      // 1. Call IDEA MCP server tool "build_project"
      //    (SSE endpoint e.g. http://127.0.0.1:63342/api/mcp, or stdio)
      // 2. Return { ok, errors[], warnings[] } for the LLM
      // 3. On connection failure → return guidance: use mvnw -o offline
    },
  });
}
```

**Fallback contract:** if the IDEA MCP connection fails (IDEA not running,
no project open), the tool MUST return a clear message directing the LLM to
`mvnw -s <settings> -pl <mod> -am compile -o` (offline, `build-speed.md`).

## Decision Flow

```
Compile verification needed
    │
    ▼
IDEA running + project open? ── yes ──▶ idea_build (MCP build_project)
    │ no                                    │ errors
    ▼                                       ▼
mvnw -o offline (build-speed.md)      report errors, fix, re-verify
```

## Prerequisites / Checks

- [ ] IDEA ≥ 2025.2 (local: 2026.2 ✓)
- [ ] MCP Server enabled in IDEA settings
- [ ] pi client connected (config written by IDEA Auto-Configure, or manual URL)
- [ ] Fallback CLI path still works offline (warmed local repo)
