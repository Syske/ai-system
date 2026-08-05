# Runtime: Proposal

Extends:

- runtime-base.md

---

## Purpose

Discuss an optimization or ad-hoc idea and produce a solution document.

The Proposal Runtime turns a topic into a structured solution document.
It may reference code under projects/ but is not bound to a change lifecycle.

The Runtime does not modify business implementation.

---

## Governance

This Runtime is bound by:

- AI Operating Rules: governance/AI_OPERATING_RULES.md
- Source of Truth: governance/SOURCE_OF_TRUTH.md
- Context Loading: governance/CONTEXT_LOADING.md
- Repository First: governance/REPOSITORY_FIRST.md
- Reflection Rules: governance/REFLECTION_RULES.md

Context is loaded according to governance/CONTEXT_LOADING.md.
Standards are loaded according to loaders/standards-loader.md.

---

## Responsibilities

The Runtime is responsible for:

- Background Collection
- Option Generation
- Trade-off Analysis
- Solution Recommendation
- Risk Identification

---

## Runtime Context

Provided by Runtime Base:

- Runtime Configuration
- Operating Rules

Resolved by Proposal Runtime:

- Topic Context
- Option Set
- Recommended Solution
- Risk Register

---

## Phase 1 — Background Collection

Collect:

- The declared Topic
- Related Materials when provided
- Relevant code references from the selected projects, when provided

When projects are selected, resolve and record, per project:

- Target Branch (from Branch Mapping entry, default: master)
- Base Branch (the branch the target branch is based on, default: master)

Record referenced code as `project:branch` in the topic context.

Generate:

Topic Context

---

## Phase 2 — Option Generation

Generate:

- Candidate solution options for the Topic

If the Topic is ambiguous or information is insufficient:

- Ask clarifying questions in the system language (config/menu.yaml → locale)
- Do not guess

Generate:

Option Set

---

## Phase 3 — Trade-off Analysis

For each option, analyze:

- Effort
- Impact
- Compatibility
- Risks
- Dependencies

When cross-project code is referenced, label it as `project:branch`.

Generate:

Trade-off Analysis

---

## Phase 4 — Solution Recommendation

Generate:

- Recommended solution with rationale
- Alternative options summary

---

## Phase 5 — Risk Identification

Identify:

- Risks
- Assumptions
- Open questions

Generate:

Risk Register

---

## Phase 6 — Solution Document

Generate:

- solution.md

The document is written in the system language (config/menu.yaml → locale, per governance/LANGUAGE_CONVENTION.md).

The document contains:

- Background
- Solution options with trade-offs
- Recommended solution
- Risks and assumptions
- Next steps
- References (any code referenced as `project:branch`, with its base branch noted)

---

## Outputs

Generate:

- solution.md

## Reflection

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

## Completion

Return:

- Solution Summary
- Recommended Solution
- Risks
