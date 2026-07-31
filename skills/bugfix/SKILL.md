---
name: bugfix
description: Bug fixing workflow — analyze, fix, and validate with tests
---

## Bug Analysis

1. Understand the bug from the user report or test failure
2. Locate the relevant source files
3. Identify root cause

## Fix & Validate

1. Make the minimal fix — change only what's necessary to resolve the bug
2. Run the failing test to confirm it passes
3. Run related tests to check for regressions
4. If tests don't exist, note that coverage is missing

## Pipeline Follow-up

After fixing, this skill is part of a pipeline:
- Review the fix with `review-changes`
- Generate tests with `mock-test` if needed
- Run `java-maven` for build verification

## Output

Return: root cause, the fix made, test results, and any risks.
