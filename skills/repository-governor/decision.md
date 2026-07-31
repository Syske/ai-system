# Decision Rules

---

## Recommendation Priority

| Severity | Priority | Action timeline |
|---|---|---|
| BLOCKER | P0 | Fix immediately |
| ERROR | P1 | This cycle |
| HIGH duplication | P1 | This cycle |
| Broken reference | P1 | This cycle |
| WARNING | P2 | Next cycle |
| MEDIUM duplication | P2 | Next cycle |
| Orphaned playbook | P2 | Next cycle |
| LOW duplication | P3 | When possible |
| Orphaned checklist | P3 | When possible |
| INFO | P4 | Consider |

---

## Governance Decisions

| Finding | Action |
|---|---|
| Skill > 1000 lines | Recommend split |
| Skill fails one-sentence test | Recommend split |
| Two Skills overlap > 60% | Recommend merge |
| Skill references deprecated Skill | Recommend update |
| Workflow references non-existent Skill | Fix reference |
| Playbook unreferenced for 3 months | Recommend archive |
| No RFC for existing pattern | Recommend RFC creation |

---

## Change Recommendations

When repository-governor suggests a change, it must specify:

| Field | Example |
|---|---|
| Type | split / merge / extract / archive / create |
| Component | `bugfix` |
| Reason | Exceeds 1000 lines |
| Action | Split analysis.md into separate diagnostic Skill |
| Effort | Medium |
| Risk | Low — additive only |

---

## Stopping Conditions

| Condition | Action |
|---|---|
| Linter script fails to execute | Stop, report "Linter unavailable" |
| Metrics script fails to execute | Stop, report "Metrics unavailable" |
| No issues found | Report "Repository healthy" |
| Issues found | Generate report with recommendations |
| User requests specific analysis | Scope to user's request |
| User cancels | Stop |
