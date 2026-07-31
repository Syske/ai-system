---
name: repository-governor
description: >
  Analyzes repository health, finds duplication, dead references, and
  structural violations. Generates evolution reports suggesting merges,
  splits, and cleanups. Delegates structural checks to repo-lint.py and
  trend analysis to repo-metrics.py. Trigger when: user says "analyze
  repository", "check health", "find duplication", "suggest improvements",
  "run governance check", or "repository report". Does NOT modify Skills
  or content — only analyzes and reports.
---

# repository-governor

## Overview

repository-governor is the **self-governance Skill** for this AI Engineering
Repository. It analyzes the entire `.opencode/` structure, cross-references
RFC compliance, detects duplication and dead references, and produces
evolution reports.

**Core philosophy:** The repository should govern itself. This Skill is the
feedback loop that keeps it healthy.

## Activation

**Activate when:**
- User says "analyze repository", "check health", "find duplication"
- User says "suggest improvements", "run governance", "audit skills"
- User asks "what needs cleanup" or "how healthy is the repo"
- A new Skill was added and governance check is needed

**DO NOT activate when:**
- User asks to modify a Skill (use the Skill directly)
- User asks for feature development (use implement)
- User asks for a specific bug fix (use bugfix)

## Workflow (7 Stages)

```
 1 — Load repository structure
  2 — Run linter (tools/repo-lint.py)
  3 — Run metrics (tools/repo-metrics.py)
 4 — Analyze duplication
 5 — Analyze dead references
 6 — Generate evolution report
 7 — Finish
```

## Reference Files

| File | Content | Load when |
|---|---|---|
| `workflow.md` | 7-stage detailed workflow | Immediately |
| `analysis.md` | Duplication and dead reference analysis rules | Stage 4-5 |
| `decision.md` | Recommendation priority, severity, governance decisions | Stage 6 |
| `checklists.md` | Repository health checklists | Stage 2-5 |
| `tools/repo-lint.py` | Automated linter | Stage 2 |
| `tools/repo-metrics.py` | Metrics reporter | Stage 3 |
