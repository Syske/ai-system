# Repository Summary — beecount-2608

## 仓库信息

| 项目 | 内容 |
| :--- | :--- |
| 客户端仓库 | https://github.com/TNT-Likely/BeeCount（Flutter） |
| 云端仓库 | https://github.com/TNT-Likely/BeeCount-Cloud（FastAPI + React，未克隆，仅依据部署配置分析） |
| 本地路径 | `/home/syske/net-workspace/workspace/projects/BeeCount` |
| 分支 | `task/beecount-2608`（基于 upstream `main` @ `70c800b` 新建） |
| 体积 | 183MB（含 git 历史） |
| 技术栈 | Flutter 3.27+ · Riverpod · Drift(SQLite) · 多云同步插件 |
| License | Business Source License（BSD 3-Clause 变体，含商用条款） |

## 客户端仓库结构（与变更相关）

```
lib/
  main.dart               # 入口，截图监听恢复
  app.dart                # 主壳：底部中心按钮、长按快捷菜单、深链派发、初始云同步
  pages/transaction/
    transaction_editor_page.dart   # 记账页容器（支出/收入/转账 Tab，437 行）
  widgets/
    biz/amount_editor_sheet.dart   # 实际记账表单（金额+键盘+备注+保存，1553 行）
    transaction/transfer_form.dart # 转账表单流程控制器（555 行）
    category/category_selector.dart
  services/
    data/tx_author_service.dart    # ★ FR-02 阻塞点（云端认证回填 author）
    billing/post_processor.dart    # ★ 保存后同步触发（fire-and-forget）
    ai/                            # AI 记账（拍照/截图/语音）
  cloud/
    sync_service.dart
    sync_diff_service.dart         # 交易级 diff 预览（快照模式）
    transactions_sync_manager.dart # 快照模式管理器（指纹+条数+时间戳）
    transactions_json.dart
    sync/                          # SyncEngine 核心（8 个 part 文件）
      sync_engine.dart             # 同步引擎（1480 行）
      sync_engine_realtime.dart    # WS 事件 + 防抖调度
      sync_engine_serialization.dart
      sync_engine_pull.dart        # cursor / LookupCache（全表 prime 200-500ms）
      sync_engine_apply.dart
      sync_engine_attachments.dart
      sync_engine_status.dart
      sync_engine_resolvers.dart
      sync_engine_profile.dart
      change_tracker.dart          # local_changes 持久化同步队列
      sync_coordinator.dart        # watch local_changes → 250ms 防抖触发 sync
  providers/
    database_providers.dart
    sync_providers.dart            # connectivity_plus 网络监听、auto_sync 开关
  styles/tokens.dart               # BeeTokens 明暗主题
  data/
    db.dart                        # Drift 数据库（NativeDatabase 后台 isolate）
    repositories/local/local_repository.dart
    repositories/local/local_transaction_repository.dart

packages/
  flutter_cloud_sync/              # 云同步插件（多后端：beecountCloud/supabase/webdav/s3/icloud）
    lib/src/providers/beecount_cloud_provider.dart   # ★ HTTP+WS 客户端（4732 行，无请求超时）
    lib/src/manager/cloud_sync_manager.dart          # 快照模式（指纹 diff）
    lib/src/config/..., lib/src/core/..., lib/src/utils/retry_helper.dart（未使用）

test/
  cloud/sync/                     # SyncEngine e2e、ChangeTracker、fakes
  sync/                           # apply 细节测试
  repositories/                   # repository 契约测试
  data/repositories/local/        # bulk sync、统计
  ai/  providers/  services/  ...
```

## 入口点

- App 入口：`lib/main.dart`；主壳：`lib/app.dart`（`_triggerInitialCloudSync` @211-376）。
- 记账表单：`AmountEditorSheet`（`amount_editor_sheet.dart:222`），被 `transaction_editor_page.dart:243` 和 `transfer_form.dart:156` 两处实例化。
- 保存：`doneKey()`（`amount_editor_sheet.dart:1057-1151`），onTap @1073 → `widget.onSubmit` @1108。
- 保存回调：`transaction_editor_page.dart:260`（`onSubmit: (res) async {...}`）。

## 现有测试

- `test/cloud/sync/sync_engine_e2e_test.dart`（854 行）：SyncEngine 端到端。
- `test/cloud/sync/change_tracker_test.dart`、`lookup_cache_test.dart`、`sync_error_store_test.dart`。
- `test/data/repositories/local/local_repository_bulk_sync_test.dart`、`local_transaction_repository_test.dart`。
- `test/repositories/`：多币种、统计、budget、账户等契约测试。
- `test/sync/`：apply 细节（多币种、exclude flags、hidden 等）。
- 缺口：TxAuthorService、PostProcessor、编辑器保存流程、离线/超时行为均无测试。

## 部署环境（现有）

- BeeCount Cloud：群晖 NAS Docker，`docker/beecount-cloud/docker-compose.yml`，端口 `8869:8080`，数据 `./data`（SQLite），镜像 `sunxiao0721/beecount-cloud:latest`，JWT_SECRET/REGISTRATION_ENABLED/CORS_ORIGINS 配置。
- Android 客户端：Flutter 构建，连接 `http://192.168.0.101:8869`。
