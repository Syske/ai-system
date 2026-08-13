# Workflows

Entry contracts for AI System execution.

Each workflow selects a runtime, declares preconditions, inputs, context, outputs, and explicit exit criteria.

Execution lifecycle (phases, checkpoints, recovery, persistence) is owned by the Runtime layer:

- ai-system/templates/runtime/

---

## Workflow Selection

| Scenario | Workflow |
|---|---|
| Initialize environment | bootstrap.md |
| Prepare context for a new change | prepare.md |
| Create specification artifacts | spec.md |
| Bind project and prepare workspace | dev-setup.md |
| Implement one task | develop.md |
| Review engineering quality | review.md |
| Verify against specification and contract | verify.md |
| Prepare release readiness | release.md |
| Diagnose and fix a defect | bugfix.md |
| Generate a HotFix test document (转测文档) | hotfix-test-doc.md |
| Analyze AI System health | analysis.md |
| Manage knowledge assets | knowledge.md |
| Review arbitrary code and produce a review result | code-review.md |
| Analyze impact, risks, and modification plan for a code target | change-impact.md |
| Discuss an optimization and produce a solution document | proposal.md |
| Requirement change on an in-flight change | prepare.md → spec.md (scoped re-entry) |

---

## Entry & Main Chain

Cold start (once per environment, AI-triggered per ADR-0009):

```text
bootstrap     # AI triggers on first use / environment loss; state in
              # workspaces/.aic-state.yaml → bootstrap.status; not re-run
              # per session (cli/main.py resolves env automatically)
```

Change lifecycle main chain:

```text
prepare → spec → dev-setup → develop → review → verify → release
```

Conditional transitions:

- review: Changes Required → develop
- verify: FAIL → develop
- release: READY → deployment (outside this workflow set)
- develop: L3 requirement change → suspend task → prepare (scoped) → spec (update change set) → resume develop

Independent entry:

- bugfix → review → verify
- hotfix-test-doc (from bugfix hotfix mode; standalone entry also available)

Standalone:

- code-review
- change-impact
- proposal

AI-internal (not user menu entries):

- analysis  — runs as an internal stage of the maintenance cycle
- knowledge — lifecycle managed by AI inside maintenance (OPERATIONS 1.7)

---

## Terminology

Identity fields always use the ID suffix.

| Field | Meaning |
|---|---|
| Workspace ID | Workspace directory name under workspaces/ |
| Project ID | Logical project identifier; names workspaces/{project_id}/ and groups its services (each service maps to projects/{service_id}) |
| Task ID | Task Card identifier (e.g. T-013) under the active change set |
| Change ID | Change set identifier: directory name under workspaces/{project_id}/openspec/changes/ (e.g. wecom-live-integration); a kebab-case name chosen at propose time (user-given or AI-derived), registered by openspec-cn new change; aggregates proposal, design, specs, contracts and task cards |
| Issue ID | External defect / issue tracker identifier |
| Release Version | Version string for a release readiness run |
| Specification Reference | Identity of a specification artifact (location, not content) |
| Environment | Environment configuration name (default: local) |

Execution modifiers:

| Field | Values | Meaning |
|---|---|---|
| Mode | (absent) | Normal first-pass run |
| Mode | re-entry | L3 requirement change on an in-flight change set; follow the scoped re-entry path (OPERATIONS.md 1.5): impact assessment → update change set in place → consistency check → resume develop |
| Mode | weekly / monthly / quarterly / on-demand | Maintenance modes for the maintain command (OPERATIONS.md 1.8) |

---

## Workflow Template

Every workflow file must contain these sections, in this order:

1. Purpose — one responsibility, one sentence
2. Runtime — runtime template path
3. Preconditions — what must exist before start
4. Inputs — Required / Optional
5. Context — minimal load set; loading order Task → Spec → Contract → Standards → Repository
6. Outputs — generated artifacts
7. Exit Criteria — Success / Stop conditions
8. Next — downstream workflow or None

Optional sections (inserted after Purpose when needed, do not reorder required sections):

- When to Use — distinguishes this workflow from related skills (e.g. review vs review-changes)

Rules:

- Workflows never contain implementation logic.
- Lifecycle detail (checkpoints, recovery, persistence) belongs to the Runtime layer.
- Context sections declare what to load; never load the entire repository.
- New workflows must follow this template and register in this index.
