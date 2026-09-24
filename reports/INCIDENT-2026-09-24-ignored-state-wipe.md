# Incident Report — 2026-09-24 仓库内被忽略状态被整体清空

| Field | Value |
|---|---|
| Type | Incident / Post-mortem（事实记录；**不新增能力**——护栏见 `reports/P72-PROTECTED-PATHS.md`） |
| Severity | 中（机器本地运行态不可恢复；版本化资产零损失） |
| Author | AI Maintainer（事故责任方：本会话） |
| Date | 2026-09-24 |
| Scope | `ai-system` 仓库工作树内的**未跟踪 + 被忽略**路径 |

---

## 1. 摘要

我在执行一次提交时，因 shell 引号错误让 bash **实际执行了 `git clean -fdx`**，导致 `ai-system`
工作树内**所有未跟踪与被忽略路径被删除**。版本化文件（100+ 提交、全部跟踪资产）**零损失**；
机器本地的运行时态（约 200 份运行日志、指标快照）**不可恢复**。

## 2. 时间线

| 时刻 | 事件 |
|---|---|
| T0 | 执行 `git commit -q -m "<长中文提交信息>"`；信息内含**反引号**包裹的示例（`git clean -fdx`、`capabilities.{…}`） |
| T0+ | 双引号字符串触发 **shell 命令替换** → bash 执行 `git clean -fdx`（并尝试执行 `capabilities.develop`，报 `command not found`） |
| T0+ | `git clean` 输出被拼入提交信息（"Removing archived/skills/…、Removing cli/__pycache__/…"），提交本身**成功** |
| T0+ε | 症状暴露：`logs/`、`metrics/`、`.ai-system/`、`config/environments/local.yaml` 消失；`path-audit` 报 2 条断链 |
| T1 | 损失评估 + 恢复（见 §4）；`path-audit` 归零、门禁全绿 |

## 3. 根因链（5 Whys）

1. **为什么被删？** 一条 `git clean -fdx` 被执行。
2. **为什么会被执行？** 提交信息用 `-m "…"` 传入，文本里的**反引号**在双引号内是命令替换语法 → 被当命令执行。
3. **为什么会造成损失？** 删除目标（`logs/`、`metrics/`）**位于仓库工作树内且被 gitignore** ——
   正好是 `-x`（含被忽略文件）的清除目标；`-f` 免询问、`-d` 连目录。
4. **为什么损失不可挽回？** 这些内容**不在 git 里**（按既有设计：运行时态机器本地、不入库），
   且**没有第二副本**（唯一副本在仓库内且可被一条命令清除）。
5. **为什么没被制度挡住？** ① 没有任何"受保护路径 / 破坏性操作"的声明与检测
   ② 提交信息的 shell 纪律未成文（本会话既有约定只覆盖"heredoc 用引号定界"，未禁止 `-m` 携带反引号）。

**一句话根因**：**运行时态与关键资产被放在"可被一条命令清除"的位置，且破坏性操作无声明、无检测、无纪律。**

## 4. 影响与恢复

| 路径 | 记录 | 性质 | 现状 |
|---|---|---|---|
| 跟踪文件（100+ 提交） | — | 版本化 | ✅ 零损失 |
| `ai-system/logs/`（约 200 份运行日志，含 2026-09-23 三份本会话日志） | ❌ | 机器本地 | 已迁至 `<workspace>/logs/`（`3c7dd9f`）；本日重建 1 份（`logs/maintain-20260924-incident-and-recovery.md`） |
| `ai-system/metrics/`（历史快照） | ⚠️ 历史不可恢复 | 机器本地·可再生成 | 已迁至 `<workspace>/metrics/`（`e488ec7`）；当期快照重新生成 |
| `config/environments/local.yaml` | ✅ | **可选覆盖层** | 无功能损失：机器层 `~/.config/ai-system/env.yaml` 完好（backend=idea、jdk8、maven 实测可解析）；模板仍在 |
| `.ai-system/` | — | 工具生成态 | 按需再生 |
| 两处路径引用断链 | — | 文档 | 已修（`d514804`）：其中一处正是 memory 以 `logs/**` 为**唯一证据** → 已改写并写入「记忆不得以 logs 为唯一证据」的教训 |

## 5. 教训（已验证、可复用）

1. **"未提交/被忽略" ≠ 安全**：一条命令即可全灭；**位置**（在仓库工作树内）就是风险本身。
2. **提交信息禁用 `-m` + 反引号/`$()`**：一律 `git commit -F -` + **引号定界 heredoc**（`<<'MSGEOF'`）。
3. **破坏性命令（`git clean -fdx`、`git reset --hard`、`git checkout -- .`、`git stash drop`、`rm -rf`）
   默认拒绝**；确需执行须先 `--dry-run`（如 `git clean -ndx`）列出清单并请求用户确认。
4. **记忆/文档不得把机器本地路径（`logs/**`）当作唯一证据**：引用 commit sha 或 `file:line`，或显式标注 `[machine-local]`。

## 6. 后续（护栏 → 已立案，待裁定）

上述教训 1/3/4 属于**新增能力**（受保护路径 + 破坏性操作默认拒绝 + 可检测），
已按流程立案：`reports/P72-PROTECTED-PATHS.md`（Status Proposed，待审）。本报告不实施任何能力改动。