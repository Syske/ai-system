---
name: explore-codebase
description: Navigate and understand codebase structure using the knowledge graph. Use when mapping modules, finding entry points, tracing usage of a class or method, or preparing a change — producing a structural overview before modifying code.
---

## Explore Codebase

Use the code-review-graph MCP tools to explore and understand the codebase.

## Relationship with explore

This skill is the **standalone codebase-structure understanding** capability —
knowledge-graph driven, independent of the CLI wizard. It is **not** loaded by
any command; use it directly when you need to map, trace, or prepare a change
against the actual code.

For OpenSpec workspace exploration (active changes, artifact reference,
capturing decisions during requirement clarification), use the **`explore`**
skill (`skills/explore/SKILL.md`) — it is loaded by the `aic-explore` command
and carries the OpenSpec-aware methodology.

**Which to use:**

| 场景 | 用哪个 |
|------|--------|
| 映射模块/查找入口点/追踪类或方法的调用（独立任务） | **explore-codebase**（本技能） |
| 变更前结构概览（知识图谱，≤5 次调用） | **explore-codebase**（本技能） |
| `aic-explore` 命令触发的 OpenSpec 工作区导航 | **explore** |
| 需求澄清时引用 proposal/design/tasks 工件 | **explore** |

### Steps

1. Run `list_graph_stats` to see overall codebase metrics.
2. Run `get_architecture_overview` for high-level community structure.
3. Use `list_communities` to find major modules, then `get_community` for details.
4. Use `semantic_search_nodes` to find specific functions or classes.
5. Use `query_graph` with patterns like `callers_of`, `callees_of`, `imports_of` to trace relationships.
6. Use `list_flows` and `get_flow` to understand execution paths.

### Tips

- Start broad (stats, architecture) then narrow down to specific areas.
- Use `children_of` on a file to see all its functions and classes.
- Use `find_large_functions` to identify complex code.

## Token Efficiency Rules
- ALWAYS start with `get_minimal_context(task="<your task>")` before any other graph tool.
- Use `detail_level="minimal"` on all calls. Only escalate to "standard" when minimal is insufficient.
- Target: complete any review/debug/refactor task in ≤5 tool calls and ≤800 total output tokens.
