# Runtime: Change Impact

Extends:

- runtime-base.md

---

## Purpose

Analyze the impact, risks, and modification plan for a specific code target before changing it.

The Change Impact Runtime analyzes a method, class, or code block across multiple projects
before modification. It produces a single report covering impact scope, risks, and a
modification plan. No implementation is performed.

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

## Responsibilities

The Runtime is responsible for:

- Target Resolution
- Impact Scope Analysis
- Risk Analysis
- Modification Plan Generation
- Spec/Task Impact Analysis
- Report Generation

---

## Runtime Context

Provided by Runtime Base:

- Runtime Configuration
- Operating Rules

Provided when Change ID is given:

- Change Set Context (spec scenarios, contracts, task cards)

Resolved by Change Impact Runtime:

- Analysis Target (project → {base branch, target branch} → code reference)
- Impact Scope
- Risk Register
- Modification Plan
- Spec/Task Impact Register

---

## Phase 1 — Target Resolution

Parse:

- Projects (multi-select list from projects/)
- Code Reference (method name, class name, or code block)
- Branch Mapping (optional free text: `project-a:branch-x, project-b:branch-y, ...`)
- Base Branch (default: master)
- Change ID (optional; locates the change set for spec/task impact)

For every project, resolve and record two branches:

| Branch | Source | Default |
|---|---|---|
| Target Branch | Branch Mapping entry for the project | Base Branch |
| Base Branch | Base Branch input | master |

Rules:

- Every declared project resolves to a repository directory under projects/
- Projects absent from Branch Mapping get Target Branch = Base Branch
- Validate that the code reference resolves in the target branch for at least one project
- Record the resolved {project: target branch, base branch} pair in the analysis context and the report

Generate:

Analysis Target

---

## Phase 2 — Impact Scope Analysis

Analyze, for the resolved code target:

- Callers and call chains
- Interfaces and contracts affected
- Dependent modules and services
- Data model / database effects
- Configuration and entry points affected

Grade the impact by blast radius:

High

Medium

Low

Generate:

Impact Scope

---

## Phase 3 — Risk Analysis

Identify:

- Technical Risks
- Compatibility Risks
- Performance Risks
- Regression Risks
- Migration Risks

For each risk, provide:

- Severity
- Likelihood
- Mitigation

Generate:

Risk Register

---

## Phase 4 — Modification Plan

Generate:

- Change approach for the target
- Files expected to change
- Steps in dependency order
- Test strategy and regression coverage
- Rollback plan
- Open questions

Generate:

Modification Plan

---

## Phase 5 — Spec/Task Impact Analysis

When a Change ID is provided, map the modification plan onto the change set:

- Spec scenarios affected by the change
- Contracts affected by the change
- Task cards affected by the change

Classify each affected artifact:

- UPDATE_REQUIRED — existing artifact must change
- NEW — new artifact is required
- UNAFFECTED — not touched by the plan

When no Change ID is provided:

- Note in the report that spec/task impact requires a Change ID (trace the change via aic-trace / prepare re-entry)

Generate:

Spec/Task Impact Register

---

## Phase 6 — Report

Generate:

- change-impact-report.md

The report is written in the system language (config/menu.yaml → locale, per governance/LANGUAGE_CONVENTION.md).

The report contains, per project:

- Analysis Target: {project, target branch}, Base Branch
- Impact Scope by blast radius
- Risk Register
- Modification Plan
- Spec/Task Impact (when Change ID is provided)
- Merge / next-step recommendation

---

## Outputs

Generate:

- change-impact-report.md

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

## Completion

Return:

- Impact Summary
- Key Risks
- Recommended Modification Plan
- Spec/Task Impact Summary (when Change ID is provided)

Present the next-action choices to the user in the system language:

| 情形 / Situation | 操作 / Action |
|---|---|
| spec/task 需要调整 | → **prepare**（scoped re-entry，OPERATIONS.md 1.5）或 **aic-trace** 对账/backfill |
| 实现就绪 | → **develop**（需提供 Project ID 与 Task ID） |
| 仅分析，不继续 | → 结束（保留 change-impact-report.md） |
