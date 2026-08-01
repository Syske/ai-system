# Runtime: Specification

Extends:

- runtime-base.md

---

## Purpose

Coordinate the complete Specification lifecycle.

The Specification Runtime never implements business code.

The Specification Runtime coordinates Skills and Frameworks to produce implementation-ready Specifications.

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

# Runtime Responsibilities

The Runtime is responsible for:

- Requirement Discovery
- Architecture Analysis
- Specification Coordination
- Contract Coordination
- Scenario Coordination
- Task Planning
- Consistency Review
- Development Readiness Assessment

---

# Runtime Context

Provided by Bootstrap Runtime:

- Environment Context (repository_root, workspaces_root, methodologies_root)

Provided by Prepare Runtime:

- Preparation Report
- Architecture Summary
- Impact Analysis

Provided by Runtime Base:

- Runtime Configuration
- Operating Rules
- Applied Standards
- Loaded Skills
- Loaded Frameworks

Resolved by Specification Runtime:

- Requirement
- Existing Specifications
- Existing Architecture
- Existing Contracts
- Existing Source Code
- Existing Tests

---

# Phase 1 — Requirement Discovery

Objective:

Understand the requested business change.

Invoke:

- requirement-analysis
- project-analysis

Collect:

- Business Goals
- Existing Behaviour
- Existing Specifications
- Existing Architecture
- Existing APIs
- Existing Database Design
- Existing Contracts
- Existing Tests

Identify:

- Unknown Information
- Risks
- Dependencies

If required information is missing:

Stop.

Generate clarification questions.

## Discovery Method

When requirements are ambiguous or incomplete, apply collaborative discovery:

1. **One question at a time**: Ask a single clarifying question, provide a recommended answer, wait for feedback before asking the next.
2. **Explore context first**: Check existing specs, contracts, and recent changes before asking.
3. **Multi-approach proposal**: When multiple design options exist, propose 2-3 approaches with trade-offs and a recommendation.
4. **Gate**: Do NOT proceed to Phase 2 until requirements are unambiguous.

Present every question and choice to the user in the system language (config/menu.yaml → locale).

---

# Phase 2 — Architecture Analysis

Objective:

Determine implementation impact.

Reuse first (from Prepare Runtime):

- Architecture Summary
- Impact Report

Invoke only if gaps remain:

- architecture-analysis

Analyze (incremental, gaps only):

- Services
- Modules
- APIs
- Database
- MQ
- RPC
- Scheduled Jobs
- External Systems

Generate:

- Impact Analysis Report

Do not design implementation.

---

# Phase 2.5 — Design Decision Pressure Test (Optional)

Objective:

Stress-test proposed design decisions before writing the Design artifact.

When the user wants to pressure-test a design or plan, or asks to "grill" /
"stress-test" the approach, invoke the `grilling` skill: walk the decision
tree one branch at a time, one question at a time, with a recommended answer,
and do not proceed until the user confirms a shared understanding.

Look up facts in the environment; only decisions are put to the user.

This step is optional and does not change the Specification contract.

---

# Phase 3 — Specification

Objective:

Generate implementation-ready specifications.

Invoke configured Methodology Provider (from config/providers.yaml → methodology.defaultProvider; provider assets at {methodologies_root}/providers/{provider}/).

Generate:

- Proposal
- Design
- Specification

The Framework determines the generated artifact format.

Do not generate implementation code.

---

# Phase 4 — Contracts

Objective:

Generate interaction contracts.

Invoke:

- contract-generation

Generate:

- API Contracts
- Data Models
- Error Definitions
- Interaction Rules
- Version Information

Contracts must remain consistent with Specifications.

If conflicts exist:

Stop immediately.

Generate Conflict Report.

---

# Phase 5 — Business Scenarios

Objective:

Describe executable business scenarios.

Invoke:

- scenario-generation

Generate:

- Business Scenarios
- Success Paths
- Failure Paths
- Rollback Paths

Scenarios must not introduce behaviour outside the Specification.

---

# Phase 6 — Task Planning

Objective:

Generate executable development tasks.

Invoke:

- planning
- task-planning

Generate:

- Global Plan
- Task Cards

Each Task must:

- Have one responsibility
- Be independently implementable
- Be independently testable
- Be independently verifiable

Generation uses the template from:
methodologies/providers/openspec-cn/templates/tasks-template.md

### 6.X — Code Quality Check Derivation

When each Task Card is generated, supplement code quality checks based on context:

Baseline (General / Security / Language):
  Do not expand item by item; emit a single baseline reference line →
  governance/standards/common/task-quality-checklist.md

From repositories/{service_id}.yaml → technology:
  protocol → protocol condition checks (MQ/RPC)

From Task content:
  REST API → REST caller validation + parameter validation
  touches DB/RPC/HTTP/MQ → performance check items
  new feature → new feature check items
  modification → modify existing code check items
  deletion → deletion check items
  touches MQ → consumer idempotency + producer message body
  touches RPC → Facade version + interface signature

Generation rules:
  baseline checks → one reference line per card; rule bodies maintained only in the standards file (Single Source of Truth)
  conditional checks → expand item by item only when the condition matches
  non-applicable items → omit directly; do not stuff them into the card

### 6.Y — Task Granularity Quality Rules

Every Task Card must satisfy:

- **Single responsibility**: One task = one independently testable deliverable
- **Bite-sized**: Each step within a task takes 2-5 minutes to execute
- **Exact paths**: Every file reference includes the full repository-relative path
- **Interface contracts**: Each task declares what it Consumes (from earlier tasks) and Produces (for later tasks) with exact signatures
- **No placeholders**: No TBD, TODO, "add error handling", "similar to Task N", or code-free descriptions of what to write

Self-review checklist after task generation:

1. **Spec coverage**: Can each spec requirement be traced to a task?
2. **Placeholder scan**: Any TBD / TODO / vague descriptions?
3. **Type consistency**: Do signatures in later tasks match definitions in earlier tasks?

---

# Phase 7 — Consistency Review

Objective:

Verify internal consistency.

Invoke:

- consistency-review

Verify:

Requirement

↓

Proposal

↓

Design

↓

Specification

↓

Contracts

↓

Scenarios

↓

Tasks

If any inconsistency exists:

Stop.

Generate Consistency Report.

---

# Phase 8 — Development Readiness

Objective:

Determine whether implementation can begin.

Verify:

✓ Requirements complete

✓ Architecture analyzed

✓ Specification completed

✓ Contracts completed

✓ Scenarios completed

✓ Tasks completed

✓ Global Plan completed

If every item passes:

Status = Ready

Otherwise:

Status = Blocked

---

# Outputs

The Runtime produces Specification Artifacts.

Typical artifacts may include:

- Proposal
- Design
- Specification
- Contracts
- Scenarios
- Global Plan
- Task Cards

The exact artifact structure is determined by the active Specification Framework.

---

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

# Completion

Return:

- Requirement Summary
- Architecture Impact
- Generated Artifacts
- Consistency Report
- Development Readiness

If Development Readiness is Ready:

Recommended Next Runtime:

Dev Setup Runtime

Then:

Development Runtime

Otherwise:

Wait for clarification. Present the clarification questions in the system language (config/menu.yaml → locale).