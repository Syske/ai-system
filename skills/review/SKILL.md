---
name: review
description: >
  Formal quality gate review. Assesses implementation quality against
  engineering standards. Produces Design / Code / Quality review reports
  and routes the task to verify, develop, bugfix, or spec re-entry.
---

# Review Skill

## Purpose

Evaluate engineering quality of a completed implementation before verification.

The Review Skill assesses:

- Design quality (architecture, layers, dependencies)
- Code quality (readability, naming, complexity, error handling)
- Standards compliance (coding, documentation, testing)
- Quality attributes (security, performance, maintainability)

The Skill produces a structured review with classified findings and a routing decision.

---

## Responsibility

This Skill is responsible for:

- Design Review
- Code Review
- Standards Compliance Review
- Quality Review
- Finding Classification (Critical / Major / Minor / Suggestion)
- False Completion Detection
- Routing Decision (Approved → verify / Changes Required → develop)

---

## Non-Responsibility

This Skill does NOT:

- Modify code
- Fix bugs
- Implement suggestions
- Modify Specifications or Contracts
- Replace `review-changes` (knowledge-graph-driven lightweight analysis)

---

## Execution

Review execution is defined by `templates/runtime/runtime-review.md`.

Phases:

1. Review Preparation — collect Task Card, Plan, Spec, Implementation, Test Results
2. Design Review — architecture consistency, layer responsibilities, dependency direction, domain boundaries
   - Grilling Method: tree-walk design decisions, single question at a time, codebase-first
3. Code Review — readability, naming, complexity, duplication, error handling, logging
   - False Completion Detection: verify every [x] in Task Card against actual implementation
4. Standards Review — coding standards, documentation standards, testing standards
5. Quality Review — security, performance, compatibility, maintainability
6. Review Summary — classify all findings
7. Task Card Verification — update Review Result status

---

## Output

- Updated Task Card (Review Result appended)
- review-report.md
- design-review.md
- code-review.md
- quality-review.md

## Routing

| Finding Type | Action |
|---|---|
| Approved, no action items | → verify |
| Minor observations | → verify + optional issue |
| Implementation issues | → develop (fix + re-review) |
| Genuine defect | → bugfix |
| Requirement gap | → spec re-entry |
| Code quality problems (lint, naming, style) | → develop |
