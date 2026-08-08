# Context Retention Strategy

Unified cross-tool strategy for selectively retaining / dropping context.
Applies to all AI tools (pi / opencode); each tool executes it through its own
compaction mechanism.

## When to Apply

- Before finishing a work unit or switching tasks
- When session context reaches 50% or more
- When attention degrades / output quality drops
- Before starting a new session (produce a handoff summary)

## Keep (by priority)

| Priority | Content | Examples |
|---|---|---|
| P0 | Decisions and conclusions of the current task | root cause, rationale, acceptance result |
| P0 | Unfinished todos and next steps | open issues, next action, blockers |
| P0 | Contract / interface changes | modified API, fields, protocols |
| P1 | Key files and commit records | changed file list, commit hashes |
| P1 | Governance decisions | adopted standards, disciplines, policies |
| P2 | Context clues | key log lines, reproduction steps |

## Drop

| Content | Reason |
|---|---|
| Early exploration detail | process noise; conclusions already captured |
| Raw compile / test output | keep only result + error lines |
| Repeated tool calls | already-completed diagnostic steps |
| Long diffs | keep only summary + blast radius |
| History unrelated to current task | completed work units |

## Execution by Tool

| Tool | Mechanism | Retention Injection |
|---|---|---|
| pi | `/compact [keep X, drop Y]` | instructions passed directly as the compaction prompt |
| opencode | `/compact` (no custom instructions) | **submit the retention priorities as a user message immediately before `/compact`**, stating the compaction must follow them |

## Handoff Summary Template (new session / new task)

```
## Handoff Summary
- Task: <current goal>
- Done: <conclusions + commits>
- Decisions: <key choices + rationale>
- Leftovers: <todos + next step>
- Contract changes: <API / fields / file list>
- Notes: <risks / blockers>
```

## Related

- `CONTEXT_LOADING.md` — Session Health Levels (40/60/80 thresholds)
- `AI_OPERATING_RULES.md` — Context Budget Discipline
