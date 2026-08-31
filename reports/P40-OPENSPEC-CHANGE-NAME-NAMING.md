# Change Proposal: P40 — OpenSpec-CN Change Name 字母开头约束与 workspace 命名惯例冲突

| Field | Value |
|---|---|
| Status | **Implemented** |
| Type | Structural（命名约定 / 标准层） |
| Author | AI Maintainer |
| Created | 2026-08-25 |
| Reference | 202610-qa-housekeeping-optimization tr5-spec run（openspec-cn commands 报错 "变更名称必须以字母开头"） |
| Process | OPERATIONS §12 Change Management |

---

## 1. Problem

workspace 命名惯例使用日期前缀 `<YYYYMM>-<desc>`（如 `202610-qa-housekeeping-optimization`、`202610-cool-italent-sync-plus`），以**数字**开头。

OpenSpec-CN 的 change name（`openspec/changes/<name>/`）要求**以字母开头**，否则 `openspec-cn new change` / `instructions` / `validate` / `show` 等命令报错：

```
✖ Error: 无效的变更名称 '202610-qa-housekeeping-optimization'：变更名称必须以字母开头
```

冲突表现：
- workspace 目录名 `workspaces/202610-xxx/` 以数字开头（惯例）。
- `openspec/changes/<name>/` 的 `<name>` 以字母开头（openspec-cn 约束）。
- 两者无法用同一标识，导致 openspec changes 目录名与 workspace 目录名不一致。

既有项目 `202610-cool-italent-sync-plus` 因目录手动创建、未走 `openspec-cn new change`，`list` 对已存在目录不校验名称，故未暴露此冲突。本次 tr5-spec 跑 `openspec-cn instructions` 时触发校验才暴露。

## 2. Root-Cause

两套命名约束在不同层面各自独立演进，未对齐：
- workspace 层（`workspaces/<change-id>/`）沿用日期前缀惯例，便于按时间排序与多项目索引。
- openspec-cn 工具层（`openspec/changes/<name>/`）要求字母开头，是 OpenSpec-CN CLI 的内置约束（不可配置）。

prepare 阶段用 `<YYYYMM>-<desc>` 作 change-id，到 tr5-spec 阶段发现 openspec changes 目录不能用同名。

## 3. Options

| 选项 | 做法 | 权衡 |
|------|------|------|
| A. openspec changes 目录用字母开头，workspace 目录不变 | workspace 保持 `202610-xxx`，openspec changes 用 `xxx`（去日期前缀）或 `cc202610-xxx`（字母前缀 + 日期） | 命令全可用；两目录名不一致，需在 proposal/spec.md 注明映射 |
| B. 整体改 change-id 为字母开头 | workspace + openspec changes + 所有引用统一改为字母开头 | 一致性最好；但 prepare 产物已用数字前缀，改动面大 |
| C. 保留数字前缀，绕过 openspec-cn CLI | 手动管理 openspec 产物，不走 CLI 校验 | 零改名；但放弃 openspec-cn validate/instructions 等工具能力，长期不可持续 |

## 4. Recommendation

**A**（openspec changes 目录用字母开头，workspace 目录不变）。

理由：
- 最小改动：workspace 层零改动，prepare 产物（proposal、reports、诊断日志、澄清记录）保持原引用。
- openspec changes 目录名是工具层标识，与 workspace 目录名解耦合理——前者服务 openspec-cn CLI，后者服务 workspace 索引。
- 映射关系在 proposal/spec.md 里一行注明即可。

命名规则建议：openspec change name = workspace 目录名**去掉日期前缀**（`202610-qa-housekeeping-optimization` → `qa-housekeeping-optimization`）。

## 5. Proposed Changes

1. **tr5-prepare / prepare 文档**：明确 openspec change name 用字母开头（去日期前缀或字母前缀），workspace 目录名保持 `<YYYYMM>-<desc>` 惯例，两者映射在 proposal/spec.md 注明。
2. **artifact-schema.md**（tr5 references）：在产物契约里补一行"openspec change name MUST 以字母开头，workspace 目录名可含日期前缀"。
3. **tr5-prepare/SKILL.md**：`openspec-cn new change <name>` 处补注 `<name>` 以字母开头，不沿用 workspace 目录名的日期前缀。
4. **既有项目处理**：`202610-cool-italent-sync-plus` 的 openspec changes 目录（若后续需跑 CLI）按同规则重命名。

## 6. Validation Plan

- `openspec-cn validate <letter-name>` 通过。
- `openspec-cn instructions <artifact> --change <letter-name>` 通过。
- workspace 目录名与 openspec changes 目录名映射在 proposal/spec.md 可查。

## 7. Risks

| 风险 | 应对 |
|------|------|
| 两目录名不一致导致引用混淆 | proposal/spec.md 注明映射；tr5 skill 文档明确 |
| 既有项目重命名遗漏引用 | 重命名时 grep 全仓引用同步更新 |

---

## Implementation Record (2026-08-26)

Applied per approval (OPERATIONS §12 → Implement → Validate):
1. 本项目 openspec changes 目录重命名：`202610-qa-housekeeping-optimization` → `qa-housekeeping-optimization`（workspace 目录名不变）
2. 映射关系在 `workspaces/202610-qa-housekeeping-optimization/openspec/changes/qa-housekeeping-optimization/proposal.md` 头部注明
3. 文档同步：`skills/tr5-spec/SKILL.md`（new change 命令处补字母开头警示 + 命名约定）、`references/artifact-schema.md`（Stage 2 补命名约束）
4. 既有项目 `202610-cool-italent-sync-plus` 暂不重命名（提案注明的条件项：若后续需跑 CLI 再按同规则处理）

**Validation**: `openspec-cn validate qa-housekeeping-optimization` 通过；`openspec-cn instructions proposal --change qa-housekeeping-optimization` 通过（修复前报"变更名称必须以字母开头"）

---

## Review Log

| Reviewer | Decision | Date |
|---|---|---|
| User (AI Maintainer operator) | **Approved**（openspec 工具限制下的合理解法，选项 A：openspec changes 字母开头 + workspace 保留日期前缀 + 映射注明；2026-08-25 立项 Proposed，2026-08-26 用户裁决批准） | 2026-08-26 |
