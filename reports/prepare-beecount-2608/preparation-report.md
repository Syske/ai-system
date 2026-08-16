# Preparation Report — beecount-2608

Change ID: beecount-2608
Runtime: Prepare
Date: 2026-08-12
Locale: zh

---

## 1. 执行摘要

已为 BeeCount 二次开发（FR-01 保存并新建 / FR-02 离线记账慢）完成完整实现上下文构建：需求收集、仓库克隆与分析、架构分析、依赖/影响/风险评估。

**核心发现（与 CR 假设不符，已在用户确认下修正方向）**：
- FR-02 真实根因**不是**"同步阻塞本地写入"——同步已是 fire-and-forget 异步。
- 真实阻塞点：保存后 `await TxAuthorService.markCreated/markEdited` → `cloud.auth.currentUser`（无超时 HTTP），离线 + token 过期时挂起到 OS TCP 超时（最长约 2 分钟）。
- 用户确认：按"修真实根因"方向（去阻塞 + 加超时 + 在线门控），不做 CR 原方案的同步队列改造。
- FR-01 保存并新建的交互细节（清空范围/金额聚焦/是否留页）留待 Spec 阶段细化。

## 2. 仓库状态

- 客户端源码已克隆：`/home/syske/net-workspace/workspace/projects/BeeCount`，分支 `task/beecount-2608`（upstream `main` @ `70c800b`）。
- 云端仅部署配置（`docker/beecount-cloud/`），源码未克隆（服务端无需改动）。
- 现有部署：群晖 NAS Docker，端口 8869，SQLite `./data`。

## 3. 关键文件定位

| 关注点 | 位置 |
| :--- | :--- |
| 记账表单 / 保存按钮 | `lib/widgets/biz/amount_editor_sheet.dart`（doneKey @1057，onTap @1073，onSubmit @1108） |
| 保存回调 | `lib/pages/transaction/transaction_editor_page.dart:260`（pop @407-408） |
| 转账表单 | `lib/widgets/transaction/transfer_form.dart` |
| ★ FR-02 阻塞点 | `lib/services/data/tx_author_service.dart:42` → `packages/flutter_cloud_sync/.../beecount_cloud_provider.dart`（`_httpClient.send` @1818/3336，无超时） |
| 同步触发（已异步） | `lib/services/billing/post_processor.dart:107`；`lib/cloud/sync/sync_coordinator.dart`；`lib/cloud/sync/sync_engine_realtime.dart` |
| 在线状态信号 | `lib/providers/sync_providers.dart:340-353`（connectivity_plus） |
| 同步引擎入口 | `lib/cloud/sync/sync_engine.dart:371` |
| 明暗主题 | `lib/styles/tokens.dart`（BeeTokens） |

## 4. 产出清单

- requirement-summary.md
- repository-summary.md
- architecture-summary.md
- dependency-report.md
- impact-report.md
- risk-report.md
- 本报告

## 5. 待 Spec 阶段确认项

1. FR-01：保存并新建交互细节（按钮位置、清空范围、金额聚焦机制、转账 tab 行为、四语言文案）。
2. FR-02：请求超时值（建议 3-5s）、在线门控信号源（connectivity_plus vs WS 状态）、refresh 冷却、是否配置开关及开关名。
3. 是否新增离线 author 补回填机制。
4. 测试新增清单（TxAuthorService / 保存流程 / 超时 / 离线门控）。

## 6. 结论

Readiness: **Ready for Specification**
Next Runtime: **Specification Runtime**
