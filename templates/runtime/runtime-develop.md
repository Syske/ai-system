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
- **Location**: code → `projects/<service-id>/`; Completion Report + Test results + updated
  Workspace Context → `workspaces/<project-id>/`; Task Card → `workspaces/<project-id>/openspec/tasks/`

## Phase 4 — Completion

Verify:

- Task Card updated (Completion Definition + Code Quality Checks + Acceptance Criteria all [x])
- Workspace Context updated
- Completion Report generated

Return Completion Report.