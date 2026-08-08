---
name: handoff
description: Produce a session handoff summary when switching tasks, compacting context, or ending a session. Use when the user is about to start a new task, compact the conversation (/compact in pi), close a session, or hand work to another agent/tool. Follows CONTEXT_RETENTION Keep/Drop priorities so decisions, conclusions, and todos survive while exploration noise is dropped.
---

# Session Handoff

## Purpose

Preserve P0/P1 context across a context boundary (compaction, task switch,
new session, cross-tool handoff) while dropping exploration noise.

Source of truth: `governance/CONTEXT_RETENTION.md` (Keep/Drop priorities).

## When to Use

- User switches to a new task and wants continuity
- User is about to compact the session (pi `/compact`)
- User is closing a session or moving to a new one
- User hands work to another tool (pi → opencode or vice versa)
- Session context is at/above 50% and a boundary is imminent

## Steps

### 1. Gather P0/P1 items

Collect from the current conversation:

- **Task**: what is the current goal / task card
- **Done**: conclusions reached + commit hashes / file paths
- **Decisions**: key choices + rationale (P0)
- **Leftovers**: open todos, next step, blockers (P0)
- **Contract changes**: modified API / fields / protocols / file list (P0)
- **Notes**: risks, reproduction steps, key log lines (P2 optional)

### 2. Drop noise

Exclude from the handoff:

- Early exploration detail (conclusions already captured)
- Raw compile / test output (keep only result + error lines)
- Repeated tool calls and completed diagnostic steps
- Long diffs (keep only summary + blast radius)
- History unrelated to the current task

### 3. Emit handoff summary

Use the template below. Keep it under ~50 lines; P0 items first.

### 4. Persist session state (cross-session)

Write the handoff summary to the project's persistent session-state file so
work survives across sessions AND across tools (pi / opencode):

```
workspaces/<project_id>/contexts/session-state.md
```

- Overwrite the previous state (it is the *current* state, not a log).
- Keep the file under ~60 lines; P0 items first.
- The file is loaded by the next session's opening context when work resumes.
- If the project has no `contexts/` dir yet, create it.
- This file is workspace state — NOT Coding Memory (experience) and NOT a
  report (outputs/).

## Handoff Summary Template

```
## Handoff Summary
- Task: <current goal>
- Done: <conclusions + commits>
- Decisions: <key choices + rationale>
- Leftovers: <todos + next step>
- Contract changes: <API / fields / file list>
- Notes: <risks / blockers / repro>
```

## Per-Tool Injection

| Tool | How to apply the handoff |
|---|---|
| pi | Present the summary to the user, then run `/compact 保留: <P0 items> 丢弃: <drop list>` with the priorities spelled out |
| opencode | Post the summary as a user message immediately before `/compact`, stating the compaction must follow it (opencode `/compact` accepts no custom instructions) |
| New session | Paste the summary as the opening context of the new session. When resuming a paused task, first read `workspaces/<project_id>/contexts/session-state.md` and the handoff summary, then continue |

## Validation

- Every P0 item (task/done/decisions/leftovers/contract) is present
- No raw tool output, no exploration logs, no repeated diagnostics
- Summary is self-contained: a fresh agent could continue from it
- Session state persisted to `workspaces/<project_id>/contexts/session-state.md`
  (unless user opted out)
