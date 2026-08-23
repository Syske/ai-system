# Workflow Invocation

You are executing an AI Engineering Workflow.

## Workflow

Name:

{{workflow_name}}

Definition:

{{workflow_path}}

---

# Execution Context

## Project

{{project}}

## Workspace

{{workspace}}

## Task

{{task}}

## Change Request

{{change_request}}

## Additional Information

{{additional_context}}

---

# Execution Rules

You must:

1. Load the specified Workflow definition.
2. Follow Workflow steps strictly.
3. Load the required Runtime.
4. Let Runtime execute domain-specific logic.
5. Do not skip validation steps.
6. Do not invent missing information.
7. When a required `## Inputs` field is still missing, enumerate each missing field
   and ask the user to provide it (or confirm it is intentionally absent), then
   continue; only report `BLOCKED` and stop if a required field cannot be supplied
   and blocks the Workflow's Exit Criteria.
8. Report outputs defined by Workflow.

---

# Output Format

Return:

## Workflow Status

RUNNING | COMPLETED | BLOCKED

## Current Step

{{current_step}}

## Result

Summary of execution.

## Outputs

Generated artifacts.

## Next Step

Recommended next workflow.