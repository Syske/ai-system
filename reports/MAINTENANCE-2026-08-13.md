# Maintenance Report — 2026-08-13

**Mode**: weekly
**Scope**: ai-system + workflow system（重复报告 / 依赖图 / 孤儿资产 / 健康分 + 治理一致性抽查）
**Date**: 2026-08-13
**Environment**: `D:\workspace\ai-workspace`（Windows, git branch `main`）

---

## 1. Tool Check Results（工具校验）

| Tool | Result | Detail |
|------|--------|--------|
| repo-lint.py | ✅ PASS | BLOCKER 0 / ERROR 0 / WARNING **35**（08-08 为 30，Δ+5，全部为 Python 英文注释新增，见 F1） |
| repo-metrics.py | ✅ PASS | snapshot 已存 `metrics/maintain-2026-08-13.json` |
| path-audit.py | ✅ PASS | files=251, refs_checked=588, placeholders=96, known_debt=3, **BROKEN 0** |
| check.py（完整性门禁） | ✅ PASS（exit 0） | 14 workflows / 14 commands；2 warning（aic-apply.md 114 行、aic-explore.md 124 行，thin-command 门禁，同 08-08） |
| proposal-audit.py | ✅ PASS | GATE ERROR 0 / WARNING 0；遗留提案 2（P18/P19）、未关闭 action item 0；P20 已实施闭环；索引已 `--refresh-index` 刷新（16 proposals） |

### repo-lint 35 warnings 构成（08-08 的 30 → 35）

| 类别 | 数量 | 明细 |
|------|------|------|
| skill.md >80 行但无 workflow.md | 6 | agent-debug-diagnosis(114)、contract-maintainer(134)、handoff(92)、idea-build(99)、java-maven(101)、review(87)（与 08-08 一致） |
| cli/commands Steps 含中文 | 3 | aic-scan(4 行)、aic-skill-source(3 行)、aic-trace(4 行)（既有债 #1-3） |
| Python 英文注释 | **23** | 08-08 为 13；新增 10：`output.py:148-153`(6) + `selection.py:73-76`(4)，由 P16 状态写入守卫引入、未登记债清单（见 F1） |
| governance/memory 含中文 | 3 | ai-system/coding-memory.md(5)、coding-memory.md(10)、java/coding-memory.md(5)（既有债 #5-7） |

> 08-08 的 5 条 `mvn` 命令 warning 本周期已归零（P17 java-maven 委派规范生效，未复发）。

### 指标对比（vs `metrics/maintain-2026-08-08.json`）

| Metric | 08-08 | 08-13 | Δ |
|--------|-------|-------|---|
| Skills | 33 | 33 | 0 |
| Avg skill size | 753 lines | 753 lines | 0 |
| Largest skill | 9968 lines | 9968 lines | 0（skill-optimizer，S1 持续跟踪） |
| Workflows | 14 | 14 | 0 |
| RFCs | 12 | **13** | +1 |
| Governance | 59 | 59 | 0 |
| Templates | 21 | 21 | 0 |
| Frontmatter | 32 valid / 1 missing | 32 valid / 1 missing | 0（architecture/ 容器无 skill.md，设计如此 F7） |

---

## 2. Weekly Inspection（周度巡检）

### 2.1 Duplication Report（重复报告）

| # | 模式 | 位置 | 严重度 |
|---|------|------|--------|
| D1 | 非 java-maven 技能硬编码 `mvn` 命令 | bugfix / mock-test | **已消除**（P17 委派化，lint mvn warning 5→0，未复发） |
| D2 | `mvn test` 命令跨技能重复 | bugfix / mock-test | 已消除（D1 同源） |
| D3 | `# Validation` 门禁模板双份 | implement/validation.md ↔ bugfix/validation.md | MED（既有，无变化） |
| D4 | retry-scope 样板 `mvn test -Dtest=…` ×8 | mock-test/diagnosis.md | 已消除（D1 同源） |
| D5 | 代码库探索技能范围重叠 | explore/skill.md ↔ explore-codebase/skill.md | LOW-MED（P19 待季度评估，无变化） |
| D6 | CLI 单 `## <X> Report` 模板 | aic-scan / aic-trace / aic-maintain | LOW（结构性，非内容重复） |
| D7 | review vs review-changes | 互相引用、职责互补 | 无（刻意拆分，正确） |

**结论**：HIGH 项 D1 已闭环；本周期无新增 HIGH/MED 重复。

### 2.2 Dependency Graph（依赖图）

- 分层：Foundation → Test → OpenSpec → Meta，深度 ≤2 层，无真实环。
- 4 个环（idea-build↔java-maven、review↔review-changes、outcome↔skill-benchmark、skill↔routing-benchmark）均为 **doc-only mention**（检测器已区分，P13 语义分层生效，无误报）。
- 结构无变化。

### 2.3 Orphan Analysis（孤儿资产）

- **无孤儿技能**：33/33 技能均有外部引用。
- runtime-base.md 非孤儿（被 14 个 runtime 模板 + aic-workflow.md + ADR-0005 引用，08-06 疑点已澄清）。
- 6 个 prompt 模板全部被引用，无孤儿。

### 2.4 Quick Health Score（健康分，15 维抽查）

| 维度 | 状态 | 得分 |
|------|------|------|
| 结构 / Skill 架构 / Workflow 架构 | ✅ | 3/3 |
| 能力分布 | ⚠️ D5 轻微重叠 | 0.8/1 |
| 依赖图 | ✅ 无真实环 | 1/1 |
| 知识组织 / 治理 / 命名 | ✅ | 3/3 |
| 语言规范 | ⚠️ 35 warnings（含 10 项新增未登记） | 0.4/1 |
| 重复控制 | ✅ D1 已消除 | 1/1 |
| 状态卫生 | ✅ P16 治理后引用合法 | 1/1 |
| 链接卫生 | ✅ 0 broken | 1/1 |
| 文档一致性 | ✅ | 1/1 |

**综合健康分：11.2 / 13 ≈ 86/100**（良好；较 08-08 的 87 微降，扣分来自 10 项新增英文注释未登记）。

---

## 3. Governance Consistency Spot Check（一致性抽查）

| # | 检查项 | 结果 | 说明 |
|---|--------|------|------|
| 3.1 | workflows/*.md 八段结构 | ✅ PASS | 14/14 全部 8 段齐全、顺序正确（Purpose→Runtime→Preconditions→Inputs→Context→Outputs→Exit Criteria→Next）；review.md 仅含允许的 When to Use 可选段 |
| 3.2 | 术语与 README 词汇表一致 | ✅ PASS | 使用词汇表术语（Project ID / Task ID / Change ID / Task Card）；无新增术语 |
| 3.3 | Runtime 引用文件存在 | ✅ PASS | 14/14 `templates/runtime/runtime-*.md` 全部存在 |
| 3.4 | Preconditions/Next 链闭合 | ✅ PASS | 16 条 Next 目标全部存在；release→deployment 为文档明示的集外引用 |
| 3.5 | config/workflows/*.yaml 极简性 | ✅ PASS | 14/14 顶层键仅 `{version, name, workflow, runtime}`，无 inputs/outputs/next 回潮（**A1 未复发**） |
| 3.6 | 引用路径存在（standards/loaders/prompts/commands） | ✅ PASS | 0 broken 实时引用；扫描到的 10 条为文档化占位符（`aic-<name>.md`、`{locale}.yaml`、`<name>.yaml` 等），非真实断链 |
| 3.7 | Link health（junction/symlink） | ✅ PASS | `projects/` = **Junction → `D:\workspace\project-resources`**（`Get-Item -Force` 实测），目标存在、可访问 |
| 3.8 | Doc-vs-reality：AGENTS.md | ✅ PASS | 图内目录与运营表目录均存在；工具点目录（.codescope/.obsidian/.pi）已登记（08-08 A4） |
| 3.9 | Doc-vs-reality：AI_DEVELOPMENT_CONTRACT | ✅ PASS | 契约 13 目录 + `.github/` 全部存在，无新增顶层目录；config/ 子层微漂移（i18n/menu.yaml/skill-groups.yaml 契约未列，信息项，08-08 已记录） |
| 3.10 | Doc-vs-reality：OPERATIONS.md | ✅ PASS | 入口/布局声明与磁盘一致（含 playbooks/ 不存在声明） |
| 3.11 | State hygiene（.aic-state.yaml） | ✅ PASS | `last_project: pywechat-live-2608` 为 **workspace-only 项目**（P16 判定合法）：workspace 目录存在，无对应业务仓库属设计内场景，非陈旧引用 |
| 3.12 | Proposal 遗留评估 | ⚠️ 2 遗留 | P18/P19（P20 已实施闭环，详见 §4） |

---

## 4. Findings & Proposal Leftovers（发现与提案遗留处置）

### 按严重度分级

| 级别 | 编号 | 发现 | 处置建议 |
|------|------|------|----------|
| INFO | F1 | 语言债未登记：P16 守卫新增 10 项英文注释（`output.py:148-153`×6、`selection.py:73-76`×4）未加入债清单，lint warning 30→35 | ✅ 已修复（S-A：直接改中文注释，warning 35→25） |
| INFO | F2 | 死链 S6 仍存：`skills/idea-build/idea-mcp.py` docstring 引用 `ai-system/skills/java-maven/idea-build.md`，该文件不存在（实际为 `skills/idea-build/SKILL.md`） | ✅ 已修复（S-B：docstring 引用路径更正） |
| INFO | F3 | `skills/idea-build/idea-mcp.py` 有未提交改动（新增 `--files` 增量编译参数，约 +10 行） | 属 workspace 未提交变更，记录不处理（需用户决定提交或还原） |
| INFO | F4 | 工作树含未跟踪 `.ai-system/generated/prepare.md` 及已修改 `reports/PROPOSALS.md`（本次 `--refresh-index` 刷新所致） | PROPOSALS.md 刷新为预期结果；prepare.md 与 .ai-system/ 记录不处理 |
| INFO | F5 | check.py 2 个 thin-command warning（aic-apply 114 行、aic-explore 124 行） | 记录；P18 季度评估 |
| INFO | F6 | skill-optimizer 仍为最大技能（9968 行） | P10 已 Implemented，持续跟踪 |
| INFO | F7 | `architecture/` 容器目录无 skill.md（frontmatter "1 missing" 来源） | 设计如此（7 子技能容器），不处理 |

### 遗留提案处置（proposal-audit）

| 提案 | 状态 | 处置建议 |
|------|------|----------|
| P18-THIN-COMMAND-SLIMMING | Proposed | **defer** — 季度窗口评估命令瘦身（thin-command 门禁为 warning 非 error） |
| P19-EXPLORE-SKILLS-RELATIONSHIP | Proposed | **defer** — 先做 Option B 职责澄清（改动小），季度评估是否升级合并 |
| P20-HOTFIX-TEST-DOC-GUARDRAILS | Implemented | ✅ 已实施（2026-08-13）：校验器豁免 + 空单元格自动填充 + 模板/SKILL 说明，见 `reports/P20-HOTFIX-TEST-DOC-GUARDRAILS.md` |

---

## 5. Fix Actions & Suggestions（修复动作与建议清单）

### 本次已执行

| # | 动作 | 类型 | 状态 |
|---|------|------|------|
| A1 | metrics snapshot 命名对齐约定：`maintain-weekly.json` → `maintain-2026-08-13.json` | L1 | ✅ 已执行 |
| A2 | proposal-audit `--refresh-index`：`reports/PROPOSALS.md` 刷新为 16 proposals | L1 | ✅ 已执行 |
| A3 | S-A：10 项 P16 守卫英文注释改中文注释（`output.py:148-153`、`selection.py:73-76`） | L1 | ✅ 已执行（warning 35→25） |
| A4 | S-B：`skills/idea-build/idea-mcp.py` docstring 死链更正为 `skills/idea-build/SKILL.md` | L1 | ✅ 已执行 |
| A5 | 新报告登记 `reports/README.md` 维护报告索引（消除 check.py not-registered warning） | L1 | ✅ 已执行 |

### 已闭环（无待确认 L1 修复）

### 结构性建议（仅输出，走 OPERATIONS §11/§12，不直接实施）

| # | 建议 | 提案 |
|---|------|------|
| S1 | 季度评估 aic-apply/aic-explore 命令瘦身 | P18 |
| S2 | explore vs explore-codebase 职责澄清（Option B）→ 季度评估合并 | P19 |
| S3 | hotfix-test-doc 发布链护栏增强 | **P20（Implemented 2026-08-13）** |

---

## 6. 结论

系统整体健康（**86/100**，较 08-08 的 87 微降）：lint/path/门禁/proposal 全绿（0 BLOCKER/ERROR），workflow 八段结构、registry 极简（A1 未复发）、引用链与 Preconditions/Next 链闭合，junction 链接健康（target `D:\workspace\project-resources` 实测可访问），契约与 OPERATIONS 文档一致，状态卫生经 P16 治理后引用合法。

本周期（08-08→08-13）无 ai-system 核心层结构性变化：仅 RFC +1、语言债 +10（P16 守卫引入的英文注释，已修复 F1）、死链 docstring 已修复（F2）。P20（extensions 工具链护栏）已实施闭环；P18/P19 季度评审。

---

**Modified Files**: `cli/services/wizard/output.py`（A3 注释中文化）、`cli/services/wizard/selection.py`（A3 注释中文化）、`skills/idea-build/idea-mcp.py`（A4 死链更正）、`reports/README.md`（A5 索引登记）、`reports/PROPOSALS.md`（A2 刷新 + P20 状态）、`reports/P20-HOTFIX-TEST-DOC-GUARDRAILS.md`（Implemented）、`metrics/maintain-weekly.json`（重命名为 `maintain-2026-08-13.json`）；extension 层（P20 实施）：`extensions/hotfix-test-doc/scripts/validate_hotfix_doc.py`、`extensions/confluence-markdown-publisher/scripts/publish_markdown_to_confluence.py`、`extensions/hotfix-test-doc/template_content.md`、`extensions/hotfix-test-doc/SKILL.md`
**New Files**: `reports/MAINTENANCE-2026-08-13.md`、`metrics/maintain-2026-08-13.json`
**Validation**: repo-lint 0 BLOCKER / 0 ERROR / **25 WARNING**（35→25）；check.py exit 0；path-audit BROKEN 0；proposal-audit GATE ERROR 0 / WARNING 0 / 遗留 2；P20 校验器回归 VALIDATION OK（接口路径 `{}` + `{test_report_link}` 字面量不再误报，真实 `{title}` 仍阻断）；`build_html_storage_body` 空单元格补齐 `<br />` 单测通过
**Deviations**: A3/A4/A5 为经用户确认后的 L1 修复批次（对应 S-A/S-B 及报告索引登记）；P20 为经用户确认后的实施（extensions 层，Option A）
**Risks**: P18/P19 为待处置提案；`skills/idea-build/idea-mcp.py` 的 `--files` 增量编译未提交改动（F3）待用户决定提交或还原
**Next Recommendation**: P18/P19 季度评审；下次维护 2026-08-20（weekly）
