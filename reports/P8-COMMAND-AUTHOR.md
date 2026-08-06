# Change Proposal: S2 — `aic-command` Authoring Command

| Field | Value |
|---|---|
| Status | **Implemented** |
| Type | Structural (new command + scaffold tool) |
| Author | AI Maintainer |
| Created | 2026-08-05 |
| Reference | MAINTENANCE-2026-08-05.md S2; symmetry with S1 (`aic-workflow`) |
| Process | OPERATIONS §12 Change Management |

---

## 1. Problem

The Command layer has no authoring/scaffold capability, symmetric to the gap
S1 fixed for the Workflow layer. Adding a command today requires a fully manual
multi-file operation:

1. `cli/commands/aic-<name>.md` — command definition (frontmatter description + Steps/Output/Guardrails)
2. `config/menu.yaml` — sections entry (`kind: command`) + `command_fields` + `field_icons`
3. `config/i18n/{locale}.yaml` — field_notes / option_descriptions
4. Optional: `cli/services/command_hooks.py` (lifecycle hooks, e.g. `scan`)

`check.py` catches `aic-` prefix / kebab-case / `opsx-` remnants / duplicates /
prompt-build / wizard-field failures only *after* the fact. No command enforces
necessity assessment (OPERATIONS §15 Golden Rule, skill-policy §2 overlap,
Evolution Principle) before creation.

## 2. Root-Cause Analysis

- Command authoring is a system-maintenance task → Command layer (mirrors
  `aic-skill-source` / `aic-workflow`), not a workflow.
- Commands are pure markdown prompt wrappers (prompt_builder renders
  `templates/prompts/command.md`); functional overlap between commands is
  subtle and undocumented → necessity assessment is even more important than
  for workflows.
- `check.py` already validates the full command chain (file naming, menu
  referential integrity, i18n keys, prompt build, wizard dry-run) → a
  scaffolded artifact can be verified deterministically.

## 3. Options

### Option A — `aic-command` command + `tools/command-scaffold.py` (Approved)

- `tools/command-scaffold.py <name> [--description "..."]`:
  - Generates `cli/commands/aic-<name>.md` (frontmatter description + Steps/Output/Guardrails skeleton)
  - Prints the menu.yaml / i18n registration checklist (sections, command_fields, field_icons, optional hooks)
  - `--list`: prints existing commands + descriptions for overlap assessment
  - Non-destructive, kebab-case validation, idempotent (refuses existing names)
- `cli/commands/aic-command.md` — command definition with a mandatory
  necessity-assessment gate (layer classification → overlap → Evolution
  Principle → user confirmation) before scaffolding.
- `config/menu.yaml` + `config/i18n/zh.yaml` — register the `command` command.

### Option B — Command only (no tool)

Smallest diff; still fully manual; no structural guarantees.

### Option C — Documentation only

Defer tooling; document the manual process.

## 4. Recommendation

**Adopt Option A** — symmetric to S1, eliminates structural failure modes
(menu/i18n drift, name collisions, missed registration) and enforces the same
necessity gate the Workflow layer now has.

## 5. Proposed Changes (Option A)

1. `tools/command-scaffold.py` — new scaffold tool.
2. `cli/commands/aic-command.md` — command definition (necessity gate first).
3. `config/menu.yaml` — register `command` in `commands_maintenance` + `command_fields`.
4. `config/i18n/zh.yaml` — field notes.
5. `tools/README.md` — register the tool (check_tools_readme gate).

## 6. Validation Plan

- `python tools/check.py` → PASS (11 commands)
- `python tools/repo-lint.py --repo-root .` → 0 blockers/errors
- `python tools/path-audit.py` → 0 broken
- Functional: scaffold `demo-cmd`, fill content, run `check.py`, verify, clean up.

## 7. Risks

- Command names must stay `aic-` kebab-case and non-colliding — enforced by the tool + check.py.
- Hooks (Python) cannot be auto-generated — the scaffold lists them as a manual step.

---

## Review Log

| Reviewer | Decision | Date |
|---|---|---|
| User (AI Maintainer operator) | **Approved — Option A** | 2026-08-05 |

---

## Implementation Record (2026-08-05)

Applied per approval (OPERATIONS §12 → Implement → Validate):

1. `tools/command-scaffold.py` — new command scaffold tool (non-destructive
   aic-<name>.md generation, `--list`, idempotent duplicate refusal).
2. `cli/commands/aic-command.md` — command definition with necessity-assessment
   gate (layer classification → overlap → Evolution Principle → user confirm).
3. `config/menu.yaml` + `config/i18n/zh.yaml` — registered `command` command
   + fields + icons.
4. `tools/README.md` — registered command-scaffold.py.
5. Functional validation: scaffolded `demo-cmd` end-to-end; cleaned up.
6. `reports/MAINTENANCE-2026-08-05.md` — S2 record.

**Validation**: check.py PASS; repo-lint 0/0/9; path-audit 0 broken.
