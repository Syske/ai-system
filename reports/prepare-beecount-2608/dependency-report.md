# Dependency Report — beecount-2608

## 模块依赖

| 模块 | 依赖 | 变更影响 |
| :--- | :--- | :--- |
| `AmountEditorSheet`（表单 UI） | `transaction_editor_page`/`transfer_form` 提供 `onSubmit` 回调；`BeeTokens`；l10n | FR-01 主改点；回调签名需扩展 |
| `TransactionEditorPage` | `repositoryProvider`、`TxAuthorService`、`PostProcessor`、`AttachmentService` | FR-01 回调逻辑、FR-02 去 await |
| `TransferForm` | 复用 `AmountEditorSheet`；`TxAuthorService`、`PostProcessor` | 同 FR-01/FR-02，需同步改 |
| `TxAuthorService` | `beecountCloudProviderInstance` → `BeeCountCloudAuthService.currentUser`（网络） | FR-02 主改点（去阻塞 + 超时/门控） |
| `PostProcessor` | `syncServiceProvider`（SyncEngine / 快照）；`syncStatusRefreshProvider` | 已异步，无阻塞；可选性优化 |
| `SyncEngine` | `BeeCountCloudProvider`（HTTP/WS）、`ChangeTracker`、Drift | 离线门控插入点（`sync_engine.dart:371` 入口） |
| `BeeCountCloudProvider` | `http.Client`（无超时）、`WebSocketChannel` | 请求超时插入点（`_request`/`_httpClient.send`） |
| `sync_providers.dart` | `connectivity_plus`、SharedPreferences（`auto_sync`） | 在线状态信号来源；`auto_sync` 仅快照模式生效 |

## 服务依赖

- App → BeeCount Cloud：HTTP（`/auth/login`,`/auth/refresh`,`/sync/push`,`/sync/pull`）+ WS（`/ws`，端口 8869）。
- App 本地：SQLite（Drift）。无 MQ / RPC / 定时任务（无周期同步器，仅 WS 心跳 20s）。
- 快照模式（S3/WebDAV/Supabase）：本项目启用的是 BeeCount Cloud，不走快照模式。

## 数据依赖

- `transactions` 表：保存核心数据模型（syncId 全局唯一）。
- `local_changes` 表：保存与同步之间的持久化队列（pushedAt 为未推送标记）。
- 修改数据模型：FR-01/FR-02 均**不需要新增表/字段**（保存并新建复用现有表单状态；性能优化为控制流改动）。
- `TxAuthorService` 回填 author 依赖云端当前用户 id（`markTxAuthor`）。

## 外部依赖

| 依赖 | 用途 | 变更 |
| :--- | :--- | :--- |
| `flutter_cloud_sync` 包 | 云同步 | FR-02 加超时/门控需改此包内 `beecount_cloud_provider.dart` |
| `http` | HTTP 客户端 | 现有，直接加 `.timeout()`，无需新依赖 |
| `connectivity_plus` | 网络状态 | 已引入，用于在线门控信号 |
| `web_socket_channel` | WS | 已有 |
| Flutter SDK | 3.27+ | 与现有 Android 构建版本一致 |

## 关键结论

1. FR-01 改动集中在 UI 层 + 回调签名，影响面小，依赖清晰。
2. FR-02 主改点 `TxAuthorService`（lib 内）+ `beecount_cloud_provider.dart`（packages 内），两个文件跨 app/packages 边界。
3. 无新增第三方依赖需求。
