# IDEA Build via MCP — Compile Verification Strategy

> Solves: CLI Maven cold-start compile is slow (62-70s on SNAPSHOT-heavy
> multi-module services). IntelliJ IDEA's resident incremental compiler is
> the fast path; IDEA 2025.2+ exposes it to external agents via the built-in
> **MCP Server** (`build_project` tool).

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
