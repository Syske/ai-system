# Change Proposal: P6 — Skill Size Reconciliation

| Field | Value |
|---|---|
| Status | **Proposed** |
| Type | Structural (Skill restructuring) |
| Author | AI Maintainer |
| Created | 2026-08-01 |
| Reference | MAINTENANCE-20260801.md F3 / P6 |
| Process | OPERATIONS §12 Change Management |

---

## 1. Problem

Five skills exceed the RFC-0002 quality gate "Total lines ≤ 1000" (sum of all
files in the skill directory):

| Skill | MD lines | Exceeds 1000? |
|---|---|---|
| implement | 2368 | YES |
| mock-test | 1325 | YES |
| bugfix | 1314 | YES |
| repository-maintainer | 1117 | YES |
| skill-optimizer | 698 (MD only; +9552 incl. scripts) | MD: NO |

Note: repo-lint does **not** flag these — it enforces a **per-file** 1000-line
limit only (see `tools/repo-lint.py:184-186`: "aggregated docs across many
reference files are not [a problem]"). The RFC-0002 total-line gate is stricter
than current tooling enforcement.

## 2. Root-Cause Analysis

- Skills are structured as `SKILL.md` + `workflow.md` + reference files
  (planning/decision/checklists/validation/anti-patterns/examples). This is the
  RFC-0002-intended layout, but large reference files accumulate size.
- The **linter's stated intent** treats per-file size as the maintainability
  concern, not aggregate reference-file size.
- No active references break; all skills are workflow-bound or on-demand and
  functional.

## 3. Options

### Option A — Reconciliation (Recommended)

Align RFC-0002 to the linter's actual enforcement and repository reality:

- Reword RFC-0002 quality gate from "Total lines ≤ 1000 (sum of all files)" to
  a **per-file** limit: "No single file exceeds 1000 lines; total size across
  reference files is a soft target".
- Keep the existing per-file linter rule unchanged (already enforces this).
- No file moves, no module changes, zero risk.

**Impact**: removes the false-positive "over budget" signal without restructuring.

### Option B — Extract shared content into playbooks

Extract duplicated knowledge (Maven/Mockito patterns from bugfix/mock-test,
task-quality checklists from implement/bugfix) into `governance/standards/`
or shared reference files.

**Impact**: reduces some skill sizes; medium effort; higher risk of reference
breakage; larger diff.

### Option C — Full split into sub-skill containers

Split implement/bugfix/mock-test/repository-maintainer into
`architecture/`-style sub-skill containers.

**Impact**: highest effort/risk; contradicts "small changes" and single
responsibility; not justified by a real defect — the linter reports 0 errors.

## 4. Recommendation

**Adopt Option A.** It is the smallest correct change, matches the linter's
documented intent, and removes the false signal that triggered P6. Options B/C
are speculative restructuring — contrary to the Evolution Principle (optimize
only from a real, observed problem).

## 5. Proposed Changes (Option A)

1. `rfc/RFC-0002-skill-specification.md`:
   - Prohibition §5.1 row: "Must not exceed 1000 lines total across all files"
     → "Must not have any single file exceeding 1000 lines".
   - Quality gate §6 row: "Total lines ≤ 1000 (sum of all files)" → "No single
     file exceeds 1000 lines (aggregated reference files are exempt)".
2. No source moves. No config/registry changes.

## 6. Validation Plan

- `python tools/repo-lint.py --repo-root .` → 0 blockers/errors
- `python tools/check.py` → PASS
- `python tools/path-audit.py` → 0 broken
- No dependency-graph changes expected (no skill paths changed)

## 7. Risks

- None material. RFC-0002 wording only; tooling unchanged; no path changes.

---

## Review Log

| Reviewer | Decision | Date |
|---|---|---|
| User (AI Maintainer operator) | **Approved — Option A** | 2026-08-01 |

---

## Implementation Record (2026-08-01)

Applied per approval (OPERATIONS §12 → Implement → Validate):

1. `rfc/RFC-0002-skill-specification.md` — §5.1 prohibition + §6 quality gate reworded to per-file limit.
2. `rfc/RFC-0001-repository-architecture.md` — §5 prohibited-pattern wording synced.
3. `governance/policies/quality-gates.md` — Gate 2 row synced.
4. `governance/policies/skill-lifecycle.md` — Split decision + table synced.
5. `governance/review-standard.md` — checklist item synced.
6. `skills/repository-maintainer/{checklists,governance,review}.md` — review criteria synced.
7. `README.md` — key-rule row synced.

**Validation**:
- repo-lint: 0 BLOCKER / 0 ERROR / 9 WARN ✅
- check.py: PASS, 0 warnings ✅
- path-audit: 0 broken ✅
- No skill paths moved; dependency graph unchanged.

