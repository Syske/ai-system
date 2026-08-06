# AI Runtime Engine Development Contract

Version: 1.1

This repository implements the AI Runtime Engine.

The Runtime Engine is responsible for orchestrating AI workflows (OpenCode, Claude Code, future agents) in a predictable, maintainable, and evolvable manner.

All future implementations MUST follow this contract.

---

# 1. Mission

The Runtime Engine is **an orchestrator**, not an AI assistant.

Its responsibilities are:

- parse user intent
- resolve workflow
- locate resources
- dispatch runtime
- execute skills
- collect results
- output execution status

Business knowledge belongs to Skills.

Workflow logic belongs to Workflows.

Runtime only orchestrates.

Never mix responsibilities.

---

# 2. Repository Architecture

The repository architecture has already been finalized.

Do NOT redesign it.

Do NOT introduce new top-level directories.

Exception: `.github/` (CI/CD pipeline config) is allowed as a top-level
directory — `governance/DIRECTORY-RESPONSIBILITY.md` explicitly excludes
CI/CD pipeline config from governance. It is tooling, not an architecture layer.

Do NOT move responsibilities across modules.

Current architecture:

ai-system/

├── cli/
│   CLI entrypoints (thin, Python)
│
├── workflows/
│   Workflow entry contracts (single semantic source)
│
├── templates/
│   ├── runtime/    Runtime execution templates
│   ├── prompts/    Prompt templates
│   └── *.md        Asset templates
│
├── loaders/
│   On-demand loading strategies (standards-loader)
│
├── skills/
│   Reusable AI capabilities
│
├── config/
│   Runtime configuration
│   ├── workflow-registry.yaml
│   ├── providers.yaml
│   ├── workflows/      Registry entries only (name / workflow / runtime); semantics live in workflows/*.md
│   └── environments/
│
├── governance/
│   Rules, contracts, policies, standards, memory
│
├── rfc/
│   Architecture RFCs
│
├── tools/
│   Helper utilities
│
├── reports/
│   Generated reports
│
├── metrics/
│   Runtime metrics
│
├── logs/
│   Runtime logs
│
└── archived/
    Retired assets (reference only, including the former ai-runtime/ platform adapter sketch)

Every implementation must respect these responsibilities.

Per-directory responsibilities, new-asset decision tree, and violation handling:
see `governance/DIRECTORY-RESPONSIBILITY.md`.

---

# 3. Architecture Principles

Always prefer:

Simple > Clever

Explicit > Implicit

Composable > Coupled

Readable > Abstract

Small Functions > Large Classes

Composition > Inheritance

Configuration > Hardcoding

Workflow > Script

Skill > Prompt

Never implement future architecture.

Only implement today's requirement.

---

# 4. Development Rules

Every task must:

- implement exactly one feature
- keep backward compatibility
- minimize code changes
- avoid unrelated refactoring
- avoid speculative abstractions
- avoid dead code
- avoid duplicated logic

If architecture improvements are discovered:

DO NOT implement immediately.

Instead:

Output a recommendation.

---

# 5. Workflow Responsibilities

Workflow is responsible for:

- loading context
- locating resources
- sequencing execution
- calling skills
- collecting outputs

Workflow must never contain business implementation.

Business implementation belongs to Skills.

---

# 6. Skill Responsibilities

A Skill is reusable knowledge.

A Skill may contain:

- workflow
- examples
- decision rules
- checklists
- anti-patterns
- templates

A Skill must never:

- know CLI details
- know runtime internals
- know routing implementation

Skills are independent modules.

Exception: a Skill MAY reference `governance/` rules and `tools/` checkers
**read-only** for compliance self-checks (e.g. a skill invoking
`repo-lint` or citing a standard). Such references are read-only
consumption, not content imports, and do not invert the dependency
direction.

---

# 7. Runtime Responsibilities

Runtime is responsible for:

- dispatching workflows
- executing skills
- passing context
- collecting execution results

Runtime does NOT own business logic.

Runtime does NOT generate prompts.

Runtime does NOT modify repository structure.

---

# 8. CLI Responsibilities

CLI is intentionally thin.

CLI only:

- parses arguments
- validates input
- invokes dispatcher

All execution belongs elsewhere.

---

# 9. Repository Governance

Never:

- redesign architecture
- rename existing modules
- create duplicate capabilities
- bypass workflows
- hardcode project paths
- embed project-specific knowledge
- violate governance policies

Always reuse existing components first.

---

# 10. Karpathy Guidelines

Every implementation must follow:

- Make the smallest correct change.
- Avoid unnecessary abstractions.
- Prefer straightforward code.
- Optimize for readability.
- Delete complexity instead of adding complexity.
- Keep functions focused.
- Make failures obvious.
- Prefer deterministic behavior.
- Avoid hidden side effects.

---

# 11. Current Development Scope

Implement ONLY the requested capability.

Do not automatically implement:

- review
- release
- deploy
- rollback
- plugin system
- event bus
- scheduler
- graph execution
- distributed runtime
- memory
- retry engine

Unless explicitly requested.

---

# 12. Deliverables

Every completed task must include:

## Modified Files

## New Files

## Execution Flow

## Design Decisions

## Validation Result

## Risks

## Future Recommendations

Only recommendations.

Do not implement future work.

---

# 13. Long-term Evolution

This Runtime Engine will evolve incrementally.

Future improvements must:

- preserve architecture
- preserve module boundaries
- preserve workflow contracts

Evolution is additive.

Never rewrite the repository.

Never replace stable modules.

When uncertain:

Choose the simpler solution.