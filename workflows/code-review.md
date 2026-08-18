# Workflow: Code Review

## Purpose

Review arbitrary code under projects/ and produce a structured review result.

## Runtime

- templates/runtime/runtime-code-review.md

## Preconditions

- None. Standalone workflow.

## Inputs

Required:

- Projects

  (one-time task: user provides repo path/URL(s), comma-separated; or selects
  from workspace.yaml mapping)

Optional:

- Target Theme
- Branch Mapping
- Base Branch (default: master)
- Review Focus
- Output Directory
- Confluence Spec Page Id

## Target Branch Resolution

(Contract: resolve each project's target branch per runtime Phase 1; ASK the
user rather than guessing when a branch is missing/ambiguous.)

1. `Target Theme` (e.g. `wecom_live`) → fuzzy-match each repo's `dev_branch`
   + local git branches by theme; present real-`cc{date}` candidates, user picks.
2. `Branch Mapping` → explicit per-project override.
3. No match → ASK the user; do not guess.
4. Base Branch defaults to `master` (override via environments/config).
5. Validate target & base exist before reviewing; else stop that project.


## Context

Load only:

- The selected projects on their target branches
- The resolved base branch for each project (default: master)
- Applied standards relevant to the review

Never load the entire repository tree or every branch into context.

## Outputs

- review-report.md

Reports are written to `outputs/code-review/{yyMMdd}-{target}/` under the workspace root.
`{target}` is a kebab-case descriptor of the session (≤30 chars); same-day reruns on the
same target append `-N`.
The report records, per project, the base branch and target branch used.
The report is written in the system language (config/menu.yaml → locale, per governance/LANGUAGE_CONVENTION.md).

## Spec-Comparison Review Mode

When the caller provides a Confluence Spec Page Id (e.g. a HotFix one-pager),
this workflow runs the spec-comparison variant defined in the `coolreview`
skill (SKILL.md → Spec-Comparison Review Mode):

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
push → update wiki page (update_confluence_page.py) → report version`
(see confluence-markdown-publisher skill "HotFix one-pager update workflow").

## Exit Criteria

Success:

- All target projects reviewed and review-report.md generated

Stop:

- Any code target (project or branch) cannot be resolved → report and stop
- Optional recap: reusable lesson this run? → run `memory-capture` skill; none → skip
## Next

- None
