---
name: bugfix
description: Diagnose and fix software defects.
workflow:
  inputs:
    required:
      - Project ID
      - Bug Description
    optional:
      - name: Issue ID
      - name: Logs
      - name: Stack Trace
      - name: Mode
        default: standard
  next:
    - review
    - hotfix-test-doc
---
# Workflow: BugFix

## Purpose

Diagnose and fix software defects.

## Runtime

- templates/runtime/runtime-bugfix.md

## Preconditions

- Dev Setup completed (Project Context and Workspace Context available)
- Bug is observable or described in enough detail to analyze

## Inputs

Required:

- Project ID
- Bug Description

Optional:

- Issue ID
- Logs
- Stack Trace
- Mode (standard / hotfix; default standard; hotfix 时基于 master 直接修复并走完整发布前链路，行为由 config/workflows/bugfix-modes.yaml 驱动)

## Context

Load only:

- Bug Description, Logs and Stack Trace
- Affected modules and related tests identified during issue analysis

Never load the entire repository tree into context.

## Outputs

- Root Cause Report
- Fix implementation (smallest safe change)
- Regression Report
- BugFix Report

Reports are written to `outputs/bugfix/{yyMMdd}-{descriptor}/` under the workspace root,
where `{descriptor}` is the bug theme (kebab-case, e.g. `incentive-bizcourse-npe`);
same-day same-theme reruns append `-N` (existing flat files under `outputs/bugfix/`
are historical and stay as-is).

## Exit Criteria

Success:

- Original defect resolved
- Existing behaviour unchanged
- Regression tests pass

Stop:

- Reproduction failed and assumptions not confirmed → stop and wait for confirmation
- Root cause not identified → never implement a fix; stop and report
- Optional recap: reusable lesson this run? → run `memory-capture` skill; none → skip
## Next

- review
- hotfix-test-doc — on hotfix mode & verify pass（按需生成转测文档，扩展提供者：extensions/hotfix-test-doc）
