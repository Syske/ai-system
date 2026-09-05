# Runtime: Development

Extends:

- runtime-base.md

---

## Purpose

Implement one Specification Task in a repeatable and verifiable manner.

---

## Governance

This Runtime is bound by:

- AI Operating Rules: governance/AI_OPERATING_RULES.md
- Source of Truth: governance/SOURCE_OF_TRUTH.md
- Context Loading: governance/CONTEXT_LOADING.md
- Repository First: governance/REPOSITORY_FIRST.md
- Reflection Rules: governance/REFLECTION_RULES.md

Context is loaded according to governance/CONTEXT_LOADING.md.
Standards are loaded according to loaders/standards-loader.md.

---

## Runtime Responsibilities

Development Runtime coordinates the complete implementation lifecycle.

Responsibilities:

- Resolve Task Context
- Create Implementation Plan
- Invoke Implement Skill (full 10-stage lifecycle)
- Mark Task Card Complete
- Update Workspace
- Generate Completion Report

---

## Runtime Context

Provided by Bootstrap Runtime:

- Environment Context (repository_root, workspaces_root, methodologies_root)

Provided by Dev Setup Runtime:

- Project Context (services list, branches, standards)

Provided by Dev Setup Runtime:

- Workspace Context (available repositories, local paths, git status)

Provided by Runtime Base:

- Runtime Configuration
- Operating Rules
- Loaded Skills
- Loaded Frameworks
- Karpathy Guidelines (mandatory engineering principles)

Resolved by Development Runtime:

- Task
- Related Modules
- Related Tests
- Related Contracts

---

## Phase 1

Resolve Development Context.

Load:

- Task
- Plan
- Specification
- Architecture
- Source Code
- Existing Tests

---

## Phase 2

Planning.

Output:

- Objective
- Dependencies
- Impact Analysis
- File Changes
- Step Sequence (small, independently verifiable steps — see skills/implement/planning.md)
- Risks
- Test Strategy

Wait for confirmation. Present the confirmation request in the system language (config/menu.yaml → locale). <!-- @keep -->

Mid-task checkpoint: after every ~3 implementation steps, briefly verify alignment (goal / plan / done-so-far) before continuing; if output degrades or scope drifts, stop and checkpoint first. <!-- @keep -->

After approval, persist the plan to:

workspaces/{project_id}/openspec/changes/{change_id}/tasks/plans/{task_id}-plan.md

Review and Verify compare the approved plan against the actual implementation.

---

## Phase 3 — Invoke Implement Skill

Execute Implement Skill (skills/implement/SKILL.md).

The Implement Skill executes the full 10-stage lifecycle:

1. Load Task Context
2. Planning
3. Wait For Approval
4. Implementation (coding + documentation)
5. Testing
6. Validation
7. Acceptance Verification
8. Mark Task Card Complete
9. Completion (report)
10. Stop

Formatting gate (Stage 6 Validation):

- Java formatting validation does **not** rely on automatic formatting tools
  (pi-lens Java formatter and google-java-format are disabled / not installed).
- After implementation, run the manual self-check per `task-quality-checklist.md` →
  `Language: Java → Formatting (manual self-check)`: 4-space indentation, multi-line
  Javadoc, no unused imports, consistent with existing code style; the review stage
  verifies this.
- Run the configured development gates from `config/main-chain-capabilities.yaml`
  (`gates.develop`, ordered):
  - `format-check-a` (mandatory): `python3 ai-system/tools/format-check.py <worktree>/src
    --changed --check-commit` — PASS → proceed; FAIL/WARN → fix or justify before
    completing (one-line Javadoc, non-ASCII method names, task-id leaks, Map-assembled
    payloads, 4-space indent ratio, method visibility §Visibility, commit subject
    → commit-content.md). `--check-commit` is REQUIRED (last-commit subject check).
  - `format-jdt-c2` (optional, environment-aware; runs when the local JDT toolchain
    is ready — this machine is ready; on others use explicit `--skip`, exit 3 means
    ENV unavailable) — eclipse JDT formatter dry run against
    `tools/jdt-format-gate/eclipse-format.xml` (IDEA default-derived profile, 375
    settings, calibrated). Exit: 0 PASS / 1 WARN (≤5 files) / 2 FAIL / 3 ENV.
  - `checkstyle-gate` (optional, environment-aware; runs when the repo carries
    `checkstyle.xml`/`suppressions.xml` and the checkstyle jar/JRE are present):
    `{checkstyle_java} -jar {checkstyle_jar} -c <repo>/checkstyle.xml <worktree>/src`
    — `error` = 0 passes; `warning` are collection-only (baseline inventory).
    Missing assets/environment → skip with a note. Incremental mode:
    `python3 ai-system/tools/checkstyle/checkstyle-gate.py <worktree>/src [--config <xml>]`
    — `git status`-driven: checks only `.java` files of this change (relative to the
    repo root, matching `suppressions.xml`); no changes / non-git → fast PASS or full scan.
- Gate results MUST be recorded in the per-run diagnostic log (logs/...md, like the
  runtime-base language gate): each gate name + exit/pass state, so the chain audit
  can verify gates actually ran.
- Gate enable/disable only edits `main-chain-capabilities.yaml → gates.develop`
  (enabled field); templates are not touched.
- Existing files not touched by this change MUST NOT be re-formatted wholesale
  (minimal diff).

Required:

- Follow Specification
- Follow Applied Standards
- Follow Contracts

Never:

- Expand Scope
- Modify Specification
- Modify Contract

---

## Reflection

Before declaring completion, execute Reflection according to governance/REFLECTION_RULES.md.

Evaluate:

1. Simpler implementation possible?
2. Code duplication introduced?
3. Standards violated?
4. Over-engineering present?
5. Anything incomplete?

Record the Reflection Report in the Completion output.
Do NOT modify code during Reflection.

---

# Outputs

Generate:

- Implementation changes (code and documentation)
- Test results
- Updated Task Card (Completion Definition + Code Quality Checks + Acceptance Criteria all [x])
- Updated Workspace Context
- Completion Report
- **Location**: code → `projects/<service-id>/`; Completion Report + Test results →
  `workspaces/<project-id>/openspec/changes/<change-id>/completion-reports/`;
  updated Workspace Context → `workspaces/<project-id>/contexts/`;
  Task Card → `workspaces/<project-id>/openspec/changes/<change-id>/tasks/cards/<task-id>.md`

## Phase 4 — Completion

Verify:

- Task Card updated (Completion Definition + Code Quality Checks + Acceptance Criteria all [x])
- Workspace Context updated
- Completion Report generated

Return Completion Report.
