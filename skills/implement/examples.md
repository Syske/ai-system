# Examples

Purpose

Provide reference execution examples for the Implement Skill.

Examples demonstrate:

- How to reason about a task.
- How to apply constraints.
- How to stop when required.
- How to validate completion.

Examples are workflow references only.

They do not replace:

- workflow.md
- decision.md
- checklists.md
- validation.md

---

# Example 1: Standard Implementation

## Task

```
T003 — Implement createUser endpoint
```

## Context

Task references:

- User creation specification
- UserService contract
- User creation scenario

---

## Execution

### Context Loading

Loaded:

- Task Card
- Specification
- Contract
- Scenario
- Existing UserService code
- Existing tests


### Standards Binding

Applied Standards:

Code Quality:
- Follow existing service patterns
- Keep changes minimal

Documentation:
- New classes require documentation
- Public methods require comments

Testing:
- Happy path
- Error path
- Boundary cases


### Planning

Scope:

In scope:

- UserController
- UserService implementation
- Request/Response DTO
- Unit tests


Out of scope:

- Database redesign
- Authentication changes
- Email validation refactoring


### Confirmation

User approves implementation plan.


### Implementation

Create:

```
UserCreateRequest.java
UserCreateResponse.java
```

Modify:

```
UserController.java
UserServiceImpl.java
```

Implementation follows:

- Existing architecture
- Contract definition
- Applied Standards


### Validation

Verify:

- Build success
- Unit tests pass
- Contract matches
- Documentation complete


Result:

Task completed.

---

# Example 2: Configuration Change with Test Impact

## Task

```
T007 — Add MQ topic configuration
```

## Context

Existing service requires:

```
@Value("${mq.topic}")
private String topic;
```

---

## Execution


Planning identifies:

Modified:

```
LiveService.java
LiveServiceTest.java
```


Risk:

Existing tests instantiate service manually.

---

## Implementation


Add configuration field.


Before completion check:

Documentation:

- Field has explanation.

Testing:

- Existing tests updated.


---

## Validation

Verify:

- Configuration loaded correctly.
- Tests pass.
- No behavior regression.


Result:

Task completed.

---

# Example 3: Contract Conflict

## Task

```
T012 — Add deleteUser endpoint
```

## Conflict


Task description:

```
deleteUser returns void
```


Contract:

```
deleteUser(DeleteRequest): DeleteResponse
```


---

## Decision


Do not implement.


Report:

```
CONFLICT DETECTED

Type:
Contract conflict

Detail:
Task requirement conflicts with contract definition.

Source:
T012 vs UserService contract

Action:
Request clarification.
```


Stop.

---

# Example 4: Missing Dependency

## Task

```
T015 — Send notification after user creation
```


## Analysis


Required:

```
NotificationService
```


Found:

- No contract
- No implementation
- No previous task


---

## Decision


Stop.


Report:

```
Missing Dependency

NotificationService is required but not defined.

Action:
Create dependency task or provide contract.
```


---

# Example 5: Standards Violation Detection

## Task

```
T020 — Add LiveProgressMqVO
```


## Implementation Result


Functionality:

PASS


Tests:

PASS


But review finds:


Violation:

```
LiveProgressMqVO.java

Missing:

- Class Javadoc
- Field comments
```


---

## Decision


Task is not complete.


Action:

Fix documentation.


Re-run:

- Standards validation
- Review checklist


Only after passing:

Mark completed.

---

# Example 6: Scope Creep


## Task

```
T030 — Add user status query
```


During implementation:


Developer notices:

```
UserStatusService
```

contains old duplicated logic.


Temptation:

Refactor the service.


---

## Decision


Do not modify.


Report:

```
Scope Alert

Detected unrelated refactoring opportunity.

Recommendation:
Create separate refactoring task.
```


Continue only with T030.

---

# Example Principle

Correct implementation means:

```
Task Requirement
        +
Contract Compliance
        +
Specification Compliance
        +
Applied Standards
        +
Tests
        +
Validation
        =
Completed Task
```

Code that works but violates standards is incomplete.