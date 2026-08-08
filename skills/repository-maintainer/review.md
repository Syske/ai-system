# Asset Review Criteria

This document defines how every asset type is reviewed. Use during
Stages 6-7 of the workflow.

---

## Skill Review (15 criteria)

| # | Criterion | Weight | Pass condition |
|---|---|---|---|
| 1 | Purpose clarity | HIGH | One-sentence purpose is clear and specific |
| 2 | Single responsibility | HIGH | Passes one-sentence test without "and" |
| 3 | Trigger conditions | HIGH | ≥ 3 trigger phrases, ≥ 1 anti-trigger |
| 4 | Workflow completeness | HIGH | ≥ 3 stages, each with Goal/Steps/Output |
| 5 | Decision rules | MEDIUM | Stopping conditions + delegation rules defined |
| 6 | Delegation correctness | HIGH | Delegates to existing Skills only |
| 7 | Knowledge duplication | HIGH | No content that belongs in a Playbook |
| 8 | Checklist duplication | MEDIUM | No checklists that duplicate `.opencode/checklists/` |
| 9 | Playbook references | MEDIUM | References Playbooks when referencing engineering knowledge |
| 10 | Total size | MEDIUM | No single file exceeds 1000 lines (aggregated reference files exempt) |
| 11 | Dependency complexity | MEDIUM | ≤ 3 direct dependencies |
| 12 | Frontmatter quality | HIGH | YAML frontmatter with name + description |
| 13 | Naming convention | MEDIUM | Directory name matches `name:` field |
| 14 | Maven delegation | HIGH | No hardcoded Maven CLI commands (unless java-maven) |
| 15 | Evolution risk | LOW | Changes to this Skill would not cascade widely |

### Skill recommendations

| Score | Recommendation |
|---|---|
| 90-100% | Keep |
| 70-89% | Simplify |
| 50-69% | Split or Merge |
| < 50% | Archive |

---

## Workflow Review (7 criteria)

| # | Criterion | Pass condition |
|---|---|---|
| 1 | Orchestration-only | No Maven commands, no test logic, no fix patterns |
| 2 | Skill references exist | All referenced Skills exist in `.opencode/skills/` |
| 3 | Execution order clear | Numbered stages or directed graph |
| 4 | Handoff conditions | Defined for each Skill transition |
| 5 | Stopping conditions | Defined for normal and failure paths |
| 6 | No embedded knowledge | No Playbook-level content |
| 7 | File size | ≤ 100 lines |

### Workflow recommendations

| Finding | Recommendation |
|---|---|
| Contains implementation logic | Extract logic to Skills |
| Repeats another workflow | Merge or reference |
| Orphaned (unreferenced) | Archive |
| Missing stopping conditions | Add them |

---

## Playbook Review (6 criteria)

| # | Criterion | Pass condition |
|---|---|---|
| 1 | Single topic | Covers exactly one technical area |
| 2 | No execution instructions | No commands, no workflow stages |
| 3 | No project-specific content | No paths, no org names |
| 4 | Referenced | At least one Skill references it |
| 5 | Coverage | Major patterns in the topic are covered |
| 6 | Up-to-date | No obviously outdated guidance |

### Playbook recommendations

| Finding | Recommendation |
|---|---|
| Unreferenced (orphaned) | Archive or add references |
| Outdated guidance | Update content |
| Overlaps another Playbook | Merge |
| Too large (> 300 lines) | Split into sub-topics |

---

## Knowledge Review (4 criteria)

| # | Criterion | Pass condition |
|---|---|---|
| 1 | Descriptive, not procedural | Describes architecture, terms, conventions |
| 2 | No execution instructions | No commands, no steps |
| 3 | Accurate | Matches current project reality |
| 4 | Referenced | At least one Skill references it |

### Knowledge recommendations

| Finding | Recommendation |
|---|---|
| Stale content | Update or archive |
| Duplicates another knowledge doc | Merge |
| Contains execution instructions | Extract to Skill or Playbook |

---

## Template Review (4 criteria)

| # | Criterion | Pass condition |
|---|---|---|
| 1 | Structure only | Contains placeholders, not filled content |
| 2 | No project-specific content | No hardcoded names or paths |
| 3 | Referenced | At least one Skill references it |
| 4 | Useful | Would be missed if removed |

### Template recommendations

| Finding | Recommendation |
|---|---|
| Unreferenced | Archive |
| Duplicates another template | Merge |
| No placeholders | Convert to template format |

---

## Checklist Review (4 criteria)

| # | Criterion | Pass condition |
|---|---|---|
| 1 | Theme-focused | Single theme (validation, completion, retry) |
| 2 | Referenced | At least one Skill references it |
| 3 | Non-duplicating | Items don't duplicate another checklist |
| 4 | Mechanical | Items are verifiable (yes/no) |

### Checklist recommendations

| Finding | Recommendation |
|---|---|
| Orphaned | Archive or add references |
| Items duplicated in another checklist | Merge |
| Items too interpretive | Rewrite as verifiable items |
