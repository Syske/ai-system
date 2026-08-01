# Coding Memory Guidelines

Version: 1.0

---

# Purpose

Coding Memory stores verified engineering experiences.

Its purpose:

- Record lessons learned from real development.
- Prevent repeating known mistakes.
- Preserve valuable debugging and implementation experience.
- Provide historical context for future tasks.

Coding Memory is an experience repository.

It is not a rule repository.

---

# Language

Memory entries MUST be written in English (AI-internal layer), per `governance/LANGUAGE_CONVENTION.md`.

User-facing reports are produced in Chinese; memory is loaded by agents at execution time, so it stays English.

---

# Responsibility Boundary

Coding Memory must keep clear boundaries with other AI system components.

---

## Coding Memory

Responsible for:

- Past problems.
- Root causes.
- Verified solutions.
- Reusable engineering lessons.

Examples:

- Production incidents.
- Difficult debugging findings.
- Repeated implementation pitfalls.
- Important review discoveries.

---

## Standards

Responsible for:

- Mandatory engineering rules.
- Coding conventions.
- Quality requirements.

Examples:

- Naming rules.
- Documentation requirements.
- Testing requirements.
- Code style rules.

Location:

```

ai-system/governance/standards/

```

---

## Skills

Responsible for:

- Execution methods.
- Implementation approaches.
- Problem-solving procedures.
- Reusable workflows.

Location:

```

ai-system/skills/

```

---

## Specifications / Contracts

Responsible for:

- Business requirements.
- Interface definitions.
- Data contracts.
- Project behavior.

Location:

```

workspaces/<project_id>/openspec/

```

---

## Runtime / Workflow

Responsible for:

- Execution lifecycle.
- Task orchestration.
- Process control.

Location:

```

ai-system/templates/runtime/
ai-system/workflows/

```

---

# Golden Rule

Coding Memory records experience, not rules.

If an entry becomes a mandatory requirement:

Move it to Standards.

If an entry becomes an execution method:

Move it to Skills.

If an entry describes business behavior:

Move it to Specification or Contract.

---

# When to Add Memory

Create a new memory entry only when at least one condition is satisfied.

---

## Production Issue

Examples:

- Production failure.
- Data inconsistency.
- Compatibility problem.
- Performance regression.
- Security issue.

---

## Repeated Development Problem

Examples:

- The same mistake occurred multiple times.
- A common implementation trap was discovered.

---

## Important Review Finding

Examples:

- Hidden compatibility risk.
- Incorrect abstraction.
- Missing dependency analysis.
- Maintainability issue.

---

## Difficult Investigation Result

Examples:

- Non-obvious root cause.
- Valuable debugging method.
- Complex environment issue.

---

# When NOT to Add Memory

Do not add memory for the following cases.

---

## Temporary Fixes

Example:

```

Changed timeout from 10s to 30s.

```

Unless the reason is generally reusable.

---

## Single Project Requirements

Example:

```

Live migration uses xxx configuration.

```

Belongs to:

```

workspaces/<project_id>/openspec/

```

---

## Coding Rules

Example:

```

All VO fields require comments.

```

Belongs to:

```

standards/documentation.md

```

---

## Personal Preferences

Example:

```

I prefer this coding style.

````

Not a memory item.

---

# Entry Format

All memory entries should follow this format.

```markdown
## [Category] Title

Date:

YYYY-MM-DD


Priority:

P0 | P1 | P2


Context:

Describe where and under what scenario this happened.


Problem:

Describe the observable issue and impact.


Root Cause:

Explain the technical reason.


Solution:

Describe the verified solution.


Lesson:

Describe what future implementations should remember.


Scope:

Describe when this experience applies.


Related:

- Standard:
- Skill:
- Specification:
- Contract:
````

---

# Field Guidelines

## Title

Purpose:

Provide a searchable and meaningful summary.

Format:

```
[Category] Short Description
```

Examples:

Good:

```
[MQ] Avoid Dynamic Message Body

[Database] Analyze Index Before Query Optimization

[API Integration] Verify Official Error Codes
```

Avoid:

```
Bug Fix

Problem

Issue
```

---

## Date

Purpose:

Record when the experience was discovered.

Format:

```
YYYY-MM-DD
```

---

## Priority

Purpose:

Indicate importance.

Values:

```
P0
P1
P2
```

Definitions are described below.

---

## Context

Purpose:

Explain where and under what scenario the problem occurred.

Should include:

* System or module.
* Technical scenario.
* Trigger condition.

Avoid:

* unnecessary business details.
* confidential information.

Good:

```
RocketMQ event communication between live-service modules.
```

Bad:

```
Live project had a problem.
```

---

## Problem

Purpose:

Describe the observable issue.

Should explain:

* What happened.
* What impact occurred.

Good:

```
Consumer failed after producer introduced a new field.
```

Bad:

```
MQ was unstable.
```

---

## Root Cause

Purpose:

Explain the actual technical reason.

Requirements:

* Focus on technical cause.
* Avoid personal blame.

Good:

```
Producer and consumer did not share an explicit message contract.
```

Bad:

```
Developer forgot.
```

---

## Solution

Purpose:

Describe the verified fix.

Should include:

* Implementation approach.
* Important constraints.
* Validation method.

Avoid:

* Temporary workaround without explanation.

---

## Lesson

Purpose:

Extract reusable experience.

This is the most important field.

A good Lesson answers:

```
What should future implementations remember?
```

Good:

```
Business MQ messages should use explicit typed contracts.
```

Bad:

```
Changed the code.
```

---

## Scope

Purpose:

Define where this memory applies.

Good:

```
All RocketMQ business events.

All Java Spring services.

External API integrations.
```

Avoid:

```
All software development.
```

---

# Priority Definition

## P0

Critical engineering experience.

Examples:

* Production incident.
* Data corruption.
* Security issue.
* Severe availability impact.

---

## P1

Important reusable engineering lesson.

Examples:

* Frequent development mistake.
* Compatibility issue.
* Difficult debugging problem.

---

## P2

Optimization experience.

Examples:

* Development efficiency improvement.
* Readability improvement.
* Minor engineering improvement.

---

# Category Guidelines

Recommended categories:

```
Java

Python

Database

MQ

Cache

API Integration

Build

Testing

Performance

Security
```

Do not create categories casually.

A new category should:

* Have long-term maintenance value.
* Apply to multiple tasks.
* Not duplicate existing categories.

---

# Memory Organization

Recommended structure:

```
ai-system/

└── governance/

    └── memory/

        ├── MEMORY_GUIDELINES.md
        ├── coding-memory.md

        ├── java/

        │   ├── coding-memory.md
        │   ├── mq.md
        │   └── database.md

        ├── python/

        │   └── coding-memory.md

        └── integration/

            ├── wecom.md
            └── dingding.md
```

---

# Before Adding Memory

Before creating a new entry:

## Check Existing Knowledge

Search:

* Standards.
* Skills.
* Existing Memory.

Avoid duplication.

---

## Verify Reusability

Ask:

```
Will another future task benefit from knowing this?
```

If no:

Do not add.

---

## Verify Lesson Quality

Every entry must contain a clear Lesson.

A record without a reusable lesson has limited value.

---

# Updating Memory

Allowed:

* Add examples.
* Clarify scope.
* Improve explanation.
* Add related references.

Avoid:

* Changing historical facts.
* Turning memory into mandatory rules.
* Mixing unrelated experiences.

---

# Agent Usage Rules

When executing tasks:

Load relevant memory only.

Do not load all memory files by default.

Select memory based on:

* Programming language.
* Framework.
* Technical domain.
* Task type.

Examples:

Java MQ change:

```
governance/memory/java/mq.md
```

Third-party API integration:

```
governance/memory/java/integration.md
```

---

# Lifecycle Triggers

Coding Memory is maintained through the `knowledge` workflow operations.
The following triggers define when each operation runs (see OPERATIONS.md 1.7):

| Operation | Trigger | Actions |
|---|---|---|
| collect | After each release or retrospective | Add verified lessons, update index |
| update | When a verified solution changes | Clarify scope, add examples, fix explanation |
| search | On demand during a task | Load only relevant category files |
| review | Monthly | De-duplicate, check contradictions, flag stale entries |
| archive | Quarterly | Move outdated entries to archive, update index |

Rules:

- `review` must run before `archive`; never archive un-reviewed entries.
- An entry is stale when its lesson no longer applies or a newer standard replaces it.
- Archiving removes the entry from the active index; the archived file keeps the historical record.
- `tools/check.py` validates memory structure (entry format, index integrity, language) on every run.

---

# Maintenance Principle

Coding Memory should grow slowly.

Quality is more important than quantity.

Prefer:

```
One valuable memory entry.
```

over:

```
Ten low-value notes.
```

---

# Final Principle

Standards define:

```
What must be done.
```

Skills define:

```
How to do it.
```

Memory explains:

```
What has been learned.
```

Keep these responsibilities separate.