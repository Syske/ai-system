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

# Phase 4.5 — Approval Gate (hotfix mode only, driven by config/workflows/bugfix-modes.yaml)

Activate only when the configured mode sets `approval_gate` (e.g. hotfix:
`approval_gate: plan`) and the current run is in that mode.

Steps:

- Present the Fix Plan: Scope, Impact, Risks, Rollback Considerations.
- Present the confirmation request in the system language (config/menu.yaml → locale).
- Wait for explicit user confirmation.
- Stop (do NOT proceed to branch/implement) until confirmed. No confirmation → stop.

---

# Phase 4.6 — Branch (hotfix mode only, driven by config/workflows/bugfix-modes.yaml)

Activate only when the configured mode's `phases` contains `branch`.

Steps:

1. Determine the base branch: `branch.from` in the mode config (hotfix default: master).
2. Build the branch name from `branch.template` placeholders
   ({date}/{type}/{desc}/{service}; values come from the BugFix context).
3. Create the branch locally: `git switch -c <name> <from>` (never push until commit verified).
4. Before creating, invoke the branch name parser (contract below) to sanity-check
   the generated name: parse(<name>) must not return None.

## Branch Name Parser Contract (stable — providers MUST NOT change)

- Logical name: `branch.parser` in the mode config (e.g. `hotfix-branch-parser`).
- Script path (resolved by provider): `extensions/<name>/scripts/branch_parser.py`
  where `<name>` is the provider extension directory matching the logical name.
- Method (fixed): `parse(branch_name: str) -> ParsedBranch | None`
- Return fields (fixed): `{date, type, desc, service}` (all `str`; empty string when absent)
- Behavior:
  - Unparseable input → return `None` (do NOT raise).
  - Empty/blank input → return `None`.
- ai-system only depends on the method name, parameter, and return fields above;
  it never depends on provider-internal parsing details.
- Provider implementation: scaffold with `python tools/branch-parser-scaffold.py init <name>`
  (generates contract skeleton + contract tests), then fill in the company-specific
  pattern (e.g. `cc{date}_{type}{desc}_{service}`).
- Gate: `tools/checks/bugfix_modes.py` (check.py item 15) enforces that a configured
  parser resolves to an existing script with the exact contract signature.

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

---

# Phase 6.5 — Commit (hotfix mode only, driven by config/workflows/bugfix-modes.yaml)

Activate only when the configured mode's `phases` contains `commit`.

Steps:

- When `commit.require_message` is true, commit with a message following
  the repository commit conventions (one fix per commit, atomic).
- Commit on the branch created in Phase 4.6.
- Do NOT push unless a later phase (doc / MR) requires it.

---

# Phase 6.6 — Doc (hotfix mode only, driven by config/workflows/bugfix-modes.yaml)

Activate only when the configured mode's `phases` contains `doc` AND regression
verification passed (or `doc.trigger` is `on-verify-pass` and Phase 6 passed).

Steps:

- Delegate to the extension named by `doc.extension` (hotfix default:
  hotfix-test-doc) to generate the 转测文档 from the committed branch.
- The extension owns the document template and publication flow.
- Output: 转测文档 generated/updated (see workflows/bugfix.md Next: hotfix-test-doc).

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

# Outputs

Generate:

- Root Cause Report
- Fix implementation (smallest safe change)
- Regression Report
- BugFix Report

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