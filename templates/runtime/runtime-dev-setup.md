# Runtime: Dev Setup

Extends:

- runtime-base.md

---

# Purpose

Resolve project context and prepare the development environment.

The Dev Setup Runtime resolves project metadata, services, branches, standards, and knowledge,
then binds project services to local repositories and builds the full workspace execution context.

The Dev Setup Runtime does not define specifications, execute tasks, dispatch runtimes, or implement business logic.

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

The Dev Setup Runtime is responsible for:

- Resolve Project Metadata
- Resolve Repository Information (from {workspace_root}/repositories/{service_id}.yaml)
- Resolve Services List
- Validate Branches
- Resolve Project Configuration
- Resolve Project Standards
- Resolve Project Knowledge
- Build Project Context
- Bind Project Context to Local Repositories
- Resolve Working Branch
- Resolve Specification Reference
- Build Workspace Context
- Persist Workspace State

---

# Runtime Context

## Provided by Runtime Base

- Runtime Configuration
- Operating Rules
- Loaded Skills
- Loaded Frameworks

## Provided by Bootstrap Runtime

- Environment Context (workspace_root, repository_root, workspaces_root, methodologies_root)
- Workspace Metadata (workspace ID, workspace path)

## Provided by Spec Runtime

- Specification Reference

## Resolved by Dev Setup Runtime

- Project Metadata
- Services List
- Repository Information (per service from {workspace_root}/repositories/{service_id}.yaml)
- Technology (per service from {workspace_root}/repositories/{service_id}.yaml)
- Branches (confirmed)
- Project Standards
- Project Knowledge
- Project Context
- Repository Workspace (local paths)
- Working Branch
- Git Status
- Workspace Context
- Workspace State

---

# Phase 1 — Resolve Project

Locate the project from workspaces/{project_id}/.

From Environment Context:

- repository_root

From project-context.yaml:

- Project ID
- Project Name
- Services list
- Branches (if any)

For each service_id in project.services:

Load {workspace_root}/repositories/{service_id}.yaml to resolve:

- Git URL
- Default branch
- Technology (language, framework, build, test)
- Local path: {repository_root}/{service_id}

Branch assignment:

```
if service_id in project.branches:
  branch = project.branches[service_id]
else:
  add to missing_branches with default_branch from repositories
```

If missing_branches is non-empty:

STOP.

Show all missing services with their default branches in a single prompt.

User confirms or specifies branch for each.

Update project-context.yaml branches section.

If the project cannot be resolved:

STOP.

Report missing project information.

---

# Phase 2 — Load Project Configuration

Load project-level configuration.

Sources:

- workspaces/{project_id}/runtime/contexts/project-context.yaml
- {workspace_root}/repositories/{service_id}.yaml (technology per service)

Do not duplicate technology information in project context.

Technology is read from repositories at runtime.

---

# Phase 3 — Resolve Project Standards

Load project applicable standards.

Invoke:

- standards-loader

Resolve:

- Language Standards
- Framework Standards
- Team Standards
- Documentation Standards
- Testing Standards

Generate:

- Applied Standards

---

# Phase 4 — Resolve Project Knowledge

Load reusable project knowledge.

Sources:

- Architecture Decisions
- Technical Documentation
- Historical Specifications
- Coding Guidelines

Generate:

- Project Knowledge Context

---

# Phase 5 — Build Project Context

Generate:

Project Context:

```yaml
project:
  id:
  name:

services:
  - {service_id}  (referenced from {workspace_root}/repositories/{service_id}.yaml)

branches:
  {service_id}: {branch}

standards:
  applied:

knowledge:
  available:
```

---

# Phase 6 — Bind Project

Load Project Context (built in Phase 5).

Verify:

- Project exists
- Repository available
- Project Context valid

Resolve:

- Project Reference
- Repository Information

---

# Phase 7 — Resolve Working Environment

From Environment Context:

- repository_root

From Project Context:

- services list
- branches

For each service_id:

```
local_path = {repository_root}/{service_id}
```

Verify:

- Directory exists → available
- Directory missing → unavailable

For available services:

- git branch --show-current
- Verify branch matches project-context branches
- Validate branch naming against conventions
- git status

## Branch Naming Convention

Verify each active branch name satisfies:

- **Type prefix**: One of `feat/`, `fix/`, `bugfix/`, `hotfix/`, `release/`, `refactor/`, `perf/`, `docs/`, `test/`, `chore/`, `ci/`, `revert/`
- **Lowercase with hyphens**: All lowercase, words separated by `-` (no underscores or CamelCase)
- **Descriptive**: Can infer purpose from name alone

Non-conforming branches are flagged with a warning.
The warning does NOT block setup but is reported for the user to decide.

Generate:

- Workspace Environment Context (available / unavailable service list)

---

# Phase 8 — Resolve Specification Reference

Bind:

- Specification ID
- Specification Location

Do not analyze specification content.

Specification processing belongs to Specification Runtime.

---

# Phase 9 — Build Workspace Context

Generate:

```yaml
workspace:
  id:
  status:

project:
  id:
  name:

environment:
  repository_root:

repository:
  available:
    - service:
      path: "{repository_root}/{service_id}"
      branch:
      git_status:
  unavailable:
    - service:

specification:
  reference:

runtime:
  status:
```

Paths use template references ({repository_root}/{service_id}).
Resolved at runtime from Environment Context.

---

# Phase 10 — Persist

Persist:

- Project Context
- Applied Standards
- Project Knowledge Context
- Workspace Context
- Workspace State

Location:

```
workspaces/{workspace-id}/
workspaces/{project_id}/contexts/project-context.yaml
```

---

# Outputs

Generate:

- Project Context
- Applied Standards
- Project Knowledge Context
- Workspace Context
- Workspace State

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

## Project Context

Contains:

- Project Information
- Services List
- Branches (all confirmed)
- Applied Standards
- Project Knowledge

Technology information is resolved from {workspace_root}/repositories/{service_id}.yaml at runtime.

## Applied Standards

- Code Standards
- Testing Standards
- Documentation Standards

## Project Knowledge

- Available Knowledge Sources

## Workspace Context

Contains:

- Workspace Information
- Project Reference
- Environment Context
- Repository Environment (available / unavailable, paths as template references)
- Branch Information
- Specification Reference

The Project Context and Workspace Context can be consumed by:

- Development Runtime
- Review Runtime
- Verification Runtime
- Release Runtime
