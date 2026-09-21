# 系统巡检报告 — 2026-09-21（weekly）

- 类型: 系统巡检（MAINTENANCE）
- 模式: weekly
- 日期: 2026-09-21
- 排期: 补做计划内周检（`next_maintenance: 2026-09-16`，逾期 5 天，本次经用户授权执行）
- 同日报表关系: 本日另有一份 on-demand 专项报告 `MAINTENANCE-2026-09-21.md`（scan/service 选择专项 +
  Tier 1/Tier 2 批次）。**本报告聚焦周度专项产物（duplication / dependency graph / orphan /
  health score）与跨项收口**，不重复前报告内容。

---

## 一、工具校验结果（自动生成，AI 核对补充说明）

| 工具 | 结果 |
|---|---|
| quick-check | verdict **OK**（findings 0） |
| lint | Skills: 32 (Files: 32) | BLOCKERS: 0 | ERRORS: 0 | WARNINGS: 28 |
| path | OK: no broken path dependencies |
| extensions | Summary: 0 errors, 0 warnings |
| check.py | **PASS**（2 WARN：开放提案 P42/P46 + 4 open action items——均为已知开放项） |
| unittest | 325 OK |
| workflow-command-audit | 0 blocker / 0 warning（15 workflows、13 commands） |
| check-contract（pre-commit 子集） | exit 0（registry / outputs / frontmatter 一致） |

### 指标对比（AI 核对变化原因）

上期 = `metrics/maintain-2026-09-17.json`；本期 = `metrics/maintain-2026-09-21.json`（本次周检快照）。

| 指标 | 上期 | 本期 | 变化 |
|---|---|---|---|
| Skills（repo-metrics 口径，含 `architecture` 容器） | 30 | 33 | +3 |
| Skills（repo-lint 口径 = SKILL.md 文件数） | — | 32 | 口径差异见 09-09 发现-6（容器目录不带 SKILL.md） |
| Workflows | 15 | 15 | = |
| RFC | 14 | 14 | = |
| Governance | 59 | 60 | +1 |
| Templates | 22 | 24 | +2 |
| 技能平均行数 | 494 | 478 | −16（复杂度下降） |

**变化归属（全部为已记录的有意变更，无未授权增长）**：

- Skills +3：09-17 `a2c36a9` methodologies 迁移迁入 `spec-updater` / `openspec-archive-change` /
  `openspec-explore`（skills/README 7→10，含决策依据与引用清理记录）。
- Governance +1：`governance/standards/common/evidence-levels.md`（09-17 后新增）。
- Templates +2：`templates/prompts/tasks-template.md`（09-17 迁移）；`templates/README.md`
  （09-21 P59 模板层作者纪律）。
- lint WARN 26（09-09）→ 28：**全部为「无 workflow.md」类**（+3 迁移技能 / −1 09-10 归档
  `apply-openspec`），**非质量回归**（英文注释类 12 条、Maven 字面量 1 条两次完全相同）。

---

## 二、巡检发现（按严重度分级）

### 高

无。

### 中

无。

### 低

1. **`tools/maintain-report.py` 指标对比取值缺陷**（本次首度定位）。
   该工具「上期」选择逻辑遍历 `metrics/maintain-*.json` 后按 `timestamp` 比较，但
   `maintain-delta-state.json` **无 `timestamp` 字段**（空字符串参与比较且字典序最后胜出）→
   被误当作上期快照，导致上期五格全为 `?`；且「变化」列**硬编码 `=`**，从不计算真实增量。
   实际影响：历次报告该表均需 AI 手工回填（09-09 报告即如此）。
   **建议**：跳过无有效 `timestamp` 的文件（或显式排除 `*-delta-state.json`），并按取到的上期
   计算真实增量。属工具小修，待确认后实施。
2. **P26 文件内状态自相矛盾**（`reports/P26-MAIN-CHAIN-BRANCH-RULE.md`）。
   第 53 行 checkbox 已记「CI 增强 **已关闭 2026-09-09**」，但同文件「开放项」段落（约 83 行）
   仍列「CI 增强（git 分支保护，后续）——2026-08-23 maintain 巡检核验后维持 defer」。
   属单点文案漂移（不影响门禁，proposal-audit 已不将其计为 open item）。**建议**：同步该句
   （1 行小修，待确认）。

### 信息

3. **依赖图（weekly 专项）**：33 技能 / 4 层（Foundation / Test / OpenSpec / Meta）；
   真实依赖无环，层级深度 ≤4。工具标注 **3 条 doc-only 提及环**（`review↔review-changes`、
   `idea-build↔java-maven`、`explore↔explore-codebase`）——**已人工复核**：均为互相指引
   （如 review/SKILL.md「Replace `review-changes`…」与 review-changes/SKILL.md「Use `review`
   (workflow) instead when…」），非运行时依赖，**无需拆环**。
4. **孤儿资产（weekly 专项）**：**0**。技能 SKILL.md 32 个、`templates/runtime/*`、
   `templates/prompts/*`、`templates/*.md`、`loaders/*.md` 全部存在外部引用。
5. **重复度（weekly 专项）**：权威层（skills/governance/templates/loaders/config/workflows，
   199 文件）**无跨资产标题级重复**——唯一大面重合来自**八段契约强制结构**
   （Purpose→…→Next，属契约要求非重复）；**逐字重复段（≥6 行且 ≥200 字符）0 处**。
   reports/ 内部的标题重合属报告模板复用，不计为知识重复。
6. **健康评分（weekly 专项）**：15 维度逐项核对 → **通过 13 / 失败 0 / N/A 2**。
   N/A 维度为 Dim 7（Playbook Coverage）与 Dim 8（Checklist Reuse）——本工作区不存在
   `playbooks/`、`checklists/` 目录（历史引用为遗留路径）。
   按 `health.md` 固定公式 `(13/15)*100 = 86.7` 落入 DEGRADED 区间，但**扣分项全部为 N/A**，
   生效维度为 **13/13 = HEALTHY**。**建议**：在 `health.md` 明确 N/A 维度的计分口径
   （排除 N/A 或单列），避免分数误导（属标准文本变更，仅建议）。
7. **metrics frontmatter「1 missing」为计数特性**（复现 09-09 信息-6）：`skills/architecture/`
   是技能容器目录（7 个子技能各有合法 SKILL.md 与 frontmatter），自身无 SKILL.md →
   repo-metrics 据此计 missing；自 08-01 起如此，**非异常**。
8. **metrics 快照命名两口径并存**（机器级观察，仅在此备注）：本机曾出现
   `maintain-20260921.json`（YYYYMMDD）与规范 `maintain-2026-09-21.json`（YYYY-MM-DD，报告
   工具期望）并存，已归一为规范名。
9. **09-09 报告遗留项复核**：合同 `governance/contracts/AI_DEVELOPMENT_CONTRACT.md` §2 图
   **已含 `logs/`（94 行）与 `archived/`（97 行）** → 09-09 发现-1 已闭环；
   `cli/commands/aic-maintain.md` **98 行**（≤100 thin-command 门禁）→ 09-09 建议-6 已闭环。

---

## 三、一致性抽查结论（逐项通过/失败）

| 检查项 | 结果 | 说明 |
|---|---|---|
| workflows/*.md 八段齐全且顺序正确 | ✅ 通过 | **15/15** 实测 Purpose→Runtime→Preconditions→Inputs→Context→Outputs→Exit Criteria→Next 顺序一致（README 为索引不计） |
| config/workflows/*.yaml 注册表瘦身（防 A1 回潮） | ✅ 通过 | 全部仅 name/workflow/runtime；grep 无 inputs/outputs/next 键 |
| 引用路径存在（standards/loaders/prompts/cli-commands） | ✅ 通过 | path-audit 0 broken |
| 链接健康（junction/symlink） | ✅ 通过（语义已变更） | P58 后 `projects/` 为**真实目录**（8 个服务），不再是符号链接；`repositories/` 为元数据源、按需 clone（`runtime-dev-setup.md` §Repository Sourcing 已文档化） |
| 文档-现实对照（AGENTS.md / 合同图 / OPERATIONS） | ✅ 通过 | 合同 §2 图含 logs//archived/；AGENTS.md 于本日 Tier 1 已修正 docs/ 描述与非规范目录表述 |
| 状态卫生（.aic-state.yaml 引用存在性） | ✅ 通过 | 4 个项目引用全部存在于 `workspaces/` |
| 运行日志覆盖（未提交改动 vs logs/） | ✅ 通过 | ai-system 与 extensions 两仓 git **均干净**（本日 12 提交全部有诊断日志归属） |
| 提案遗留（proposal-audit + 索引） | ⚠️ 1 WARN | 0 gate error / 0 warn；开放提案 2（P42 defer 至专项会话、P46 待线上）；open action items 4（P22×2 / P26×1 / P28×1）；本报告索引本次补登 |
| 扩展域巡检（extensions-lint + 逐扩展健康） | ✅ 通过 | 0 error / 0 warning；本日 extensions 仓 13 项遗留改动已归因入库，另修敏感扫描误报；仓整洁无悬空改动 |
| 知识生命周期（2.6，logs 回收） | ✅ 通过 | 近 203 条日志核查高频主题：`check_tr5`(12)/`JDT`(9)/`memory`(13)/`脱敏`(5)/`验证标记`(2) **均已有捕获载体**（P41 已实施、JDT 门禁、本日 pre-commit memory 门禁、MEMORY_GUIDELINES、P46b）；向导「循环」主题**仅 1 次**（本日）→ 非复发、已由 P57 覆盖；无新增需捕获项 |
| 工具门禁全绿复核 | ✅ 通过 | 见第一节；唯一 2 WARN 为已知开放提案/开放项自我归因 |

---

## 四、修复动作与建议清单

| # | 类型 | 内容 | 状态 |
|---|---|---|---|
| 1 | 收尾（例行） | 本报告登记 reports/README.md 索引（proposal-policy §6，关闭自举 WARN） | ✅ 本次执行 |
| 2 | 收尾（例行） | `maintain-delta.py --record` 建立新增量基线 | ✅ 本次执行 |
| 3 | 收尾（例行） | 计划内周检补做：`maintenance.yaml` last_run=2026-09-21 / mode=weekly / next_maintenance=**2026-09-28** | ✅ 本次执行 |
| 4 | 小修（已确认并实施） | `tools/maintain-report.py` 上期快照误选 `maintain-delta-state.json` + 变化列硬编码（发现-1）→ 已修：跳过无 `timestamp` 的文件、按 timestamp 选最接近上期、**计算真实增量**；补 6 常驻测试 | ✅ 本次执行 |
| 5 | 小修（已确认并实施） | P26 开放项段落同步 CI 项已关闭文案（发现-2） | ✅ 本次执行 |
| 6 | 建议（已确认并实施） | `skills/repository-maintainer/health.md` 明确 N/A 维度计分口径：`Score = passing / (15 - N/A) * 100` | ✅ 本次执行 |
| 7 | 例行无操作 | 无新增提案、无新增知识捕获、无单点 typo/死链需就地修复 | — |
| 8 | 已闭环核查 | 09-09 遗留：合同 §2 图（已含 logs//archived/）、aic-maintain 行数门禁（98 行） | ✅ 均闭环 |

本次除例行收尾（索引 / delta 基线 / 维护态）外，就地修改 **3 处已确认小修**（修复清单 4/5/6，均经用户确认）：
`tools/maintain-report.py` 指标对比取值 + `reports/P26-MAIN-CHAIN-BRANCH-RULE.md` 文案 + 
`skills/repository-maintainer/health.md` N/A 计分口径；其余未动。

---

## 五、quick-check 趋势（自动生成）

| 日期 | verdict | findings |
|---|---|---|
| 2026-09-09 | OK | 0 |
| 2026-09-11 | OK | 0 |
| 2026-09-14 | OK | 0 |
| 2026-09-17 | OK | 0 |
| 2026-09-21 | OK | 0 |

连续 5 次快照 verdict 全 OK、findings 全 0，无回归趋势。

---

## 六、提案状态（自动生成）

- proposal-audit: **0 gate error / 0 warn** / 开放提案 **2** / open action items **4**
  - 开放: `P42-TR5-TEMPLATE-SKELETON.md`（用户确认 defer 至 tr5 专项会话，接手要点已备妥）
  - 开放: `P46-TR5-DEBT-VALIDATION-MARKER.md`（(b) 已实施 / (a) 待线上 TR5 update）
  - open action items: P22:143（交互向导常驻自动化测试）、P22:144（`repo_path_for` 数据源收口）、
    P26:52（分支扩展 provider）、P28:46（AI 可选 Change ID）
- 本日提案收口：P41 → **Implemented**（extensions `6d8a176`）；P57/P58/P59 实施；P22/P29 状态同步。