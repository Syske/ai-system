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

---

## 2026-08-01 — Routing & Frameworks Archival

**Reason:** `routing/` and `frameworks/` had no runtime consumer. The CLI wizard derives workflow recommendations by parsing each workflow's `## Next` section (`cli/services/wizard.py`), not from a route table; `routing/ai-routing.yaml` duplicated `config/workflow-registry.yaml`. `frameworks/` contained two 0-byte placeholder subdirs (serena/context7) and a facade contract that belongs in standards.

### Value Preserved

| Content | Destination |
|---|---|
| `frameworks/rpc/facade-standard.md` (BaseRequest/BaseResult contract) | Merged into `governance/standards/cool/rpc-conventions.md` §6 |
| `routing/ai-routing.yaml` execution rules | Rewritten into `governance/policies/routing-policy.md` (now describes wizard-driven routing) |

### Moved Files

| Original Path | Reason |
|---|---|
| `routing/ai-routing.yaml` | No consumer; duplicated workflow-registry |
| `frameworks/rpc/facade-standard.md` | Contract moved into standards |
| `frameworks/analysis/serena/{README.md,version.yaml}` | 0-byte placeholder |
| `frameworks/context/context7/{README.md,version.yaml}` | 0-byte placeholder |

### Consequential Updates

- `governance/contracts/AI_DEVELOPMENT_CONTRACT.md`: architecture diagram no longer lists `routing/` or `frameworks/`
- `tools/setup.py`: `SYSTEM_DIRS` dropped `routing`, `frameworks`
- `governance/policies/routing-policy.md`: no longer claims `routing/ai-routing.yaml` is authoritative; documents wizard-driven routing
