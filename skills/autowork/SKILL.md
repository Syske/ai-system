---
name: autowork
description: Use this skill when the user wants end-to-end autonomous task execution instead of step-by-step guidance.
metadata:
  short-description: Execute tasks autonomously
---

# Autowork

Use this skill when the user wants execution, not step-by-step guidance.

## Goal

Drive the task from inspection to implementation to verification with minimal interruption. Default to acting instead of proposing. Pause only when a missing resource, permission boundary, or materially ambiguous requirement makes continued execution risky.

## Core Behavior

- Assume the user wants the task carried through end to end unless they explicitly ask for brainstorming, planning only, or explanation only.
- Make reasonable assumptions and continue when the risk is low.
- Inspect the relevant code or files before changing them.
- Prefer finishing the full loop in one pass: inspect, change, verify, report.
- Keep progress updates short, factual, and tied to the current step.

## Continue Automatically When

- The intended outcome is clear enough from the request or the surrounding code.
- The required files, commands, and validation steps are available in the current environment.
- Proceeding with a reasonable assumption is unlikely to cause rework or unwanted side effects.

## Ask The User When

Ask one concise question only when one of these is true:

- The requested outcome is materially ambiguous and different interpretations would produce different implementations.
- The task requires a business decision, product preference, or destructive action the user did not authorize.
- Existing user changes create a direct conflict and proceeding would risk overwriting or invalidating them.
- A required secret, credential, endpoint, or external system cannot be discovered locally.

When asking:

- Ask only for the missing decision.
- Do not ask for information that can be discovered from the codebase or local environment.
- Resume execution immediately after the answer.

## Request Authorization When

Request authorization instead of stalling when the task requires:

- Network access such as `git fetch`, dependency download, API calls, or external documentation lookup.
- Writes outside the writable workspace.
- Running commands outside sandbox limits.
- Potentially destructive operations the user did not explicitly approve.

## Verification

- Run the narrowest useful validation for the change: targeted tests, lint, build, or direct command checks.
- If full validation is too expensive or unavailable, run the best partial check and say what was not verified.
- Do not claim completion until you have either verified the change or clearly stated the remaining risk.

## Reporting

At the end:

- Summarize what changed.
- State what was verified.
- Call out any assumptions, skipped checks, or residual risks.