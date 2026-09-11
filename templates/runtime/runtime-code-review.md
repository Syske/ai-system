# Runtime: Code Review

Extends:

- runtime-base.md

---

## Purpose

Review arbitrary code under projects/ and produce a structured review result.

The Code Review Runtime reviews multiple projects, each on its declared branch,
without requiring a Task Card, Specification, or Dev Setup.

The Runtime does not modify business implementation by default. In spec-comparison
mode the user may explicitly authorize a fix-apply extension
(see "Spec-Comparison Fix-Apply Extension" below); without that authorization
the runtime stays review-only.

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
- Target Theme (subject; optional — used to fuzzy-match each project's
target branch)
- Branch Mapping (optional explicit override: `project-a:branch-x, ...`)
- Base Branch (default: master)

For every project, resolve and record two branches:

| Branch | Source | Default |
|---|---|---|
| Target Branch | Target Theme fuzzy match → Branch Mapping override → ask user | ask user |
| Base Branch | Base Branch input | master |

### Target Branch by theme (rules)

When a Target Theme is given, resolve each project's target branch by fuzzy
matching the theme against `workspace.yaml → repository.available[].dev_branch`
and local git branches:

- If `Branch Mapping` covers a project, adopt that branch directly — do NOT
  re-present candidates (explicit override, no double-ask).
- Otherwise collect candidate branches containing the theme (case-insensitive
  substring). Candidates come from (in order): the project's
  `workspace.yaml dev_branch`, then `git -C <repo> branch --format=%(refname:short)`.
- A SINGLE real candidate (or only one `cc{date}` variant) is adopted directly.
- Present the matched branches for user selection only when 0 or several
  distinct candidates exist. The `cc{date}` prefix is taken from the REAL
  matched branch — do not invent a date.
- Single project also uses this flow (theme → its own branch candidates).
- If a project has NO match for the theme, and no Branch Mapping override,
  ASK the user for that project's branch name — never guess.
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

Review priority follows the user's `Review Focus` selection: the provided
focus areas (e.g. 性能/安全/并发) are examined first and in depth; the other
dimensions above still get coverage. Default (全面审查) = full review across
all dimensions.

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

## Spec-Comparison Fix-Apply Extension (user-authorized)

The base runtime is review-only. When the caller runs the spec-comparison
variant (see workflows/code-review.md "Spec-Comparison Review Mode") and the
user explicitly authorizes applying the recommended fixes, the runtime extends
Phase 6 with:

1. Sync — merge the base branch into each target branch before applying fixes.
2. Fix-Apply — implement the user-authorized review findings on the target branch.
3. Build/Check — compile and/or smoke-verify the fixes (e.g. py_compile, unit tests).
4. Commit & Push — commit the fixes on the target branch and push to origin.
5. Record — append a fix-applied disposition table to review-report.md.

Authorization rule: this extension NEVER runs without explicit user
authorization. Any such run records an L1 deviation in the diagnostic log;
unresolved findings (capacity/ops questions, structural debt) are recorded for
later, not silently implemented.

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
