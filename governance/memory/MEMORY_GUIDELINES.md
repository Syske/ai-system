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

# Privacy / Sanitization

ai-system is a **PUBLIC repository** (private: False) — memory entries are
pushed to GitHub. Machine-specific or sensitive content MUST NOT be committed.

Prohibited in any entry:

- Local absolute paths: `/mnt/d/...`, `/home/<user>/...`, `~/.jdks`, and Windows
  drive-letter absolute paths (never spell the drive literal).
- Person-name ↔ business-name combinations that identify an individual.
- Internal repository / artifact-server addresses (codeup, internal maven
  mirrors, VPN hosts).

Parameterization:

- Environment-specific facts are written generically: `<maven-home>`,
  `<jdk-home>`, `<repo-root>` — keep the version/behavior that is reusable,
  drop the machine context.
- Example (reusable): `surefire provider pinned by spring-boot-dependencies
  2.1.13 is missing from the OFFLINE maven repo`.
  Example (prohibited): a machine-specific absolute path such as
  the local maven installation directory (never spell the path itself).

Guard: never copy a raw error/log line that embeds an absolute path; redact
before storing. When in doubt, omit the path.

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

VO fields require business-meaning comments; trivial self-explanatory fields may omit them.

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

```

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
```

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

Canonical structure (**follows the live tree** — a guideline that does not match reality is worse than none):

```
governance/memory/
├── MEMORY_GUIDELINES.md
├── coding-memory.md              # entry point / cross-language index
├── ai-system/                    # lessons about the AI system itself
│   ├── coding-memory.md          #   one file per topic (e.g. workflow-chain.md,
│   │                             #   language-boundary.md, file-contract.md, …)
└── java/                         # one directory per language / stack
    ├── coding-memory.md          #   topic index of that directory
    ├── integration.md            #   cross-system integration lessons
    ├── mq.md
    └── spring.md
```

Rules:

- One directory per language / stack (`java/`, …); one file per topic inside it;
  that directory's `coding-memory.md` is its topic index.
- Lessons about ai-system itself go under `ai-system/` (not under a language dir).
- Adding a language = adding a directory; adding a topic = adding a file + its index entry.

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

# Experience Inbox

`governance/memory/drafts/` is the **Experience Inbox**: a low-friction staging
area for unverified candidates, not memory and not a memory draft. It sits under
`governance/memory/` only for proximity; the name and this section exist because
the path alone invites the wrong inference.

The directory is git-ignored. Its content never reaches the repository.

## Hard Rule: Inbox Is Not Knowledge

> **An agent must not use `governance/memory/drafts/` content as a basis for
> knowledge by default.**

Forbidden:

| Forbidden | Counter-example form |
|---|---|
| Citing Inbox content as a fact in an answer | "Per candidate X, ..." where X was never verified |
| Linking or referencing an Inbox path in rules, skills, reports, or canonical entries | ``see `governance/memory/drafts/{yyyymmdd}-{session|topic}.md` `` |
| Reasoning from Inbox content as "verified experience" | using an unverified candidate to support a technical judgement |
| Writing an Inbox path into any tracked asset | index, script doc, ADR, report |
| Widening the memory gate exemption under the guise of this rule | parking "actually worth keeping long term" content in the Inbox |

Permitted, and only under these conditions:

| Permitted | Condition |
|---|---|
| Writing a candidate | at session end |
| Reading during triage | the triage role only (`aic-maintain` step 2.6) |
| Deleting after triage | once the outcome is committed |
| Reporting "the Inbox holds N candidates awaiting triage" | in the triage report |

The most dangerous misreading is that something called a memory draft is memory
itself, and therefore readable. A candidate can carry a plausible story and a
false citation; the source field exists so triage can **reject** it. If candidates
are cited as knowledge before triage, source verification becomes theatre.

## Candidate Format

Filename: `governance/memory/drafts/{yyyymmdd}-{session|topic}.md`. Create the
directory on demand (`mkdir -p`). Any language, any format. No line limit —
completeness of the source beats brevity.

Five fields are mandatory, all of them:

```markdown
## Candidate: <one-line title>

- What: <what happened or was learned>
- Why: <why it matters beyond this session>
- Source: <file:line, commit hash, command output, or URL>
- Candidate Category: memory | standards | skill | project-workspace
```

`Source` is the field that makes triage possible, and its **form** matters as
much as its presence. Verification strength, strongest first:

| Form | Verifiable after the source file is edited? |
|---|---|
| Commit hash (`git show abc1234:path`) | **Yes** — immutable |
| Quoted snippet or command output | **Yes** — self-contained |
| `file:line` | **No** — the line drifts as the file evolves |

Measured during the P71 S2 end-to-end run: a candidate citing
`tools/checks/memory.py:20` was substantively correct, but `DRAFTS_DIR` had
moved to line 31. A line-exact check would have rejected a true claim; a
file-exists-only check would have passed a fabricated one.

Triage therefore treats a stale or out-of-range `file:line` as **needs
confirmation**, not as proof of fabrication, and confirms by content. Capture
should prefer a commit hash or a quoted snippet when one is available — a
candidate that survives its own source's next edit is the one worth promoting.

Language is not constrained at capture. The **canonical** layer stays English
(`MEMORY_GUIDELINES.md` Language section, enforced by the pre-commit gate). The
translation is the triage step's responsibility, not capture's — capture does
not translate.

## Triage

Triage runs on the maintenance cadence (`OPERATIONS.md` 1.7), reading
`drafts/*.md`. For each candidate, verify the source **first**, then dedupe,
then route it:

| Destination | Route to |
|---|---|
| Canonical experience | `governance/memory/<category>/` (English, full entry format) |
| A rule, not an experience | `governance/standards/` |
| A capability, not an experience | `skills/` |
| Belongs to one project only | the project workspace |
| Discard | record the reason, per candidate |

After triage: commit what was promoted, delete the drafts, record the counts.
Counts are mandatory — see the maintenance operational metric (P71 5.9). A
triage run that reports no counts is not a completed triage run.

No candidate is a legitimate outcome. An empty Inbox after triage is a normal
result, not a failure.

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