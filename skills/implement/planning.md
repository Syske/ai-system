# Implementation Planning

Purpose

Generate a complete, reviewable implementation plan for a single OpenSpec Task Card before any code is written.

Planning must be completed and approved before entering the Implementation stage.

**Before planning, review the plan source critically:**
- Identify ambiguous instructions or missing dependencies before starting
- If the source plan has gaps or unclear steps: raise concerns, do not guess
- Plan must be iterable in bite-sized steps (2-5 minutes each)

---

# Planning Inputs

Before planning, collect and understand:

- Task Card
- Global Plan
- Specification
- Contract
- Scenario
- Applied Standards
- Related Source Code
- Existing Tests

If any required input is missing:

Stop.

Report the missing information.

Wait for clarification.

---

# Task Understanding

Before generating a plan, answer the following questions.

## Task

| Question | Expected Answer |
|---|---|
| What is the Task ID and title? | Task Card |
| What business capability is being implemented? | Task Description |
| What are the acceptance criteria? | Task Card |
| Which Spec sections define the behavior? | Specification |
| Which Contract definitions apply? | Contract |
| Which Scenarios define the expected flow? | Scenario |

---

## Context

| Question | Expected Answer |
|---|---|
| Which modules are affected? | Source Code |
| Which files will be modified? | Code Analysis |
| Which new files are required? | Code Analysis |
| Which files will be deleted? | Code Analysis |
| Which upstream systems call this implementation? | Contract |
| Which downstream systems are affected? | Contract |
| Which configurations are involved? | Spec |
| Which databases are affected? | Spec |
| Which MQ/Event definitions are affected? | Contract |

---

# Implementation Constraints

Identify all implementation constraints before planning.

Typical constraints include:

## Compatibility

- Backward compatibility must be preserved.
- Existing public behavior must not change unless explicitly required.

## Contract

- Contract definitions cannot be modified.
- Request/Response structures must follow the Contract.

## Specification

- Specification cannot be modified.
- Implementation must satisfy the Specification.

## Standards

Apply all loaded standards, including:

- AI Coding Rules
- Code Quality
- Clean Code
- Documentation
- Testing
- Language-specific standards

## Architecture

- Follow existing architecture.
- Reuse existing implementations whenever possible.
- Avoid unnecessary abstraction.

## External Systems

- Verify third-party APIs using official documentation.
- Never rely on assumptions or memory.

---

# Scope Analysis

Determine the exact implementation scope.

## In Scope

Include only changes required by:

- Task Card
- Specification
- Contract
- Acceptance Criteria

## Out of Scope

Do not include:

- Future Task Cards
- Unrelated refactoring
- Architecture redesign
- Specification updates
- Contract updates
- Performance optimizations not required by the task

If scope creep is detected:

Report it.

Exclude it from the implementation plan.

---

# Implementation Strategy

Determine the implementation approach.

Consider:

## Existing Code

- Can existing implementation be reused?
- Which existing patterns should be followed?

## Code Changes

Determine:

- Modify existing classes
- Create new classes
- Create new DTO / VO / Entity
- Create new configuration
- Create new tests

## Integration

Identify required:

- RPC changes
- REST API changes
- MQ changes
- Database changes
- Configuration changes

Choose the smallest implementation that satisfies the current Task Card.

---

# Risk Analysis

Identify implementation risks.

Include:

## Technical Risks

Examples:

- Backward compatibility
- Complex business logic
- Existing technical debt

## External Dependency Risks

Examples:

- Third-party API changes
- RPC dependency
- MQ dependency
- Database dependency

## Testing Risks

Examples:

- Difficult-to-mock dependencies
- Integration impact
- Existing unstable tests

For each identified risk:

- Describe the impact.
- Describe the mitigation strategy.

---

# Implementation Plan

Generate a concise implementation plan.

The plan should include:

## Task Summary

- Task ID
- Title
- Objective

## File Changes

### New Files

- File path
- Purpose

### Modified Files

- File path
- Summary of changes

### Deleted Files

- File path
- Reason

## Step Sequence

Break the implementation into small, independently verifiable steps.

Each step must include:

- Goal — one sentence
- Files — exact paths touched in this step
- Test first — the test to write or extend before the change
- Change — the smallest change that makes the test pass
- Verify — the exact command to run (build / test) and the expected result

Step rules:

- Each step is small enough to review in one pass.
- Each step leaves the branch consistent (compiles, tests pass).
- Steps are ordered by dependency; later steps never rework earlier steps.
- During Implementation, execute the approved steps in order; never skip verification.
- Deviations from the approved sequence follow Change Control (L1 record / L2 confirm / L3 stop).
- Build and test commands come from repositories/{service_id}.yaml (build section) or the java-maven resolution rules; never invent build commands.
- Contract or spec drift discovered during implementation: stop immediately (never modify the contract in the same cycle). Flag the task as blocked, update the spec through the spec-updater / contract-maintainer path, regenerate the contract, then resume the task. This is a L3 stop — do not silently adjust the code to match a "more correct" contract.

## Impact Analysis

- Public APIs
- Internal logic
- Configuration
- Database
- MQ/Event
- Dependencies

## Testing Strategy

Include:

- Happy Path
- Error Path
- Boundary Conditions

## Validation Strategy

Include:

- Build
- Unit Tests
- Contract Compliance
- Specification Compliance
- Applied Standards Compliance

---

# Planning Output

Present the implementation plan to the user.

The implementation plan must be:

- Complete
- Reviewable
- Traceable to the Task Card
- Limited to the current Task Card

Do not generate implementation code.

Wait for explicit user approval.

After approval, persist the plan to:

workspaces/{project_id}/openspec/changes/{change_id}/tasks/plans/{task_id}-plan.md

The persisted plan is the comparison anchor for Review and Verify.

---

# Stop Rules

Immediately stop planning if:

- Required inputs are missing.
- Specification conflicts with Contract.
- Task dependencies are incomplete.
- Scope is unclear.
- Official documentation cannot be verified.
- The implementation cannot satisfy the acceptance criteria.

Report the issue.

Wait for clarification.