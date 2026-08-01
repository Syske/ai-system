# Quality Gates

This document defines the quality gates that every component in the
repository must pass. These gates are enforced by `tools/repo-lint.py`
and by the repository-governor Skill.

---

## Gate 1: Structural Integrity

| Check | Scope | Failure |
|---|---|---|
| skill.md exists | Every Skill | Missing entrypoint |
| YAML frontmatter present | Every skill.md | Missing frontmatter |
| `name:` matches directory name | Every skill.md | Name mismatch |
| `description:` present | Every skill.md | Missing description |
| workflow.md exists (if skill.md > 80 lines) | Skills > 80 lines | Missing workflow |
| No orphaned files (files not referenced by any skill.md) | All files | Orphan detected |

## Gate 2: Content Quality

| Check | Scope | Failure |
|---|---|---|
| No single file exceeds 1000 lines (aggregated reference files exempt) | Per Skill | Skill exceeds limit |
| No Maven commands (`mvn ` strings) | Non-java-maven skills | Prohibited command |
| No absolute paths (`C:\`, `/home/`, `/usr/`) | All files | Hardcoded path |
| No hardcoded project names | All files | Non-generic content |
| Description 100-1024 characters | Every skill.md | Invalid length |
| At least 3 trigger phrases in description | Every skill.md | Insufficient triggers |

## Gate 3: Dependency Integrity

| Check | Scope | Failure |
|---|---|---|
| All Skill references exist in `ai-system/skills/` | All files referencing skills | Broken reference |
| No circular dependencies | Skill dependency graph | Cycle detected |
| Foundation Layer (L1) depends only on L1 | java-maven, codegraph-helper, karpathy | Layer violation |
| Test Layer (L2) depends only on L1-Foundation | mock-test | Layer violation |

## Gate 4: Duplication

| Check | Scope | Failure |
|---|---|---|
| No checklist duplication with `ai-system/skills/*/checklists.md` | All checklists.md | Duplicate detected |
| No playbook content duplication | All skill files | Duplicate detected |
| No template content duplication | All skill files | Duplicate detected |

## Gate 5: Documentation

| Check | Scope | Failure |
|---|---|---|
| Stopping conditions defined | Every skill.md | Missing stop conditions |
| Delegation documented | Every skill.md | Missing delegation |
| At least 3 workflow stages | Every workflow.md | Insufficient stages |

---

## Gate Severity

| Severity | Meaning | Action |
|---|---|---|
| **BLOCKER** | Must fix before merge | Linter exit code 2 |
| **ERROR** | Should fix before merge | Linter exit code 1 |
| **WARNING** | Should fix, but not blocking | Linter exit code 0 with report |
| **INFO** | Suggestion for improvement | Linter reports only |
