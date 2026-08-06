# Reports Index

集中索引 `reports/` 下所有分析、维护、提案、迁移与规范文档，便于查找与跟进待办。

- 每项一行：类型 / 主题 / 日期 / 文件 / 遗留待办。
- 提案（P 系列）状态与门禁见 `PROPOSALS.md`（proposal-audit 维护，勿手工改状态）。
- 新报告入目录即登记；本文件不参与 proposal-audit 门禁。

---

## 提案（P 系列）

状态与门禁见 [PROPOSALS.md](PROPOSALS.md)，此处仅列主题索引：

| 提案 | 主题 | 日期 |
|------|------|------|
| P6 | Skill Size Reconciliation | 2026-08-01 |
| P7 | `aic-workflow` Authoring Command | 2026-08-05 |
| P8 | `aic-command` Authoring Command | 2026-08-05 |
| P9 | `aic-skill-launch` Skill Launcher | 2026-08-05 |
| P10 | skill-optimizer 脚本拆分（超限文件 + 双入口去重） | 2026-08-06 |
| P11 | skill-optimizer 网络思想吸收（held-out 门控/demo-augment/description 调优） | 2026-08-06 |
| P12 | 移除 langchain 依赖（openai SDK 直调） | 2026-08-06 |
| P13 | 破除 3 个 Skill 依赖环（检测器语义分层） | 2026-08-06 |
| P14 | 跨服务 SNAPSHOT 治理纪律（S4） | 2026-08-06 |
| P15 | 多-SKILL.md 输入防护（E3 缺陷修复） | 2026-08-06 |

---

## 维护报告（MAINTENANCE）

| 日期 | 模式 | 范围 | 文件 | 遗留待办 |
|------|------|------|------|----------|
| 2026-07-22 | weekly | 首次全量巡检 + release.md 评估 | `MAINTENANCE-20260722.md` | — |
| 2026-08-01 | monthly | 结构/能力/生命周期/演进 | `MAINTENANCE-20260801.md` | — |
| 2026-08-05 | on-demand | aic-sync 同步核查 | `MAINTENANCE-2026-08-05.md` | — |
| 2026-08-06 | monthly | 架构/能力矩阵/一致性抽查 + 修复批次 | `MAINTENANCE-2026-08-06.md` | —（S1-S4 已闭环） |
| 2026-08-06 | on-demand | aic-sync 复查 | `MAINTENANCE-2026-08-06-aic-sync.md` | — |
| 2026-08-06 | on-demand | live-facade SNAPSHOT 风险 | `MAINTENANCE-2026-08-06-live-facade-snapshot-risk.md` | —（P14 已闭环） |
| 2026-08-06 | on-demand | 方法长度与注释约定 | `MAINTENANCE-2026-08-06-method-comment-convention.md` | P1/P2/P3 → propose（见 P11 记录） |

---

## 评估与评审报告

| 类型 | 主题 | 日期 | 文件 | 遗留待办 |
|------|------|------|------|----------|
| Quarterly | 季度评估（E9） | 2026-08-06 | `QUARTERLY-REVIEW-2026-08-06.md` | Q4/Q5 下季度 |
| Assessment | CLI 规范化评估 | 2026-08-06 | `CLI-STANDARDIZATION-ASSESSMENT.md` | **C1 待办（明日执行）→ C2/C3/C4** |
| Assessment | 架构评估 | 2026-07 | `ARCHITECTURE-ASSESSMENT-2026-07.md` | — |
| Assessment | 三方 Skill 参考价值 | 2026-08-01 | `THIRD-PARTY-SKILL-ASSESSMENT-2026-08-01.md` | — |
| Review | Workflow 层优化 | 2026-07 | `WORKFLOW-OPTIMIZATION-REPORT-2026-07.md` | — |
| Report | Repository Optimization | — | `REPOSITORY-OPTIMIZATION-REPORT.md` | — |
| Report | Repository Architecture v2 | — | `REPOSITORY-ARCHITECTURE-REPORT-v2.md` | — |
| Review | 架构评审 | 2026-07 | `architecture-review-2026-07.md` | — |

---

## 规范速查

| 主题 | 文件 | 说明 |
|------|------|------|
| AI-System 扩展规范（命名/流程/命令） | `EXTENSION-STANDARDS.md` | 新增资产前的权威速查（Golden Rule） |

---

## 迁移（MIGRATION）

| 主题 | 文件 | 状态 |
|------|------|------|
| AI System Repository Migration Plan v2 | `MIGRATION-PLAN-v2.md` | — |
| AI System Repository Migration Report v1 | `MIGRATION-REPORT-v1.md` | — |

---

## 结构分析目录（analysis-*）

各目录含 `analysis-report.md` / `consistency-report.md` / `dependency-report.md` / `recommendations.md`：

| 目录 | 主题 | 日期 |
|------|------|------|
| `analysis-2026-08-01-structure-governance/` | governance 结构分析 | 2026-08-01 |
| `analysis-2026-08-01-workflows-structure/` | workflows 结构分析 | 2026-08-01 |
| `analysis-2026-08-03-structure-workflows/` | workflows 结构复查 | 2026-08-03 |

---

## 维护纪律

- 新增 `MAINTENANCE-*` / `P*` 报告：登记上方对应表（proposal-audit 自动扫门禁）。
- 新增评估/规范/迁移文档：登记对应表。
- 遗留待办列有内容的报告，在下一次维护/评估中优先跟进；闭环后更新该列。
