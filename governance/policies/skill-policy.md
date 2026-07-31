# Contribution Guide

This document describes how to add new Skills or modify existing ones.

---

## 1. Before You Start

Read these documents:

| Document | Reason |
|---|---|
| `RFC-0001-repository-architecture.md` | Understand what a Skill, Workflow, Playbook are |
| `RFC-0002-skill-specification.md` | Understand mandatory components and quality gates |
| `repo-lint.md` | Understand naming rules |

## 2. Check for Overlap

Before creating a new Skill, search existing Skills for overlapping purpose:

```shell
grep -r "your-keyword" ai-system/skills/*/skill.md
```

If overlap > 60%, do not create a new Skill. Extend the existing one instead.
If overlap > 30% but < 60%, document the relationship.

## 3. Create the Skill

```
ai-system/skills/<name>/
  skill.md              # Required: entrypoint with YAML frontmatter
  workflow.md           # Recommended: if skill.md > 80 lines
  decision.md           # Recommended: if > 5 decision points
  checklists.md         # Optional: skill-specific items only
  examples.md           # Optional: end-to-end examples
  anti-patterns.md      # Optional: behaviors to avoid
```

Follow RFC-0002 for the exact file format.

## 4. Run the Linter

```shell
python tools/repo-lint.py --repo-root .
```

Fix all BLOCKER and ERROR items before proceeding.

## 5. Submit for Review

Follow `review-standard.md` for the review workflow.

## 6. Record Metrics Baseline

```shell
python tools/repo-metrics.py --repo-root . --snapshot metrics/baseline-<date>.json
```

## 7. Update the Optimization Report (if applicable)

If the new Skill significantly changes the repository structure, update
`reports/REPOSITORY-OPTIMIZATION-REPORT.md` or create a new architecture
review document in `reports/`.

---

## Quick Reference

| Action | Command |
|---|---|
| Check overlap | `grep -r "keyword" ai-system/skills/*/skill.md` |
| Run linter | `python tools/repo-lint.py --repo-root .` |
| Run linter (JSON) | `python tools/repo-lint.py --repo-root . --json` |
| Run metrics | `python tools/repo-metrics.py --repo-root .` |
| Save metrics snapshot | `python tools/repo-metrics.py --repo-root . --snapshot metrics/<name>.json` |
| Compare metrics | `python tools/repo-metrics.py --repo-root . --compare metrics/<previous>.json` |
| Dependency graph | `python tools/dependency-graph.py --repo-root .` |
