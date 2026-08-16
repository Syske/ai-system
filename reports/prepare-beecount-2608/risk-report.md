# Risk Report — beecount-2608

## 技术风险

| 风险 | 等级 | 说明 | 应对 |
| :--- | :--- | :--- | :--- |
| FR-01 回调签名改造影响转账分支 | 中 | `AmountEditorSheet` 仅被 2 处使用（`transaction_editor_page.dart:243`、`transfer_form.dart:156`），改签名两处都要适配 | 用可选参数/新回调保持向后兼容；覆盖转账测试 |
| FR-02 去 await 后 author 回填可能丢失 | 中 | `markCreated/markEdited` 改 fire-and-forget 后，若未等云端认证即关页，author 回填不可靠 | 离线短路 + 网络恢复后台补回填；或短路仅离线生效，在线仍等待但限时 |
| `_isAccessTokenExpired` 提前 30s + refresh 无冷却 | 中 | 每次保存触发网络重试，是慢的放大因素 | 加 refresh 冷却（复用 `_silentRecoveryCooldown` 模式）+ 请求超时 |
| 在线门控信号来源未定 | 低 | connectivity_plus 与 WS 连接状态不一致时门控误判 | Spec 阶段确定信号源；门控失败应安全降级（超时保护兜底） |

## 兼容性风险

| 风险 | 等级 | 说明 | 应对 |
| :--- | :--- | :--- | :--- |
| 上游频繁更新冲突 | 中 | 定制代码在 fork 上，合并上游会产生冲突 | 改动集中独立模块；通过配置开关隔离；跟随上游小步同步 |
| License（BSL）商用限制 | 低 | Business Source License 含商用条款；内部使用无碍 | 保持 fork 私有，不对外分发；与现有使用一致 |
| Flutter 版本兼容 | 低 | 上游要求 Flutter 3.27+ | 用与现有 Android 构建一致的 SDK 版本 |
| 多端兼容 | 中 | 客户端改动需与 Web/其他设备同步兼容 | 只改客户端内部控制流，不动协议；TC-08 多端联调 |

## 性能风险

| 风险 | 等级 | 说明 | 应对 |
| :--- | :--- | :--- | :--- |
| 同步任务主 isolate 争抢 CPU | 中 | SyncEngine push/pull 在主 isolate 跑，LookupCache.prime 全表 200-500ms | 本次范围外（用户确认不做队列改造）；记录为后续优化项 |
| 保存响应不达标 | 中 | 若超时设置不当（过长）仍会卡顿 | 超时默认 3-5s；测量验证 <200ms |
| 性能优化效果不达预期 | 中 | 若离线慢另有放大因素 | 增加性能日志定位瓶颈，分阶段迭代 |

## 迁移风险

| 风险 | 等级 | 说明 | 应对 |
| :--- | :--- | :--- | :--- |
| 无 schema 迁移 | 无 | 本次无数据模型变更 | — |
| 配置开关引入 | 低 | 新功能需开关控制（FR-01 可默认开启，FR-02 安全默认开启） | 开关名/默认值 Spec 阶段定 |

## 高优先级关注点

1. FR-02 改动横跨 app 与 packages 两个包，验证需同时跑 `flutter analyze` + 两个包的测试。
2. 去 await 与在线门控必须保证：离线保存快速成功 + 恢复网络后数据最终一致（local_changes 队列兜底）。
3. `fake_beecount_cloud_provider.dart` 无法复现离线场景，需补离线相关 fake/测试。
