# Proposal Policy

Defines the format, maintenance process, and gates for ai-system change
proposals (`reports/P*.md`).

## 1. Proposal Format (Required Template)

Every proposal `reports/P<number>-<topic>.md` must contain the following header
table and sections:

```markdown
# Change Proposal: P<number> — <topic>

| Field | Value |
|---|---|
| Status | **Proposed** |
| Type | Structural (...) / Fix / Doc |
| Author | AI Maintainer |
| Created | YYYY-MM-DD |
| Reference | Trigger source (e.g. F#/S# from a MAINTENANCE-… report; user request) |
| Process | OPERATIONS §12 Change Management |

---

## 1. Problem        # Current issue / gap
## 2. Root-Cause     # Root-cause analysis (if applicable)
## 3. Options        # At least two options compared (incl. Recommended)
## 4. Recommendation # Recommended option + rationale
## 5. Proposed Changes  # Concrete change list
## 6. Validation Plan   # How to validate
## 7. Risks             # Risks and mitigation

---

## Review Log

| Reviewer | Decision | Date |
|---|---|---|
| User (AI Maintainer operator) | **Pending** | YYYY-MM-DD |

---

## Implementation Record (YYYY-MM-DD)   # appended after implementation

Applied per approval (OPERATIONS §12 → Implement → Validate):
1. … (concrete changes)
**Validation**: check.py / repo-lint / path-audit result
```

**Rules**:
- Section order is fixed (1 Problem → 7 Risks).
- `Status`, `Review Log`, and `Implementation Record` are machine-readable fields
  (parsed by proposal-audit).
- After the Review Log records a decision, `Status` MUST be updated to the
  corresponding state (see §2) and `reports/PROPOSALS.md` index synced.

### 1.1 Sizing Triage

When a routine run discovers a change worth recording, triage by impact surface
(trigger rule: see the **Issue Capture** section in `AI_OPERATING_RULES` — before
recording, JIT-load this file + OPERATIONS §12).

| Category | Criterion | Handling |
|---|---|---|
| In-place minor fix (L1, **no P-proposal**) | Single-point doc-drift / typo / broken link / text alignment; does NOT touch structure/contract/multiple files/standards/new capability | Fix in place after confirmation + record in diagnostic-log + the maintenance report "Fix Actions" section |
| Proposal (via §12) | Touches structure / contract / multiple files / standards / new capability | File a P-proposal per §1 template + register in PROPOSALS.md/README |

> Same threshold as the `maintain` command minor-fix bypass; this section is the
> single source of truth for it.
>
> **Retroactive evidence**: P32 (prepare workflow Outputs location, a single-line text
> alignment) belonged to the in-place minor-fix path but was filed as a full
> P-proposal — the typical over-processing that occurs when this triage rule is
> absent. Future cases of the same kind should take the in-place bypass.

## 2. Lifecycle

| State | Meaning | Trigger |
|---|---|---|
| `Proposed` | Filed, awaiting review | When a proposal is created |
| `Approved` | Review passed, awaiting implementation | After the Review Log records Approved; **Status should be synced** |
| `Rejected` | Review denied | After the Review Log records Rejected |
| `Implemented` | Implemented and validated | After appending an Implementation Record, Status is set to Implemented |
| `Archived` | Archived (not implemented) | When explicitly abandoned |

**Rules**:
- Status MUST be consistent with the Review Log / Implementation Record (gate-verified).
- Implemented proposals are not deleted; they are retained as history (the
  `PROPOSALS.md` status column is synced).

## 3. Process

1. **Discover issue**: a gap found in practice / during an audit → generate a
   proposal (§1 template).
2. **Index registration**: add a row in `reports/PROPOSALS.md` (status Proposed).
3. **Review**: the user confirms direction (Approved / Rejected).
4. **Status update**: sync the proposal's Status + PROPOSALS.md.
5. **Implement**: OPERATIONS §12 (Analyze → Propose → Review → Approve → Implement
   → Validate).
6. **Record**: append an Implementation Record, Status → Implemented, sync
   PROPOSALS.md.
7. **Audit recycle**: every maintenance run executes `tools/proposal-audit.py`
   and evaluates leftovers (Proposed / unclosed action items).

## 4. Gate

`tools/proposal-audit.py` (wired into `tools/check.py` checks):

| Check | On failure |
|---|---|
| Proposal file must contain a `Status` field | ERROR |
| `Status` must be a legal value (Proposed/Approved/Rejected/Implemented/Archived) | ERROR |
| `Approved` but the Review Log has no Approved entry | WARN |
| `Implemented` but no Implementation Record | ERROR |
| `reports/PROPOSALS.md` index disagrees with the proposal file's Status | WARN |
| Leftovers exist (Proposed / unclosed `- [ ]` action items) | WARN (listed in the audit report) |

## 5. Reference

- OPERATIONS §12 (Change Management)
- AI_OPERATING_RULES (Evolution Principle / Minimal Change)

---

## 6. Reports Index Discipline

`reports/README.md` is the full classified index of reports
(proposals/maintenance/assessments/specs/migrations/analysis). All new reports
must be registered to prevent action items from going adrift:

| Report type | Registration location | Enforced |
|----------|----------|----------|
| Proposal P series | `PROPOSALS.md` (auto-verified by the gate) + README index | Required (proposal-audit ERROR/WARN) |
| MAINTENANCE / assessment / quarterly / spec / migration / analysis | `README.md` matching table | Required (proposal-audit WARN) |

**Rules**:

1. After writing a new report, register it **immediately** in the matching table
   (date / topic / file / leftover action items).
2. For reports with leftover action items, update that column in the index once
   closed.
3. The index files themselves (`reports/README.md`, `PROPOSALS.md`) are not
   registered.
4. `tools/proposal-audit.py` verifies: a `.md` file under `reports/` that is not
   referenced by the README index → WARN.
