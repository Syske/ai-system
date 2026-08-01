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

---

## 2026-08-01 — Placeholder Template Archival

**Reason:** Four template files under `templates/` were placeholders (not usable templates) and had no active references. Skill/spec/test structure is governed by RFC-0002, the skill-policy guide, and the external methodologies provider; routing configuration is governed by `routing/ai-routing.yaml` + `governance/policies/routing-policy.md`.

### Moved Files

| Original Path | Reason |
|---|---|
| `templates/skill-template.md` | Placeholder; skill structure per RFC-0002 / skill-policy |
| `templates/spec-template.md` | Placeholder; spec generation by external methodology provider |
| `templates/test-template.md` | Placeholder; test structure per testing standard |
| `templates/routing-template.md` | Placeholder; routing per ai-routing.yaml + routing-policy |
