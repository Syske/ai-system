# Change Proposal: P31 — standards/cool 公司规范迁出通用层（extensions + loader 可配置）

| Field | Value |
|---|---|
| Status | **Proposed** |
| Type | Structural (L3，ADR-0009 两层分离) |
| Author | AI Maintainer |
| Created | 2026-08-23 |
| Reference | ADR-0009 合规诊断（`reports/ADR-0009-COMPLIANCE-DIAGNOSIS-2026-08-13.md` P1，待评审） |
| Process | OPERATIONS §12 Change Management |

---

## 1. Problem

`governance/standards/cool/`（5 文件：enum-dml / enum-naming / i18n / rocketmq-conventions /
rpc-conventions，含 `net.coolcollege.*`）是**公司特有**规范，却位于 ai-system 通用层：

- 违反 ADR-0009 原则 6（两层分离：公司特有 → extensions 层）+ extensions/README 定位
- 被 `loaders/standards-loader.md:129-133` 与 `templates/runtime/runtime-release.md`（4 处）
  **正式引用**，为活跃资产
- 影响：换公司克隆 ai-system 会带上 coolcollege 规范；公司规范变更需改 ai-system 通用层
  （通用层被公司内容污染）

## 2. Root-Cause

历史直接落通用层；standards-loader 的 standards 路径**硬编码**，无配置化加载点
（对比 layers.skills 已有可配置路径机制）。

## 3. Options

- **A. 迁移 + 可配置 loader（Recommended）**：`governance/standards/cool/` → extensions 层
  （如 `extensions/company-standards/cool/`）；standards-loader 增加配置化路径（仿
  `layers.skills`：config 引用 → 相对 workspace/extensions）；`runtime-release.md` 引用同步
  更新；cool 命名脱敏（`net.coolcollege.*` → 中性占位）
- **B. 就地标注"公司特有"**：在 cool/README 标注非通用，loader 仍引用——最小改动，
  不解决泄漏与克隆污染
- **C. 维持现状**：不处理

## 4. Recommendation

采用 **Option A**（方向正确），但**实施时机按 Evolution Principle 门控**：当前仅一家公司
在使用，真实痛苦（第二家公司接入/公司规范独立演进）尚未触发。建议本提案先完成设计评审
（Approved），实施可（a）立即排期，或（b）等真实触发（第二家公司接入、或公司规范需独立
变更）再执行——两种路径都在本提案范围内。

## 5. Proposed Changes

- [ ] `governance/standards/cool/*` → `extensions/company-standards/cool/`（extensions 为独立
  git 仓，需走扩展仓流程提交）
- [ ] `loaders/standards-loader.md`：standards 根路径配置化（仿 layers.skills：环境配置
  `layers.standards.path` 或 config 引用，缺省指向通用层）
- [ ] `templates/runtime/runtime-release.md`（4 处引用）+ 其他引用同步更新
- [ ] cool 内容脱敏核查（`net.coolcollege.*` 等品牌名 → 中性表述）
- [ ] 一致性抽查：path-audit / check.py / 文档-现实对照

## 6. Validation Plan

- path-audit 0 broken（迁移后引用全部可达）
- standards-loader 在两种路径形态（通用层缺省 / extensions 配置）下均可解析
- runtime-release 引用更新后 check.py / workflow-audit 全绿

## 7. Risks

- **L3 结构性**：跨仓（ai-system + extensions 独立仓）协调；需变更管理评审
- **引用面**：loader + release 模板 + 可能的历史报告引用；path-audit 兜底
- **脱敏遗漏**：cool 文件内品牌/内网域名需逐文件核查（参考 tr5 全量脱敏先例）

---

## Review Log

| Reviewer | Decision | Date |
|---|---|---|
