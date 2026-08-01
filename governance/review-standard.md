# Skill Review Process

This document defines the review process for changes to Skills and
other repository components.

---

## 1. When Review Is Required

| Change type | Review required | Reviewer |
|---|---|---|
| New Skill creation | Yes | Repository Governor (or senior engineer) |
| Skill workflow changes | Yes | At least 1 peer |
| Skill decision rule changes | Yes | At least 1 peer |
| RFC creation | Yes | Repository Governor |
| ADR creation | Yes | Repository Governor |
| Playbook changes | Yes | At least 1 peer |
| Playbook creation | Yes | At least 1 peer |
| Knowledge document changes | Recommended | Subject matter expert |
| Template changes | Recommended | Team lead |
| Linter/metrics changes | Yes | Repository Governor |
| Bugfix to a Skill | Recommended | Peer review optional |

## 2. Review Checklist for New Skills

- [ ] `skill.md` exists with valid YAML frontmatter
- [ ] `name:` matches directory name
- [ ] Description includes trigger phrases and anti-triggers
- [ ] Description is 100-1024 characters
- [ ] Single responsibility confirmed (one-sentence test)
- [ ] No single file exceeds 1000 lines (aggregated reference files exempt)
- [ ] No Maven commands (unless the Skill is java-maven)
- [ ] No project-specific paths or names
- [ ] No duplicated checklists (check against `ai-system/skills/*/checklists.md`)
- [ ] No duplicated playbook content
- [ ] Dependency graph is acyclic
- [ ] Stopping conditions defined
- [ ] Delegation documented
- [ ] At least 3 workflow stages
- [ ] Stage 8 (or equivalent hard gate) present if user confirmation needed
- [ ] Linter passes with no BLOCKER or ERROR

## 3. Review Checklist for Skill Changes

- [ ] Change is traceable to a single purpose (no mixed concerns)
- [ ] Change does not introduce prohibited content (Maven, paths, duplicate)
- [ ] Change does not break the Skill's workflow structure
- [ ] Change preserves the Skill's single responsibility
- [ ] Dependencies remain acyclic
- [ ] Linter still passes

## 4. Review Process Flow

```
Submit change
  ↓
Run linter: tools/repo-lint.py
  ↓
  ├─ BLOCKER or ERROR → Fix, resubmit
  │
  └─ PASS or WARNING → Assign reviewer
                         ↓
                        Review
                         ↓
                        ├─ Approve → Merge
                        └─ Changes requested → Fix, resubmit
```

## 5. Escalation

If a reviewer and author disagree on a design decision, the dispute is
escalated to the Repository Governor (or the most senior engineer).

The decision is recorded as an ADR.
