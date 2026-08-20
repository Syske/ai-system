# Single Source of Truth

Version: 1.0

---

## Purpose

Define the authoritative priority of all information sources in the AI Runtime.

When two sources conflict, the higher source always wins.

---

## Priority Hierarchy

```
1. Contract
       ↓
2. Specification
       ↓
3. Task Card
       ↓
4. Workflow
       ↓
5. Skill
       ↓
6. Template
       ↓
7. Example
```

---

## Rules

### 0. External Inputs are Unverified (External AI Conclusions)

Conclusions produced by an **external AI / analyst / share link** are **unverified
inputs**, NOT sources of truth. They do not sit anywhere in the hierarchy above and
never override Contract / Specification / Task Card / repository evidence.

Before any external conclusion may enter reports, memory, or deliverables, it must
pass the checkpoint in `templates/prompts/external-ai-review.md` (claim-by-claim
KEEP / REVISE / REJECT / UNVERIFIABLE with evidence). Conflicts between an external
conclusion and internal evidence are arbitrated by the user
(`AI_USER_RESPONSIBILITY_CONTRACT` D10 / E2).

### 1. Contract is Supreme

A Contract defines the exact interface between systems.

If any lower source contradicts a Contract, the Contract wins.

Contracts are NOT modified during implementation (L3 Change Control).

### 2. Specification Defines Behavior

A Specification defines what the system must do.

If a Task Card or Workflow contradicts a Specification, the Specification wins.

Specifications are NOT modified during implementation (L3 Change Control).

### 3. Task Card is Implementation Scope

A Task Card defines the exact scope of one implementation unit.

Do not expand beyond the Task Card scope, even if lower sources suggest additional work.

### 4. Workflow Defines Process

A Workflow defines what process should be executed and in what order.

Skills execute within Workflow boundaries, never outside them.

### 5. Skill Defines Method

A Skill defines how a specific activity is performed.

Templates contain reusable patterns, not authoritative rules.

### 6. Template is a Pattern

Templates are reusable scaffolds. They are never authoritative over Skills or Workflows.

### 7. Example is Illustrative

Examples demonstrate patterns. They are never authoritative and may be outdated.

---

## Enforcement

Every Runtime must obey this hierarchy.

When in doubt, escalate to the next higher source.

Never resolve conflicts by guessing.

---

## Reference

This document is referenced by `governance/AI_OPERATING_RULES.md`.

Every Runtime Template must include:

```
Source of truth: governance/SOURCE_OF_TRUTH.md
```
