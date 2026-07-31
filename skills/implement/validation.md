# Validation

Purpose

Verify that the implementation is correct, complete, and compliant before the task can be considered finished.

Validation is the final quality gate before completion.

## The Iron Law

```
NO COMPLETION CLAIMS WITHOUT FRESH VERIFICATION EVIDENCE
```

Before claiming any status:

1. **IDENTIFY**: What command proves this claim?
2. **RUN**: Execute the FULL command (fresh, complete)
3. **READ**: Full output, check exit code, count failures
4. **VERIFY**: Does output confirm the claim?
5. **ONLY THEN**: Make the claim

Skip any step = not verifying.

---

# Validation Scope

Every implementation must be validated from the following perspectives:

- Build
- Testing
- Specification
- Contract
- Coding Standards
- Documentation
- Acceptance Criteria

Validation must be based on evidence rather than assumptions.

---

# Build Validation

Verify:

- Project builds successfully
- No compilation errors
- No new warnings introduced (when applicable)

Result:

- Passed
- Failed

---

# Testing Validation

Verify automated tests.

Minimum coverage:

- Happy Path
- Error Path
- Boundary Conditions

When applicable also verify:

- Regression
- Integration
- Exception handling

Result:

- Passed
- Failed
- Unable to verify

---

# Contract Validation

Verify implementation against the Contract.

Check:

- API signatures
- Request fields
- Response fields
- Error codes
- Required constraints

Any deviation from the Contract must be reported.

Do not modify the Contract.

---

# Specification Validation

Verify implementation against the Specification.

Check:

- Functional behavior
- Business rules
- Scenario coverage
- Configuration requirements

Do not modify the Specification.

---

# Coding Standards Validation

Verify compliance with all Applied Standards.

Examples include:

- AI Coding Rules
- Code Quality
- Clean Code
- Language-specific standards

Typical checks:

- Naming consistency
- Readability
- Error handling
- Logging
- Code duplication
- Maintainability

---

# Documentation Validation

Verify documentation required by the Applied Standards.

Typical checks:

- Class Javadoc
- Method documentation
- Field documentation
- Complex business logic explanation

Documentation must explain *why*, not only *what*.

---

# Acceptance Criteria Validation

Verify every acceptance criterion individually.

Each criterion must be marked as:

| Result | Meaning |
|----------|---------|
| Satisfied | Fully implemented and verified |
| Not Satisfied | Missing or incorrect |
| Unable to Verify | Evidence is insufficient |

Do not mark the task as completed unless every criterion is satisfied.

---

# Validation Report

Generate a validation summary including:

## Build

- Passed / Failed

## Testing

- Executed tests
- Results

## Contract

- Passed / Failed

## Specification

- Passed / Failed

## Standards

- Passed / Failed

## Documentation

- Passed / Failed

## Acceptance Criteria

List every criterion and its verification result.

---

# Validation Failure

If any validation fails:

- Stop completion.
- Report the failure.
- Describe the root cause.
- Fix the implementation.
- Repeat validation.

Do not continue until all validation checks pass.

---

# Completion Gate

A task passes validation only when:

- Build succeeds
- Tests pass
- Contract is satisfied
- Specification is satisfied
- Applied Standards are satisfied
- Documentation is complete
- Acceptance Criteria are fully satisfied

Otherwise the task remains incomplete.