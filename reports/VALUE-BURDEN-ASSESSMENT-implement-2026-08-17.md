# Value-Burden Assessment — implement skill (keep)

- 日期 / Date: 2026-08-17
- 评估对象 / Object: `skills/implement/`（当前最大活跃技能，2368 行 / 8 个 .md 文件）
- 决策 / Decision: **保留（keep）**——已兑现价值 + 健康负担
- 依据 / Basis: `governance/AI_OPERATING_RULES.md` Value-Burden Check

---

## 一、价值证据（已兑现，非潜在）

| 维度 | 证据 | 判定 |
|---|---|---|
| 工作流强绑定 | `templates/runtime/runtime-develop.md` L101 引用 `implement/planning.md`、L119 "Phase 3 — Invoke Implement Skill → skills/implement/workflow.md"；`runtime-bugfix.md` L234 列 implement 为依赖 | ✅ 被核心工作流直接调用 |
| 明确角色 | "Contract-driven: implements exactly one OpenSpec Task Card"——Task Card + Spec → 计划/实现/测试/验证/自审 | ✅ 目标唯一 |
| 产出被下游消费 | plan 持久化到 `workspaces/.../tasks/plans/{task_id}-plan.md`；Review/Verify 比较计划与实现 | ✅ 真实闭环 |
| repo-lint | implement 相关 warning = 0 | ✅ 健康 |

## 二、负担核算

- 2368 行，拆分为 8 个 .md：SKILL(317) + workflow(257) + 6 主题文件(185-446)。
- 非单个超长文件、无脚本/字节码膨胀——纯方法论文档，每文件 <500 行。
- 与 skill-optimizer（50 脚本 + 代码量）本质不同：implement 是**可读可维护的方法论**，非代码工具。

## 三、相对负担

- dev-core 中最大（implement 2368 vs bugfix 1352 / mock-test 1322 / java-maven 1083），
  多余体量来自其三重主执行角色：规划(planning.md) + 执行(workflow.md) + 验证自审(validation.md)。

## 四、关联澄清

- `implement`（执行 1 Task Card）/ `task-splitter`（拆任务）/ `wayfinder`（事前决策图）
  三层递进，无命名或职责重叠。

## 五、判定与后续

- Value-Burden：✅ 价值证据充分 + 负担健康 → **保留**，不做减法。
- 触发条件不成立（2368 < 3000 行触发阈值）。
- 后续 MAINTENANCE/QUARTERLY 按 Value-Burden Check 常规复核即可，无针对 implement 的特办项。

---

注：本评估为 2026-08-17 skill-optimizer 归档后的收尾核查；归档后活跃技能最高行数为
implement(2368)，已无 >3000 行技能，Value-Burden Check 的强制触发对象不存在。
