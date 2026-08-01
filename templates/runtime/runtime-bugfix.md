# Runtime: BugFix

Extends:

- runtime-base.md

---

## Purpose

Diagnose and resolve software defects.

The Runtime focuses on identifying the root cause, applying the smallest safe fix, and preventing regressions.

## Governance

This Runtime is bound by:

- AI Operating Rules: governance/AI_OPERATING_RULES.md
- Source of Truth: governance/SOURCE_OF_TRUTH.md
- Context Loading: governance/CONTEXT_LOADING.md
- Repository First: governance/REPOSITORY_FIRST.md
- Reflection Rules: governance/REFLECTION_RULES.md

Context is loaded according to governance/CONTEXT_LOADING.md.
Standards are loaded according to loaders/standards-loader.md.

## The Iron Law

```
NO FIXES WITHOUT ROOT CAUSE INVESTIGATION FIRST
```

Random fixes waste time and create new bugs. Symptom fixes are failure.
If you have not completed root cause analysis, you CANNOT propose fixes.

---

# Responsibilities

The Runtime is responsible for:

- Issue Analysis
- Reproduction
- Root Cause Analysis
- Fix Planning
- Minimal Change Implementation
- Regression Verification
- BugFix Reporting

---

# Runtime Context

Provided by Bootstrap Runtime:

- Environment Context (repository_root, workspaces_root, methodologies_root)

Provided by Dev Setup Runtime:

- Project Context

Provided by Dev Setup Runtime:

- Workspace Context

Provided by Runtime Base:

- Runtime Configuration
- Operating Rules
- Applied Standards

Resolved by BugFix Runtime:

- Issue Context
- Root Cause
- Fix Plan

---

# Phase 1 — Issue Analysis

Collect:

- Bug Description
- Logs
- Stack Trace
- Monitoring Data
- Related Commits
- Related Issues

Identify:

- Affected Modules
- Suspected Components

Read error messages completely. Do not skip past errors or warnings.
Stack traces often contain the exact solution.
Note line numbers, file paths, error codes.

Generate:

Issue Summary

---

# Phase 2 — Reproduction

Attempt to reproduce the defect.

Collect:

- Inputs
- Environment
- Expected Behaviour
- Actual Behaviour

If reproduction fails:

Record assumptions.

Continue only with explicit confirmation. Present the confirmation request in the system language (config/menu.yaml → locale).

---

# Phase 3 — Root Cause Analysis

Analyze:

- Call Chain
- Data Flow
- Configuration
- Dependencies

## Multi-Component Systems

When the system has multiple components (API → service → database, CI → build → deploy):

**BEFORE proposing fixes, add diagnostic instrumentation at each component boundary:**
- Log what data enters and exits each component
- Verify environment/config propagation
- Check state at each layer
- Run ONCE to gather evidence, THEN analyze to identify the failing component

## Trace Data Flow

When error is deep in the call stack:
- Where does the bad value originate?
- What called this with bad value?
- Keep tracing upward until you find the source
- Fix at source, not at symptom

Determine:

Root Cause

Generate:

Root Cause Report

## Rule of Three

If 3+ fix attempts have failed: STOP and question the architecture.
- Each fix revealing new problems in different places = architectural issue
- Discuss fundamentals with your human partner before attempting more fixes
- This is NOT a failed hypothesis — this is a wrong architecture

Do not implement a fix until the root cause is identified.

---

# Phase 4 — Fix Planning

Plan the fix.

The plan must include:

- Scope
- Impact
- Risks
- Rollback Considerations

Prefer the smallest safe change.

---

# Phase 5 — Implementation

Invoke:

- implement

Requirements:

- Preserve backward compatibility
- Avoid unrelated refactoring
- Keep changes localized

---

# Phase 6 — Regression Verification

Invoke:

- testing
- verification

Verify:

- Original defect resolved
- Existing behaviour unchanged
- Regression tests pass

Generate:

Regression Report

# Reflection

Before declaring completion, execute Reflection according to governance/REFLECTION_RULES.md.

Evaluate:
1. Simpler implementation possible?
2. Code duplication introduced?
3. Standards violated?
4. Over-engineering present?
5. Anything incomplete?

Record the Reflection Report in the Completion output.
Do NOT modify code during Reflection.

---

# Phase 7 — Completion

Generate:

- BugFix Report
- Root Cause Report
- Regression Report

Return:

- Fix Summary
- Modified Files
- Verification Status