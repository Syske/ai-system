# 系统巡检报告 — 2026-08-31（on-demand：task 制定/拆分对齐 + tasks.md 淘汰）

- 类型: 系统巡检（MAINTENANCE）
- 模式: on-demand
- Scope: skills/task-splitter（SKILL + workflow）+ skills/archive-openspec + skills/explore + cli/commands/aic-propose + task 制定/拆分责任定义
- 日期: 2026-08-31

---

## 一、工作背景

对 ai-system 的 **task 制定与拆分** 流程做审计：task-splitter 产出的任务格式与位置须与主链实际消费方（CLI provider / develop / dev-setup / archive）对齐。发现 task-splitter 输出（per-service 紧凑格式 + global-plan.md）与权威 Task Card（`tasks/cards/*.md` + tasks-template.md 格式）错位，且缺少 `branch` / `Completion Definition` / 代码质量检查等核心字段。

## 二、巡检发现（按严重度分级）

### 高

1. **task-splitter 输出格式/位置与主链消费方错位** — task-splitter 产出 `tasks/<service>.md` 紧凑格式 + `global-plan.md`，而权威消费方按 `*/tasks/cards/*.md` 枚举任务（`cli/services/providers.py:task_ids`）、develop/dev-setup 读取 `branch`/`Completion Definition`/代码质量检查。task-splitter 的输出无法直接喂给 develop 回路。
2. **Task Card 关键字段缺失** — `branch`（dev-setup 建分支依据，runtime-dev-setup.md:267,286）、`## 代码质量检查` 推导（runtime-spec 6.X）、`Completion Definition`（develop 完成勾选）在 task-splitter 完全未定义。
3. **`tasks.md`（变更根）与 `cards/` 双源** — 卡片化真实变更（wecom-live-integration）无 `tasks.md` 也正常运转，根 `tasks.md` 为冗余任务载体；且 `archive-openspec` 只读 `tasks.md` 统计完成度，卡片变更归档时任务完成度检查静默跳过（归档校验缺口）。

### 中

4. **`aic-trace`/`explore`/`aic-propose` 仍指向 `tasks.md`** 作为任务清单位置，未随卡片化更新，与权威 `tasks/cards/` 不一致。

## 三、修复动作与建议清单

| # | 动作 | 级别 | 状态 |
|---|---|---|---|
| ① | **task-splitter 对齐**：SKILL.md + workflow.md 重写——输出改为 `tasks/cards/T-{id}.md`（tasks-template.md 字段结构），新增 Task Card 字段模板（含 branch/完成定义/代码质量检查推导），T3 global-plan 定位为排序视图（引用 card ID + blocking 边），版本 1.0.0→1.1.0 | L1（文档/skill 一致性，已确认） | ✅ 已实施 |
| ② | **tasks.md 淘汰**：task-splitter 输出目录移除根 `tasks.md`；`archive-openspec` 任务完成度检查改为统计 `tasks/cards/*.md`（无 cards 回退 tasks.md，无则继续）；`explore`/`aic-propose` 同步指向 `tasks/cards/` | L1（避免双源 + 堵归档缺口，已确认） | ✅ 已实施 |
| ③ | 保留每服务索引 `{service}-tasks.md`（aic-trace.md:34 引用的真实产物）与 `global-plan.md` | L1（非本次淘汰对象） | ✅ 保留 |

## 四、验证

- `extensions-lint`：0 errors / 0 warnings
- CLI 单测：164 测试 OK（含 wizard/prompt_builder 改动回归）
- 一致性：task-splitter 与 `cli/services/providers.py:102` / `aic-trace.md:34` / `archive-openspec` / runtime-spec 6.X-6.Y / dev-setup branch 对齐；无悬空 `tasks/<service>.md` 旧格式引用
- 遗留：所有 `{service}-tasks.md` 均为合法的每服务索引引用，非本次淘汰对象

## 五、备注

本次为系统/技能一致性变更，与既有的 P37/P38（wizard 交互）、P39（extensions-lint）、P40-P44、tr5 prepare 注册等未提交在途工作一起入列提交；本文档独立记录本次 task 制定/拆分对齐操作。
