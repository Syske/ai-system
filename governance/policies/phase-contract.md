# Phase Contract Policy

Defines the machine contract for **Phases** — the execution units inside a
Runtime template (`templates/runtime/runtime-<name>.md`).

A Phase answers *what exists, when it runs, what it depends on, what it
declares*. It does **not** answer *how* — that is the Runtime's Markdown.

| Field | Value |
|---|---|
| Status | Active |
| Type | Policy (machine contract spec) |
| Authority | SSOT for Phase Contract |
| Gate | `tools/checks/phase_contract.py` (check.py item 16) |
| Reference | `reports/P76-PHASE-CONTRACT.md` (proposal + decision record) |
| Related | `governance/policies/proposal-policy.md` (proposal governance) · `rfc/ADR-0006-workflow.md` (Workflow-First) · `rfc/RFC-0003` (size gate) |

---

## 1. Why

Phases are the real execution unit of a Runtime — `bugfix` has 12, `dev-setup`
10, `release` / `spec` 9. But a Phase used to exist only as a Markdown heading
inside a Runtime template, with three consequences:

1. **Conditional execution was invisible to the agent.** `runtime-bugfix.md`'
s 5 hotfix-only Phases were expressed as prose ("Activate only when …") in
   the Phase body and heading suffix. Prompt skeletoning
   (`cli/services/prompt_builder.py::_skeletonize_runtime`) injects only the
   heading and the first requirement line — neither the suffix nor the
   activation sentence reaches the prompt. The agent could not know some Phases
   might not run.
2. **Cross-Phase dependencies could not distinguish state.** Phase 6.6 required
   "the branch is committed and pushed" (execution finished) while Phase 6.7
   required "regression verification passed" (a gate succeeded). Same prose
   shape, materially different meaning.
3. **No Phase declared what it produced.** `grep "Output:|declares"` across
   `templates/runtime/*.md` returned almost nothing; only the Runtime-level
   `# Outputs` block was machine-checked against the workflow's `## Outputs`.

This policy makes all three explicit and checkable.

---

## 2. Responsibility Boundary

```text
workflow.md frontmatter
    phases:            ← Phase Contract (what / when / depends / declares)
        │  phase.id  ↕  binding
        ▼
templates/runtime/runtime-<name>.md
    ## Phase <id> — <name>
        ...            ← execution spec (how)
```

- **The structured frontmatter block decides**: which Phases exist (`id`),
  their `name`, `activation`, cross-Phase `depends` conditions, and
  `declares`.
- **The Runtime Markdown decides**: the steps, checks, gates and commands of
  each Phase.

**There is no second source.** A Phase's identity (`id`) is the join key; the
Runtime heading must match it exactly (gate C5).

**Not a source for either**: the `## Phases` section in the workflow body
(§6) is a *pointer*, never a copy of the table.

---

## 3. Schema (frontmatter block)

```yaml
---
name: bugfix
description: Diagnose and fix software defects.
workflow:
  inputs:
    required: [Project ID, Bug Description]
  next: [review, hotfix-test-doc]
  outputs:
    base: "outputs/bugfix/{yyMMdd}-{descriptor}/"
  phases:
    - id: "1"
      name: Issue Analysis
    - id: "2"
      name: Reproduction
    - id: "3"
      name: Root Cause Analysis
    - id: "4"
      name: Fix Planning
    - id: "4.5"
      name: Approval Gate
      activation: "WHEN mode.approval_gate"
    - id: "4.6"
      name: Branch
      activation: "WHEN mode.phases ∋ branch"
    - id: "5"
      name: Implement
    - id: "6"
      name: Regression Verification
      pass_criterion: "Verification Status = PASS (runtime-verify Phase 7/8 criteria)"
    - id: "6.5"
      name: Commit
      activation: "WHEN mode.phases ∋ commit"
    - id: "6.6"
      name: Submit MR
      activation: "WHEN mode.phases ∋ mr ∧ phase(\"6.5\").completed"
    - id: "6.7"
      name: Doc
      activation: "WHEN mode.phases ∋ doc ∧ phase(\"6\").passed"
    - id: "7"
      name: Completion
---
```

| Field | Required | Meaning |
|---|---|---|
| `id` | yes | Phase number. Decimals allowed (`4.5`). Must equal the Runtime heading's number. |
| `name` | yes | Phase name. Must equal the Runtime heading's name. |
| `activation` | no | Defaults to `always`. Otherwise `WHEN <expression>` (§4). |
| `pass_criterion` | no | The Phase's pass/fail verdict definition. **Required** if any other Phase references `phase("<this id>").passed`. |
| `declares` | no | Defaults to `[]`. File-type artifacts this Phase is **directly responsible** for producing (§5). |

> Frontmatter is excluded from the 100-line body limit
> (`tools/checks/workflow.py::check_workflow_size` strips it), so a large
> `phases` block costs no body budget.

---

## 4. Activation

### 4.1 Grammar (v1 — deliberately not a general expression language)

```
activation := "always" | "WHEN " condition
condition  := atom ( " ∧ " atom )*
atom       := mode_ref | phase_ref
mode_ref   := "mode." key                  # key must exist in the mode config
phase_ref  := "phase(\"" id "\")." state   # id must exist in this phases block
state      := "active" | "completed" | "passed"
```

Examples:

```yaml
activation: always                                  # unconditional (or omit)
activation: "WHEN mode.approval_gate"               # mode config key
activation: "WHEN mode.phases ∋ branch"             # mode contains a phase
activation: "WHEN mode.phases ∋ mr ∧ phase(\"6.5\").completed"
```

**Natural language is forbidden.** A validator cannot parse
`when MR is enabled and the branch was committed in Phase 6.5`, and unparseable
conditions are how the current prose ambiguity arose.

### 4.2 State Semantics (hard rules)

| State | Meaning |
|---|---|
| `phase("<id>").active` | The Phase is enabled for this run. |
| `phase("<id>").completed` | The Phase ran its execution spec to the end. |
| `phase("<id>").passed` | The Phase's **defined** verification / gate / acceptance criterion succeeded. |

**Hard rule**: `phase("<id>").passed` may only reference a Phase that declares
`pass_criterion`.

- `passed` is **not** a synonym for `completed`. Executing to the end does not
  imply the gate passed.
- Do **not** silently degrade a `.passed` reference to `.completed`.
- Do **not** invent a new gate just to satisfy a `.passed` reference. If a Phase
  genuinely has no pass/fail verdict, that is a **contract gap** — fix the
  Phase's criterion, not the reference.

Gate **C2** rejects `.passed` references without `pass_criterion`.

---

## 5. Declares (one-way constraint)

### 5.1 Semantics

| | Meaning |
|---|---|
| `Phase Declares` | **Direct production responsibility.** When the Phase completes, this artifact should exist or be updated. |
| `Workflow Outputs` | **Workflow-level output contract.** The public output set of the whole workflow. An artifact may be contributed by several Phases, or be a final aggregate. |

### 5.2 Constraint

```text
Phase Declares  ⊆  Workflow Outputs        ← GATE ERROR (C3)
Workflow Outputs ⊆ Phase Declares          ← NOT CHECKED
```

Rejecting a declared artifact that the workflow never promised prevents a
Phase from producing a **wild artifact** outside the workflow contract.

The reverse is **not** checked, because most workflows are
"many Phases → few Outputs" (measured: `bugfix` 12 Phases → 4 Outputs,
`external-review` 8 → 2, `code-review` 6 → 1). A Completion Report is typically
an aggregate of several Phases, not the private output of one. Forcing reverse
coverage would produce meaningless declarations written to satisfy a validator.

Only **file-type artifacts** belong in `declares` — not runtime verdicts
(`READY` / `PASS` / `BLOCKED`), which cannot be verified by comparison.

---

## 6. The `## Phases` Section (workflow body)

The workflow body carries a **fixed three-line pointer** — never the table:

```markdown
## Phases

Phase execution contract is defined by the workflow configuration.
The configured Phase contract MUST match the Runtime Phase structure.
```

Rationale: the body is under the 100-line limit (`rfc/RFC-0003`), and several
workflows already sit near it (`code-review` 99, `prepare` 94,
`external-review` 93 body lines). The table is machine data and lives in
frontmatter, which the limit excludes.

This section is **uniform across all workflows** — no per-workflow exception,
and the 100-line limit is not relaxed to make room for it.

The rendered contract is injected into the prompt at execution time (see
`reports/P76-PHASE-CONTRACT.md` §5.3 for the render step; pending in S2).

---

## 7. One Phase per Row (no range merging)

Every Phase is listed individually. Range notation such as `1–3` is **not**
part of the contract.

A range would force the machine to decide whether `1–3` means the three Phases
`1`, `2`, `3` or a single group named `1–3`. As soon as one Phase inside the
range carries its own `activation`, the range's meaning must be reinterpreted
— a "Phase Range DSL" that a simple contract does not need.

Visual compaction in the rendered table is fine (omit a repeated `always`, show
`—` for an empty `declares`); the **data** stays one row per Phase.

---

## 8. Gates

`tools/checks/phase_contract.py` (check.py item 16):

| ID | Check | Level |
|---|---|---|
| C1 | An `activation` references a `phase("<id>")` that does not exist | ERROR |
| C2 | `phase("<id>").passed` where `<id>` has no `pass_criterion` | ERROR |
| C3 | A Phase `declares` an artifact not present in the workflow `## Outputs` | ERROR |
| C4 | A workflow `## Outputs` entry declared by no Phase | *not reported* |
| C5 | The `phases[].id` set differs from the Runtime's `# Phase <id>` heading set | ERROR |
| C6 | Duplicate `id`, or empty `name` | ERROR |
| C7 | `activation` is not parseable per §4.1 (natural language, unknown `mode.*` key) | ERROR |
| C8 | The `## Phases` body section is missing | ERROR (check.py) / BLOCKER (workflow-command-audit) |

**Every gate ships with a negative test** — a fixture that violates it and
asserts the gate fires. A gate that cannot be proven to fail is a gate that may
silently stop working (this repository has hit that class of defect three times
in 2026-09 alone: `proposal-audit` globbing `P*.md` instead of `rglob`,
`path-audit` not checking references inside `reports/`, and
`check_outputs_consistency` returning early when `rt_items` is empty).

---

## 9. Authoring Rules

1. `id` and `name` are **copied verbatim** from the Runtime heading
   (`## Phase <id> — <name>`). Phase identity is a join key (§2), not a
   re-description.
2. `activation` defaults to `always`. Only write `WHEN …` for Phases that can
   genuinely be skipped.
3. Add `pass_criterion` when a Phase has a real gate — and then reference it
   with `.passed`. Do not reference `.passed` speculatively.
4. `declares` is for direct production responsibility only. Leave it empty when
   the Phase produces no file of its own.
5. Adding, removing or renaming a Phase means editing **both** the Runtime
   template and the workflow frontmatter; C5 will fail if only one is done.
6. Phase ids are **stable** once referenced. Renumbering breaks
   cross-references in other Phases, in Skills, and in generated code comments
   (e.g. `Phase 4.6` is referenced by `tools/checks/bugfix_modes.py` and
   `tools/branch-parser-scaffold.py`).

---

## 10. Validation

```bash
python3 -m unittest cli.tests.test_phase_contract   # negative tests + real repo
python3 tools/check.py                              # gate item 16
```

---

## Review Log

| Date | Change | Reviewer |
|---|---|---|
| 2026-09-29 | Initial policy (P76 S1) | User (Approved S1 scope; ⑦⑧⑨ decided) |
