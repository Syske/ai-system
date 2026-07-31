# Implement Skill Workflow

Purpose

Implement exactly one approved OpenSpec Task Card in a predictable, verifiable and repeatable manner.

This workflow orchestrates the implementation process.

Implementation rules, quality standards and validation are delegated to the corresponding Skill documents.

---

# Stage 1 — Load Task Context

Goal

Load all information required for implementation.

Actions

1. Read the Task Card.
2. Read the referenced Spec.
3. Read the referenced Contract(s).
4. Read the referenced Scenario(s).
5. Identify prerequisite task cards.
6. Verify prerequisite tasks are completed.

If any required context is missing:

STOP.

Report the issue.

Do not continue.

Output

- Task Summary
- Referenced Specifications
- Referenced Contracts
- Referenced Scenarios
- Dependency Summary

---

# Stage 2 — Planning

Goal

Generate an implementation plan.

Execute:

planning.md

Output

Implementation Plan

Wait for user confirmation before continuing.

---

# Stage 3 — Wait For Approval

This is a mandatory checkpoint.

Do not generate implementation code until the user explicitly approves the implementation plan.

If rejected:

Return to Stage 2.

If approved:

Continue to Stage 4.

---

# Stage 4 — Implementation

Goal

Implement the approved Task Card.

Before generating code, execute:

- decision.md
- checklists.md
- anti-patterns.md

Use:

- examples.md (when examples are needed)

Generate code only after all implementation constraints are established.

Requirements

- Implement only the current Task Card.
- Do not modify Spec.
- Do not modify Contract.
- Do not implement future tasks.
- Keep changes minimal.
- Preserve backward compatibility.

Output

Implemented code.

---

# Stage 5 — Testing

Goal

Write tests BEFORE production code, following TDD Red-Green-Refactor.

Generate tests according to:

- Applied Standards
- Task acceptance criteria

TDD cycle:

1. **RED**: Write the failing test first. Verify it fails for the expected reason.
2. **GREEN**: Write the MINIMAL code to make the test pass. No more.
3. **REFACTOR**: Clean up both test and production code while keeping green.

Never write production code before the test exists and fails.

Cover at minimum:

- Happy Path
- Error Path
- Boundary Conditions

If additional test fixture updates are required:

Invoke the appropriate testing Skill.

Output

Updated test code.

---

# Stage 6 — Validation

Goal

Validate the implementation.

Execute:

validation.md

If validation fails:

Return to Stage 4.

Output

Validation Results

---

# Stage 7 — Acceptance Verification

Goal

Verify that every acceptance criterion is satisfied.

For each acceptance criterion:

- Verify implementation.
- Verify tests.
- Verify evidence.

If any criterion is not satisfied:

Return to Stage 4.

Output

Acceptance Verification Report

---

# Stage 8 — Mark Task Card Complete

Goal

Update the Task Card file to reflect completion.

Actions

1. Re-open the Task Card file.
2. For each `- [ ]` in **完成定义**: mark as `- [x]`.
3. For each `- [ ]` in **代码质量检查**: mark as `- [x]`.
4. For each `- [ ]` in **验收标准**: verify and mark as `- [x]`.
5. Save the updated Task Card file.

Do not skip this step.

If any item cannot be verified, do not mark it complete.
Return to the appropriate stage to resolve the issue.

6. Append or update the **Review Result** section at the bottom of the Task Card file:

```markdown
## Review Result

**Status**: ⚠️  Pending Review
**Date**: {current_date}

Independent review has NOT yet been executed.
All [x] marks above reflect implementer self-check only.
Review may revert any item that is not actually satisfied.
```

This status will be updated by the `review` workflow (Approved / Changes Required).

7. Verify all commits on the task branch follow commit conventions:
   - Format: `<type>(<scope>): <description>`
   - Type must be one of: feat, fix, refactor, perf, test, docs, style, chore, ci, revert
   - Description is a short Chinese or English summary (imperative mood, no period at end)
   - Each commit does exactly one thing (atomic)
   Flag any non-conforming commits for interactive rebase before completion.

---

# Stage 9 — Completion

Goal

Generate the implementation report.

Include:

- Task Summary
- Files Created
- Files Modified
- Files Deleted
- Validation Results
- Acceptance Results
- Known Risks
- Follow-up Recommendations

Do not automatically start the next Task Card.

---

# Stage 10 — Stop

Stop after the current Task Card is completed.

The next Task Card must be started by an explicit user request.