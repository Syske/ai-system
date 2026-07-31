# Runtime: Project

Extends:

- runtime-base.md

---

# Purpose

Resolve and initialize a Project Context.

The Project Runtime prepares project-level information required by downstream workflows.

The Project Runtime does not manage workspace state, branch state, code changes, or business implementation.

---

# Responsibilities

The Project Runtime is responsible for:

- Resolve Project Metadata
- Resolve Repository Information (from {workspace_root}/repositories/{service_id}.yaml)
- Resolve Services List
- Validate Branches
- Resolve Project Configuration
- Resolve Project Standards
- Resolve Project Knowledge
- Build Project Context

---

# Runtime Context

## Provided by Runtime Base

- Operating Rules
- Runtime Configuration
- Loaded Skills
- Loaded Frameworks

## Provided by Bootstrap Runtime

- Environment Context (workspace_root, repository_root, specs_root, workspaces_root)

## Resolved by Project Runtime

- Project Metadata
- Services List
- Repository Information (per service from {workspace_root}/repositories/{service_id}.yaml)
- Technology (per service from {workspace_root}/repositories/{service_id}.yaml)
- Branches (confirmed)
- Project Standards
- Project Knowledge

---

# Phase 1 — Resolve Project

Locate the project from specs/{project_id}/.

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

- specs/{project_id}/project-context.yaml
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

# Outputs

Generate:

* Project Context
* Applied Standards
* Project Knowledge Context

---

# Completion

Return:

## Project Context

* Project Information
* Services List
* Branches (all confirmed)
* Applied Standards
* Project Knowledge

Technology information is resolved from {workspace_root}/repositories/{service_id}.yaml at runtime.

## Applied Standards

* Code Standards
* Testing Standards
* Documentation Standards

## Project Knowledge

* Available Knowledge Sources

---

# Used By

Project Context can be consumed by:

* Dev Setup Runtime
* Specification Runtime
* Development Runtime
* Review Runtime
* Verification Runtime
* Release Runtime

```

---