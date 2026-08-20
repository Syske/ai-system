---
name: change-impact
description: Analyze impact, risks, and modification plan for a code target.
workflow:
  inputs:
    required: [Projects, Code Reference]
    optional:
      - name: Branch Mapping
      - name: Base Branch
        default: master
      - name: Change ID
      - name: Output Directory
  next: [prepare, develop, None]
---
# Workflow: Change Impact

## Purpose

Analyze the impact, risks, and modification plan for a specific code target before changing it.

## Runtime

- templates/runtime/runtime-change-impact.md

## Preconditions

- None. Standalone workflow.

## Inputs

Required:

- Projects

  (one-time task, no project container required) 用户直接提供仓库路径/URL
  （可多个，逗号分隔）；有项目容器时也可从 workspace.yaml 映射选择。
- Code Reference

Optional:

- Branch Mapping
- Base Branch (default: master)
- Change ID
- Output Directory

## Context

Load only:

- The selected projects on their declared branches
- The code target and its callers, call chain, and dependencies
- The change set's spec scenarios, contracts, and task cards, when Change ID is provided
- Applied standards relevant to the analysis

For every project, resolve and record:

- Base Branch
- Target Branch

Never load the entire repository tree or every branch into context.

## Outputs

- change-impact-report.md

Reports are written to `outputs/change-impact/{yyMMdd}-{target}/` under the workspace root.
`{target}` is a kebab-case descriptor of the session (≤30 chars); same-day reruns on the
same target append `-N` (outputs/change-impact/260813-live-api-timeout/).
The report records, per project, the base branch and target branch used.
The report includes a Spec/Task Impact section when a Change ID is provided.
The report is written in the system language (config/menu.yaml → locale, per governance/LANGUAGE_CONVENTION.md).

## Exit Criteria

Success:

- Impact, risks, and modification plan analyzed; change-impact-report.md generated
- Spec/Task Impact assessed when a Change ID is provided

Stop:

- The code target cannot be resolved → report and stop
- Optional recap: reusable lesson this run? → run `memory-capture` skill; none → skip
## Next

- prepare — on spec/task adjustment required (scoped re-entry, per OPERATIONS.md 1.5)
- develop — on implementation readiness (provide Project ID and Task ID)
- None — analysis only
