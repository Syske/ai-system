---
name: code-review
description: Review arbitrary code and produce a review result.
workflow:
  inputs:
    required: [Projects]
    optional:
      - name: Target Theme
      - name: Branch Mapping
      - name: Base Branch
        default: master
      - name: Review Focus
        default: 全面审查
      - name: Confluence Spec Page Id
  next: [None]
  outputs:
    base: "outputs/code-review/{yyMMdd}-{target}/"
  phases:
    - id: "1"
      name: "Target Resolution"
    - id: "2"
      name: "Scope Definition"
    - id: "3"
      name: "Code Review"
    - id: "4"
      name: "Baseline Comparison"
    - id: "5"
      name: "Finding Classification"
    - id: "6"
      name: "Review Report"
---
# Workflow: Code Review

## Purpose

Review arbitrary code under projects/ and produce a structured review result.

## Runtime

- templates/runtime/runtime-code-review.md

## Phases

Phase execution contract is defined by the workflow configuration.
The configured Phase contract MUST match the Runtime Phase structure.

## Preconditions

- None. Standalone workflow.

## Inputs

Required:

- Projects
  (one-time task: repo paths/URLs comma-separated, or select from workspace.yaml mapping)

Optional:

- Target Theme
- Branch Mapping
- Base Branch (default: master)
- Review Focus (default: 全面审查)
- Confluence Spec Page Id

## Context

Load only:

- The selected projects on their target branches
- The resolved base branch for each project (default: master)
- Applied standards relevant to the review

Never load the entire repository tree or every branch into context.

### Target Branch Resolution

Per runtime Phase 1 (target resolution): `Branch Mapping` overrides; otherwise
`Target Theme` fuzzy-matches each repo's `dev_branch` + local git branches; no
match → ASK the user, never guess.

## Outputs

- review-report.md

Reports are written to `outputs/code-review/{yyMMdd}-{target}/` under the workspace root.
`{target}` is a kebab-case descriptor of the session (≤30 chars); same-day reruns on the
same target append `-N`.
The report records, per project, the base branch and target branch used.
The report is written in the system language (config/menu.yaml → locale, per governance/LANGUAGE_CONVENTION.md).

### Spec-Comparison Review Mode

When the caller provides a Confluence Spec Page Id (e.g. a HotFix one-pager),
this workflow runs the spec-comparison variant (steps below, inlined — no
external skill):

1. Fetch spec page via `confluence-markdown-publisher`
   (`get_confluence_page.py --page-id <id> --output page.html --json`).
2. Parse spec into a claim checklist (changed methods, constants e.g. batch
   size, behaviour guarantees, scope, release branch).
3. Normal baseline sync + diff review (steps above).
4. Verify every spec claim vs code; check "no behaviour change" promises
   against actual failure/loop semantics.
5. Report: spec-vs-code comparison table → findings by severity →
   assumptions/questions → conclusion.

HotFix one-pager workflows close the loop after fixes:
`fetch wiki → sync branch → diff review → fix → build (idea-build) → commit →
push → report version`.

The remote Confluence wiki is user-managed: the agent only writes a local
`change-summary-wiki.md`; fix-apply requires explicit user authorization (see
runtime-code-review.md "Spec-Comparison Fix-Apply Extension").

## Exit Criteria

Success:

- All target projects reviewed and review-report.md generated

Stop:

- Any code target (project or branch) cannot be resolved → report and stop
- Optional recap: reusable lesson this run? → run `memory-capture` skill; none → skip
## Next

- None
