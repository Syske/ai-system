# Workflow: Project

## Purpose

Initialize Project Context.

The Project Workflow prepares project-level context required by downstream workflows.

This workflow does not analyze source code, manage workspace state, or implement business changes.

---

# Inputs

Required:

- Project ID

Optional:

- Repository

---

# Step 1 — Validate Project

Verify:

- Environment Context is available (from Bootstrap)
- Project ID exists in specs/{project_id}/
- Project configuration exists
- All referenced repositories exist in {workspace_root}/repositories/{service_id}.yaml

If validation fails:

STOP.

Report missing project information.

---

# Step 2 — Start Runtime

Load:

- ai-system/templates/runtime/runtime-project.md

---

# Step 3 — Execute Runtime

The Project Runtime resolves:

- Project Metadata
- Services List (from project-context.yaml)
- Repository URLs and technology (from {workspace_root}/repositories/{service_id}.yaml)
- Project Standards
- Project Knowledge

Technology information is read from {workspace_root}/repositories/{service_id}.yaml.
Not resolved or duplicated here.

Generate:

- Project Context

---

# Step 4 — Confirm Branches

If project declares a branches section, use those branches.

For any service in project.services that does NOT have a branch declared in project.branches:

- Collect ALL missing services
- Show a single prompt with default_branch from {workspace_root}/repositories/{service_id}.yaml for each
- User confirms or specifies branch for each service

If project.branches is missing entirely (no branches declared at all):

- Collect ALL services
- Show a single prompt for all services with their default_branch
- User confirms or specifies branch for each service

After user confirmation:

Update project-context.yaml branches section.

---

# Step 5 — Persist Context

Store:

- Project Context

Location:

workspaces/{project_id}/contexts/project-context.yaml


---

# Step 6 — Finish

Return:

## Project Context

Contains:

- Project Information
- Services List
- Branches (all confirmed)
- Applied Standards
- Project Knowledge

Technology information is read from {workspace_root}/repositories/{service_id}.yaml at runtime.
Not duplicated in project context.

The Project Context can be consumed by:

- Dev Setup Workflow
- Specification Workflow
- Development Workflow
- Review Workflow
- Verification Workflow
- Release Workflow
