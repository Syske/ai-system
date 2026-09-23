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

- Environment Context (workspace_root, repository_root, workspaces_root)
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

## Repository Sourcing (P58 — authoritative)

- `{workspace_root}/repositories/{service_id}.yaml` is the **only** service metadata
  source (git URL / default branch / technology).
- `{repository_root}` (`projects/`) is a **real directory**; a missing service is
  cloned on demand:
  `python3 tools/repo-ensure.py ensure {service_id}` (see also Phase 7 verification).
- **Legacy pool is read-only reference, NOT a source**: a machine-specific copy of
  repositories (e.g. a mounted resource drive such as
  `/mnt/d/workspace/project-resources`) may still exist. Never resolve services or
  read code from it; it predates the P58 real-`projects/` model and is never synced.

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

Present the prompt in the system language (config/menu.yaml → locale).

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

Verify (P58 on-demand clone):

- Directory exists → available
- Directory missing → run `python3 tools/repo-ensure.py ensure {service_id}`
  (clones from `repositories/{service_id}.yaml` git URL); clone OK → available,
  clone failed (no metadata / no network / no auth) → unavailable with a `note`
  giving the reason. Do not silently fall back to "unavailable" when the
  service has metadata — attempt the clone first.

For available services:

- git branch --show-current
- Verify branch matches project-context branches
- Validate branch naming against the Task Card `branch` rule (parse via the
  main-chain branch parser; see below)
- git status

## Branch Naming & Immutability (main chain; preset-based, P63 2026-09-23)

- **The format is never written by hand.** The only legal formats are presets in
  `cli/services/branch_parser.py` (`plain` = default `cc{date}_{desc}_{service}`; `ipd` =
  `cc{date}_ipd_{desc}_{service}` for iteration-driven requirements). The scenario→preset
  map is `config/branch-formats.yaml` (single source; change a value there to re-point a
  scenario — no code, no regex). `bugfix` is provider-owned and is **not** a main-chain
  preset.
- **Assemble → confirm the NAME → freeze**: pick the preset for the scenario, assemble the
  concrete name with `render(preset, date, desc, service)` (output is guaranteed
  parseable), and present that **concrete name** — the user confirms the name, never a
  format string. A confirmed branch name must NOT change afterwards.
- Segments: `{date}` = 8 digits; `{desc}` / `{service}` = `[a-z0-9-]+` — **no underscore**
  (`render` rejects it: `qa_manage` → `qa-manage`).
- Each service gets an independent branch (`{service}` in the name); apart from
  the branch name everything else is identical.
- **Validate**: parse the active branch with the main-chain parser (`parse(name)`; or a
  provider resolved from `branch.parser` logic name →
  `extensions/<name>/scripts/branch_parser.py`, mirroring the bugfix contract): the name
  must match a preset and carry the expected date/desc/service. Unparseable — including
  any hand-written format string — → report and stop.
- **Create & backfill**: if `project-context.yaml branches` is empty for a
  service, assemble the name from the scenario→preset map and backfill it into
  `project-context.yaml branches`.
- **Freeze (immutable)**: after create/confirm, the branch name and
  `project-context.branches` are frozen. If a previously confirmed branch is
  detected as changed (rename / rebase away / config edit), **STOP** and report;
  the only allowed change is a newly added project with explicit authorization.

Non-conforming branches are flagged and block setup per the rule above
(no silent accept of arbitrary branch names).

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
- Repository Mapping (workspace.yaml, ADR-0008) — see below

Location:

```
workspaces/{workspace-id}/
workspaces/{project_id}/contexts/project-context.yaml
workspaces/{project_id}/workspace.yaml   (repository mapping, ADR-0008)
```

## Repository Mapping (workspace.yaml)

Generate or refresh `workspaces/{project_id}/workspace.yaml` (ADR-0008 logical
mapping) from the Project Context built in the phases above. It is the single
repo-mapping source the wizard and code-review / change-impact / release consume:

- `repository.available` — for every service with an operable worktree (Phase 7):
  - `service`: service id
  - `path`: Phase 6 repository path (authoritative master checkout)
  - `branch`: `master`
  - `dev_branch`: Phase 1 `branches[{service}]` (frozen branch name)
  - `remote`: git URL from `{workspace_root}/repositories/{service}.yaml`

> P58 path normalization: write `path` as the relative service id
> (e.g. `platform-api`) when the service lives in the repository root
> (resolved as `{repository_root}/{service_id}`), so mappings stay portable
> across machines instead of baking in absolute paths.
- `repository.unavailable` — services involved in the change but NOT operable
  (no worktree / read-only reference / path missing), each with a `note` giving
  the ADR-0008 classification reason (e.g. "branch not wired in")
- `task` — current task id / service / status / spec_ref / contract_ref from
  Project Context (multi-task projects: list the range / current phase honestly)
- `specification.reference` — main openspec reference

Refresh triggers (dev-setup rerun): keep available/unavailable in sync with the
current worktree set; drop stale entries from previous runs; never fabricate
path/remote (read from project-context repository section and
`repositories/{service}.yaml`) and never list services that do not participate
in the change (ADR-0008).

---

# Outputs

Generate:

- Project Context
- Applied Standards
- Project Knowledge Context
- Workspace Context
- Workspace State
- Repository Mapping (`workspaces/<project-id>/workspace.yaml`, ADR-0008 — wizard / code-review / change-impact / release consume)
- **Location**: → `workspaces/<project-id>/` (workspace context/state + repository mapping); applied standards per `loaders/standards-loader.md`

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
