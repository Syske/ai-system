# Workflow: Spec

## Purpose

Create specification artifacts for the next task.

## Runtime

- templates/runtime/runtime-spec.md

## Preconditions

- Prepare completed for this change (Preparation Report available)

## Inputs

Required:

- Change ID

Optional:

- Requirement Documents
- Existing Design
- Mode

## Context

Load only:

- Environment Context (from Bootstrap)
- Preparation Report, Architecture Summary, Impact Report (from Prepare)
- Existing Specifications and Contracts within the change scope

Never load the entire repository tree into context.

## Outputs

- Proposal
- Design
- Specification
- Contracts
- Scenarios
- Global Plan
- Task Cards

## Exit Criteria

Success:

- Development Readiness = Ready
- Specification, Contracts, Scenarios and Tasks internally consistent

Stop:

- Required information missing → generate clarification questions and stop
- Consistency check failed → generate Consistency Report and stop

## Next

- dev-setup — on ready
