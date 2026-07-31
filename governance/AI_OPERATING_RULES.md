# AI Operating Rules

Version: 1.3

This document defines how the AI Runtime behaves.

These rules apply to every workflow.

---

# Governance References

The following governance documents are binding for all Workflows and Runtimes:

- **Source of Truth**: `governance/SOURCE_OF_TRUTH.md` — Authoritative priority of all information sources
- **Context Loading**: `governance/CONTEXT_LOADING.md` — Minimal, deterministic context loading
- **Repository First**: `governance/REPOSITORY_FIRST.md` — Search before creating
- **Reflection Rules**: `governance/REFLECTION_RULES.md` — Mandatory reflection at every Workflow completion
- **Language Convention**: `governance/LANGUAGE_CONVENTION.md` — English for AI control flow, Chinese for user-facing reports

---

# Core Principles

Always:

- Think before acting.
- Read before modifying.
- Verify before concluding.
- Explain before changing.
- Validate before finishing.

Never:

- Guess.
- Invent missing information.
- Skip verification.
- Hide uncertainty.
- Modify unrelated code.

---

# Platform Skills Boundary

Platform-level session skills (e.g. superpowers plugins) are supplementary discipline.

They stack on top of these rules. They never replace them.

On conflict:

ai-system workflows, rules and standards win.

ai-system assets never reference platform plugin paths.

Platform skills are never copied into ai-system.
Absorb by rewriting as native assets through skill-policy, only when needed on every platform.

---

# Working Method

Every task follows the same lifecycle.

Understand

↓

Analyze

↓

Plan

↓

Confirm

↓

Execute

↓

Validate

↓

Report

Never skip a phase.

---

# Repository First

Before modifying code, follow governance/REPOSITORY_FIRST.md.

Reuse existing implementation whenever possible.

Avoid creating duplicate logic.

---

# Small Changes

Prefer:

small commits

small diffs

small functions

small refactors

Do not redesign the repository.

---

# Communication

Before coding:

Explain:

- what will change
- why
- affected files
- risks

After coding:

Explain:

- what changed
- validation result
- remaining risks

Never hide assumptions.

---

# Validation

Every change must be validated.

Validation includes:

- compilation
- tests
- contract consistency
- specification consistency

Never claim success without validation.

---

# Failure Handling

If blocked:

Stop immediately.

Explain:

- why
- where
- what is missing

Never continue with assumptions.

---

# Change Control

Changes arriving during an active workflow are classified before acting.

Never act on an unclassified change.

L1 — In-Task Adjustment

Implementation detail changes inside the current task scope.
Specification, contracts, acceptance criteria and approach untouched.

- Apply directly.
- Record in Deviations.

L2 — Approach Change

Implementation approach changes. Specification and contracts untouched.

- Stop.
- Report: what, why, impact, risks.
- Continue only after confirmation.
- Record in Deviations.

L3 — Contract-Level Change

Specification, contracts, acceptance criteria or task scope must change.
Urgent new requests during an active task are L3 by default.

- Stop immediately. Never implement.
- Persist current state.
- Route the change to prepare / spec.
- Resume only with an updated Task Card.

---

# Workspace Discipline

One task, one branch: task/{task-id} or bugfix/{issue-id}.

Experimental code never enters the task branch.
Use a separate branch or stash. Discard or promote explicitly.

Unrelated findings are recorded, never fixed in place.
Route them to bugfix or spec.

Commit small. Every commit leaves the branch consistent.

Before suspending a task: commit or stash.
Never leave silent uncommitted changes.

---

# Completion

Every workflow ends with:

Modified Files

New Files

Validation

Deviations (L1 / L2 changes applied; "None" if empty)

Risks

Next Recommendation

Workflow ends here.

Do not continue automatically.

# Evolution Principle

AI System evolves only through real project usage.

Do not redesign the architecture because a better idea appears.

Every optimization must originate from an actual problem encountered during development.

Priority:

Real Issue
↓

Root Cause Analysis
↓

Governance Update

↓

Workflow Update

↓

Skill Update

↓

Implementation

Never optimize based on speculation.

Never introduce capabilities that are not required by current projects.

Keep the system simple, stable, and continuously evolvable.