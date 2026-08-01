# Violation Rules

This document defines how violations are classified and handled.

Violations are deviations from governance, standards, policies, or contracts.

---

## Severity Levels

| Severity | Meaning | Action |
|---|---|---|
| **BLOCKER** | Breaks the system, security, data integrity, or a contract | Must fix before any merge/release. Blocks the workflow. |
| **ERROR** | Violates a standard or policy but is locally recoverable | Must fix before merge. Reported as a failed check. |
| **WARNING** | Deviates from recommended practice; acceptable with justification | Should fix; may defer with a documented reason. |
| **INFO** | Suggestion for improvement | Advisory only; no action required. |

---

## Violation Categories

| Category | Examples | Typical Severity |
|---|---|---|
| **Contract violation** | Interface signature mismatch, breaking change without version bump | BLOCKER |
| **Security violation** | Secrets in code, missing auth, unsafe deserialization | BLOCKER |
| **Data integrity** | SQL without rollback, missing data migration | BLOCKER |
| **Specification deviation** | Implementation differs from approved spec/scenario | ERROR |
| **Standard violation** | Naming, documentation, testing standard not followed | ERROR |
| **Naming violation** | `repo-lint.md` conventions not followed | ERROR |
| **Context loading violation** | Loading the entire repository tree | ERROR |
| **Change control violation** | Unclassified change applied (L2/L3 bypassed) | ERROR |
| **Style / minor quality** | Dead code, missing doc, formatting | WARNING |
| **Optimization suggestion** | Better abstraction, readability improvement | INFO |

---

## Handling

1. **Detect.** Violations are detected by automated tools (`tools/repo-lint.py`, `tools/check.py`) or by review.
2. **Classify.** Assign a severity from the table above.
3. **Fix or justify.**
   - BLOCKER / ERROR: fix before proceeding. Never merge with an open BLOCKER.
   - WARNING: fix or record a documented justification.
   - INFO: record as a suggestion; may be deferred.
4. **Record.** Deviations are reported in the Completion Report (per `AI_OPERATING_RULES.md`).

---

## Change Control Reference

Violations during an active workflow are classified by Change Control
(see `governance/AI_OPERATING_RULES.md`):

| Level | Meaning | Handling |
|---|---|---|
| L1 | In-task adjustment | Apply directly, record in Deviations |
| L2 | Approach change | Stop, report, continue after confirmation |
| L3 | Contract-level change | Stop, route to prepare/spec, resume only with updated Task Card |

Unclassified changes are treated as L3 by default.

---

## Enforcement

- Automated: `tools/repo-lint.py` (BLOCKER/ERROR), `tools/check.py` (integrity gate)
- Manual: `governance/review-standard.md` (skill review)
- Quality definitions: `governance/policies/quality-gates.md`
