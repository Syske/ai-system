# Architecture Summary — beecount-2608

## 1. 总体架构

```
BeeCount App (Flutter, Drift 本地库)
  │  UI 层：TransactionEditorPage / AmountEditorSheet / TransferForm
  │         ↓
  │  Provider 层：Riverpod（repositoryProvider, syncServiceProvider 等）
  │         ↓
  │  数据层：LocalRepository → Drift(transactions, local_changes)
  │         ↓  保存后
  │  同步层：PostProcessor.sync (fire-and-forget)
  │         ├─ SyncEngine.sync()  ──► BeeCountCloudProvider ──► BeeCount Cloud (WS+HTTP)
  │         └─ SyncCoordinator(250ms) → _scheduleAutoSync(2s)
  │
  ▼
BeeCount Cloud (FastAPI + React, Docker 8869, SQLite, WebSocket /ws)
```

## 2. 记账保存路径（现状）

```
AmountEditorSheet.doneKey.onTap (amount_editor_sheet.dart:1073)
  └─ widget.onSubmit(res)  (amount_editor_sheet.dart:1108, 不 await)
       └─ TransactionEditorPage.onSubmit async (transaction_editor_page.dart:260)
            ├─ repo.addTransaction / updateTransaction  (本地 Drift，毫秒级)
            │    └─ change_tracker.recordLedgerChange → local_changes 表
            ├─ await TxAuthorService.markCreated/markEdited  ★ FR-02 阻塞点
            │    └─ await cloud.auth.currentUser  (无超时 HTTP → 离线挂起)
            │    └─ repo.markTxAuthor (本地 UPDATE)
            ├─ 附件/标签保存 (本地)
            ├─ PostProcessor.sync (fire-and-forget, 不阻塞)
            ├─ 刷新 counts/stats/budget、更新小组件
            └─ Navigator.pop ×2 关闭 sheet + 页面
```

## 3. 关键组件职责

| 组件 | 职责 | 备注 |
| :--- | :--- | :--- |
| `LocalRepository` | 本地写库 + 登记 local_changes | 保存路径的核心，纯本地快 |
| `ChangeTracker` | local_changes 持久化队列（pushedAt 标记） | 天然的同步队列 |
| `SyncCoordinator` | watch local_changes → 250ms 防抖 → triggerAutoSync | 反应式触发 |
| `SyncEngine` | BeeCount Cloud 增量同步（push/pull/cursor/apply） | 主 isolate 执行 |
| `BeeCountCloudProvider` | HTTP API + WS 客户端（心跳 20s / 重连 3s） | ★ 无请求超时 |
| `PostProcessor` | 保存后统一触发同步（SyncEngine 分支 fire-and-forget） | 不阻塞 UI |
| `TxAuthorService` | 保存后回填创建/修改人（云端当前用户） | ★ 阻塞保存 |

## 4. 数据库

- Drift (SQLite)，单连接，`NativeDatabase.createInBackground`（`lib/data/db.dart:1240-1259`）。
- 核心表：`transactions`、`local_changes`（同步队列）、tags/categories/accounts 等。
- 未配置 WAL/busy_timeout（单连接串行，暂无并发冲突，但 pull 大事务会抢锁）。

## 5. 同步机制（BeeCount Cloud 增量模式）

- 触发：保存后（PostProcessor + SyncCoordinator 双通道）、WS connected、网络恢复、启动、手动。
- WS：`/ws?token=`，20s ping，断线 3s 重连，重连成功发 `connected` 事件 → 全量 sync。
- push：读 local_changes 未推送行 → 逐条序列化 → 单次 POST `/sync/push` → markPushed。
- pull：GET `/sync/pull`（cursor）→ LookupCache.prime 全表（10k+ 行 200-500ms）→ 事务 apply → cursor 推进。
- diff：增量模式无指纹（仅靠 local_changes + cursor）；指纹+条数+时间戳属于快照模式（S3/WebDAV）。

## 6. 在线/离线判定（现状缺口）

- `connectivity_plus`（`lib/providers/sync_providers.dart:340-353`）仅用于网络恢复后触发 sync，**不拦截保存/认证路径**。
- WS 客户端只有 `connected` 事件，**无在线状态流**暴露。
- 云端 HTTP 请求（`_request` / `_httpClient.send`）**无应用级超时**。

## 7. 架构调整目标（FR-02，修真实根因）

```
现状： 保存 → await TxAuthorService(云端认证, 无超时) → 关页面    ← 离线挂起
目标： 保存 → 本地落库(快) → 立即关页面(<200ms)
       └─ TxAuthorService / 云端交互 全部改为后台异步 + 在线门控 + 请求超时
```

## 8. 主题

- `BeeTokens`（`lib/styles/tokens.dart`）按 `isDark(context)` 分流明暗，新增 UI 组件用现有 token / `colorScheme.primary` 即可自动适配。
