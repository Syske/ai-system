# Value-Burden Decision — skill-sync archive

- 日期 / Date: 2026-09-23
- 决策 / Decision: **归档（archive）skill-sync** —— 依据 `governance/AI_OPERATING_RULES.md`
  的 Value-Burden Check
- 触发 / Trigger: 用户在 R4 残债收尾中问询「skill-sync 对我们有什么价值」；经
  使用证据 + 负担双维度实证后，用户裁决「确认归档」
- 决策权 / Authority: 用户（owner）—— 规则明示归档是**决策**而非自动删除

---

## 一、影响面审计（移除会怎样）

| 层面 | 影响 | 处理 |
|---|---|---|
| Workflow / runtime | 零影响（`workflows/` 无任何引用） | — |
| 其它 Active Skill | 零影响 —— 唯一的历史调用方 `skill-optimizer` / `iterative-optimizer` **已于 2026-08-17 归档** | — |
| `config/`（menu / skill-groups / provider） | 零影响（无条目） | — |
| CLI / 产品面 | 零影响（`cli/commands/` 无对应命令、`config/menu.yaml` 无登记；仅靠自然语言触发） | — |
| **`tools/skill_index.py` 口径** | 技能数 **39 → 38** | 自动收敛，无需改代码 |
| **`skills/README.md`** | 索引行悬空 | 删行 + 更正该节计数 |
| **`cli/tests/test_skill_sync_policy.py`** | 断言对象移出 `skills/` → 测试失去意义 | **随技能移入** `archived/.../tests/`（先例：skill-optimizer 的 `scripts/tests/`） |
| **`cli/tests/test_t5_hardening.py`** | 有一处读取 `skills/skill-sync/scripts/pull.js` 的源码断言 → 会 `FileNotFoundError` | 改指归档快照路径 |
| `tools/path-audit.py` | 一处 EXAMPLE_ONLY 注释指向已归档文件 | 更正注释（条目保留，便于恢复时复用） |
| `.github/workflows/ci.yml` | 本仓**无 `.github/`**（先例当年有） | 无需处理 |
| 能力损失 | 内网 Witty-Skill-Insight / Agent Insight 平台的**唯一**技能上传/拉取通道 | 归档保留可用，但恢复需 ADR + 全门禁 |

## 二、价值审计（值不值得这个体积）

| 证据（Value-Burden Check 第 1 步） | 结果 |
|---|---|
| 下游消费者 | ❌ 仅 `skill-optimizer`（`workflow.md:241-265` 调用 `push.js`）与 `iterative-optimizer`（`DEFAULT_TASK_SYNC`）+ `archived/commands/aic-skill-optimize.md` —— **全部已归档** |
| 实际运行记录（`logs/` `reports/` `outputs/` 全量搜 `push.js` / `pull.js`） | ❌ 仅命中维护/审计类记录（`r1-security-*`、`code-review-*`、`r4-skills-*`）；**零条真实 push/pull** |
| 平台是否在用（本机凭据） | ❌ `~/.agent-insight/.env`、`~/.witty/.env`、`~/.skill-insight/.env` **三者均不存在** |
| 是否被使用牵引演进 | ❌ `git log -- skills/skill-sync` = 5 次提交，首提之后**全是审计驱动的加固**（描述长度 lint、T5 加固、R1 安全加固、R4 退出码），**零功能提交** |
| 平台侧产物（沿用 2026-08-17 判据） | ❌ `~/.agent-insight/skill-history/` 快照历史不存在（当年归档 skill-optimizer 的同一判据） |

**负担核算（第 2 步）**：576 行 / 4 文件（`push.js` 248、`sync-policy.js` 136、`pull.js` 131、`SKILL.md` 61），
其中 `sync-policy.js` **整体是 R1 安全加固产物**；另有专属契约测试 119 行 / 10 项；
占据技能枚举口径与 `skills/README.md` 索引；并可归属 R1 / T5 / R4 三批维护工时
（本轮对话的 R4 §2.2 重构亦为其支出）。

**判断（第 3 步）**：价值证据缺失 **且** 负担非轻 → 正当的 review / shrink / archive 候选；
owner 裁决 **archive**。

**旁证**：`reports/VALUE-BURDEN-DECISION-skill-optimizer-2026-08-17.md` 当年已用同一判据
归档该链的消费端，只剩运输层 `skill-sync` 在册；`reports/P10-SKILL-OPTIMIZER-SPLIT.md:44`
载明 skill-sync 本身即源自那次一次性优化工程。

## 三、归档执行记录

- 归档：`skills/skill-sync/` → `archived/skills/skill-sync/`（`git mv`，保留历史）
- 测试随行：`cli/tests/test_skill_sync_policy.py` → `archived/skills/skill-sync/tests/test_skill_sync_policy.py`
  （路径常量已随位置修正；**不再被 `discover -s cli/tests` 收集**，单跑仍 10 项 OK）
- 连带更新：`skills/README.md`（删行 + 计数）、`cli/tests/test_t5_hardening.py`（改指归档快照）、
  `tools/path-audit.py`（注释更正）、`archived/ARCHIVE.md`（新增 2026-09-23 记录）
- **R4 §2.2 撤销**：判决前在途的 `loadConfiguration` 抽共享模块重构（未提交）已 `git checkout` 撤销
  —— 不再为将归档资产投入重构；`archived/` 保持 HEAD（`f36f744`）时的快照，不追加改进
- **未走 Deprecate 宽限期**：`skill-lifecycle.md` 的 Deprecate → 1 个月宽限期 → Archived 序列
  适用于「有替代品/能力过时」；本次走 Value-Burden 路线，与 2026-08-17 先例一致（直接归档）
- 恢复条件：`skill-lifecycle.md` Stage Archived —— 需 ADR 说明 + 全门禁通过 + linter 通过

## 四、本轮不处理（记录为待办）

- `skills/README.md` 仍有**既有**计数漂移：`On-Demand Skills (10)` 实际 19 行（含 2 行删除标记）
- `k8s-logs` 是真实技能但**未登记**在该索引（本轮发现；建议随 R3 文档批次一并补齐）

（本地机观测范围限制：本决策只看得到 ai-system 仓与本机；组织内其它机器是否仍在使用该平台
不在本报告的可见范围内。）