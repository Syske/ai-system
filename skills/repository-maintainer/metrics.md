# Metrics

This document defines the metrics collected during repository analysis.
Use during Stage 3 of the workflow.

---

## Asset Counts

| Metric | Source | Data type |
|---|---|---|
| Number of Skills | `.opencode/skills/` directory count | Integer |
| Number of Workflows | `.opencode/workflows/` directory count | Integer |
| Number of Playbooks | `.opencode/playbooks/` file count | Integer |
| Number of Knowledge documents | `.opencode/knowledge/` file count | Integer |
| Number of Templates | `.opencode/templates/` file count | Integer |
| Number of Checklists | `.opencode/checklists/` file count | Integer |
| Number of RFCs | `D:\workspace\ai-workspace\ai-system\rfc\RFC-*` file count | Integer |
| Number of ADRs | `D:\workspace\ai-workspace\ai-system\rfc\NNNN-*` file count | Integer |
| Number of governance documents | `D:\workspace\ai-workspace\ai-system\governance` file count | Integer |

## Size Metrics

| Metric | Calculation |
|---|---|
| Total repository lines | Sum of all lines in `.opencode/`, `D:\workspace\ai-workspace\ai-system`, `tools/` |
| Average Skill size | Total Skill lines / Number of Skills |
| Largest Skill | Max(Skill total lines) |
| Smallest Skill | Min(Skill total lines) |
| Total RFC lines | Sum of all RFC file lines |
| Total governance lines | Sum of all governance file lines |

## Quality Metrics

| Metric | Calculation | Good | Warning | Critical |
|---|---|---|---|---|
| Frontmatter compliance | % of Skills with valid frontmatter | 100% | 80-99% | < 80% |
| Naming compliance | % of Skills with name matching directory | 100% | 90-99% | < 90% |
| Linter BLOCKER count | Count from tools/repo-lint.py | 0 | 1-3 | > 3 |
| Linter ERROR count | Count from tools/repo-lint.py | < 5 | 5-15 | > 15 |
| Linter WARNING count | Count from tools/repo-lint.py | < 10 | 10-20 | > 20 |

## Duplication Metrics

| Metric | Calculation |
|---|---|
| Duplicate ratio | Number of duplicate checklist items / Total checklist items |
| Shared asset ratio | Number of shared assets referenced / Total shared assets |
| Playbook coverage | Number of Playbooks referenced / Total Playbooks |
| Template usage | Number of Templates referenced / Total Templates |
| Checklist usage | Number of Checklists referenced / Total Checklists |

## Dependency Metrics

| Metric | Calculation |
|---|---|
| Dependency count | Total edges in dependency graph |
| Max depth | Longest transitive dependency chain |
| Cycle count | Number of circular dependencies |
| Orphan count | Number of assets with zero references |
| Isolation ratio | Orphan count / Total assets |

## Lifecycle Metrics

| Metric | Calculation |
|---|---|
| Draft Skills | Skills in Draft stage |
| Experimental Skills | Skills in Experimental stage |
| Stable Skills | Skills in Stable stage |
| Deprecated Skills | Skills in Deprecated stage |
| Archived Skills | Skills in Archived stage |

## Trend Comparison

When a previous metrics snapshot exists, compute deltas:

```
Metric: Skill count
  Previous: 15
  Current:  17
  Delta:    +2
  Trend:    ↑ (growing)

Metric: Duplicate ratio
  Previous: 0.12
  Current:  0.10
  Delta:    -0.02
  Trend:    ↓ (improving)

Metric: Linter ERROR count
  Previous: 25
  Current:  20
  Delta:    -5
  Trend:    ↓ (improving)
```

## Metric Collection Method

```shell
# Collect all metrics via the metrics tool
python tools/repo-metrics.py --repo-root . --snapshot D:\workspace\ai-workspace\ai-system\metrics\<date>.json

# Compare with previous snapshot
python tools/repo-metrics.py --repo-root . --compare D:\workspace\ai-workspace\ai-system\metrics\<previous>.json
```
