# Repository Health Model

This document defines the 15-dimension health model used to evaluate
repository quality. Every dimension produces: current state, risk level,
recommendation, priority, and estimated impact.

---

## Dimension 1: Repository Structure

| Attribute | Value |
|---|---|
| **Question** | Is every asset in its correct directory? |
| **Check** | Skills in `.opencode/skills/`, Workflows in `.opencode/workflows/`, etc. |
| **Risk if failing** | Assets are undiscoverable; tooling breaks |
| **Data source** | Stage 2 scan |

## Dimension 2: Skill Architecture

| Attribute | Value |
|---|---|
| **Question** | Do Skills follow RFC-0002? |
| **Check** | Frontmatter, workflow stages, decision rules, delegation |
| **Risk if failing** | Inconsistent Skills; AI agents cannot rely on them |
| **Data source** | Stage 6 review |

## Dimension 3: Workflow Architecture

| Attribute | Value |
|---|---|
| **Question** | Do Workflows orchestrate without implementing? |
| **Check** | No Maven commands, no test logic, no embedded knowledge |
| **Risk if failing** | Workflows become bloated; Skills become untestable |
| **Data source** | Stage 7 review |

## Dimension 4: Capability Distribution

| Attribute | Value |
|---|---|
| **Question** | Is every capability owned by exactly one Skill? |
| **Check** | Capability matrix shows no >60% overlap between any two Skills |
| **Risk if failing** | Duplicated effort; inconsistent behavior |
| **Data source** | Stage 8 analysis |

## Dimension 5: Dependency Graph

| Attribute | Value |
|---|---|
| **Question** | Is the dependency graph acyclic and shallow? |
| **Check** | No cycles; max depth ≤ 4 hops |
| **Risk if failing** | Circular dependencies cause cascading failures |
| **Data source** | Stage 5 analysis |

## Dimension 6: Knowledge Organization

| Attribute | Value |
|---|---|
| **Question** | Is project knowledge in `.opencode/knowledge/` and separated from Skills? |
| **Check** | No project-specific content inside Skills |
| **Risk if failing** | Skills are not reusable across projects |
| **Data source** | Stage 2 scan + Stage 7 review |

## Dimension 7: Playbook Coverage

| Attribute | Value |
|---|---|
| **Question** | Are all major engineering topics covered by Playbooks? |
| **Check** | Maven, Mockito, ReflectionTestUtils, Spring Boot Test, JUnit |
| **Risk if failing** | Duplicated knowledge across Skills |
| **Data source** | Stage 9 analysis |

## Dimension 8: Checklist Reuse

| Attribute | Value |
|---|---|
| **Question** | Are common checklists shared rather than duplicated? |
| **Check** | Validation, completion, retry checklists in `.opencode/checklists/`, referenced |
| **Risk if failing** | Inconsistent quality gates; duplicated maintenance |
| **Data source** | Stage 9 analysis |

## Dimension 9: Template Reuse

| Attribute | Value |
|---|---|
| **Question** | Are report templates shared rather than embedded? |
| **Check** | Templates in `.opencode/templates/`, referenced from Skills |
| **Risk if failing** | Inconsistent report formats |
| **Data source** | Stage 9 analysis |

## Dimension 10: Naming Consistency

| Attribute | Value |
|---|---|
| **Question** | Do all components follow `repo-lint.md`? |
| **Check** | kebab-case, lowercase skill.md, name matches directory |
| **Risk if failing** | Confusion, broken tooling |
| **Data source** | Stage 4 analysis |

## Dimension 11: Version Consistency

| Attribute | Value |
|---|---|
| **Question** | Are RFC and ADR versions consistent? |
| **Check** | No gaps in RFC numbering; ADRs reference correct RFCs |
| **Risk if failing** | Lost traceability |
| **Data source** | Stage 2 scan |

## Dimension 12: Lifecycle Status

| Attribute | Value |
|---|---|
| **Question** | Is every asset in the correct lifecycle stage? |
| **Check** | Draft → Experimental → Stable → Deprecated → Archived |
| **Risk if failing** | Unmaintained assets confuse users |
| **Data source** | Stage 6-7 review |

## Dimension 13: Repository Complexity

| Attribute | Value |
|---|---|
| **Question** | Is the repository getting simpler or more complex over time? |
| **Check** | Trend of total lines, total files, dependency depth, duplicate ratio |
| **Risk if failing** | Growing complexity makes maintenance unsustainable |
| **Data source** | Stage 3 metrics + trend comparison |

## Dimension 14: Repository Growth

| Attribute | Value |
|---|---|
| **Question** | Is growth intentional and controlled? |
| **Check** | Every new asset classified correctly; no unauthorized growth |
| **Risk if failing** | Bloat; loss of focus |
| **Data source** | Stage 3 metrics trend |

## Dimension 15: Backward Compatibility

| Attribute | Value |
|---|---|
| **Question** | Are `.opencode/skills/` and `.opencode/commands/` unchanged? |
| **Check** | No Skills moved or removed; no commands renamed |
| **Risk if failing** | Broken AI agent invocations |
| **Data source** | Stage 4 analysis |

---

## Health Score Calculation

```
Score = (passing_dimensions / 15) * 100
```

| Score | Status | Meaning |
|---|---|---|
| 90-100 | HEALTHY | Repository is in good shape |
| 70-89 | DEGRADED | Some dimensions need attention |
| 50-69 | AT RISK | Multiple dimensions failing |
| < 50 | CRITICAL | Immediate intervention required |

## Maintenance State Update (aic-maintain Output)

Report fields, the `config/maintenance.yaml` update contract and the
`last_findings` discipline for a maintenance run (aic-maintain command).

- **Maintenance Report** fields:
  - 工具校验结果（lint BLOCKER/ERROR/WARN 计数、指标变化）
  - 巡检发现（按严重度分级）
  - 一致性抽查结论（逐项通过/失败）
  - 修复动作与建议清单
  - quick-check 趋势（近 N 日快照对比）

- 完成后更新 `ai-system/config/maintenance.yaml`（提交态，系统级；跨机维护连续性）：

  ```yaml
  last_run: {date}
  mode: {mode}
  next_maintenance: {date + interval}   # weekly:+7d monthly:+30d quarterly:+90d
  last_findings: [...]                    # 本次问题摘要（系统级 only）
  ```

- **last_findings 纪律**：只放系统级（指标/工具门禁/提案/修复）。机器/环境观察
  （如本机 python shim、extensions 仓未提交、本机是否生成 ~/.config）**只进 per-run
  diagnostic-log（logs/，本地）**，不写入此提交态文件。判定触发词：含
  `当前机器` / `WSL` / `shim` / `extensions 仓...未提交` → 机器级 → 排除。
