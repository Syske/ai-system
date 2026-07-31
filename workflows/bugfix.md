# Workflow: BugFix

## Purpose

Diagnose and fix software defects.

## Runtime

- ai-system/templates/runtime/runtime-bugfix.md

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

## Exit Criteria

Success:

- Original defect resolved
- Existing behaviour unchanged
- Regression tests pass

Stop:

- Reproduction failed and assumptions not confirmed → stop and wait for confirmation
- Root cause not identified → never implement a fix; stop and report

## Next

- review
