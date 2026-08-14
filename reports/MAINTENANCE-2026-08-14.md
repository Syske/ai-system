# Maintenance Report — 2026-08-14

**Mode**: on-demand（巡检当前提案）
**Scope**: 提案审计（proposal-audit）+ 治理一致性抽查（全量基础项）
**Date**: 2026-08-14
**Environment**: WSL2（`/mnt/d/workspace/ai-workspace`，git branch `main`）

> 上次例行维护 2026-08-13（weekly）。本次为 on-demand，聚焦提案状态与治理一致性。

---

## 1. Tool Check Results（工具校验）

| Tool | Result | Detail |
|------|--------|--------|
| quick-check.py | ✅ OK | 0 findings；快照 `metrics/quick-check-2026-08-14.json`（08-13 亦 OK，连续 2 日无问题） |
| repo-lint.py | ✅ PASS | BLOCKER **0** / ERROR **0** / WARNING **27**（08-13 为 35，Δ-8，语言债回落） |
| repo-metrics.py | ✅ PASS | snapshot 已存 `metrics/maintain-2026-08-14.json` |
| path-audit.py | ✅ PASS | files=260, refs_checked=637, placeholders=105, known_debt=3, **BROKEN 0** |
| check.py（完整性门禁） | ✅ PASS（exit 0） | 15 workflows / 13 commands；1 warning（P22 提案未闭合，预期） |
| proposal-audit.py | ✅ PASS | GATE ERROR 0 / WARNING 0；**17 proposals**：16 Implemented / 1 Proposed（P22）；未关闭 `- [ ]` action item **0**；索引已 `--refresh-index` 刷新 |

### repo-lint 27 warnings 构成（08-13 的 35 → 27）

| 类别 | 数量 | 明细 |
|------|------|------|
| skill.md >80 行但无 workflow.md | 8 | agent-debug-diagnosis(114)、apply-openspec(129)、contract-maintainer(134)、explore(150)、handoff(92)、idea-build(99)、java-maven(101)、review(87) |
| cli/commands Steps 含中文 | 3 | aic-scan(4)、aic-skill-source(3)、aic-trace(4)（既有债，未新增） |
| Python 英文注释 | 10 | interactive.py(2)、menu_config.py(2)、test_services.py(2)、test_skill_launcher.py(3)、test_state_store.py(1)、context-audit.py(2) |
| governance/memory 含中文 | 3 | ai-system/coding-memory.md(5)、coding-memory.md(10)、java/coding-memory.md(5)（既有债） |

> 08-13 的 Python 注释 23 条中部分已随测试重构消解（Δ-13），无新增来源。

### 指标对比（vs `metrics/maintain-2026-08-13.json`）

| Metric | 08-13 | 08-14 | Δ |
|--------|-------|-------|---|
| Skills | 33 | 33 | 0 |
| Workflows | 14 | **15** | +1（hotfix-test-doc 入册） |
| RFCs | 13 | **14** | +1 |
| Governance | 59 | **61** | +2 |
| Templates | 21 | **22** | +1 |
| Frontmatter | 32 valid / 1 missing | 32 valid / 1 missing | 0 |

### quick-check 趋势

| Date | Verdict | Findings |
|------|---------|----------|
| 2026-08-13 | OK | 0 |
| 2026-08-14 | OK | 0 |

（快照仅 2 日，趋势样本不足；连续 OK，无恶化。）

---

## 2. 巡检发现（按严重度分级）

### 🔴 BLOCKER / 🔶 ERROR
无。

### 🟡 WARN

| # | 级别 | 发现 | 位置 |
|---|------|------|------|
| F1 | WARN | 提案 P22-WSL-ENVIRONMENT-INTEGRATION 状态 Proposed，Review Log 为 **Pending**，未闭合 | `reports/P22-*.md` |
| F2 | WARN | 12/15 workflow 文件为 CRLF 行尾、4 个为 LF，混排（抽查脚本误报的根因；建议统一 LF） | `workflows/*.md` |
| F3 | WARN | aic-maintain.md 引用 "README glossary"，但 ai-system 无独立 glossary 文件，实际为 `workflows/README.md` 的选择表；措辞过时 | `cli/commands/aic-maintain.md:56` |
| F4 | WARN | 8 个 skill.md >80 行但无 workflow.md（既有债，未新增） | 见 §1 构成表 |
| F5 | WARN | language-convention 债 16 条（中文 Steps ×3 + 英文注释 ×10 + memory 中文 ×3，既有债，未新增） | 见 §1 构成表 |

### 🔵 INFO

| # | 发现 |
|---|------|
| I1 | `python` 命令在 WSL 命中不可执行的 Windows pyenv shim，须用 `python3`；与 P22 阶段二 env-init 自检相关 |
| I2 | extensions 仓库有 **10 个未提交修改**（codeup-submit-mr / hotfix-branch-parser / hotfix-test-doc 等），未影响 lint（0/0），但建议尽快提交 |
| I3 | `config/environments/wsl.yaml` 已按 P22 声明 gitignore（.gitignore:22 验证通过），模板 `wsl.yaml.template` 已入库 |
| I4 | release → deployment 为文档化"workflow set 之外"的出口，非断链 |

---

## 3. 治理一致性抽查结论（逐项）

| 检查项 | 结论 |
|--------|------|
| workflows/*.md 八节齐全且有序 | ✅ 15/15 通过（Purpose→Runtime→Preconditions→Inputs→Context→Outputs→Exit Criteria→Next） |
| 术语与 README 选择表一致 | ✅ 工作流名/主链与 `workflows/README.md` 一致；"glossary"措辞见 F3 |
| Runtime 引用文件存在 | ✅ 15/15 runtime 文件均在 `templates/runtime/` |
| Preconditions/Next 链闭合 | ✅ 所有 Next 目标存在；deployment 为文档化外部出口（I4） |
| config/workflows/*.yaml 保持最小化 | ✅ 全部仅 name/workflow/runtime；bugfix-modes.yaml 为合法 modes 配置（非注册表膨胀） |
| governance/standards、loaders、templates/prompts、cli/commands 引用路径存在 | ✅ 0 broken（path-audit 637 refs） |
| Link health（projects 等 junction/symlink） | ✅ `projects -> /mnt/d/workspace/project-resources` 存在且可访问 |
| Doc-vs-reality（AGENTS.md / AI_DEVELOPMENT_CONTRACT §2 / OPERATIONS） | ✅ 全部目录存在；workflow-registry.yaml、providers.yaml 在位 |
| State hygiene（workspaces/.aic-state.yaml） | ✅ `pywechat-live-2608` 存在；maintenance 状态为 08-13/weekly，本次将更新 |
| 提案遗留（proposal-audit） | ✅ 17 proposals 全审计，索引已刷新；P22 为唯一未闭合（见 F1） |

---

## 4. 提案 P22 处置建议（巡检核心）

| 阶段 | 状态 | 建议处置 |
|------|------|----------|
| 阶段一（WSL 集成登记：wsl.yaml + 依赖 + PATH 收敛） | 已落地（Implementation Record 2026-08-14，验证全过） | **approve** —— 建议将 P22 状态改为 Approved，登记实施记录 |
| 阶段二（`aic env-init` 子命令 + 环境自动感知） | 未开始（4 个 Open Items） | **defer** —— 需新提案/阶段二提案审批后实施；Open Items 4 项保持跟踪 |

**P22 Open Items**（defer 跟踪）：
1. `aic env-init` 子命令（挂载点探测 + 环境生成 + 依赖 + PATH + 自检）
2. 默认环境按运行平台自动选择
3. 交互向导完整自动化测试（agent 启动后真实交互断言）
4. `contexts/project.yaml` 与 `workspace.yaml` repo 路径来源统一（`repo_path_for` 单一数据源）

---

## 5. 修复动作与建议清单

| # | 动作 | 类型 | 需确认 |
|---|------|------|--------|
| A1 | 12 个 workflow 文件 CRLF → LF 统一（F2） | 小修（行尾归一） | 是 |
| A2 | aic-maintain.md:56 "README glossary" → "workflows/README.md 选择表"（F3） | 小修（文档措辞） | 是 |
| A3 | P22 状态 Proposed → Approved（阶段一已落地），阶段二 defer（F1） | 状态登记 | 是 |
| A4 | language-convention 债 16 条 + 8 个 skill workflow.md 缺失 | 既有债，继续跟踪（不新增） | 否 |
| A5 | extensions 仓库 10 个未提交修改 | 移交扩展维护流程提交 | 否（仅记录） |

> 结构性问题无；无 OPERATIONS §12 change management 流程需求（不涉及目录调整/模块合并/契约修改）。

---

## 5.1 修复批次（用户确认后执行，2026-08-14）

| 项 | 动作 | 结果 |
|----|------|------|
| A1 | 12 个 workflow 文件 CRLF → LF 统一（F2） | ✅ 已执行，0 CRLF 残留；八节顺序抽查误报根因消除 |
| A2 | aic-maintain.md:56 “README glossary” → “workflows/README.md selection table”（F3） | ✅ 已执行 |
| A3 | P22 Status Proposed → **Approved**（阶段一落地确认），Review Log 更新；阶段二 defer 至新提案（F1） | ✅ 已执行，索引已刷新 |
| A4 | MAINTENANCE-2026-08-14.md 补登记 reports/README.md 索引（proposal-policy §6 门禁） | ✅ 已执行 |

**Validation**：`check.py` PASS **0 warning**（修复前 1）；`proposal-audit` errors 0 / warnings 0 / open proposals **0**；`quick-check` OK 0 findings；`repo-lint` 27 WARN 不变（无新增）。

---

## 5.2 跨平台治理落地（P23，用户批准后执行，2026-08-14）

用户决策：LF 唯一入库规范 + text=auto 策略 + 全仓归一。四批落地：

| 批 | 动作 | 结果 |
|----|------|------|
| 批1 | P23 提案登记 L1-L5 约定 | ✅ `reports/P23-CROSS-PLATFORM-MAINTENANCE-GOVERNANCE.md` |
| 批2 | `.gitattributes` 入库（LF 唯一规范，text=auto） | ✅ 357 个行尾噪音 M → 0；`git add --renormalize` |
| 批3 | `.githooks/pre-commit` python → python3 | ✅ hook 实跑输出真实 lint 摘要（PASS 0 warning） |
| 批4 | `repo-lint.py` 新增 `check_line_endings` 规则（WARN） | ✅ 混排触发验证（CRLF 2/LF 1 精确报告） |

**Validation**：repo-lint 0 BLOCKER/ERROR / 27 WARN（语言债，混排 0）；check.py PASS 0 warning；proposal-audit 0 gate errors / 0 leftover；quick-check OK；path-audit 0 broken；工作树 clean（stat 缓存陈旧条目经 `git add -u` 归零，内容 blob 与 HEAD 一致）。

**关键经验**：`git checkout -- .` 不会重写已被 gitattributes 判定等价的 CRLF 工作区文件（status 干净但字节仍 CRLF）；需 `sed`/`dos2unix` 显式归一工作区字节。

---

## 6. 环境备注（记录维护经验）

- **python shim**：WSL 下 `python` 命中 `/mnt/c/Users/syske/.pyenv/pyenv-win/shims/python`（不可执行），必须 `python3`。已影响本次所有工具调用；P22 阶段二 env-init 自检应显式校验 `python3`。
- **CRLF 教训**：行尾混排会导致基于文本匹配的门禁误报（本次 section 顺序抽查的 DIFF 全为误报）。后续抽查脚本应先行 `tr -d '\r'` 或统一 LF。
- **既有未提交改动（会话前，非本次引入）**：`git status` 显示约 360 个条目（含 archived/*、reports/*、config/workflows/*.yaml 等），原因：工作区大量文件为 CRLF、HEAD 为 LF，且 P22 阶段二落地记录（providers.py 修复说明、validation 补充）已在工作区未提交。本次仅提交式登记（不入 git commit）；`git diff -w` 核实本次实质变更仅 4 文件（aic-maintain.md 2 行、P22 状态 2 处、PROPOSALS.md 索引、README.md 索引）。建议后续统一处理：全仓 CRLF→LF 一次提交 + 未提交改动审查。
- **pre-commit hook 假阳性（2026-08-14 提交时发现）**：`.githooks/pre-commit` 调用 `python`，WSL 下命中不可执行 shim，报错被 `|| true` 吞掉后仍打印 “gates passed”——gate 实际未执行。建议 hook 改为 `python3`（或探测可用解释器），否则门禁形同虚设。本次两笔提交（6035d19 / f6b1855）已单独用 `python3 tools/check.py` 等真实跑过 gate。

---

## 7. 结论

- 工具校验：**全部 PASS**（0 BLOCKER / 0 ERROR）。
- 巡检发现：0 严重项；4 WARN（1 提案未闭合 + 3 文档/行尾类）+ 2 INFO。
- 治理一致性：**10/10 通过**。
- 提案状态：16/17 已闭合；P22 建议 approve（阶段一）＋ defer（阶段二）。
