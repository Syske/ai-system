# Impact Report — beecount-2608

## 变更范围总览

两个功能均围绕记账保存链路与云同步，改动集中在客户端 app 与同步插件包，**不涉及云端服务端、数据模型、外部契约**。

## FR-01：保存并新建按钮

### Modified Modules（修改模块）

| 文件 | 改动 |
| :--- | :--- |
| `lib/widgets/biz/amount_editor_sheet.dart` | 新增「保存并新建」按钮（doneKey 区域 / 键盘底行）；新增表单重置逻辑（_amountStr='0'、_acc/_op 清空、_noteCtrl、_selectedTagIds、_pendingAttachments、_selectedAccountId、_date）；金额输入聚焦/高亮机制 |
| `lib/pages/transaction/transaction_editor_page.dart` | onSubmit 回调扩展（区分"保存并关闭"vs"保存并新建"）或新增回调 |
| `lib/widgets/transaction/transfer_form.dart` | 转账分支同步适配（保存并新建在转账 tab 的行为） |
| `lib/l10n/`（`app_*.arb` + 生成的 `app_localizations*.dart`） | 新增「保存并新建」文案（四语言） |

### Modified Interfaces / Contracts

- `AmountEditorSheet.onSubmit` 回调签名（`ValueChanged<AmountEditorResult>`）——需扩展（新增参数或新回调），**属内部组件接口，非跨系统契约**。
- 无外部 API / 契约变更。

### Modified Data Models

- 无数据库 schema 变更。

## FR-02：离线记账慢优化（修真实根因）

### Modified Modules

| 文件 | 改动 |
| :--- | :--- |
| `lib/services/data/tx_author_service.dart` | `markCreated/markEdited` 不再阻塞保存：拆 fire-and-forget（`unawaited`），或离线/无 session 短路，或在 `currentUser` 前加超时 |
| `lib/pages/transaction/transaction_editor_page.dart` | 将 `TxAuthorService` await 移到 `Navigator.pop` 之后（不延迟关页面） |
| `lib/widgets/transaction/transfer_form.dart` | 同上（`transfer_form.dart:260/208` 的 await） |
| `packages/flutter_cloud_sync/lib/src/providers/beecount_cloud_provider.dart` | `_request`/`_httpClient.send`（@1818/3336）加应用级超时（建议 3-10s）；`tryRefreshSession` 冷却（避免每次保存都重试）；`_isAccessTokenExpired` 提前 30s 判定调整 |
| `lib/cloud/sync/sync_engine.dart`（可选） | `sync()` 入口（@371）加离线门控（在线信号由 connectivity_plus 或 WS 状态提供），离线跳过云端 |
| `lib/providers/sync_providers.dart`（可选） | 将 WS/connectivity 在线状态暴露为 stream 供门控使用 |

### Modified Interfaces / Contracts

- 均在内部：`BeeCountCloudProvider` 内部方法加超时，不改变对外方法签名。
- `sync()` 离线门控为行为变更（离线时不再发起网络请求），语义符合预期。

### Modified Data Models

- 无数据库 schema 变更。
- 行为变更：`markTxAuthor` 回填 author 变为"尽力而为"（离线时跳过，不会阻塞/失败）。

## 受影响测试（需新增/调整）

| 测试 | 影响 |
| :--- | :--- |
| 新增：`TxAuthorService` 测试 | 离线/无 session/超时短路行为 |
| 新增：编辑器保存流程测试 | 保存并新建 vs 保存并关闭 |
| 新增：BeeCountCloudProvider 超时测试 | `_request` 超时抛错而非挂起 |
| 新增：SyncEngine 离线门控测试 | 离线时 sync 直接返回 |
| 调整：`test/cloud/sync/_fakes/fake_beecount_cloud_provider.dart` | 如需模拟离线 |
| 回归：现有 sync/cloud 测试 | 确认无破坏 |

## 不涉及

- BeeCount Cloud 服务端（无改动）。
- 数据迁移。
- 云端 API 契约（`/sync/push`、`/sync/pull`、`/auth/*`）。
