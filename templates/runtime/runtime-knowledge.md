# Runtime: Knowledge

Extends:

- runtime-base.md

---

## Purpose

Manage reusable knowledge assets.

The Knowledge Runtime provides long-term knowledge capabilities for AI System and Engineering workflows.

The Runtime does not perform implementation.

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

# Responsibilities

The Runtime is responsible for:

- Knowledge Discovery
- Knowledge Collection
- Knowledge Extraction
- Knowledge Classification
- Knowledge Validation
- Knowledge Storage
- Knowledge Retrieval
- Knowledge Lifecycle Management

---

# Runtime Context

Provided by Runtime Base:

- Runtime Configuration
- Operating Rules
- Workspace Context

Resolved by Knowledge Runtime:

- Knowledge Sources
- Knowledge Assets
- Knowledge Metadata
- Knowledge Relationships

---

# Knowledge Types

Supported knowledge categories:

## AI System Knowledge

Examples:

- Runtime Design
- Workflow Patterns
- Skill Guidelines
- Prompt Patterns
- Framework Usage
- Agent Architecture

---

## Engineering Knowledge

Examples:

- Architecture Decisions
- Coding Standards
- Design Patterns
- Troubleshooting Records
- Performance Practices

---

## Project Knowledge

Examples:

- Domain Rules
- Business Concepts
- Module Knowledge
- Historical Decisions

---

# Phase 1 — Knowledge Discovery

Collect knowledge sources.

Sources may include:

- Documentation
- Specifications
- ADR
- Code Analysis
- Runtime Reports
- Review Reports
- Incident Reports

Generate:

Knowledge Candidates

---

# Phase 2 — Knowledge Extraction

Extract:

- Concepts
- Rules
- Relationships
- Examples
- Constraints

Generate:

Knowledge Items

---

# Phase 3 — Knowledge Classification

Classify:

- Category
- Scope
- Owner
- Version
- Lifecycle State

---

# Phase 4 — Knowledge Validation

Verify:

- Accuracy
- Completeness
- Consistency

Reject:

- Duplicate Knowledge
- Contradictory Knowledge
- Temporary Information

---

# Phase 5 — Knowledge Storage

Store:

- Knowledge Content
- Metadata
- Relationships
- Source References

---

# Phase 6 — Knowledge Retrieval

Provide:

- Context Retrieval
- Related Knowledge
- Historical Decisions
- Recommendations

Used by:

- Spec Runtime
- Develop Runtime
- Review Runtime
- Analysis Runtime

---

# Outputs

Generate:

- Knowledge Assets
- Knowledge Index
- Knowledge Metadata
- Knowledge Report

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

# Completion

Return:

- Knowledge Operation Result
- Updated Assets
- Retrieval Context