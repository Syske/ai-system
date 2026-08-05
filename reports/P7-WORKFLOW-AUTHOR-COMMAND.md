# Change Proposal: S1 — `aic-workflow` Authoring Command

| Field | Value |
|---|---|
| Status | **Proposed** |
| Type | Structural (new command + optional scaffold tool) |
| Author | AI Maintainer |
| Created | 2026-08-05 |
| Reference | MAINTENANCE-2026-08-05.md F1 / S1 |
| Process | OPERATIONS §12 Change Management |

---

## 1. Problem

Adding a new workflow today requires a fully manual multi-file operation:

1. `workflows/<name>.md` — 8-section contract (Purpose/Runtime/Preconditions/Inputs/Context/Outputs/Exit Criteria/Next)
2. `config/workflows/<name>.yaml` — minimal registry entry (version/name/workflow/runtime)
3. `templates/runtime/runtime-<name>.md` — runtime template (extends runtime-base.md)
4. Register in `config/workflow-registry.yaml`
5. Register in `config/menu.yaml` sections (+ icon, optional number)
6. Update `workflows/README.md` selection table

No command or skill scaffolds this. The Skill layer has `aic-skill-source` + `skill-author` + `skill-policy`; the Workflow layer only has documentation (OPERATIONS §1.10.1 + workflows/README.md template + ADR-0006). As workflow count grows (11 → 14 in the last month), manual registration risks:

- 8-section contract drift (missing / out-of-order sections)
- registry ↔ config ↔ md ↔ runtime reference gaps
- missing menu / README registration
- `check.py` / `repo-lint.py` catching failures only *after* the fact

## 2. Root-Cause Analysis

- Workflow authoring is a system-maintenance task, not a business process — so it does **not** belong in the workflow registry as a meta-workflow (violates RFC-0003 "Workflow orchestrates, does not implement").
- The correct layer is the **Command layer** (mirrors `aic-skill-source` / `aic-maintain`), optionally backed by a thin scaffold script (mirrors `tools/pack.py` / `tools/setup.py`).
- `check.py` already validates the full chain (registry → config → workflow md → runtime md, 8-section presence, Next convention, menu referential integrity, wizard dry-run) — so a scaffolded artifact can be verified deterministically.

## 3. Options

### Option A — `aic-workflow` command + `tools/workflow-scaffold.py` (Recommended)

Add:

- `tools/workflow-scaffold.py <name> [--purpose "..."] [--next <workflow>]`:
  - Generates `workflows/<name>.md` from the 8-section template (with purpose/next pre-filled, runtime path defaulted to `templates/runtime/runtime-<name>.md`)
  - Generates `config/workflows/<name>.yaml` (minimal: version/name/workflow/runtime)
  - Generates `templates/runtime/runtime-<name>.md` skeleton (extends runtime-base.md, governance block, empty phases)
  - Appends the registry entry to `config/workflow-registry.yaml` (idempotent: refuses if name exists)
  - Prints the menu.yaml / README registration checklist
  - Non-destructive: never overwrites existing files; validates name (kebab-case, not already registered)
- `cli/commands/aic-workflow.md` — command definition guiding the operator to run the scaffold, fill content, register menu/README, and run `check.py` + `repo-lint.py`.
- `config/menu.yaml` + `config/i18n/zh.yaml` — register the command with fields (Workflow Name required; Purpose, Next Workflow optional).

**Impact**: new command + new tool + menu/i18n entries. Deterministic scaffolding; the 8-section contract and reference chain are guaranteed by script; content authoring stays with the operator/AI. Matches the "registry-driven add" best practice already documented in `reports/analysis-2026-08-03-structure-workflows/recommendations.md`.

### Option B — Command only (prompt-driven, no tool)

Add only `cli/commands/aic-workflow.md` + menu/i18n entries. The command instructs the operator to create the files manually per the template.

**Impact**: smallest diff (no Python tool). But still fully manual; the script's structural guarantees (correct 8-section order, matching runtime path, registry append) are not enforced — identical failure modes as today, only better-documented.

### Option C — Extend `workflow-architect` skill

Add a "produces registerable assets" output stage to `skills/architecture/workflow-architect`.

**Impact**: skill-level, reusable as design guidance. But skills do not modify the system (implementation belongs to commands/tools); the registration mechanics would still need a command. Weaker fit than Option A for the stated problem (automating the multi-file registration).

## 4. Recommendation

**Adopt Option A.** It is the smallest correct change that eliminates the structural failure modes (contract drift, broken references, missed registration) while keeping content authoring human/AI-driven. Option B is the fallback if a new Python tool is considered over-engineering; Option C addresses design, not registration.

## 5. Proposed Changes (Option A)

1. `tools/workflow-scaffold.py` — new scaffold tool (kebab-case validation, idempotent file generation, registry append, checklist output; registered in `tools/README.md`).
2. `cli/commands/aic-workflow.md` — command definition (frontmatter description; inputs: Workflow Name / Purpose / Next Workflow; steps: run scaffold → fill 8 sections → register menu + README → run check.py / repo-lint.py → report).
3. `config/menu.yaml` — add `workflow` command to `commands_maintenance` section + `command_fields` entry.
4. `config/i18n/zh.yaml` — add field_notes for the new fields.
5. `tools/checks/` — no change expected (command auto-discovered; scaffold tool validated by `tools/README.md` registration check).
6. `workflows/README.md` — no template change (already documents the 8-section contract).

## 6. Validation Plan

- `python tools/check.py` → PASS (discovers 10 commands, wizard dry-run includes `workflow`)
- `python tools/repo-lint.py --repo-root .` → 0 blockers/errors
- `python tools/path-audit.py` → 0 broken
- Functional: run `python tools/workflow-scaffold.py demo-wf --purpose "Demo" --next review`, then `check.py`; verify generated files, then `Remove-Item` the demo artifacts (scaffold is non-destructive but the demo files must be cleaned up).

## 7. Risks

- New tool adds surface area; mitigated by thin scope (file generation + registry append only) and `check.py` as the safety net.
- Menu/i18n edits must satisfy `check_menu` (title keys, icon presence). Mitigated by following existing `maintain`/`pack` registration patterns.
- Future workflows still require content authoring effort — expected; the tool removes structural risk, not domain thinking.

---

## Review Log

| Reviewer | Decision | Date |
|---|---|---|
| User (AI Maintainer operator) | **Approved — Option A** | 2026-08-05 |

---

## Implementation Record (2026-08-05)

Applied per approval (OPERATIONS §12 → Implement → Validate):

1. `tools/workflow-scaffold.py` — new scaffold tool (kebab-case validation, non-destructive generation of `workflows/<name>.md` + `config/workflows/<name>.yaml` + `templates/runtime/runtime-<name>.md`, idempotent registry append, manual-step checklist).
2. `tools/README.md` — registered workflow-scaffold.py (satisfies `check_tools_readme`).
3. `cli/commands/aic-workflow.md` — command definition (scaffold → fill 8 sections → menu/README registration → check.py/repo-lint validation).
4. `config/menu.yaml` — `commands_maintenance` section entry + `command_fields` (Workflow Name required; Purpose, Next Workflow optional) + field icons.
5. `config/i18n/zh.yaml` — field notes for Workflow Name / Purpose / Next Workflow.
6. `reports/MAINTENANCE-2026-08-05.md` — S1 record.

**Validation**:
- Functional: scaffolded `demo-wf` end-to-end (4 files + registry append → filled 8 sections → check.py PASS 15 workflows → idempotent re-run refused → cleaned up, restored 14 workflows) ✅
- `check.py`: PASS, 0 warnings ✅
- `repo-lint.py`: 0 BLOCKER / 0 ERROR / 9 WARN ✅
- `path-audit.py`: 0 broken ✅

