# Maintenance Report — 2026-08-06

**Mode**: monthly
**Scope**: ai-system + workflow system（架构评审 / 能力矩阵 / 生命周期 / 演进建议 + 治理一致性抽查）
**Date**: 2026-08-06
**Environment**: `D:\workspace\ai-workspace`（Windows, git branch `main`）

---

## 1. Tool Check Results（工具校验）

| Tool | Result | Detail |
|------|--------|--------|
| repo-lint.py | ✅ PASS | BLOCKER 0 / ERROR 0 / WARNING 9（与 08-01 一致，无新增） |
| repo-metrics.py | ✅ PASS | snapshot 已存 `metrics/maintain-2026-08-06.json` |
| path-audit.py | ✅ PASS | files=142, refs=511, placeholders=75, known_debt=3, **BROKEN 0** |
| check.py（完整性门禁） | ✅ PASS（exit 0） | 14 workflows / 13 commands；1 warning（reports/ 有 2 个未关闭 action item，见 §4） |
| proposal-audit.py | ✅ PASS | GATE ERROR 0 / WARNING 0；4 提案全部 Implemented；索引已 `--refresh-index` 刷新 |

### repo-lint 9 warnings（与上次完全一致，均为既有项）

- 4× `skill.md > 80 行但无 workflow.md`：agent-debug-diagnosis、contract-maintainer、java-maven、review
- 5× 技能内 Maven 命令引用：bugfix×2、mock-test×3

### 指标对比（vs `metrics/maintain-2026-08-05.json`）

| Metric | 08-05 | 08-06 | Δ |
|--------|-------|-------|---|
| Skills | 26 | 26 | 0 |
| Workflows | 14 | 14 | 0 |
| RFCs | 12 | 12 | 0 |
| Governance | 55 | 56 | +1 |
| Templates | 19 | 21 | +2 |
| Frontmatter | 25 valid / 1 missing | 25 valid / 1 missing | 0 |

> governance +1（proposal-policy.md 等）、templates +2 对应 08-05~08-06 的提案索引/门禁与 skill-launch 相关工作，增长合理。

---

## 2. Monthly Inspection（月度巡检）

### 2.1 Architecture Review（架构评审）— ✅ PASS

| Check | Result |
|-------|--------|
| 顶层目录与 AI_DEVELOPMENT_CONTRACT 一致（cli/workflows/templates/loaders/skills/config/governance/rfc/tools/reports/metrics/logs/archived） | ✅ 13 目录全部存在，零多余 |
| 无新增顶层目录（契约约束） | ✅ 未违反 |
| 层结构：workflow 声明契约、runtime 承载生命周期 | ✅ 一致 |
| 引用完整性（governance/loaders/prompts/commands 范围内） | ✅ 0 broken（75 个文件、511 引用） |

架构稳定，无需重构。依赖图存在 3 个既有环（见 §5 建议 S3），均为 skill 层引用关系，非架构层问题。

### 2.2 Capability Matrix（能力矩阵）

| 能力 | 主属技能 | 他处出现 | 评估 |
|------|----------|----------|------|
| Maven 执行 | java-maven | bugfix、mock-test（命令示例引用） | ⚠️ 轻微重复（既有 lint warning，参考示例性质，低优先级） |
| Mockito 测试 | mock-test | bugfix | 部分重复，可接受 |
| 代码评审 | review | review-changes、review workflow | 归属正确 |
| 技能优化 | skill-optimizer | iterative-optimizer（编排层） | 归属正确 |
| 契约维护 | contract-maintainer | — | 归属正确 |
| 架构设计 | architecture/（7 个子技能容器） | 由 spec/prepare/review 等 workflow 按阶段调用 | 归属正确（skills/README.md 登记完整） |

无能力无主。唯一重复信号仍是 lint 已暴露的 Maven 命令引用，无需新增治理。

### 2.3 Lifecycle Report（生命周期）

| Stage | Assets |
|-------|--------|
| Active | 26 技能（含 architecture/ 容器 7 子技能）+ 14 workflows + 13 commands |
| Deprecated | 无新增 |
| Archived | `refactor-safely` **已归档** ✅（08-01 报告建议项已闭环，现位于 `archived/skills/refactor-safely`） |

### 2.4 Evolution Suggestions（演进建议）

1. **拆分超大技能**（RFC-0002 ≤1000 行预算，持续超标项）：skill-optimizer 9552 / implement 2375 / agent-debug-diagnosis 1777 / iterative-optimizer 1392 / mock-test 1325 / bugfix 1314 / repository-maintainer 1117。建议下季度评估向 playbooks/ 抽取。
2. **处理 `.aic-state.yaml` 陈旧引用**（见 §3.6，中优先级）。
3. **破环 3 个依赖环**（review↔review-changes、outcome↔skill-benchmark、skill↔routing-benchmark）：需确认是否为有意互引，若是应转为单向依赖（分析期记录，不动手）。
4. **清理根目录 `nul` 空文件**（0 字节，Windows 保留名误创建产物）。
5. **metrics 口径确认**：skills 计数 26（metrics 与 lint 现一致，08-01 的 27/26 差异已消除）✅。

---

## 3. Governance Consistency Spot Check（一致性抽查）

| # | 检查项 | 结果 | 说明 |
|---|--------|------|------|
| 3.1 | workflows/*.md 八段结构 | ✅ PASS | 14 个 workflow 全部 8 段齐全、顺序正确（Purpose→Runtime→Preconditions→Inputs→Context→Outputs→Exit Criteria→Next）；review.md 仅在 Purpose 后插入允许的 When to Use |
| 3.2 | 术语与 README 词汇表一致 | ✅ PASS | 全部使用词汇表术语与身份字段约定（Project ID / Task ID / Change ID 等） |
| 3.3 | Runtime 引用文件存在 | ✅ PASS | 14 个 `templates/runtime/runtime-{name}.md` 全部存在；`runtime-base.md` 无 workflow 引用（孤儿，信息项） |
| 3.4 | Preconditions/Next 链闭合 | ✅ PASS | Next 目标均存在；release→deployment 为文档明示的集外引用 |
| 3.5 | config/workflows/*.yaml 极简性 | ✅ PASS | 14 个文件顶层键仅 `version/name/workflow/runtime`，无 inputs/outputs/next 回潮（A1 未复发） |
| 3.6 | yaml↔md 一一对应 | ✅ PASS | 14 yaml ↔ 14 md，命名一致；仅 workflows/README.md 为文档 |
| 3.7 | 引用路径存在（standards/loaders/prompts/commands） | ✅ PASS | 范围内 0 broken；范围外发现 3 处死链（见 §4-F2） |
| 3.8 | Link health | ✅ PASS | `projects/` 为 Junction → `D:\workspace\project-resources`，可访问（约 100 个仓库）；`worktrees/` 为普通目录（git worktree 根，非 junction，正常） |
| 3.9 | Doc-vs-reality：AGENTS.md | ⚠️ 微偏差 | 9 个目录图全部在盘；但根目录 `extensions/`（8 个插件子目录）未在图示与运营表中登记；`nul` 空文件亦未登记 |
| 3.10 | Doc-vs-reality：AI_DEVELOPMENT_CONTRACT | ✅ PASS | 契约 13 目录与实测完全一致，契约"不新增顶层目录"规则成立 |
| 3.11 | State hygiene（.aic-state.yaml） | ❌ FAIL | `last_project: pywechat-live-2608` → 工作区 `workspaces/pywechat-live-2608/` 存在，但业务仓库 `projects/pywechat-live-2608` 在 junction 目标中**不存在**（陈旧引用） |
| 3.12 | Proposal 遗留评估 | ⚠️ 2 项 | 见 §4 |

---

## 4. Findings & Proposal Leftovers（发现与提案遗留处置）

### 按严重度分级

| 级别 | 编号 | 发现 | 处置建议 |
|------|------|------|----------|
| WARN | F1 | `.aic-state.yaml` 引用 `projects/pywechat-live-2608`，仓库已不在 junction 目标中 | **建议修复**（结构性变更：删除/更新 state 引用，需确认） |
| WARN | F2 | 3 处死链：`rfc/ADR-0002`→`playbooks/maven.md`、`rfc/RFC-0001`→`playbooks/reflection-test-utils.md`（playbooks/ 目录不存在）、`reports/MAINTENANCE-2026-08-06-method-comment-convention.md:18`→`governance/workflows/bugfix.md`（实为 `workflows/bugfix.md`） | **建议修复**（文档级小修：RFC 引用标注"规划中"或改链；report 改路径） |
| WARN | F3 | 依赖环 3 个（review↔review-changes、outcome↔skill-benchmark、skill↔routing-benchmark） | 记录，待确认意图后转为单向 |
| INFO | F4 | 根目录 `nul` 空文件（0 字节，Windows 保留名产物） | 建议删除（一次性清理） |
| INFO | F5 | AGENTS.md 未登记 `extensions/` 与 `nul` | 建议补登记（文档小修） |
| INFO | F6 | `runtime-base.md` 无 workflow 引用（孤儿模板） | 记录，季度评估是否归档 |
| INFO | F7 | lint 9 warnings 与技能超限（≥1000 行）持续 | 季度拆分计划跟踪（S1） |

### 遗留提案处置（proposal-audit 2 项）

| 来源 | 遗留项 | 处置 |
|------|--------|------|
| `MAINTENANCE-2026-08-06-live-facade-snapshot-risk.md:44` | 跨服务 SNAPSHOT 治理纪律（建议纳入治理文档，待确认） | **defer（暂缓）**：短期决策已闭环（发灰度统一 RELEASE，2026-08-06 已确认）；治理文档增补属 governance 修改，走 §11/§12 变更流程，建议下月重新评估 |
| `MAINTENANCE-2026-08-06-method-comment-convention.md:73` | P1/P2/P3：方法行数标准统一（≤80）、私有方法注释要求、bugfix 流程挂接 | **propose（待审）**：P1/P2/P3 均修改 governance 标准与 bugfix 流程（L3 契约级），需按 OPERATIONS §12 变更流程评审批准后实施；期间 80 行实践已落地 |

---

## 5. Fix Actions & Suggestions（修复动作与建议清单）

### 本次已确认并执行的修复（2026-08-06 已实施）

| # | 动作 | 状态 |
|---|------|------|
| A1 | 修复 `MAINTENANCE-2026-08-06-method-comment-convention.md:18-19` 两处死链（`governance/workflows/bugfix.md` → `workflows/bugfix.md`、`governance/skills/bugfix/SKILL.md` → `skills/bugfix/SKILL.md`） | ✅ 已修复 |
| A2 | AGENTS.md 运营表补登记 `extensions/` | ✅ 已修复 |
| A3 | 删除根目录 0 字节 `nul` 空文件（Windows 保留名，经 `\\?\` 路径删除） | ✅ 已修复 |
| A4 | 清空 `.aic-state.yaml` 陈旧引用（`last_project: null`, `projects: {}`） | ✅ 已修复 |
| A5 | 两个遗留 action item 已关闭并标注处置：live-facade-snapshot-risk → **defer**；method-comment-convention → **propose** | ✅ 已关闭 |
| S2 | RFC-0001 / ADR-0002 中 `playbooks/` 引用标注"规划中"（forward reference） | ✅ 已标注 |

> 结构性建议 S1（拆分超大技能）、S3（破依赖环）、S4（SNAPSHOT 治理）保持建议状态，走 OPERATIONS §11/§12 变更流程，未直接实施。
>
> **S1 进展（2026-08-06）**：已完成 Analyze → 撰写并登记提案 `P10-SKILL-OPTIMIZER-SPLIT.md`（Status: Proposed，已入 PROPOSALS.md 索引）。分析结论：现行 RFC-0002 单文件门禁下，仅 skill-optimizer 的 3 个脚本文件超限（main.py 1240 / main_parallel.py 1125 / diff_viewer.py 1164），且 main.py 与 main_parallel.py 为近重复双入口；其余 6 个技能无单文件超限（md 聚合合规）。提案含拆分 + 去重方案（Option A）与 repo-lint 扩展名盲区修复（.py/.cjs/.sh 纳入检查）。**待 Review → Approve 后实施**。

| # | 动作 | 类型 |
|---|------|------|
| A1 | 修复 `reports/MAINTENANCE-2026-08-06-method-comment-convention.md:18-19` 两处死链：`governance/workflows/bugfix.md` → `workflows/bugfix.md`、`governance/skills/bugfix/SKILL.md` → `skills/bugfix/SKILL.md`（均已核实不存在） | L1 文档小修 |
| A2 | AGENTS.md 补登记 `extensions/` 目录（运营表） | L1 文档小修 |
| A3 | 删除根目录 0 字节 `nul` 空文件 | L1 清理 |
| A4 | 更新 `.aic-state.yaml` 的陈旧 `last_project` 引用 | L2 需确认（涉及运行状态） |
| A5 | 关闭 proposal-audit 遗留项追踪：在报告中标注处置（defer / propose） | L1 记录 |

### 结构性建议（仅输出建议，走 §11 变更流程：Analyze → Propose → Review → Approve）

| # | 建议 | 目标 |
|---|------|------|
| S1 | 拆分 skill-optimizer（9552 行）等超大技能，向 playbooks/ 抽取 | RFC-0002 预算合规 |
| S2 | RFC 中 playbooks/ 引用标注"规划中"状态，避免死链误判 | 链接卫生 |
| S3 | 确认并破除 3 个依赖环 | 依赖图清洁 |
| S4 | 跨服务 SNAPSHOT 治理纪律纳入 governance（下月评估） | 供应链纪律 |

---

## 6. 结论

系统整体健康：lint/路径/门禁全绿，架构与契约一致，workflow 与 registry 极简、链闭合，无回归。本周期（08-01→08-06）演进聚焦 skill-launch / 提案索引门禁，均正常落地；08-01 建议的 `refactor-safely` 归档已闭环。

需跟进 2 项：`.aic-state.yaml` 陈旧引用（F1）、3 处文档死链（F2）。其余为记录与季度建议。

---
**Modified Files**: `reports/MAINTENANCE-2026-08-06-method-comment-convention.md`（死链修复+遗留关闭）、`reports/MAINTENANCE-2026-08-06-live-facade-snapshot-risk.md`（遗留关闭）、`../AGENTS.md`（补登记 extensions/）、`../workspaces/.aic-state.yaml`（清空陈旧引用）、`rfc/ADR-0002-playbook-architecture.md`（playbooks 规划中标注）、`rfc/RFC-0001-repository-architecture.md`（playbooks 规划中标注）
**New Files**: `reports/MAINTENANCE-2026-08-06.md`、`metrics/maintain-2026-08-06.json`
**Validation**: repo-lint 0/0/9、path-audit 0 broken、check.py exit 0、proposal-audit 0 gate errors
**Deviations**: 无
**Risks**: `.aic-state.yaml` 若长期不更新，后续 maintain/develop 可能复用陈旧项目上下文
**Next Recommendation**: 确认 A1–A5 修复批次；下月评估 S4（SNAPSHOT 治理）与季度拆分计划 S1
