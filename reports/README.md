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
| [P6](P6-SKILL-SIZE-PROPOSAL.md) | Skill Size Reconciliation | 2026-08-01 |
| [P7](P7-WORKFLOW-AUTHOR-COMMAND.md) | `aic-workflow` Authoring Command | 2026-08-05 |
| [P8](P8-COMMAND-AUTHOR.md) | `aic-command` Authoring Command | 2026-08-05 |
| [P9](P9-SKILL-LAUNCHER.md) | `aic-skill-launch` Skill Launcher | 2026-08-05 |
| [P10](P10-SKILL-OPTIMIZER-SPLIT.md) | skill-optimizer 脚本拆分（超限文件 + 双入口去重） | 2026-08-06 |
| [P11](P11-SKILL-OPTIMIZER-ABSORPTION.md) | skill-optimizer 网络思想吸收（held-out 门控/demo-augment/description 调优） | 2026-08-06 |
| [P12](P12-LANGCHAIN-REMOVAL.md) | 移除 langchain 依赖（openai SDK 直调） | 2026-08-06 |
| [P13](P13-DEPENDENCY-CYCLE-CLEANUP.md) | 破除 3 个 Skill 依赖环（检测器语义分层） | 2026-08-06 |
| [P14](P14-SNAPSHOT-GOVERNANCE.md) | 跨服务 SNAPSHOT 治理纪律（S4） | 2026-08-06 |
| [P15](P15-MULTISKILL-GUARD.md) | 多-SKILL.md 输入防护（E3 缺陷修复） | 2026-08-06 |
| [P16](P16-STATE-WRITE-GUARD.md) | wizard 状态写入增加项目存在性校验（S2 根因修复） | 2026-08-08 |
| [P17](P17-MAVEN-DELEGATION-GOVERNANCE.md) | java-maven 委派规范（D1 根治） | 2026-08-08 |
| [P18](P18-THIN-COMMAND-SLIMMING.md) | aic-apply / aic-explore 命令瘦身（thin-command 门禁） | 2026-08-08 |
| [P19](P19-EXPLORE-SKILLS-RELATIONSHIP.md) | explore 与 explore-codebase 技能关系澄清（季度评估合并） | 2026-08-08 |
| [P20](P20-HOTFIX-TEST-DOC-GUARDRAILS.md) | hotfix-test-doc 发布链护栏增强（校验误报 + 空单元格自动修复） | 2026-08-11 |
| [P21](P21-HOTFIX-TEST-DOC-RENDER-FIX.md) | hotfix-test-doc 模板标题渲染缺陷修复与回填工具 | 2026-08-12 |
| [P22](P22-WSL-ENVIRONMENT-INTEGRATION.md) | WSL 环境集成与初始化能力 | 2026-08-14 |
| [P24](P24-PROVIDER-CONTRACT-TEST-FIX.md) | Provider Wizard 契约测试夹具修复（win32 平台 check.py 回归，已实施 exit 0） | 2026-08-17 |

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
| 2026-08-08 | weekly | 工具校验/周度巡检/一致性抽查 + 修复批次 A1-A4 | `MAINTENANCE-2026-08-08.md` | F1-F3 已修复（A1-A4 已闭环） |
| 2026-08-13 | weekly | 工具校验/周度巡检/一致性抽查 + 修复批次 S-A/S-B | `MAINTENANCE-2026-08-13.md` | F1-F2 已修复（S-A/S-B 已执行）；P18/P19 已闭环(2026-08-14)；P20 遗留 |
| 2026-08-13 | on-demand | extensions 域巡检（Scope=extensions） | `EXTENSIONS-MAINTENANCE-2026-08-13.md` | F1: 6 个 OPTIMIZATION_LOG 空模板待补录 |
| 2026-08-14 | on-demand | 巡检当前提案 + 治理一致性抽查 | `MAINTENANCE-2026-08-14.md` | P22 已 approve（阶段二 defer 至新提案）；F2/F3 已修复 |
| 2026-08-14 | on-demand | 跨平台治理落地（P23 批次：gitattributes/hook/lint） | `P23-CROSS-PLATFORM-MAINTENANCE-GOVERNANCE.md` | —（P23 已 Implemented） |
| 2026-08-17 | on-demand | 工具校验/周度巡检/一致性抽查 | `MAINTENANCE-2026-08-17.md` | R1: check.py 回归（FakeWizard 缺 projects_root）→ 已立提案 P24 待评审；其余全 PASS |

---

## 评估与评审报告

| 类型 | 主题 | 日期 | 文件 | 遗留待办 |
|------|------|------|------|----------|
| Quarterly | 季度评估（E9） | 2026-08-06 | `QUARTERLY-REVIEW-2026-08-06.md` | Q4/Q5 下季度 |
| Assessment | CLI 规范化评估 | 2026-08-06 | `CLI-STANDARDIZATION-ASSESSMENT.md` | **C1 待办（明日执行）→ C2/C3/C4** |
| Assessment | bugfix skill 优化评估 | 2026-08-08 | `BUGFIX-SKILL-ASSESSMENT-2026-08-08.md` | — |
| Maintenance | 语言检查存量债登记 | 2026-08-08 | `MAINTENANCE-2026-08-08-language-lint-debt.md` | #1-3 参数说明可接受 / #4 顺手修 / #5-7 memory 翻译待办 |
| Maintenance | aic 项目识别与状态记录修复 | 2026-08-08 | `MAINTENANCE-2026-08-08-aic-project-recognition.md` | workspace.yaml 初始化未自动化 |
| Assessment | 上下文/注意力/架构缺口评估+修复 | 2026-08-08 | `GAP-ASSESSMENT-2026-08-08-context-attention-architecture.md` | memory 沉淀/跨会话状态持久化遗留(已闭环于 skills) |
| Assessment | ADR-0009 合规性系统诊断 | 2026-08-13 | `ADR-0009-COMPLIANCE-DIAGNOSIS-2026-08-13.md` | **P1 standards/cool 迁移待评审；P2 废弃命令待清理** |
| Assessment | Token 缓存命中率优化 | 2026-08-13 | `CACHE-OPTIMIZATION-2026-08-13.md` | **R1 骨架化 agent 读取待实测；R2 实际命中率待验证；R3 强制全量开关待实现** |
| Daily | 日终报告 | 2026-08-08 | `DAILY-2026-08-08.md` | — |
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
