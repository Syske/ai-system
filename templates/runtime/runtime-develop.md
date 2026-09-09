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
- Plan (`tasks/plans/{task_id}-plan.md` — if present)
- Specification
- Architecture
- Source Code
- Existing Tests

### Plan Gate (A1 — 计划定案门禁)

Before any implementation, an **approved plan** must exist:

- **Plan present and approved**: verify it still matches the Task Card (scope /
  contracts / acceptance), then proceed to Phase 3.
- **Plan absent**: planning is MANDATORY. Do NOT self-decide design during
  context loading or investigation — every Task Card blank, cross-document
  design decision and contract gap must be resolved inside the plan (Phase 2)
  and confirmed by the user before any code is written.

Prohibited:

- Entering implementation with an unconfirmed, self-inferred design (the
  T-009 anti-pattern: filling card blanks + cross-reading many docs + SDK field
  research as an un-gated investigation, then implementing).
- Treating context-loading investigation as a substitute for a confirmed plan.

If the plan is missing and design gaps are found during investigation: STOP,
  write them into the Phase 2 plan, and wait for user confirmation. <!-- @keep -->

### Investigation Discipline (A2/A3 — 注意力与上下文纪律)

During context loading / investigation:

- Checkpoint every ~3 tool steps: briefly report progress / remaining / risks to
  the user (ATTENTION_MANAGEMENT) — do NOT run a long un-briefed chain (the
  T-009 interruption anti-pattern).
- Read large source files (services / adapters > ~200 lines) by targeted
  grep / method-locator, not full-file reads; load only what the Task needs.
- Defer SDK / third-party API field verification to implementation-time
  compile checks — do not unzip jars or research APIs during investigation
  unless the confirmed plan depends on it. <!-- @keep -->

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
- Method-Granularity Design Summary (P50): for design-critical methods (interface/contract surface) — signature, return granularity & failure-branch representation, resource/error semantics (refactor / resource-class cards extend to internal critical semantics: finally/reset, key state transitions)
- Reuse Decision (P50): every planned method marked reuse / extend / new — after a mandatory existing-implementation scan (REPOSITORY_FIRST / karpathy Read Existing Code); discovered similar implementations surface an explicit reuse decision for confirmation (no silent copy or re-implementation)

Wait for confirmation. Present the confirmation request in the system language (config/menu.yaml → locale). The plan confirmation includes the method-granularity design summary: AI self-checks the plan against the P49 checklists (return-granularity / non-necessary entities) first, then presents. <!-- @keep -->

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
    `--changed` 增量口径（P51）：git status 驱动，仅扫本 change 改动文件；
    JDT hunk × 改动行交集——存量基线豁免（BASELINE 记录诊断日志）、新增行拦截
    （NEW-DIFF），退出码按新增差异文件数映射（存量债不再整文件报 diff）。
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

Post-Implementation Confirmation (P50, conditional — before the final commit):

- Trigger: Task Card marked `实现后置确认: required` (interface/contract surface,
  refactor / behavior change, cross-component / cross-repo contract — set by
  task-splitter; AI feature-detection as fallback). Mechanical cards (DTO / channel
  beans / config / docs) skip.
- Present the implementation method-granularity summary and wait for user
  confirmation before committing:
  - new/changed methods + signatures
  - return granularity & failure-branch representation (P49 self-check applied)
  - resource/error semantics (refactor class)
  - reuse-decision execution (per plan reuse scan; any bypass flagged)
  - deviations vs the confirmed plan (plan-level deviations surface as L2 stop-confirm)
  - gate results summary (format-check-a / format-jdt-c2 / checkstyle / unit tests)
- Confirmation requested in the system language (config/menu.yaml → locale).
  Outcome recorded in the per-run diagnostic log. <!-- @keep -->

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
