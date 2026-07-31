# Workflow: Workspace

## Purpose

Create and initialize a Workspace execution context.

The Workspace Workflow prepares the working environment required by downstream workflows.

The Workspace Workflow does not define specifications, implement tasks, or coordinate business changes.

---

# Inputs

Required:

- Workspace ID
- Project ID

Optional:

- Specification
- Branch

---

# Step 1 — Validate Workspace

Verify:

- Environment Context is available (from Bootstrap)
- Project Context is available
- Workspace ID is valid
- At least one service repository is available locally

If validation fails:

STOP.

Report missing workspace information.

---

# Step 2 — Start Runtime

Load:

- ai-system/templates/runtime/runtime-workspace.md

---

# Step 3 — Execute Runtime

The Workspace Runtime resolves:

- Workspace Metadata
- Project Binding (from Project Context)
- Repository Workspace (paths derived as {repository_root}/{service_id})
- Working Branch (from Project Context branches)
- Git State
- Current Specification Reference
- Execution Context

Repository paths are derived from Environment Context repository_root.
Do not store absolute paths in workspace context.
Use template references: {repository_root}/{service_id}

Generate:

- Workspace Context

---

# Step 4 — Persist Workspace Context

Store:

- Workspace State
- Workspace Context

Location:

workspaces/{workspace-id}/

Path references use template format:
  path: "{repository_root}/{service_id}"

Resolved at runtime from Environment Context.

---

# Step 5 — Finish

Return:

## Workspace Context

Contains:

- Workspace Information
- Project Reference
- Repository Path
- Branch
- Specification Reference
- Execution State


The Workspace Context can be consumed by:

- Specification Workflow
- Development Workflow
- Review Workflow
- Verification Workflow
- Release Workflow