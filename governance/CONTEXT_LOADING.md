# Context Loading Strategy

Version: 1.0

---

## Purpose

Define how every Runtime loads context.

Context is expensive. Every token loaded increases noise and reduces focus.

The goal is minimal, deterministic, just-in-time context loading.

---

## Principle

```
LOAD ONLY WHAT THE TASK REQUIRES. NOTHING MORE.
```

---

## Loading Order

Context must be loaded in this priority order:

```
Task Card
    ↓
Contract
    ↓
Specification
    ↓
Affected Source Code
    ↓
Coding Standards (applied)
    ↓
Referenced Skills
```

Higher items are loaded first. If a higher item resolves the question, stop — do not load lower items.

---

## Forbidden Patterns

Never:

- Load the entire repository tree into context
- Load all Specifications at once
- Load all Task Cards at once
- Load documentation unrelated to the current task
- Load examples before the relevant standard
- Load historical memory unless the task specifically requires it

---

## Per-Runtime Rules

### spec

Load: Preparation Report → Architecture Summary → existing specs/contracts in change scope

Do NOT load: full repository source code

### dev-setup

Load: Environment Context → Workspace Metadata → repository YAML metadata → spec reference (identity only)

Do NOT load: repository source code

### develop

Load: Task Card → Specification → Contracts → Applied Standards → affected modules and tests

Do NOT load: entire repository tree

### bugfix

Load: Bug Description → Logs → Stack Trace → affected modules → related tests

Do NOT load: entire repository tree

### review

Load: Task Card → Specification → Contracts → Applied Standards → implementation changes → test results

Do NOT load: entire repository tree

### prepare

Load: Environment Context → Change Request → target repository structure and entry points

Do NOT load: entire repository tree

---

## Context Reuse

Context loaded by a prior Runtime phase is available for subsequent phases.

Do not reload the same context unless it has changed.

---

## Reference

Every Runtime Template must reference this document.

The reference line is:

```
Context loading: governance/CONTEXT_LOADING.md
```
