# Runtime: Code Review

Extends:

- runtime-base.md

---

## Purpose

Review arbitrary code under projects/ and produce a structured review result.

The Code Review Runtime reviews multiple projects, each on its declared branch,
without requiring a Task Card, Specification, or Dev Setup.

The Runtime does not modify business implementation.

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
- Scope Definition
- Code Review
- Baseline Comparison
- Finding Classification
- Recommendation Generation

---

## Runtime Context

Provided by Runtime Base:

- Runtime Configuration
- Operating Rules

Resolved by Code Review Runtime:

- Review Targets (project → {base branch, target branch})
- Review Scope
- Review Findings
- Review Suggestions

---

## Phase 1 — Target Resolution

Parse:

- Projects (multi-select list from projects/)
- Branch Mapping (optional free text: `project-a:branch-x, project-b:branch-y, ...`)
- Base Branch (default: master)

For every project, resolve and record two branches:

| Branch | Source | Default |
|---|---|---|
| Target Branch | Branch Mapping entry for the project | Base Branch |
| Base Branch | Base Branch input | master |

Rules:

- Every declared project resolves to a repository directory under projects/
- Projects absent from Branch Mapping get Target Branch = Base Branch
- Validate that both the target branch and the base branch exist for every project before review
- Record the resolved {project: target branch, base branch} pair in the review context and the report

Generate:

Review Targets

---

## Phase 2 — Scope Definition

Collect:

- The changed/declared scope of each target
- Review Focus, when provided

Generate:

Review Scope

---

## Phase 3 — Code Review

Review:

- Readability
- Naming
- Complexity
- Duplication
- Error Handling
- Logging
- Resource Management

Cross-reference against the applied standards and the smell baseline
(skills/review/smell-baseline.md):

Mysterious Name, Duplicated Code, Feature Envy, Data Clumps, Primitive Obsession,
Repeated Switches, Shotgun Surgery, Divergent Change, Speculative Generality,
Message Chains, Middle Man, Refused Bequest.

Each finding must cite the file and line it applies to.

Generate:

Code Review Findings

---

## Phase 4 — Baseline Comparison

For every project, compare the target branch against its recorded base branch:

- Identify files and lines that differ between base branch and target branch
- Classify findings as introduced by the target branch or pre-existing in the base branch

Generate:

Baseline Comparison

---

## Phase 5 — Finding Classification

Classify findings:

Critical

Major

Minor

Suggestion

Group findings by project (project:branch).

Generate:

Classified Findings

---

## Phase 6 — Review Report

Generate:

- review-report.md

The report is written in the system language (config/menu.yaml → locale, per governance/LANGUAGE_CONVENTION.md).

The report contains, per project:

- Review Target: {project, target branch}
- Base Branch: the branch the target branch was compared against
- Findings by severity, each marked as introduced-by-branch or pre-existing
- Improvement suggestions
- Merge recommendation

---

## Outputs

Generate:

- review-report.md

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

- Review Summary
- Findings by Project
- Recommendations
