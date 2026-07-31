# Runtime: Workspace

Extends:

- runtime-base.md

---

# Purpose

Initialize and manage a Workspace Context.

The Workspace Runtime prepares the execution environment required by downstream workflows.

The Workspace Runtime does not define specifications, execute tasks, dispatch runtimes, or implement business logic.

---

# Responsibilities

The Workspace Runtime is responsible for:

- Resolve Workspace Metadata
- Bind Project Context
- Resolve Repository Workspace
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

- Environment Context (workspace_root, repository_root, specs_root, workspaces_root)

## Provided by Project Runtime

- Project Context

## Resolved by Workspace Runtime

- Workspace Metadata
- Repository Workspace (local paths)
- Working Branch
- Git Status
- Specification Reference
- Workspace Context
- Workspace State

---

# Phase 1 — Resolve Workspace

Locate workspace configuration.

Resolve:

- Workspace ID
- Workspace Status
- Workspace Metadata

If workspace does not exist:

Initialize workspace.

---

# Phase 2 — Bind Project

Load Project Context.

Verify:

- Project exists
- Repository available
- Project Context valid

Resolve:

- Project Reference
- Repository Information

---

# Phase 3 — Resolve Working Environment

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
- git status

Generate:

- Workspace Environment Context (available / unavailable service list)

---

# Phase 4 — Resolve Specification Reference

If specification exists:

Bind:

- Specification ID
- Specification Location

Do not analyze specification content.

Specification processing belongs to Specification Runtime.

---

# Phase 5 — Build Workspace Context

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

# Phase 6 — Persist Workspace State

Persist:

- Workspace Context
- Workspace Status

Location:
```
workspaces/{workspace-id}/
```

# Outputs

Generate:

- Workspace Context
- Workspace State

# Completion

Return:

## Workspace Context

Contains:

- Workspace Information
- Project Reference
- Environment Context
- Repository Environment (available / unavailable, paths as template references)
- Branch Information
- Specification Reference

The Workspace Context can be consumed by:

- Specification Runtime
- Development Runtime
- Review Runtime
- Verification Runtime
- Release Runtime
