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

Optional:

- Branch Mapping
- Base Branch (default: master)
- Review Focus
- Output Directory

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

Reports are written to `outputs/code-review/{date}-{target}/` under the workspace root.
The report records, per project, the base branch and target branch used.
The report is written in the system language (config/menu.yaml → locale, per governance/LANGUAGE_CONVENTION.md).

## Exit Criteria

Success:

- All target projects reviewed and review-report.md generated

Stop:

- Any code target (project or branch) cannot be resolved → report and stop

## Next

- None
