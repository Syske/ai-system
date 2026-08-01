# RFC-0001: Repository Architecture

| Field | Value |
|---|---|
| Status | **Approved** |
| Type | Architecture |
| Author | Repository Governance |
| Created | 2026-07-02 |
| Supersedes | None |

---

## Abstract

This RFC defines the canonical architecture of this AI Engineering Repository.
It establishes the vocabulary, layer structure, relationship rules, and naming
conventions that every component in the repository must follow.

Adherence to this RFC is mandatory for all current and future repository content.

---

## 1. Vocabulary

The repository defines six component types:

### 1.1 Skill

A **Skill** is an executable capability that an AI agent loads and follows.
It defines a deterministic workflow for completing a specific task.

**Characteristics:**
- Has a defined purpose and trigger conditions
- Has a single responsibility
- Contains a workflow with observable stages
- Contains decision rules and stopping conditions
- May delegate to other Skills
- Does NOT contain extensive engineering knowledge
- Does NOT orchestrate other Skills (that is a Workflow's job)

**Location:** `ai-system/skills/<name>/`

### 1.2 Workflow

A **Workflow** is an orchestration layer that coordinates multiple Skills
to complete a higher-level process.

**Characteristics:**
- Defines execution order of Skills
- Defines handoff conditions between Skills
- Defines stopping conditions for the process
- Does NOT implement capabilities — only references Skills
- Does NOT contain engineering knowledge
- Does NOT duplicate any Skill's internal workflow

**Location:** `ai-system/workflows/<name>/`

### 1.3 Playbook

A **Playbook** is a reusable reference document containing engineering best
practices, diagnostic patterns, and decision guidance.

**Characteristics:**
- Contains language-level or framework-level knowledge
- Is project-agnostic (reusable across repositories)
- Does NOT contain execution instructions
- Does NOT contain project-specific information
- Is referenced by Skills, never invoked directly

**Location:** `ai-system/governance/standards/`, `ai-system/governance/memory/`, `ai-system/frameworks/`

### 1.4 Knowledge

A **Knowledge** document is a project-specific reference containing
architecture descriptions, domain terminology, and conventions.

**Characteristics:**
- Is project-specific (not reusable across repositories)
- Is descriptive, not procedural
- Answers "what" and "why", not "how"
- Is referenced by Skills and Workflows for context

**Location:** `ai-system/governance/memory/`

### 1.5 Template

A **Template** is a reusable document structure with placeholders for
generating reports, summaries, and proposals.

**Characteristics:**
- Defines the structure, not the content
- Has clearly marked placeholders (`<placeholder>`)
- Is referenced by Skills when generating output
- Is fill-in-the-blank, not narrative

**Location:** `ai-system/templates/<name>.md`

### 1.6 Checklist

A **Checklist** is a reusable, mechanically executable list of verification
items for quality gates.

**Characteristics:**
- Contains only verifiable items (Yes/No/Pass/Fail)
- Has a single theme (validation, completion, retry, release)
- Is referenced by Skills, not duplicated in them
- Items are actionable, not interpretive

**Location:** per-Skill `checklists.md`

---

## 2. Layer Architecture

```
                    ┌──────────────────────────────────────────┐
                    │          Layer 4: Workflows             │
                    │  (orchestration, no implementation)     │
                    │                                         │
                    │  develop  │  bugfix  │  review          │
                    │  release  │  openspec                   │
                    └────────────────┬─────────────────────────┘
                                     │ invokes
                    ┌────────────────┴─────────────────────────┐
                    │          Layer 3: Orchestration Skills   │
                    │  (delegates to Layer 1-2)               │
                    │                                         │
                    │  bugfix  │  implement  │  repository-   │
                    │           │              governor       │
                    └────────────────┬─────────────────────────┘
                                     │ delegates to
             ┌───────────────────────┼───────────────────────┐
             │                       │                       │
             ▼                       ▼                       ▼
  ┌────────────────────┐  ┌────────────────────┐  ┌────────────────────┐
  │ Layer 2: Test      │  │ Layer 2: OpenSpec  │  │ Layer 1: Foundation│
  │ Skills             │  │ Skills             │  │ Skills             │
  │                    │  │                    │  │                    │
  │ mock-test          │  │ openspec-explore   │  │ java-maven         │
  │                    │  │ openspec-propose   │  │ codegraph-helper   │
  │                    │  │ spec-updater       │  │ karpathy-guidelines│
  │                    │  │ contract-maintainer│  │                    │
  │                    │  │ task-splitter      │  │                    │
  └────────────────────┘  └────────────────────┘  └────────────────────┘
```

### Layer Rules

| Rule | Violation example |
|---|---|
| Layer N may only invoke Layer ≤ N | A Workflow (L4) must not invoke a Foundation Skill (L1) directly — go through Orchestration |
| Layer 1 (Foundation) must not depend on any other layer | java-maven must not reference bugfix |
| Layer 2 (Test/OpenSpec) must only depend on Layer 1 | mock-test must not depend on implement |
| Layer 3 (Orchestration) may depend on Layers 1-2 | bugfix may depend on mock-test and java-maven |
| Layer 4 (Workflow) may only reference Skill triggers | A Workflow may not implement any logic |

---

## 3. Component Relationship Rules

| Component | May reference | Must not reference |
|---|---|---|
| Skill | Playbooks, Knowledge, Templates, Checklists, other Skills (via delegation) | Workflows, itself |
| Workflow | Skills (by activation trigger) | Playbooks, Knowledge (directly); must not implement logic |
| Playbook | Nothing (standalone knowledge) | Skills, Workflows, project-specific paths |
| Knowledge | Nothing (standalone project context) | Execution instructions |
| Template | Nothing (standalone structure) | Specific content, project names |
| Checklist | Nothing (standalone items) | Skill-specific items |

---

## 4. Naming Conventions

| Component | Pattern | Examples |
|---|---|---|
| Skill directory | `kebab-case`, single or hyphenated word | `bugfix`, `java-maven`, `mock-test` |
| Skill entrypoint | `skill.md` | Must be lowercase |
| Workflow directory | `kebab-case` | `develop`, `bugfix`, `openspec` |
| Playbook file | `<topic>.md` | `maven.md`, `mockito.md` |
| Knowledge file | `<topic>.md` | `architecture.md`, `domain-terms.md` |
| Template file | `<purpose>-report.md` | `implementation-report.md` |
| Checklist file | `<theme>.md` | `validation.md`, `completion.md` |
| RFC file | `RFC-NNNN-<kebab-title>.md` | `RFC-0001-repository-architecture.md` |
| ADR file | `NNNN-<kebab-title>.md` | `0001-openspec-integration.md` |

---

## 5. Prohibited Patterns

| Pattern | Why |
|---|---|
| Skill with a single file exceeding 1000 lines | Violates single responsibility; becomes unmaintainable |
| Skill containing Maven commands directly | Must delegate to java-maven |
| Skill containing ReflectionTestUtils patterns | Must reference playbooks/reflection-test-utils.md |
| Skill duplicating a checklist | Checklist must be shared via the Skill's own checklists.md |
| Skill embedding a report template | Template must live in `ai-system/templates/` |
| Workflow implementing business logic | Workflow orchestrates, does not implement |
| Playbook containing project paths | Playbook must be reusable |
| Knowledge containing execution instructions | Knowledge describes, does not instruct |
| Circular dependency between Skills | Dependency graph must remain acyclic |

---

## 6. Governance Compliance

All components in this repository are subject to automated linting
via `scripts/repo-lint.py` (see `RFC-0002` for Skill-level rules,
`RFC-0003` for Workflow-level rules).

Non-compliance must be resolved before the component is accepted.
