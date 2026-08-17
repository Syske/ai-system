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

> Note: `governance/policies/routing-policy.md` was subsequently deleted in commit 54d36e5 (2026-08-01) as redundant — routing is wizard-driven, with no separate policy document.

---

## 2026-08-01 — Maintainers Archival

**Reason:** `maintainers/` held five 0-byte placeholder docs (capability-matrix, dependency-graph, duplication-report, health-check, weekly-report) plus a placeholder README; their outputs are actually produced in `reports/` (MAINTENANCE-{date}.md) and `metrics/` (maintain-{date}.json). `DIRECTORY-RESPONSIBILITY-GUIDE.md` described the retired `ai-runtime/` architecture and referenced the deleted `routing/` directory.

### Value Preserved

| Content | Destination |
|---|---|
| Directory responsibility table | `governance/DIRECTORY-RESPONSIBILITY.md` (rewritten for current architecture) |
| Golden rule | `governance/DIRECTORY-RESPONSIBILITY.md` |
| New-asset decision tree (updated) | `governance/DIRECTORY-RESPONSIBILITY.md` |
| Violation handling table (updated) | `governance/DIRECTORY-RESPONSIBILITY.md` |

### Moved Files

| Original Path | Reason |
|---|---|
| `maintainers/README.md` | Placeholder |
| `maintainers/capability-matrix.md` | Placeholder |
| `maintainers/dependency-graph.md` | Placeholder |
| `maintainers/duplication-report.md` | Placeholder |
| `maintainers/health-check.md` | Placeholder |
| `maintainers/weekly-report.md` | Placeholder |
| `maintainers/DIRECTORY-RESPONSIBILITY-GUIDE.md` | Outdated (retired ai-runtime); value absorbed into new guide |

### Consequential Updates

- `governance/DIRECTORY-RESPONSIBILITY.md`: new v3 guide (current architecture)
- `governance/contracts/AI_DEVELOPMENT_CONTRACT.md`: architecture diagram no longer lists `maintainers/`; references the new guide
- `tools/setup.py`: `SYSTEM_DIRS` dropped `maintainers`
- `config/ai-bootstrap.yaml`: dropped `../routing` layer (directory deleted)

---

## 2026-08-01 — refactor-safely Skill Archival

**Reason:** `refactor-safely` was deprecated (status: deprecated in frontmatter) and had no references from workflows, CLI commands, config, or menu.yaml. Superseded by the `review` workflow (Phase 2 Design Review) and the `review-changes` skill.

### Moved Files

| Original Path | Reason |
|---|---|
| `skills/refactor-safely/` | Deprecated + unreferenced; replacement documented in frontmatter |

### Consequential Updates

- `skills/README.md`: removed the "Experimental / Deprecated" section row


---

## 2026-08-17 — skill-optimizer + iterative-optimizer Archival (Value-Burden Check)

**Reason:** The internal "meta-optimizer" cluster (~11.7k lines: skill-optimizer ~10k +
iterative-optimizer 1.4k, ~25-27% of all skill code) showed no demonstrated value
evidence after the new Value-Burden Check: no `~/.agent-insight/skill-history/` snapshots,
no benchmark.json / diff.html / optimized artifacts, zero `OPTIMIZATION_LOG.md`, and no
record of any skill actually optimized end-to-end. Value evidence missing + significant
burden → archive candidate per governance/AI_OPERATING_RULES.md (Value-Burden Check).

`iterative-optimizer` archived together (A'): its entire optimization stage drives
skill-optimizer (default optimize prompt), so archiving only skill-optimizer would leave
a half-dead "shell with no engine".

See `reports/VALUE-BURDEN-DECISION-skill-optimizer-2026-08-17.md`.

### Moved Files

| Original Path | Reason |
|---|---|
| `skills/skill-optimizer/` | Overbuilt meta-optimizer, no value evidence |
| `skills/iterative-optimizer/` | Same chain, no independent value evidence |

### Consequential Updates

- `.github/workflows/ci.yml`: removed skill-optimizer unit + smoke test steps
- `skills/README.md`: removed both index rows
- CLI decoupled `optimize` mode: `cli/services/skill_launcher.py`, `cli/services/providers.py`,
  `cli/main.py` (mode choices + legacy `skill-optimize` command)
- Deleted dead code: `templates/prompts/skill-optimize.md`, `cli/services/skill_optimize.py`
- Tests updated: `cli/tests/test_services.py` (`test_providers_skill_modes`,
  `test_run_skill_optimize_falls_back`)
- `cli/commands/aic-skill.md` rewritten launch-only
- Stale refs cleaned: `governance/policies/security-policy.md`, `config/skill-groups.yaml`,
  `tools/extensions-init.py`, `tools/path-audit.py` allowlist, `cli/services/wizard/{fields,steps}.py`
- Removed from archived tree: `.env` (live key, never committed), `__pycache__/`
