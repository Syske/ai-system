# Runtime: Analysis

Extends:

- runtime-base.md

---

## Purpose

Analyze an AI System.

The Runtime produces structured analysis and optimization recommendations.

No implementation is performed.

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

- Context Analysis
- Structure Analysis
- Dependency Analysis
- Consistency Analysis
- Quality Assessment
- Gap Analysis
- Recommendation Generation

---

## Runtime Context

Provided by Runtime Base:

- Runtime Configuration
- Operating Rules

Resolved by Analysis Runtime:

- AI System Context
- Runtime Graph
- Workflow Graph
- Skill Graph
- Framework Graph

---

## Phase 1 — Context Analysis

Collect:

- Runtime
- Workflow
- Skills
- Frameworks
- Governance
- Configuration

Generate:

System Overview

---

## Phase 2 — Structure Analysis

Analyze:

- Directory Structure
- Runtime Hierarchy
- Workflow Relationships
- Skill Relationships

Generate:

Structure Report

---

## Phase 3 — Dependency Analysis

Analyze:

- Runtime Dependencies
- Skill Dependencies
- Framework Dependencies
- Circular Dependencies

Generate:

Dependency Report

---

## Phase 4 — Consistency Analysis

Verify:

Workflow

↓

Runtime

↓

Skills

↓

Framework

↓

Templates

Generate:

Consistency Report

---

## Phase 5 — Quality Assessment

Evaluate:

- Modularity
- Maintainability
- Reusability
- Scalability
- Extensibility

Generate:

Quality Report

---

## Phase 6 — Recommendations

Generate:

- Improvement Suggestions
- Refactoring Opportunities
- Missing Components
- Best Practices

---

## Outputs

Generate:

- analysis-report.md
- dependency-report.md
- consistency-report.md
- recommendations.md

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

## Knowledge Feedback

Before declaring completion, identify reusable findings from the analysis
(patterns, decisions, pitfalls, standards gaps) and guide their collection
into the knowledge base (`governance/memory/`) via the Knowledge workflow
(`collect` operation). This closes the loop: knowledge → analysis →
updated knowledge → future prepare/spec.

---

## Completion

Return:

- Analysis Summary
- Quality Assessment
- Recommendations