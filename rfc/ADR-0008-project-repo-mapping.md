# ADR-0008: Project ↔ Repository Logical Mapping

Status: Accepted

Date: 2026-08-08

---

## Context

ai-system keeps OpenSpec artifacts and runtime state in
`workspaces/<project_id>/` and business repositories in `projects/`. When
maintaining a project, we want to locate its business code from the
workspace view. Candidate approaches:

1. **Symlink migration**: link each repository under `projects/` into
   `workspaces/<id>/projects/` (Windows junction)
2. **Logical mapping**: `workspaces/<id>/workspace.yaml` records
   service → repo path / branch / remote

## Decision

**Adopt logical mapping (Option 2) — no migration, no symlinks.**

1. `projects/` stays the authoritative source of business code (AGENTS.md
   contract unchanged).
2. `workspaces/<project_id>/workspace.yaml` `repository` section records the
   mapping:
   - `available`: [{service, path, branch, dev_branch, remote}] — repos
     wired into the current task
   - `unavailable`: [{service, note}] — repos involved but not wired in
     (records intent + reason)
3. ai-system reads the mapping (`providers.project_repos`); the wizard
   project list shows the mapped service names.

## Repository available / unavailable Classification

**available** = directly operable repository; must satisfy ALL:

1. Participates in the current task change (proposal/design mentions it)
2. Local path exists and is accessible (path points to a real directory)
3. Has an operable development branch (dev_branch checked out or creatable)
4. Team owns it (can modify/commit; not read-only reference)

**unavailable** = participates but is NOT directly operable; ANY of:

- Path unavailable (missing / located elsewhere, not wired in)
- Branch not wired in (dev_branch not checked out)
- Another team owns it / read-only reference
- Only interface knowledge needed; no code change

**Classification order** (for each newly involved service):

```
1. Does it participate in the current task change?
   ├─ no  → do NOT list in workspace.yaml (task-relevant services only)
   └─ yes → 2
2. Is a local path present and accessible?
   ├─ no  → unavailable (note: path missing)
   └─ yes → 3
3. Is there an operable dev branch?
   ├─ no  → unavailable (note: branch not wired in)
   └─ yes → 4
4. Does the team own it (modifiable/committable)?
   ├─ no  → unavailable (note: other team / read-only)
   └─ yes → available (full fields)
```

**Format requirements**:

- available entries MUST carry full fields: service / path / branch /
  dev_branch / remote
- unavailable entries MUST carry a `note` (reason); a reason-less entry is
  unclassifiable and must be completed

## workspace.yaml Initialization

**Executor: the AI (during the development flow)** — when a new workspace
project begins, the AI creates and maintains workspace.yaml in the
spec/develop phase.

```
Trigger: a new workspace project is detected (dev-setup / prepare phase
         finds workspaces/<project_id>/ without workspace.yaml)

Flow:
 1. Identify the project: read openspec/changes/*/proposal.md task
    description; extract the involved service list
 2. Classify each service available/unavailable (rules above)
 3. Generate workspace.yaml:
    - task section: current task id / service / status / spec_ref
    - repository section: filled per classification
    - specification section: references the main openspec path
 4. Validate: project_repos(wizard) reads it correctly; repo-less projects
    get an empty mapping
 5. Commit: workspace.yaml is project metadata, committed with the project
    (NOT into the ai-system repository)
```

**Update triggers** (as the task progresses):

- New service joins the change → classify and add to available/unavailable
- Service status changes (branch wired in / path restored) → move between
  available / unavailable
- Task completes → update task.status to completed

**Prohibited**:

- Never fabricate path/remote (must come from real repositories)
- Never list services not participating in the change (keep workspace.yaml
  scoped to task-relevant services)
- No dual-source lifecycle (use archived/ directory for lifecycle, not a
  status field in workspace.yaml)

## Rationale

- **Physical separation, logical association**: business repos stay in
  `projects/` (single authoritative source); workspace only records where
  they point
- **No symlink fragility**: Windows junctions need admin rights, break
  easily, and git/build tooling support them inconsistently
- **Reuses existing format**: pywechat-live-2608/workspace.yaml already had
  a repository mapping (2026-07); this decision makes ai-system consume it,
  not a new format
- **Backward compatible**: projects without a mapping show
  "(no repo mapped)", behavior unchanged

## Consequences

- Project selection shows mapped repos (user confirms the services behind a
  project)
- Future extensions: repo_path_for() repo location, branch hints, remote
  comparison
- `workspaces/<id>/contexts/` stays for runtime state (session-state.md
  etc.); the mapping lives in workspace.yaml (project-level metadata)
- available/unavailable have explicit classification rules; the AI maintains
  them automatically during the flow
- workspace.yaml initialization is executed by the AI at project creation
  (flow above)

## References

- `AGENTS.md` — projects/ and workspaces/ responsibility boundary
- `workspaces/pywechat-live-2608/workspace.yaml` — mapping format instance
- `cli/services/providers.py` — project_repos() reading implementation
