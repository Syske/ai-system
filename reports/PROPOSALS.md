# Proposals Index

集中索引 ai-system 的所有变更提案（`reports/P*.md`），便于查看与确认。

- 每行一个提案：状态 / 主题 / 创建日期 / 文件。
- 状态定义见 `governance/policies/proposal-policy.md`（Proposed / Approved / Rejected / Implemented / Archived）。
- 维护：新增提案时登记一行；状态变更时同步更新本表 + 提案文件 Status 字段。
- 门禁：`python tools/proposal-audit.py` 校验本表与提案文件 Status 一致性、遗留项清单。

---

## 提案清单

| 状态 | 提案 | 创建 | 文件 |
|---|---|---|---|
| Implemented | Skill Size Reconciliation | 2026-08-01 | `P6-SKILL-SIZE-PROPOSAL.md` |
| Implemented | `aic-workflow` Authoring Command | 2026-08-05 | `P7-WORKFLOW-AUTHOR-COMMAND.md` |
| Implemented | `aic-command` Authoring Command | 2026-08-05 | `P8-COMMAND-AUTHOR.md` |
| Implemented | `aic-skill-launch` Skill Launcher | 2026-08-05 | `P9-SKILL-LAUNCHER.md` |

## 当前遗留（未关闭）

由 `python tools/proposal-audit.py` 生成：

<!-- proposal-audit 结果会在此区更新；不要手工维护本段 -->
