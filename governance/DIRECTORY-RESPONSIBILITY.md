# Directory Responsibility Guide

> Maintainer: Architecture Maintainer
> Version: v3 (2026-08-01)
> Principle: single responsibility per directory; authoritative architecture diagram lives in `governance/contracts/AI_DEVELOPMENT_CONTRACT.md`.

---

## AI System Directory Responsibilities

| Directory | Responsibility | Contains | Does NOT contain |
|-----------|---------------|----------|------------------|
| `cli/` | Command-line entrypoints (thin, Python) | argument parsing, wizard, prompt builder | Provider-specific CLI |
| `workflows/` | **Workflow entry contracts (single semantic source)** | `workflows/<name>.md` + README | Workflow execution engine |
| `templates/` | Template library | runtime/, prompts/ | Runtime cache |
| `loaders/` | On-demand loading strategies | standards-loader | — |
| `skills/` | **All Skills (authoritative source)** | SKILL.md, scripts, references | Runtime adapters |
| `config/` | System configuration | workflow-registry.yaml, providers.yaml, menu.yaml, workflows/, environments/, i18n/ | Runtime-specific config |
| `governance/` | Rules, contracts, policies, standards, memory | AI_OPERATING_RULES, SOURCE_OF_TRUTH, standards/, policies/, memory/ | CI/CD pipeline config |
| `rfc/` | Architecture decisions | RFCs, ADRs | Code implementation |
| `tools/` | Helper utilities | check.py, repo-lint.py, path-audit.py, setup.py | — |
| `reports/` | Generated reports | analysis, maintenance, migration reports | Temporary logs |
| `metrics/` | Health metrics snapshots | maintain-{date}.json | Metric data storage |
| `logs/` | Operation logs | error logs, maintenance logs | Runtime logs |
| `archived/` | Retired assets (reference only) | former ai-runtime/, old templates, old routing | Active assets |

---

## Decision Rules

A new asset belongs to `ai-system/` when it is:

- Knowledge (not execution)
- Shared across all providers
- A long-lived asset

A new asset does NOT belong to `ai-system/` when it is:

- Provider-specific execution code
- Runtime / SDK / cache
- Temporary log or cache
- Business project code (belongs to `projects/`)

---

## Golden Rule

> 一个问题出现在哪个目录，决定了它由谁解决、如何解决、以及解决周期的长度。
> Which directory a problem appears in determines who solves it, how, and how long it takes.

---

## New Asset Decision Tree

```
New asset
    │
    ▼
Is it a Skill / Workflow / Governance / Template / RFC / standard?
    │                              │
    ├─ yes ────────────────────────┤
    │                              │
    ▼                              ▼
ai-system/                         Is it business project code?
                                  │                  │
                                  ├─ yes ────────────┤
                                  │                  │
                                  ▼                  ▼
                               projects/             Is it runtime/generated
                                                     (logs, metrics, reports, cache)?
                                                          │            │
                                                          ├─ yes ──────┤
                                                          │            │
                                                          ▼            ▼
                                                     Generated report   its target dir
                                                          │              belongs to the
                                              ┌───────────┴──────────┐   consuming
                                              │                       │   project
                                              ▼                       ▼
                                    about ai-system itself   about a specific business
                                    (workflow/command/       project (deploy check,
                                    standard improvement)    risk, migration)
                                              │                       │
                                              ▼                       ▼
                                       ai-system/reports/    workspaces/{project_id}/
                                                              outputs/<workflow>/
                                                              (release/, review/, ...)
```

Rules:
- Knowledge, shared, long-lived assets → `ai-system/`.
- Business project code → `projects/` (references ai-system, never duplicates).
- Generated outputs → `logs/`, `metrics/`, `reports/`; never commit temp/cache.
- Generated reports → subject decides location: ai-system's own improvement → `ai-system/reports/`;
  a specific business project's deploy/risk/migration matter → `workspaces/{project_id}/outputs/<workflow>/`
  (e.g. `outputs/release/`, `outputs/review/`).

---

## Violation Handling

| Violation | Example | Handling |
|-----------|---------|----------|
| Skill outside `skills/` | `projects/foo/.claude/skills/` | Move to `ai-system/skills/`, use references |
| Workflow outside `workflows/` | `projects/foo/workflows/` | Move to `ai-system/workflows/` |
| Governance outside `governance/` | `config/governance/` | Move to `ai-system/governance/` |
| Source asset in generated dir | `reports/foo-skill/` | Move to `ai-system/skills/` |
| Generated output in source dir | `ai-system/skills/foo/report.md` | Move to `reports/` |
| Business project report in ai-system | project deploy/risk report placed in `ai-system/reports/` | Move to `workspaces/{project_id}/outputs/<workflow>/` |

---

## Related

- Architecture diagram & principles: `governance/contracts/AI_DEVELOPMENT_CONTRACT.md`
- Workflow contracts: `workflows/README.md`
- Naming rules: `governance/repo-lint.md`

*Guide maintained by Architecture Maintainer*
