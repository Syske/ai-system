# Maintenance Report — 2026-08-17

**Mode**: on-demand（无 Scope → 执行周度巡检集 + 全量治理一致性抽查）
**Date**: 2026-08-17
**Environment**: Git Bash on Windows（pyenv Python 3.10.11，`python`/`python3` 均可用；非 WSL，上次记录的 shim 问题不适用）

> 上次例行维护 2026-08-14（on-demand 提案巡检）。本次为 on-demand 无 Scope，按 OPERATIONS §9.1 周度集执行（duplication / dependency graph / orphan / health），叠加治理一致性全量抽查。

---

## 1. Tool Check Results（工具校验）

| Tool | Result | Detail |
|------|--------|--------|
| quick-check.py | ✅ OK | 0 findings；快照 `metrics/quick-check-2026-08-17.json` |
| repo-lint.py | ✅ PASS | BLOCKER **0** / ERROR **0** / WARNING **27**（与 08-14 持平，无新增） |
| repo-metrics.py | ✅ PASS | snapshot `metrics/maintain-2026-08-17.json`；与 08-14 **逐项一致** |
| path-audit.py | ✅ PASS | files=260, refs_checked=638, placeholders=105, known_debt=3, **BROKEN 0** |
| check.py（完整性门禁） | ❌ **FAIL（exit 1）** | 71 tests：**1 error**（详见 §2 R1）；08-14 为 PASS 0 warning → **回归** |
| proposal-audit.py | ✅ PASS | GATE ERROR 0 / WARNING 0；**18 proposals 全闭合**（17 Implemented + 1 Approved）；未关闭 `- [ ]` action item **0**；索引已 `--refresh-index` |

### repo-lint 27 warnings 构成（与 08-14 相同，无新增）

| 类别 | 数量 | 明细 |
|------|------|------|
| skill.md >80 行但无 workflow.md | 8 | agent-debug-diagnosis、apply-openspec、contract-maintainer、explore、handoff、idea-build、java-maven、review（既有债） |
| cli/commands Steps 含中文 | 3 | aic-scan(4)、aic-skill-source(3)、aic-trace(4)（既有债） |
| Python 英文注释 | 13 | interactive.py(2)、menu_config.py(2)、test_services.py(2)、test_skill_launcher.py(3)、test_state_store.py(2)、context-audit.py(2)（既有债） |
| governance/memory 含中文 | 3 | ai-system/coding-memory.md(5)、coding-memory.md(10)、java/coding-memory.md(5)（既有债） |

### 指标对比（vs `metrics/maintain-2026-08-14.json`）

| Metric | 08-14 | 08-17 | Δ |
|--------|-------|-------|---|
| Skills | 33 | 33 | 0 |
| Workflows | 15 | 15 | 0 |
| RFCs | 14 | 14 | 0 |
| Governance | 61 | 61 | 0 |
| Templates | 22 | 22 | 0 |
| Frontmatter | 32 valid / 1 missing | 32 valid / 1 missing | 0 |

### quick-check 趋势

| Date | Verdict | Findings |
|------|---------|----------|
| 2026-08-13 | OK | 0 |
| 2026-08-14 | OK | 0 |
| 2026-08-17 | OK | 0 |

（连续 3 日 OK，无恶化。）

---

## 2. 巡检发现（按严重度分级）

### 🔴 ERROR

| # | 级别 | 发现 | 位置 |
|---|------|------|------|
| R1 | ERROR | **check.py 完整性门禁回归（exit 1）**：`test_reads_repository_mapping` 抛 `AttributeError: 'FakeWizard' object has no attribute 'projects_root'`。根因：P22 提交 `6035d19` 为 `_repo_path`（providers.py:47）引入 `wizard.projects_root` 依赖，但 `FakeWizard`（test_skill_launcher.py:175）未补该属性。`sys.platform == "linux"` 分支（WSL）绕过该访问所以此前通过；本机 win32 分支必触达 → **平台相关回归**。工作树 clean，非未提交改动引入 | `cli/tests/test_skill_launcher.py:175` + `cli/services/providers.py:47` |

### 🟡 WARN

| # | 级别 | 发现 | 位置 |
|---|------|------|------|
| W1 | WARN | language-convention 债 27 条（8 skill workflow.md + 3 中文 Steps + 13 英文注释 + 3 memory 中文，既有债，无新增） | 见 §1 构成表 |
| W2 | WARN | `skills/architecture/` 无顶层 skill.md/SKILL.md（目录含 7 个子 skill），repo-metrics frontmatter 计 1 missing（既有，08-14 即如此；lint 按文件计不受影响） | `skills/architecture/` |

### 🔵 INFO

| # | 发现 |
|---|------|
| I1 | extensions 仓库**已干净**（0 未提交改动；08-14 的 I2「10 个未提交修改」已解决）；extensions-lint 随 quick-check 运行 0 errors / 0 warnings |
| I2 | 依赖图无真实环，仅 5 组 doc-only mention 环（java-maven↔idea-build、review↔review-changes、explore↔explore-codebase、benchmark-generator 组）；最大层深 4（Meta 层），符合 health 模型 ≤4 要求 |
| I3 | 重复信号极低：844 条 >40 字符长行中仅 5 条重复（ratio 0.006）；无相同标题结构 skill |
| I4 | `projects` junction → `D:\workspace\project-resources` 可访问（LinkType: Junction） |

---

## 3. 治理一致性抽查结论（逐项）

| 检查项 | 结论 |
|--------|------|
| workflows/*.md 八节齐全且有序 | ✅ 15/15 通过（review.md 含合法可选节 `When to Use`，模板允许插于 Purpose 后） |
| 术语与 README 选择表一致 | ✅ 工作流名与 `workflows/README.md` 选择表一致 |
| Runtime 引用文件存在 | ✅ registry 15/15 → runtime 文件均存在（脚本校验通过） |
| Preconditions/Next 链闭合 | ✅ backtick 精确扫描：**0** 个开放 Next 目标；deployment 为文档化外部出口 |
| config/workflows/*.yaml 保持最小化 | ✅ 15 个注册 yaml 全部仅 version/name/workflow/runtime，无 extra keys；bugfix-modes.yaml 为合法 modes 配置（A1 复发预防确认） |
| governance/standards、loaders、templates/prompts、cli/commands 引用路径存在 | ✅ path-audit 0 broken（638 refs）；智能 backtick 扫描剩余 20 项均为 doc 级命名约定（如 `REFLECTION_RULES.md` 相对 governance 目录、生成物占位名），非真实断链 |
| loaders/standards-loader.md 引用存在 | ✅ 全部 standards 文件在位（根相对/standards 相对双解析） |
| Link health（projects junction/symlink） | ✅ `projects -> D:\workspace\project-resources` 存在且可访问 |
| Doc-vs-reality（AGENTS.md / AI_DEVELOPMENT_CONTRACT §目录树 / OPERATIONS §9） | ✅ 全部目录存在；契约目录树 12 项与磁盘一致；workflow-registry.yaml、providers.yaml、config/workflows/、config/environments/ 在位 |
| State hygiene（workspaces/.aic-state.yaml） | ✅ projects 引用存在（pywechat-live-2608）；maintenance 状态本次更新 |
| 提案遗留（proposal-audit） | ✅ 18 proposals 全闭合（P22 Approved 已生效）；0 open action items；索引已刷新 |

**一致性抽查：11/11 通过。**

---

## 4. 修复动作与建议清单

| # | 动作 | 类型 | 需确认 |
|---|------|------|--------|
| A1 | **R1 修复**：`test_skill_launcher.py` FakeWizard 补 `projects_root` + 新增双平台回归用例 `test_repo_path_dual_platform` | 小修（测试夹具补属性，L1） | ✅ 已实施（P24）|
| A2 | W1 language-convention 债 27 条 | 既有债，继续跟踪（无新增） | 否 |
| A3 | W2 `skills/architecture/` 顶层文件缺失 | 既有结构，继续跟踪（新增顶层 skill.md 或列入指标白名单） | 否 |
| A4 | extensions 仓库保持干净 | 仅记录 | 否 |

> 结构性问题无；无 OPERATIONS §11 change management 流程需求（不涉及目录调整/模块合并/契约修改）。R1 修复属于测试夹具修正，不触碰架构。

---

## 5. 结论

- 工具校验：**quick-check / repo-lint / repo-metrics / path-audit / proposal-audit 全 PASS**；**check.py PASS（exit 0）**（R1 已修复，见 P24）。
- 巡检发现：R1 已闭环（P24 Implemented）；2 WARN 均为既有债；4 INFO。
- 治理一致性：**11/11 通过**。
- 提案状态：19/19 已闭合。

---

## 6. 维护经验（记录）

- **平台相关测试脆弱性**：`_repo_path` 的 `sys.platform == "linux"` 分支会静默掩盖 `wizard.projects_root` 缺失——WSL 下测试全绿、win32 下必红。教训：provider 的 wizard 契约（属性集）应显式声明并写入测试夹具；涉及平台分支的 provider 改动需双平台跑 `check.py`。
- **on-demand 无 Scope**：按 OPERATIONS §9.1 周度集执行，`next_maintenance` 保持既有周度节奏（2026-08-20）不变，on-demand 不重置周期。
