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

---

## 2026-08-23 — 死模板归档：workflow-trigger.md

**Reason:** `templates/prompts/workflow-trigger.md` 无任何代码消费（prompt_builder 仅读
workflow.md/command.md；chain/skill launcher 仅读 skill-launch.md），其 `{{workflow_path}}`
占位符无填充方。08-20 P1 修复批次曾随 main.py 一并编辑该文件，但实际修复在 main.py
（context 透传）；模板为死代码维护，归档保留历史。

### Moved Files

| Original Path | Reason |
|---|---|
| `templates/prompts/workflow-trigger.md` | 死模板（零代码引用），归档保留 |

---

## 2026-09-23 — skill-sync Archival (Value-Burden Check)

**Reason:** `skills/skill-sync/`（576 行 / 4 文件：push.js 248、sync-policy.js 136、pull.js 131、
SKILL.md 61）经 Value-Burden Check 复核后无价值实证：唯一调用方 `skill-optimizer` /
`iterative-optimizer` 已于 2026-08-17 归档；`logs/` `reports/` `outputs/` 中**零条真实 push/pull
运行记录**；本机三个凭据路径（`~/.agent-insight/.env`、`~/.witty/.env`、`~/.skill-insight/.env`）
**均不存在**；`git log -- skills/skill-sync` 的 5 次提交中首提之后**全是审计驱动的加固**
（描述长度 lint / T5 / R1 安全 / R4 退出码），零功能提交。价值证据缺失 + 负担非轻 → 归档候选。

**未走 Deprecate 宽限期**：`governance/policies/skill-lifecycle.md` 的
Deprecate → 1 个月宽限期 → Archived 序列适用于「有替代品 / 能力过时」；本次走 Value-Burden
路线，与 2026-08-17 先例一致（直接归档，不设宽限）。

See `reports/VALUE-BURDEN-DECISION-skill-sync-2026-09-23.md`.

### Moved Files

| Original Path | Reason |
|---|---|
| `skills/skill-sync/` | 内网 Insight 平台的技能上传/拉取通道，无价值实证（无消费者 / 无运行记录 / 平台未配置） |
| `cli/tests/test_skill_sync_policy.py` → `archived/skills/skill-sync/tests/` | 契约测试随技能同生命周期归档（先例：skill-optimizer 的 `scripts/tests/`）；路径常量随位置修正，单跑仍 10 项 OK |

### Consequential Updates

- `skills/README.md`：删 `skill-sync` 索引行；该节计数按实际行数更正（`(6)` → `(1)`，原声明本已漂移）
- `cli/tests/test_t5_hardening.py`：`test_source_uses_execfile_not_template_exec` 改指
  **归档快照**路径（保留 T5 execFileSync 修复的历史证据；恢复正常需重跑该断言）
- `tools/path-audit.py`：EXAMPLE_ONLY 的 `../skill-generator` 注释更正为归档路径
  （条目保留 —— `archived/` 不在 path-audit 扫描范围，但恢复该技能时仍需此豁免）
- 技能枚举口径自动收敛：`tools/skill_index.py` 39 → **38**（无需改代码）
- `.github/workflows/ci.yml`：本仓**无 `.github/`**（2026-08-17 先例当年存在的 2 个 CI 步骤
  在当前树上已不存在），无需处理
- CLI / `config/menu.yaml` / `config/skill-groups.yaml` / workflows：**零引用**，无需解绑
- **R4 §2.2 撤销**：判决前在途的 `loadConfiguration` 抽共享模块重构（未提交）已撤销；
  `archived/` 保持 HEAD（`f36f744`）快照，不追加改进
- 恢复条件（`skill-lifecycle.md` Stage Archived）：ADR 说明 + 全质量门禁通过 + linter 通过
