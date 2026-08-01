# Skill Lifecycle

This document defines the lifecycle stages that every Skill in the
repository passes through.

---

## Lifecycle Stages

```
                     ┌──────────┐
                     │  Draft   │
                     └────┬─────┘
                          │ RFC approved, passes quality gates
                          ▼
                     ┌──────────┐
                     │ Proposed │
                     └────┬─────┘
                          │ Linter passes, metrics recorded
                          ▼
                     ┌──────────┐
                     │  Active  │
                     └────┬─────┘
                          │ Replaced or superseded
                          ▼
                     ┌────────────┐
                     │ Deprecated │
                     └────┬───────┘
                          │ Archived after deprecation period
                          ▼
                     ┌──────────┐
                     │ Archived │
                     └──────────┘
```

---

## Stage: Draft

**Entry condition:** An idea or need for a new Skill exists.

**Activities:**
1. Write RFC-0002-compliant plan
2. Identify triggers, purpose, inputs, outputs
3. Design workflow stages
4. Identify dependencies (which Skills will it delegate to)
5. Run overlap check against existing Skills

**Duration:** Unlimited, but must be approved within 2 weeks or dropped.

**Gate to Proposed:**
- RFC-0002 compliance plan approved
- Overlap check passes (no >60% overlap with existing Skill)
- Dependency graph remains acyclic

---

## Stage: Proposed

**Entry condition:** RFC approved, Skill design is complete.

**Activities:**
1. Create the Skill directory with all files
2. Run `tools/repo-lint.py` — must pass with no BLOCKER or ERROR
3. Run `tools/repo-metrics.py` — baseline metrics recorded
4. Submit for review per `governance/review-standard.md`
5. Address review feedback

**Duration:** Must pass review within 1 month or return to Draft.

**Gate to Active:**
- Linter passes (BLOCKER=0, ERROR=0)
- Review approved
- Metrics baseline recorded

---

## Stage: Active

**Entry condition:** Skill passes all quality gates and review.

**Activities:**
1. Skill is available for use by AI agents
2. Skill is available for invocation by Workflows
3. Linter runs on every change
4. Metrics are tracked over time

**Maintenance requirements:**
- Linter must pass on every commit
- At least one metrics check per month
- Dependencies must be kept current
- If the Skill references a deprecated Skill, it must be updated

**Duration:** Until the Skill is replaced or superseded.

---

## Stage: Deprecated

**Entry condition:** A newer Skill replaces this one, or the capability is
no longer needed.

**Activities:**
1. ADR documents deprecation reason
2. All Workflows referencing this Skill are updated
3. All Skills referencing this Skill are updated
4. `skill.md` frontmatter updated: `status: deprecated`
5. Deprecation notice added: `DEPRECATED: Use <replacement> instead.`

**Grace period:** 1 month (Workflows and Skills have 1 month to migrate).

**Gate to Archived:**
- No remaining references from any Active Skill or Workflow
- Grace period has elapsed

---

## Stage: Archived

**Entry condition:** Deprecation period ended, no remaining references.

**Activities:**
1. Skill directory moved to `archive/skills/<name>/`
2. Entry in archive index created
3. Linter updated to exclude archive directory from main checks

**Recovery:** An archived Skill can be restored to Active if:
- An ADR explains why it was unarchived
- All quality gates pass
- Linter passes

---

## Lifecycle Decisions

| Decision | Criteria | Authority |
|---|---|---|
| **Create** | New capability, no overlap > 60% | RFC approval |
| **Split** | Skill exceeds 1000 lines, or has multiple responsibilities | Linter flag + review |
| **Merge** | Two Skills overlap > 60% | Overlap detection + review |
| **Deprecate** | Replacement exists or capability obsolete | ADR + review |
| **Archive** | Deprecation grace period ended | Automated (linter check) |
| **Restore** | New need for archived capability | ADR + review |

## Split Decision

A Skill should be split when:

| Indicator | Threshold |
|---|---|
| Total lines | > 1000 lines |
| Workflow stages | > 10 stages |
| Responsibilities | Fails one-sentence test |
| Dependencies | Depends on 5+ other Skills |

## Merge Decision

Two Skills should be merged when:

| Indicator | Threshold |
|---|---|
| Overlap in purpose | > 60% overlap |
| Overlap in triggers | > 50% trigger overlap |
| Always invoked together | > 80% co-invocation rate |
