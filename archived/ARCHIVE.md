# Archive Record

## 2026-07-11 — Workflow Restructuring

**Reason:** Merged `workspace` and `project` workflows into a single `dev-setup` workflow.
Workspace init promoted to bootstrap; project resolution and environment setup unified.

### Moved Files

| Original Path | Reason |
|---|---|
| `config/workflows/workspace.yaml` | Replaced by `config/workflows/dev-setup.yaml` |
| `config/workflows/project.yaml` | Merged into `config/workflows/dev-setup.yaml` |
| `workflows/workspace.md` | Replaced by `workflows/dev-setup.md` |
| `workflows/project.md` | Merged into `workflows/dev-setup.md` |
| `templates/runtime/runtime-workspace.md` | Replaced by `templates/runtime/runtime-dev-setup.md` |
| `templates/runtime/runtime-project.md` | Merged into `templates/runtime/runtime-dev-setup.md` |

### New Chain

```
bootstrap → prepare → spec → dev-setup → develop → review → verify → release
```
