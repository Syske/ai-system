# Code Graph Tools (MCP) — Token Efficiency Standard

**Single source** for graph-tool usage rules. Skills that read the code graph **reference** this
standard in one line; they do not restate the rules (that restatement was the source of the
duplication this standard removes).

## Purpose

Keep code-graph exploration cheap: one minimal entry call, minimal detail by default.

## Scope

Skills that call the code-graph MCP tools (`code-review-graph`):

- `skills/debug-issue/SKILL.md`
- `skills/explore-codebase/SKILL.md`
- `skills/review-changes/SKILL.md`

## Rules

1. **ALWAYS** start with `get_minimal_context(task="<your task>")` before any other graph tool.
2. Use `detail_level="minimal"` on all calls. Only escalate to `"standard"` when minimal is
   insufficient.

## Rationale

Heavy exploration tools return whole source sections; calling them first (or at `standard`
detail) floods the session context and forces compaction mid-task. The minimal-context entry
call tells you *which* symbols matter before you pay for their bodies.

## Enforcement

Loaded with the consuming skill (see `loaders/standards-loader.md` → Task-Type Standards →
Code-Graph Tool Task). Violations surface as context blowup, which the session-level
context-management rules (`governance/CONTEXT_LOADING.md`) treat as a discipline breach.

## Violations

Skipping the minimal entry call is a **Minor** violation (cost, not correctness) — handle per
`governance/violation-rules.md`.