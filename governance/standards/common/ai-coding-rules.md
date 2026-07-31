# AI Coding Rules
Version: 1.0
---
# Goal
This document defines behavioral constraints for AI Agents during software development.

Objectives:
- Ensure implementation correctness
- Ensure implementation maintainability
- Ensure implementation verifiability
- Ensure minimal changes
- Ensure traceable development process

Functional completion is not the only goal.
---
# Core Principles
Always follow these principles:
1. Spec First
2. Contract First
3. Official Documentation First
4. Smallest Change
5. Verify Before Complete

No principle may be ignored.
---
# Rule 1: Spec is the Single Source of Truth
Must: Implement according to Spec.
Forbidden: Interpreting business logic on your own.
Forbidden: Adding requirements on your own.
Forbidden: Removing requirements on your own.
If Spec has: gaps, ambiguity, or conflicts → stop development immediately.
---
# Rule 2: Contract First
Interface implementations must:
    Strictly follow: field names, field types, error codes, return values, events, MQ Messages.
    Forbidden: Guessing fields.
    Forbidden: Modifying the Contract.
---
# Rule 3: Official Documentation First
When dealing with:
    Third-party SDKs
    HTTP APIs
    MQ
    Databases
    Frameworks
Must:
    Consult official documentation first.
Forbidden:
    Implementing based on memory or experience.
If:
    Official documentation
    Project code
    Spec
Conflict:
    Stop development and report.
---
# Rule 4: Minimal Change Principle
Only modify:
    What the current task requires.
Forbidden:
    Incidental refactoring.
Forbidden:
    Incidental bug fixes.
Forbidden:
    Reformatting the entire project.
Forbidden:
    Expanding the change scope.
Issues discovered:
    Record as suggestions.
    Wait for a future task.
---
# Rule 5: Maintain Compatibility
New capabilities:
    Must not break:
        API
        MQ
        Database
        Configuration
        DTO
        VO
        Entity
If modification is required:
    Must:
        Remain compatible with the old implementation.
---
# Rule 6: Analyze Impact Before Modification
When modifying:
    Interfaces
    VOs
    DTOs
    Entities
    Mappers
    Services
    Shared utilities
Must:
    Analyze:
        All references.
    Confirm:
        Nothing is missed.
    Must not:
        Modify one place and commit immediately.
---
# Rule 7: Prefer Reuse
Prefer:
    Extending existing implementations.
Forbidden:
    Copying existing code.
Forbidden:
    Duplicate implementation.
For new shared capabilities:
    Must:
        Extract into shared components.
---
# Rule 8: No Guessing
If you don't know:
    Stop immediately.
Must:
    Report.
Must not:
    Continue based on assumptions.
---
# Rule 9: Code Must Be Verifiable
New code:
    Must:
        Be:
            Compilable
            Testable
            Reviewable
    Must not:
        Be only theoretically correct.
    Must:
        Be actually verified.
---
# Rule 10: Tests Are Part of the Feature
Tests are not secondary work.
New:
    Business code
Must:
    Include:
        Automated tests.
    Cover at minimum:
        Happy path
        Error path
        Boundary conditions
---
# Rule 11: Review Is Part of Development
Coding complete:
    Does not mean the task is done.
Must:
    Perform:
        Self Review.
Check:
    Spec
    Contract
    Naming
    Comments
    Exception handling
    Logging
    Tests
    Performance
    Security
    Documentation
Only when all pass:
    Can the task be completed.
---
# Rule 12: Documentation
New:
    Classes
    Public methods
    VOs
    DTOs
    MQ messages
Must: Include documentation.
    Complex logic:
        Explain:
            Why.
        Not:
            What it does.
---
# Rule 13: Logging Standards
Logs must:
    Help locate problems.
Logs must at minimum include:
    Business ID
    Request ID (if available)
    Key parameters
Forbidden:
    Outputting:
        Passwords
        Tokens
        Secrets
        Private data
---
# Rule 14: Exception Standards
Forbidden: Swallowing exceptions.
Forbidden: Empty catch blocks.
Must:
    Preserve business semantics.
    Log the error.
---
# Rule 15: No Leftovers
Before committing code:
    Must confirm:
        None of the following remain:
            TODO
            FIXME
            Debug Code
            printStackTrace
            System.out.println
            Dead Code
---
# Rule 16: Task Boundaries
One execution:
    Completes only:
        One Task.
Must not:
    Implement the next Task ahead of time.
Must not: Modify future functionality.
---
# Rule 17: Workflow
Must:
    Strictly follow the Runtime Workflow.
Must not:
    Skip:
        Planning
        Review
        Testing
        Verification
---
# Rule 18: Definition of Done
A task is complete only when ALL of the following are met:
✔ Spec complete
✔ Contract complete
✔ Compiles
✔ Unit tests pass
✔ Review passes
✔ Documentation complete
✔ Task Card updated
✔ No new TODOs
✔ No new warnings
---
# Rule 19: Issues Found
If issues are found in: Spec, Contract, or Architecture.
Must: Stop.
Output: Problem, impact, recommendation. Wait for confirmation.
Must not: Fix on your own.
---
# Rule 20: Output Requirements
All outputs must include:
1. Task understanding
2. Modification plan
3. Impact scope
4. Risks
5. Testing strategy
6. Verification results
7. Review results
Must not: Output code directly.
Wait for confirmation before: Starting implementation.
---
# Absolute Prohibitions
Absolutely forbidden:
- Guessing business logic
- Guessing fields
- Guessing error codes
- Guessing APIs
- Modifying Spec
- Modifying Contract
- Skipping tests
- Skipping review
- Removing backward compatibility
- Expanding change scope without authorization
- Leaving debug code
- Leaving TODO
- Leaving FIXME
- Outputting non-compilable code

Violating any of the above requires immediately stopping the task and reporting the reason.
