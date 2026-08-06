---
name: repository-maintainer
description: >
  Continuously maintains the AI engineering repository by analyzing health,
  reviewing all asset types (Skills, Workflows, Playbooks, Knowledge,
  Templates, Checklists), detecting duplication and orphaned content,
  verifying RFC compliance, and generating prioritized maintenance plans.
  Treats the repository as a software product — optimizes for consistency,
  reusability, and long-term maintainability.
  Trigger when: user says "maintain repository", "audit repository",
  "review all skills", "check health", "find issues", "repository needs
  cleanup", or quarterly maintenance cycle starts.
  Does NOT modify assets without explicit user approval.
---

# repository-maintainer

## Overview

repository-maintainer is the **repository-as-product engineer**. It treats
the entire `<repo-root>/`, `.opencode/`, and `tools/` ecosystem as a software product
and continuously improves its consistency, maintainability, reusability,
discoverability, and composability.

**Core philosophy:** Optimize the whole, not the parts. Prefer simplification
over expansion. Prefer composition over duplication. The repository should
be easier to maintain after every maintenance cycle.

## Activation

**Activate when:**
- User says "maintain repository", "audit everything", "review all skills"
- User says "check health", "find issues", "repository needs cleanup"
- Quarterly or monthly maintenance cycle starts
- After adding a new Skill or significant structural change

**DO NOT activate when:**
- User asks to analyze a single Skill (use repository-governor instead)
- User asks for software development (use implement, bugfix, etc.)
- User asks for a quick health check only (use tools/repo-lint.py)

## Workflow (14 Stages)

```
 1 — Observe                             8 — Analyze Capabilities
 2 — Analyze Repository                   9 — Analyze Shared Assets
 3 — Collect Metrics                     10 — Generate Risks
 4 — Analyze Architecture                11 — Prioritize Recommendations
 5 — Analyze Dependencies                12 — Generate Repository Maintenance Report
 6 — Review Skills                       13 — WAIT FOR USER APPROVAL
 7 — Review Workflows/Playbooks/etc.     14 — Execute and Finish
```

**Stage 13 is a hard gate.** No structural changes without approval.

## Quick Decision Table

| Question | Rule |
|---|---|
| What asset type does a finding belong to? | Skill / Workflow / Playbook / Knowledge / Template / Checklist |
| Should this Skill be kept? | Evaluate 15 criteria; recommend Keep/Simplify/Split/Merge/Archive |
| Should this Playbook be kept? | Evaluate reuse, duplication, coverage, outdated content |
| Is circular dependency present? | Detect via dependency graph, recommend break |
| Is there duplicate knowledge? | Cross-reference all assets for overlapping content |
| Should I make changes now? | No — wait for user approval (Stage 13 hard gate) |

## Reference Files

| File | Content | Load when |
|---|---|---|
| `workflow.md` | 14-stage detailed maintenance workflow | Immediately |
| `health.md` | 15-dimension repository health model | Stage 3-4 |
| `review.md` | Asset review criteria (Skill/Workflow/Playbook/Knowledge/Template/Checklist) | Stage 6-7 |
| `analysis.md` | Dependency and capability analysis | Stage 5, 8 |
| `metrics.md` | Metrics collection and trend comparison | Stage 3 |
| `governance.md` | RFC compliance verification | Stage 4 |
| `decision.md` | Asset classification, lifecycle, priority decisions | Stage 10-11 |
| `checklists.md` | Quality gates and review checklists | Stage 12 |
