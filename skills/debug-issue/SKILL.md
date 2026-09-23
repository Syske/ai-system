---
name: debug-issue
description: Systematically debug issues using graph-powered code navigation. Use when investigating a bug, tracing a failing scenario, or understanding how code paths connect — navigating dependencies, callers, and callees to locate root cause with evidence.
---

## Debug Issue

Use the knowledge graph to systematically trace and debug issues.

### Steps

1. Use `semantic_search_nodes` to find code related to the issue.
2. Use `query_graph` with `callers_of` and `callees_of` to trace call chains.
3. Use `get_flow` to see full execution paths through suspected areas.
4. Run `detect_changes` to check if recent changes caused the issue.
5. Use `get_impact_radius` on suspected files to see what else is affected.

### Tips

- Check both callers and callees to understand the full context.
- Look at affected flows to find the entry point that triggers the bug.
- Recent changes are the most common source of new issues.

## Token Efficiency Rules
Applied per `governance/standards/common/code-graph-tools.md`(single source — no local restatement).
