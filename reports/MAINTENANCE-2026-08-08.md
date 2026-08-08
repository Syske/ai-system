# Maintenance Report — 2026-08-08

**Mode**: weekly
**Scope**: ai-system + workflow system（重复报告 / 依赖图 / 孤儿资产 / 健康分 + 治理一致性抽查）
**Date**: 2026-08-08
**Environment**: `D:\workspace\ai-workspace`（Windows, git branch `main`）

---

## 1. Tool Check Results（工具校验）

| Tool | Result | Detail |
|------|--------|--------|
| repo-lint.py | ✅ PASS | BLOCKER 0 / ERROR 0 / WARNING 30（08-06 为 9，+21 来自 Rule 3 语言检查扩展，均为存量债，见 F3） |
| repo-metrics.py | ✅ PASS | snapshot 已存 `metrics/maintain-2026-08-08.json` |
| path-audit.py | ✅ PASS | files=250, refs=582, placeholders=92, known_debt=3, **BROKEN 0** |
| check.py（完整性门禁） | ✅ PASS（exit 0） | 14 workflows / 14 commands；2 warning（aic-apply.md 114 行、aic-explore.md 124 行，thin-command 门禁） |
| proposal-audit.py | ✅ PASS | GATE ERROR 0 / WARNING 0；遗留提案 0、未关闭 action item 0；索引已 `--refresh-index` 刷新（10 proposals） |

### repo-lint 30 warnings 构成（08-06 的 9 → 30）

| 类别 | 数量 | 明细 |
|------|------|------|
| skill.md >80 行但无 workflow.md | 6 | agent-debug-diagnosis(114)、contract-maintainer(134)、handoff(92)、idea-build(99)、java-maven(101)、review(87)（较 08-06 新增 handoff、idea-build 2 项） |
| 技能内 Maven 命令引用 | 5 | bugfix×2、mock-test×3（与 08-06 一致） |
| cli/commands Steps 含中文 | 3 | aic-scan(4 行)、aic-skill-source(3 行)、aic-trace(4 行)（既有） |
| Python 英文注释 | 13 | interactive.py×2、menu_config.py×2、test_services.py×2、test_skill_launcher.py×3、test_state_store.py×2、context-audit.py×2（Rule 3 扩展暴露，其中 11 项未入债清单，见 F3） |
| governance/memory 含中文 | 3 | ai-system/coding-memory.md(5 行)、coding-memory.md(10 行)、java/coding-memory.md(5 行)（Rule 3 新暴露） |

### 指标对比（vs `metrics/maintain-2026-08-06.json`）

| Metric | 08-06 | 08-08 | Δ |
|--------|-------|-------|---|
| Skills | 26 | 33 | **+7** |
| Avg skill size | 879 lines | 753 lines | −126 |
| Largest skill | 8990 lines | 9968 lines | +978（skill-optimizer，S1 持续跟踪） |
| Workflows | 14 | 14 | 0 |
| RFCs | 12 | 12 | 0 |
| Governance | 56 | 59 | +3 |
| Templates | 21 | 21 | 0 |
| Frontmatter | 25 valid / 1 missing | 32 valid / 1 missing | +7 valid（architecture/ 容器无 skill.md，已知/设计如此） |

> +7 Skills：apply-openspec、archive-openspec、explore、handoff、idea-build、memory-capture、propose-openspec —— OpenSpec 流程技能族扩展，增长合理；平均规模下降说明新增技能均为轻量级。

---

## 2. Weekly Inspection（周度巡检）

### 2.1 Duplication Report（重复报告）

| # | 模式 | 位置 | 严重度 |
|---|------|------|--------|
| D1 | 非 java-maven 技能硬编码 `mvn` 命令 | bugfix/anti-patterns.md:58、bugfix/validation.md:32,46-47、mock-test/anti-patterns.md:70、mock-test/diagnosis.md(8×)、mock-test/mockito.md:199 | **HIGH** — 违反 `repository-maintainer/governance.md:30`（"No Maven commands unless java-maven"） |
| D2 | `mvn test` 命令跨技能重复 | bugfix/validation.md、mock-test/diagnosis.md、mock-test/mockito.md | MED（D1 同源） |
| D3 | `# Validation` 门禁模板双份（219 行 vs 80 行变体） | implement/validation.md ↔ bugfix/validation.md | MED |
| D4 | retry-scope 样板 `mvn test -Dtest=…` ×8 | mock-test/diagnosis.md（文件内） | MED |
| D5 | 代码库探索技能范围重叠 | explore/skill.md ↔ explore-codebase/skill.md（OpenSpec 工作区 ↔ 知识图谱，机制与入口均不同） | LOW-MED（暂不合并） |
| D6 | CLI 单 `## <X> Report` 模板 | aic-scan / aic-trace / aic-maintain | LOW（结构性，非内容重复） |
| D7 | review vs review-changes（87 vs 43 行） | 互相引用、职责互补 | 无（刻意拆分，正确） |

**结论**：唯一 HIGH 项为 D1 —— mvn 命令分散在 bugfix/mock-test，与 repository-maintainer 自身治理规则冲突（文档 vs 现实偏差）。修复方向：改为引用 java-maven 的委派说明（见 §5 建议 S1）。

### 2.2 Dependency Graph（依赖图）

- 分层：Foundation → Test → OpenSpec → Meta，深度 ≤2 层，无真实环。
- 4 个环（idea-build↔java-maven、review↔review-changes、outcome↔skill-benchmark、skill↔routing-benchmark）均为 **doc-only mention**（检测器已区分，08-06 P13 语义分层生效，无误报）。
- 新增技能均为 standalone 或 OpenSpec 层（apply/archive/propose-openspec standalone、task-splitter→contract-maintainer），无异常依赖。

### 2.3 Orphan Analysis（孤儿资产）

- **无孤儿技能**：33 个技能均有 ≥2 处外部引用（最低 memory-capture/autowork/open-cli 2 处 = skills/README.md 索引 + 配置引用）。
- **runtime-base.md 非孤儿**（修正 08-06 疑点）：被全部 14 个 `templates/runtime/runtime-*.md` 引用 + `cli/commands/aic-workflow.md` + `rfc/ADR-0005` 引用。08-06 判定"无 workflow 直接引用"属实，但经 runtime 模板间接引用链完整，无需归档。
- 6 个 prompt 模板全部被引用（workflow.md 40 refs、command.md 3 refs 等），无孤儿。

### 2.4 Quick Health Score（健康分，15 维抽查）

| 维度 | 状态 | 得分 |
|------|------|------|
| 结构 / Skill 架构 / Workflow 架构 | ✅ | 3/3 |
| 能力分布 | ⚠️ D5 轻微重叠 | 0.8/1 |
| 依赖图 | ✅ 无真实环 | 1/1 |
| 知识组织 / 治理 / 命名 | ✅ | 3/3 |
| 语言规范 | ⚠️ 30 warnings（存量债已登记） | 0.5/1 |
| 重复控制 | ⚠️ D1 HIGH | 0.5/1 |
| 状态卫生 | ⚠️ F1 复发（见 §4） | 0.5/1 |
| 链接卫生 | ✅ 0 broken | 1/1 |
| 文档一致性 | ✅ | 1/1 |

**综合健康分：11.3 / 13 ≈ 87/100**（良好；较 08-06 结构面无回退，扣分集中在语言债、D1 重复与 F1 状态引用复发）。

---

## 3. Governance Consistency Spot Check（一致性抽查）

| # | 检查项 | 结果 | 说明 |
|---|--------|------|------|
| 3.1 | workflows/*.md 八段结构 | ✅ PASS | 14/14 全部 8 段齐全、顺序正确（Purpose→Runtime→Preconditions→Inputs→Context→Outputs→Exit Criteria→Next）；review.md 仅含允许的 When to Use |
| 3.2 | 术语与 README 词汇表一致 | ✅ PASS | 全部使用词汇表术语（Project ID / Task ID / Change ID / Task Card）；仅 2 处大小写变体（"task cards"），路径占位符 `{project_id}` 与词汇表一致 |
| 3.3 | Runtime 引用文件存在 | ✅ PASS | 14/14 `templates/runtime/runtime-*.md` 全部存在 |
| 3.4 | Preconditions/Next 链闭合 | ✅ PASS | Next 目标均存在；release→deployment 为文档明示的集外引用 |
| 3.5 | config/workflows/*.yaml 极简性 | ✅ PASS | 14/14 顶层键仅 `{version, name, workflow, runtime}`，无 inputs/outputs/next 回潮（**A1 未复发**） |
| 3.6 | 引用路径存在（standards/loaders/prompts/commands） | ✅ PASS | 0 broken 实时引用；仅 2 处标注性引用（wizard.py 模块化拆分声明、code-quality.md 归档记录） |
| 3.7 | Link health（junction/symlink） | ✅ PASS | `projects/` = **Junction → `D:\workspace\project-resources`**（`Get-Item -Force` 实测），目标存在、89 个仓库可访问；worktrees/、extensions/ 为普通目录（正常） |
| 3.8 | Doc-vs-reality：AGENTS.md | ⚠️ 微偏差 | 图内 9 目录全在盘；运营表 3 目录全在盘；3 个工具点目录未登记（`.codescope/` `.obsidian/` `.pi/`，低风险，见 F5） |
| 3.9 | Doc-vs-reality：AI_DEVELOPMENT_CONTRACT | ✅ PASS | 契约 13 目录 + `.github/` 全部存在，无新增顶层目录；子层微漂移：config/ 实际含 i18n/、menu.yaml、skill-groups.yaml（契约片段未列，信息项） |
| 3.10 | Doc-vs-reality：OPERATIONS.md | ✅ PASS | 入口/布局声明与磁盘完全一致（含 playbooks/ 不存在声明） |
| 3.11 | State hygiene（.aic-state.yaml） | ⚠️ WARN | `last_project: pywechat-live-2608` 引用**复发**：workspace 目录 `workspaces/pywechat-live-2608/` 存在，但业务仓库不在 junction 目标 `D:\workspace\project-resources` 中（与 08-06 F1 同模式，见 F1） |
| 3.12 | Proposal 遗留评估 | ✅ PASS | 0 遗留提案、0 未关闭 action item（详见 §4） |

---

## 4. Findings & Proposal Leftovers（发现与提案遗留处置）

### 按严重度分级

| 级别 | 编号 | 发现 | 处置建议 |
|------|------|------|----------|
| WARN | F1 | `.aic-state.yaml` 状态引用**复发**（08-06 A4 已清空）：`last_project: pywechat-live-2608` 的 workspace 目录存在但业务仓库不在 junction 目标中 —— 与 08-06 F1 同模式 | 同 A4：清空/更新 state 引用（L2，需确认）；并建议查明为何被重新写入 |
| WARN | F2 | D1 重复：bugfix/mock-test 硬编码 `mvn` 命令，违反 `repository-maintainer/governance.md:30` 自身规则（文档 vs 现实偏差） | 改为引用 java-maven 委派说明（L2 技能文档修改，需确认） |
| INFO | F3 | 语言债清单不完整：lint 30 warnings 中 13 项英文注释 + 3 项 governance memory 中文，债清单 `MAINTENANCE-2026-08-08-language-lint-debt.md` 仅登记 8 项（缺 11 项 Python 注释：menu_config×2、test_services×2、test_skill_launcher×3、test_state_store×2、context-audit×2） | 补登记债清单（L1 文档小修） |
| INFO | F4 | check.py 2 个 thin-command warning（aic-apply 114 行、aic-explore 124 行） | 记录；季度评估命令瘦身 |
| INFO | F5 | AGENTS.md 未登记 3 个工具点目录（.codescope/.obsidian/.pi） | 补登记（L1 文档小修，可选） |
| INFO | F6 | skill-optimizer 仍为最大技能（9968 行，较 08-06 +978） | S1 拆分提案 P10 持续跟踪（待 Review→Approve） |
| INFO | F7 | `architecture/` 容器目录无 skill.md（frontmatter "1 missing" 的来源） | 设计如此（7 子技能容器），记录不处理 |

### 遗留提案处置（proposal-audit）

- **GATE ERROR 0 / WARNING 0**；10 个提案全部已闭合（Implemented/Approved），0 未关闭 `- [ ]` action item；索引已刷新。
- 08-06 遗留的 method-comment-convention（P1/P2/P3, propose 待审）状态：本次 audit 未报未闭合 → 已进入提案索引管理（PROPOSALS.md），继续走 Review→Approve 流程。

---

## 5. Fix Actions & Suggestions（修复动作与建议清单）

### 本次已确认并执行的修复（2026-08-08 已实施）

| # | 动作 | 类型 | 状态 |
|---|------|------|------|
| A1 | 清空 `.aic-state.yaml` 陈旧引用（`last_project: null`, `projects: {}`） | L2（经确认） | ✅ 已修复 |
| A2 | bugfix/mock-test 硬编码 `mvn` 命令改为 java-maven 委派引用（5 处：bugfix/anti-patterns.md、bugfix/validation.md、mock-test/anti-patterns.md、mock-test/diagnosis.md ×8、mock-test/mockito.md） | L2（经确认） | ✅ 已修复（lint mvn warnings 5→0） |
| A3 | 补登记 11 项英文注释语言债到 `MAINTENANCE-2026-08-08-language-lint-debt.md`（#9-13）及 2 项 governance memory 中文（#14-15） | L1 | ✅ 已修复 |
| A4 | AGENTS.md 运营表补登记 `.codescope/` `.obsidian/` `.pi/` | L1 | ✅ 已修复 |
| A5 | 新报告登记 `reports/README.md` 维护报告索引 | L1 | ✅ 已修复（check.py 3→2 warnings） |

### 结构性建议（仅输出建议，走 OPERATIONS §11/§12 变更流程，不直接实施）

| # | 建议 | 目标 | 提案 |
|---|------|------|------|
| S1 | 已实施：java-maven 委派规范（lint 正则扩展 + governance 小节 + 20 处字面量改写） | 消除 HIGH 重复 | **P17-MAVEN-DELEGATION-GOVERNANCE**（**Implemented** 2026-08-08） |
| S2 | 根因已定位：wizard `_save_state`（output.py）无条件回写且无存在性校验；修复已实施（`_project_exists()` 守卫 + selection.py 过滤 + 9 单测） | 状态卫生根治 | **P16-STATE-WRITE-GUARD**（**Implemented** 2026-08-08） |
| S3 | 季度评估：aic-apply/aic-explore 命令瘦身（thin-command 门禁） | check.py 0 warning | **P18-THIN-COMMAND-SLIMMING**（Proposed） |
| S4 | 季度评估：explore vs explore-codebase 是否合并 | 能力矩阵清洁 | **P19-EXPLORE-SKILLS-RELATIONSHIP**（Proposed） |
| S5 | **Build 抽象观察项**：不新增抽象 build skill（现无第二构建工具需求，Evolution Principle）。触发条件：工作区出现第一个需受治理的 Gradle/npm 等非 Maven 构建项目 → 执行意图解耦（P17 表述泛化为 `Delegate build execution: <intent>`）+ 新增对应 build skill | 避免推测性抽象 | 观察（defer，按触发条件激活） |
| S6 | idea-build/idea-mcp.py:8 死链：引用不存在的 `java-maven/idea-build.md`（应为 `skills/idea-build/`，path-audit 不覆盖 .py 内字符串） | 链接卫生 | 观察（待修） |
| S7 | java-maven 入口文件为 `SKILL.md`（大写），RFC-0001/0002 要求小写 `skill.md`（Windows 大小写不敏感掩盖，跨平台会暴露） | 命名合规 | 观察（待评估，涉技能重命名需走变更流程） |

---

## 6. 结论

系统整体健康（87/100）：lint/path/门禁/proposal 全绿，workflow 八段结构、registry 极简（A1 未复发）、引用链与 Preconditions/Next 链闭合，junction 链接健康（target `D:\workspace\project-resources` 实测可访问），契约与 OPERATIONS 文档一致。本周期（08-06→08-08）新增 7 个 OpenSpec 流程技能，均为轻量、standalone，无结构性问题。

需跟进 3 项：P18（命令瘦身）、P19（explore 关系澄清）待季度评审；S5（build 抽象）按触发条件激活；S6/S7 为观察项（死链、命名合规）。其余为记录与季度建议。

---
**Modified Files**: `skills/bugfix/anti-patterns.md`、`skills/bugfix/validation.md`、`skills/mock-test/anti-patterns.md`、`skills/mock-test/diagnosis.md`、`skills/mock-test/mockito.md`（A2 委派化）、`reports/MAINTENANCE-2026-08-08-language-lint-debt.md`（A3 补登记）、`reports/README.md`（A5 索引登记）、`../AGENTS.md`（A4 运营表）、`../workspaces/.aic-state.yaml`（A1 清空）
**New Files**: `reports/MAINTENANCE-2026-08-08.md`、`metrics/maintain-2026-08-08.json`
**Validation**: repo-lint 0/0/25（mvn warnings 5→0）、check.py exit 0（3→2 warnings）、path-audit 0 broken、proposal-audit 0 gate errors
**Deviations**: A5（README 索引登记）为修复过程中新增的 L1 项，已在批次内执行
**Risks**: P17/P18/P19 为待审提案（P16 已闭环）；D1 剩余 `mvn -pl ...` 形态命令转 P17 统一治理
**Next Recommendation**: P16/P17 已 Implemented（状态卫生 + 重复治理闭环）；P18/P19 留季度评审；S5 build 抽象观察项按触发条件激活（出现首个非 Maven 构建项目时执行意图解耦 + 新增 build skill）
