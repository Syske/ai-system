---
name: bugfix
description: Bug fixing workflow — analyze root cause, implement the smallest safe fix, and validate with regression tests. Use when a defect is reported, when behavior diverges from the expected spec, or when a failing test needs a verified repair.
---

## Bug Analysis

1. Understand the bug from the user report or test failure
2. For hard bugs / non-obvious root cause: build a tight feedback loop first
   (see `feedback-loop.md`) — a red-capable repro before hypothesising
3. Locate the relevant source files
4. Identify root cause

## Fix & Validate

1. Make the minimal fix — change only what's necessary to resolve the bug
2. Run the failing test to confirm it passes
3. Run related tests to check for regressions
4. If tests don't exist, note that coverage is missing

## Pipeline Follow-up

After fixing, this skill is part of a pipeline:
- Review the fix with `review-changes`
- Generate tests with `mock-test` if needed
- Run build verification with the configured backend: `idea-build` when
  `build.backend=idea`, else `java-maven` (default CLI)

## Output

Return: root cause, the fix made, test results, and any risks.
