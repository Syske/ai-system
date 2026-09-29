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
  outputs:
    base: "outputs/bugfix/{yyMMdd}-{descriptor}/"
  phases:
    - id: "1"
      name: "Issue Analysis"
    - id: "2"
      name: "Reproduction"
    - id: "3"
      name: "Root Cause Analysis"
    - id: "4"
      name: "Fix Planning"
    - id: "4.5"
      name: "Approval Gate"
      activation: "WHEN mode.approval_gate"
    - id: "4.6"
      name: "Branch"
      activation: "WHEN mode.phases ∋ branch"
    - id: "5"
      name: "Implement"
    - id: "6"
      name: "Regression Verification"
      pass_criterion: "Verification Status = PASS (runtime-verify Phase 7/8 criteria)"
    - id: "6.5"
      name: "Commit"
      activation: "WHEN mode.phases ∋ commit"
    - id: "6.6"
      name: "Submit MR"
      activation: "WHEN mode.phases ∋ mr ∧ phase(\"6.5\").completed"
    - id: "6.7"
      name: "Doc"
      activation: "WHEN mode.phases ∋ doc ∧ phase(\"6\").passed"
    - id: "7"
      name: "Completion"
---
# Workflow: BugFix

## Purpose

Diagnose and fix software defects.

## Runtime

- templates/runtime/runtime-bugfix.md

## Phases

Phase execution contract is defined by the workflow configuration.
The configured Phase contract MUST match the Runtime Phase structure.

## Preconditions

- Dev Setup completed (Project Context and Workspace Context available)
  — if missing, run dev-setup first (independent entry: the user may not have
  set up the workspace yet)
- Bug is observable or described in enough detail to analyze

## Inputs

Required:

- Project ID
- Bug Description

Optional:

- Issue ID
- Logs
- Stack Trace
- Mode (standard / hotfix; default standard; hotfix fixes directly on master and runs the full pre-release chain, behavior driven by config/workflows/bugfix-modes.yaml)

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
- hotfix-test-doc — on hotfix mode & verify pass (generate the hotfix-test doc on demand; extension provider: extensions/hotfix-test-doc)
