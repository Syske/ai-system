# Value-Burden Decision — skill-optimizer archive

- 日期 / Date: 2026-08-17
- 决策 / Decision: **归档（archive）skill-optimizer** —— 依据新增 Value-Burden Check 规则
- 触发 / Trigger: 用户问询"移除 skill-optimizer 的影响"与"SKILL-OPTIMIZER 提供的价值"，
  经影响面 + 价值双维度实证后决策

---

## 一、影响面审计（移除会怎样）

| 层面 | 影响 | 处理 |
|---|---|---|
| Workflow / runtime | 零影响（无绑定） | — |
| config/ | 零影响（无 menu/group/provider 条目，仅 1 注释） | 清注释 |
| tools/check.py / repo-lint | 照常 PASS（不断言存在） | — |
| **CI** (`ci.yml`) | 🔴 2 步骤显式跑 optimizer 测试+smoke → 必红 | 删 CI 步骤 |
| **iterative-optimizer** | 🔴 默认优化 prompt 指向 optimizer → 悬空 | 改 prompt 默认串 |
| **`aic-skill optimize`** | ⚠ CLI 照常跑但输出悬空 prompt | 删 CLI+模板 |
| 能力损失 | 自动技能优化引擎（4 模式+3 动作+snapshot/diff） | 归档保留可用 |

## 二、价值审计（值不值得这个体积）

| 证据 | 结果 |
|---|---|
| ~/.agent-insight/skill-history/ 快照历史 | 不存在 |
| 全仓 benchmark.json / diff.html / optimized* 产物 | 无 |
| OPTIMIZATION_LOG.md（约定应有） | 0 个 |
| 任何 skill 内 backup/snapshot/revert 残留 | 无 |
| 报告声称"优化 X skill 成功" | 无 |

**结论**：~10k 行（~25-27% 全仓 skill 代码）服务于**无使用痕迹**的功能 = `c) overbuilt relative to actual need`。
价值证据缺失 + 负担显著 → 按 Value-Burden Check 进入归档候选。

## 三、归档执行记录

**范围扩展（A′）**：依 Value-Burden 同链逻辑，`iterative-optimizer`（1392 行，整个优化环节依赖
skill-optimizer，无独立价值证据）一并归档，避免"外层循环壳 + 无引擎"的半死状态。

- 归档：`skills/skill-optimizer` 与 `skills/iterative-optimizer` → `archived/skills/`
- 密钥/字节码清理：归档内 `.env`（含 DEEPSEEK key，确认未提交）、`__pycache__` 已删除
- 连带清理：
  - `.github/workflows/ci.yml`：删 skill-optimizer unit + smoke 两步骤
  - `skills/README.md`：删两 skill 索引行
  - CLI 解绑 optimize 模式：`skill_launcher.py`（路由）、`providers.py`（mode 选项）、
    `cli/main.py`（mode choices + legacy skill-optimize 命令）
  - 死代码删除：`templates/prompts/skill-optimize.md`、`cli/services/skill_optimize.py`
  - 测试更新：`test_providers_skill_modes`（删 optimize）、`test_run_skill_optimize_falls_back`（optimize→回退）
  - `governance/policies/security-policy.md`（.env.example 引用）
  - stale 注释：skill-groups.yaml、extensions-init.py、path-audit.py allowlist、wizard fields/steps tuple
  - `cli/commands/aic-skill.md` 重写为 launch-only
- 验证：见执行报告（check.py / unittest / path-audit 全绿后完成）

## 四、维护规则落地

本决策同时驱动新治理规则 **Value-Burden Check** 写入 `governance/AI_OPERATING_RULES.md`
（见该文件 Evolution Principle 之后），后续 MAINTENANCE / QUARTERLY 对 >3000 行技能强制执行。
