# Workflow: Proposal

## Purpose

Discuss an optimization or ad-hoc idea and produce a solution document.

## Runtime

- templates/runtime/runtime-proposal.md

## Preconditions

- None. Standalone workflow.

## Inputs

Required:

- Topic

Optional:

- Projects
- Branch Mapping
- Related Materials
- Output Directory

## Context

Load only:

- The declared Topic
- Related Materials when provided
- The selected projects on their declared branches, when relevant

When projects are selected, resolve and record, per project:

- Base Branch
- Target Branch

Never load content outside the discussion scope.

## Outputs

- solution.md

Documents are written to `outputs/proposal/{date}-{title}/` under the workspace root.
`{title}` is a kebab-case descriptor of the session (≤30 chars); same-day reruns on the
same title append `-N`.
The document records any referenced code as `project:branch`.
The document is written in the system language (config/menu.yaml → locale, per governance/LANGUAGE_CONVENTION.md).

## Exit Criteria

Success:

- solution.md generated with a recommended solution

Stop:

- Information insufficient to form a solution → generate clarification questions and stop

## Next

- None
