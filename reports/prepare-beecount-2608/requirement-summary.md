# Requirement Summary — beecount-2608

Change ID: beecount-2608
Source: Change Request（用户提供，含一份预起草 Spec）
Locale: zh

---

## 变更目标

针对 BeeCount（蜜蜂记账，开源 Flutter App + 自建 Cloud）做二次开发，解决两个交互/性能痛点。

## FR-01：记账页面增加「保存并新建」按钮

- 在记账表单保存按钮旁新增「保存并新建」按钮。
- 点击 → 保存当前记录 → 清空表单 → 进入下一笔录入状态。
- 兼容现有长按图标快捷记账（拍照/截图/语音）。
- 交互细节（清空范围、金额框聚焦机制、是否留页）留待 Spec 阶段细化（用户确认）。

## FR-02：优化「开启云同步后离线记账慢」的性能问题

- 现象：开启 BeeCount Cloud 同步后，本地保存操作响应变慢。
- CR 假设根因：保存被云端连接检查、差异计算等同步前置环节阻塞。
- 代码分析结论（已核实）：**CR 假设不成立**。同步本身已是 fire-and-forget 异步（不阻塞 UI）。
  真实根因是保存链路中 `TxAuthorService.markCreated/markEdited`（`lib/pages/transaction/transaction_editor_page.dart:319`）
  → `cloud.auth.currentUser`（`lib/services/data/tx_author_service.dart:42`）这一**无超时的云端 HTTP 认证调用**：
  离线 + access token 过期时挂起到 OS 级 TCP 超时（Android 最长约 2 分钟）。
- 用户已确认方向：**修真实根因**（去阻塞 + 加超时 + 在线门控），不做 CR 原方案的同步队列改造。
- 性能目标：保存响应 < 200ms（底线 < 500ms），测量：点击保存 → UI 返回保存成功状态。

## 交付约束

- 代码兼容上游（通过配置开关隔离，便于合并上游更新）。
- `flutter analyze` 零警告；关键逻辑补单元测试；Commit 遵循 Conventional Commits。
- 多端（App ↔ Cloud ↔ Web）数据一致。

## 未知信息 / 待 Spec 澄清

- FR-01：保存并新建后的具体行为与金额框"聚焦"实现（用户：spec 阶段再细化）。
- FR-02：超时值（建议 3–10s）、在线门控信号来源（connectivity_plus vs WS 连接状态）。
- 是否需要把改动打上配置开关及开关名。

## 结论

需求已基本理解；待澄清项不影响进入 Spec（可在 Spec 中细化并再次确认）。
