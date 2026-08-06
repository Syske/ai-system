# Maintenance Report — 2026-08-06

**Mode**: on-demand
**Scope**: 归档流程核查 —— `/aic-sync` 是否需要新增
**Date**: 2026-08-06
**Environment**: Windows (`D:\workspace\ai-workspace`)
**Trigger**: `optimize-liveinfo-modify-by-bizid` 变更归档时,`aic-archive.md` 指引执行 `/aic-sync` 逻辑,但该命令不存在

---

## 1. 事实核查 / Facts

| # | 引用 | 位置 | 实际状态 |
|---|------|------|----------|
| F1 | 命令 `/aic-sync` | `ai-system/cli/commands/aic-archive.md:59`("execute the `/aic-sync` logic") | ❌ 不存在 —— `cli/commands/` 下无 `aic-sync.md` |
| F2 | Skill `openspec-sync-specs` | `ai-system/cli/commands/aic-archive.md:155`("use the Skill tool to invoke `openspec-sync-specs`") | ❌ 不存在 —— `ai-system/skills/` 下无此 skill |
| F3 | 实际同步能力 | — | ✅ 由 `openspec-cn archive -y` **内建**完成(本次实测:`specs 更新成功, + 4 新增`,增量 spec 合并到 `openspec/specs/live-info-modify-cleanup/spec.md`) |

**根因**:`aic-archive.md` 的同步指引与实际实现不一致——文档引用两个不存在的实体,而真实能力内建于 OpenSpec CLI,无需任何额外命令或 skill。

## 2. 结论 / Decision

**不需要新增 `/aic-sync` 命令。**

依据(Evolution Principle, AI_OPERATING_RULES):
- 同步增量 spec 的能力**已经存在**于 `openspec-cn archive`(归档时自动提示并执行),独立命令是重复能力
- 本次实战未暴露"需要独立同步入口"的真实场景——归档流程已完整走通
- 新增命令违反 Minimal Change 原则

**正确动作:修复文档,而非新增命令。**
`aic-archive.md` 两处失效引用应改为指向真实机制(OpenSpec CLI 内建同步 / `openspec-cn archive`),避免误导后续执行。

## 3. 建议修复 / Proposed Fix

| 位置 | 现状 | 建议 |
|------|------|------|
| `aic-archive.md:59` | "execute the `/aic-sync` logic" | 改为 "run `openspec-cn archive <name> -y`,其内建同步会合并增量 spec"(保留"无论同步与否都继续归档"的语义) |
| `aic-archive.md:155` | "invoke `openspec-sync-specs`" | 删除或改为指向 CLI 内建同步,不再引用不存在的 skill |

## 4. 状态 / Status

- [x] 文档修复已完成：`aic-archive.md` L59/L157 均已改为 `openspec-cn archive <name> -y`（内建同步合并增量 spec），不再引用不存在的 `/aic-sync` 命令与 `openspec-sync-specs` skill
- 关联变更 `optimize-liveinfo-modify-by-bizid` 已归档: `openspec/changes/archive/2026-08-06-optimize-liveinfo-modify-by-bizid/`

## 5. 其他发现(本次归档过程)

| # | 发现 | 状态 |
|---|------|------|
| O1 | `openspec-cn archive` 交互提示在非交互会话中被强制关闭(`Error: User force closed the prompt`),需 `-y` 标志 | 已用 `-y` 解决,无碍 |
| O2 | 归档期间 `WeComLiveStatusSyncServiceTest` 引用不存在的 `triggerProgressRecalc`,导致 live-api 全量测试编译失败 | 预存问题,已记录待独立排查(bugfix) |
| O3 | `LiveInfoServiceTest` 5 个用例失败(`syncWeComLiveData_*`×3、`updateLiveStatusByFeedId`×2),stash 对照证实与本次变更无关 | 预存问题,已记录待独立排查 |
