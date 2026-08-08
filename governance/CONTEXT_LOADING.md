# Context Loading Strategy

Version: 1.0

---

## Purpose

Define how every Runtime loads context.

Context is expensive. Every token loaded increases noise and reduces focus.

The goal is minimal, deterministic, just-in-time context loading.

---

## Principle

```
LOAD ONLY WHAT THE TASK REQUIRES. NOTHING MORE.
```

---

## Loading Order

Context must be loaded in this priority order:

```
Task Card
    ↓
Contract
    ↓
Specification
    ↓
Affected Source Code
    ↓
Coding Standards (applied)
    ↓
Referenced Skills
```

Higher items are loaded first. If a higher item resolves the question, stop — do not load lower items.

---

## Forbidden Patterns

Never:

- Load the entire repository tree into context
- Load all Specifications at once
- Load all Task Cards at once
- Load documentation unrelated to the current task
- Load examples before the relevant standard
- Load historical memory unless the task specifically requires it

---

## Per-Runtime Rules

### spec

Load: Preparation Report → Architecture Summary → existing specs/contracts in change scope

Do NOT load: full repository source code

### dev-setup

Load: Environment Context → Workspace Metadata → repository YAML metadata → spec reference (identity only)

Do NOT load: repository source code

### develop

Load: Task Card → Specification → Contracts → Applied Standards → affected modules and tests

Do NOT load: entire repository tree

### bugfix

Load: Bug Description → Logs → Stack Trace → affected modules → related tests

Do NOT load: entire repository tree

### review

Load: Task Card → Specification → Contracts → Applied Standards → implementation changes → test results

Do NOT load: entire repository tree

### prepare

Load: Environment Context → Change Request → target repository structure and entry points

Do NOT load: entire repository tree

---

## Context Reuse

Context loaded by a prior Runtime phase is available for subsequent phases.

Do not reload the same context unless it has changed.

---

## Context Budget Discipline

Context is a finite budget. Long sessions, verbose tool output, and MCP tool
schemas silently consume it. Follow these rules to keep headroom:

1. **Big outputs → summarize before continuing.** After a large tool result
   (compile log, full diff, search dump), replace it with a short summary in
   the working notes; do not carry the raw output forward.
2. **MCP tool schemas are the biggest lever.** Each MCP tool costs ~500 tokens
   of schema per call context; a large server (20+ tools) can outweigh all
   skills combined. Keep MCP servers to what the current task needs; disable
   unused ones.
3. **Load on demand, release after use.** Skills/rules/standards are loaded
   per task (see Loading Order); once resolved, do not keep re-reading them.
4. **Audit after changes.** When adding a skill, rule, MCP server, or long
   reference doc, estimate the token cost it adds and whether it stays under
   the session budget.
5. **Sluggishness / degraded output is a signal.** If a session feels slow or
   quality drops, audit context consumption (inventory loaded components,
   classify always/sometimes/rarely, rank token savings) before continuing.

## Layered Context Management

Prevention beats compression. Route work by operation type so the main
session holds only decisions + conclusions:

| Operation type | Route | Why |
|---|---|---|
| Exploration / search / audit / multi-file scan | **subagent isolation** (pi-worker style) | returns conclusions only; main context stays flat |
| Large tool output (compile, diff, log dump) | keep summary only (result + key lines) | ~70% of bloat is raw output |
| Session > 50% context | **active `/compact` with focus instructions** | pre-empts attention decay |
| New large task | **new session + handoff summary** | clean window for deep reasoning |

Selective retention is defined in **`CONTEXT_RETENTION.md`** (what to keep / drop by
priority, plus the handoff summary template). Follow it when compacting or
switching tasks. For pi: pass the retention priorities as `/compact` instructions.

## Session Health Levels

| Usage | Action |
|---|---|
| < 40% | Normal; deep reasoning OK |
| 40-60% | Summarize big outputs; delegate exploration to subagents |
| > 60% | Actively compact with focus; consider session boundary |
| > 80% | Split session now; keep only essential conclusions |

---

## Reference

Every Runtime Template must reference this document.

The reference line is:

```
Context loading: governance/CONTEXT_LOADING.md
```
