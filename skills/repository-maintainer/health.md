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
