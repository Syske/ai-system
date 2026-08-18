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
- Target Theme (需求主题; optional — used to fuzzy-match each project's
target branch)
- Branch Mapping (optional explicit override: `project-a:branch-x, ...`)
- Base Branch (default: master)

For every project, resolve and record two branches:

| Branch | Source | Default |
|---|---|---|
| Target Branch | Target Theme fuzzy match → Branch Mapping override → ask user | Base Branch |
| Base Branch | Base Branch input | master |

### Target Branch by theme (rules)

When a Target Theme is given, resolve each project's target branch by fuzzy
matching the theme against `workspace.yaml → repository.available[].dev_branch`
and local git branches, then PRESENT the matches for user selection:

- For each selected project, collect candidate branches containing the theme
  (case-insensitive substring). Candidates come from (in order): the project's
  `workspace.yaml dev_branch`, then `git -C <repo> branch --format=%(refname:short)`.
- Show the matched branches grouped by project; let the user pick per project.
  The `cc{date}` prefix is taken from the REAL matched branch — do not invent a
  date. If several date variants exist, list them and let the user choose.
- Single project also uses this flow (theme → its own branch candidates).
- If a project has NO match for the theme, and no Branch Mapping override,
  ASK the user for that project's branch name — never guess.
- Branch Mapping explicitly overrides the theme match for the named projects.
- Validate both target and base exist in the repo before review; otherwise
  report and stop that project's review.

Rules:

- Every declared project resolves to a repository directory under projects/
- Multi-project reviews share one theme but resolve branch per project; never
  reuse one project's branch for another.
- Record the resolved {project: target branch, base branch} pair in the review
  context and the report.

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
