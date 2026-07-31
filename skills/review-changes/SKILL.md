---
name: review-changes
description: Perform a structured code review using change detection and impact
---

## When to Use

Use `review-changes` when:
- Assessing risk/impact of uncommitted local changes
- Quick knowledge-graph-driven analysis（not a formal quality gate）
- Exploring codebase impact of an idea before writing a spec

Use `review` (workflow) instead when:
- A task needs a formal quality gate before `verify`
- Task Card compliance verification is required
- The full Design / Code / Standards / Security / Performance review is needed

---

## Review Changes

Perform a thorough, risk-aware code review using the knowledge graph.

### Steps

1. Run `detect_changes` to get risk-scored change analysis.
2. Run `get_affected_flows` to find impacted execution paths.
3. For each high-risk function, run `query_graph` with pattern="tests_for" to check test coverage.
4. Run `get_impact_radius` to understand the blast radius.
5. For any untested changes, suggest specific test cases.

### Output Format

Provide findings grouped by risk level (high/medium/low) with:
- What changed and why it matters
- Test coverage status
- Suggested improvements
- Overall merge recommendation

## Token Efficiency Rules
- ALWAYS start with `get_minimal_context(task="<your task>")` before any other graph tool.
- Use `detail_level="minimal"` on all calls. Only escalate to "standard" when minimal is insufficient.
- Target: complete any review/debug/refactor task in ≤5 tool calls and ≤800 total output tokens.
