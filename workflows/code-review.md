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

  (one-time task, no project container required) 用户直接提供仓库路径/URL
  （可多个，逗号分隔）；有项目容器时也可从 workspace.yaml 映射选择。

Optional:

- Branch Mapping
- Base Branch (default: master)
- Review Focus
- Output Directory
- Confluence Spec Page Id (external spec to compare the diff against, e.g. a
  HotFix one-pager; enables Spec-Comparison Review Mode below)

## Context

Load only:

- The selected projects on their target branches
- The resolved base branch for each project (default: master)
- Applied standards relevant to the review

For every project, resolve and record:

- Base Branch
- Target Branch

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

1. Fetch the spec page via the `confluence-markdown-publisher` skill
   (`get_confluence_page.py --page-id <id> --output page.html --json`).
2. Parse the spec into a claim checklist (changed methods, constants like batch
   size, behaviour guarantees, scope, release branch).
3. Run the normal baseline sync + diff review (workflow steps above).
4. Verify every spec claim against code; check "pure optimization, no behaviour
   change" promises against actual failure/loop semantics.
5. Report with a spec-vs-code comparison table first, findings by severity,
   then assumptions/questions, then conclusion.

HotFix one-pager workflows additionally close the loop after review fixes:

```text
fetch wiki → sync branch → diff review → fix → build (idea-build) → commit →
push → update wiki page (update_confluence_page.py) → report back new version
```

This loop is documented in the confluence-markdown-publisher skill under
"HotFix one-pager update workflow (review follow-up)".

## Exit Criteria

Success:

- All target projects reviewed and review-report.md generated

Stop:

- Any code target (project or branch) cannot be resolved → report and stop
- Optional recap: reusable lesson this run? → run `memory-capture` skill; none → skip
## Next

- None
