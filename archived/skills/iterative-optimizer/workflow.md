# Iterative Optimizer Workflow

本文件定义 iterative-optimizer 的完整执行流程。SKILL.md 为入口摘要与工具清单，本文件为分步细节。

---

## 第一步：引导用户 & 初始化

### 1.1 检查是否已有配置文件

```bash
ls ./iter-config.yaml
```

**如果已存在**：直接跳到 1.5 选择模型。

**如果不存在**：进入 1.2 收集信息。

### 1.2 从用户输入中提取信息

用户的任务通常类似：

> 帮我迭代优化 /user/work/.opencode/skills/openeuler-docker-fault 这个 skill，目标是准确率达到 0.9 以上，最多跑 5 轮

从中提取：

- **skill 路径**：用户给出的完整路径
- **skill 名称**：从路径中取最后一级目录名
- **达标分数**：0~1 之间的小数（如 0.9 表示 90%），填入 `optimization.score_threshold`
- **最大轮次**：如 5

用户给出的路径统一存储为**目录路径**（如果给的是 SKILL.md 文件路径则取父目录）。

### 1.3 补充缺失信息

如果用户还没有提供以下信息，需要追问：

1. **测试框架**：当前仅支持 opencode
2. **测试任务 prompt**：每轮执行的具体任务
3. **达标分数阈值**（`optimization.score_threshold`）：0~1 之间的小数，如 0.9
4. **交互预设**（可选）：执行过程中可能需要的应答信息
5. **故障注入命令**（可选）：测试前注入和测试后清理的命令

不需要追问的（有默认值）：

- **优化任务 prompt**：默认 `请使用 skill-optimizer 技能基于 <SKILL_PATH> 这个 skill 的最近执行记录，动态优化这个 skill`
- **同步任务 prompt**：默认 `请使用 skill-sync 技能将 <SKILL_PATH> 上传到 insight 平台`
- **优化目标描述**（`optimization.goal`）：可选文字描述，不参与达标计算

### 1.4 生成配置文件

收集完后，在用户工作目录下生成 `iter-config.yaml`。

配置文件格式参考 `examples/iter-config-template.yaml` 或 `examples/docker-fault-iter-config.yaml`。

### 1.5 选择模型

先检查 `iter-config.yaml` 中是否已配置 `model` 字段：

```bash
python3 <skill_dir>/scripts/parse_config.py iter-config.yaml --get model
```

- **如果有值**（如 `deepseek/deepseek-chat`）：直接使用，跳过模型选择，进入 1.6。
- **如果为空或不存在**：执行 `opencode models` 获取可用模型列表，展示给用户选择。

记住最终确定的模型名（后续记为 `<MODEL>`）。

### 1.6 初始化工作空间

```bash
bash <skill_dir>/scripts/init_workspace.sh --model "<MODEL>"
```

该脚本会解析配置、创建日志目录、将模型名和所有配置写入 `.iter-state.env` 状态文件。

---

## 第二步：迭代循环

从 `.iter-state.env` 中读取配置。**你需要在内存中维护一份版本记录表，每轮更新**：

```
版本记录:
| 轮次 | Skill 版本路径                              | 得分 | 达标？ |
|------|---------------------------------------------|------|--------|
|  1   | iteration-logs/round-1/skill-snapshot/...   | 0.62 |  否    |
|  2   | iteration-logs/round-2/skill-snapshot/...   | 0.85 |  否    |
|  3   | <SKILL_PATH>（当前最新）                     | 0.93 |  是    |
```

每轮执行以下步骤：

### 2.0 递增轮次

```bash
ROUND=$(bash <skill_dir>/scripts/update_round.sh)
```

读取 MAX_ROUNDS，如果 ROUND 超出限制则终止循环。

### 2.1 备份当前 Skill

```bash
SNAPSHOT_PATH=$(bash <skill_dir>/scripts/snapshot_skill.sh \
    --skill-path "<SKILL_PATH>" \
    --round-dir "<WORK_DIR>/round-<ROUND>")
```

将 SNAPSHOT_PATH 记入版本记录表。

### 2.2 上传当前 Skill

```bash
bash <skill_dir>/scripts/oc_run.sh \
    --query "<TASK_SYNC>" \
    --model "<MODEL>" \
    --log "<WORK_DIR>/round-<ROUND>/sync-upload.log"
```

阅读返回的文本，如果在等待确认（如"是否上传？"），提取输出末尾的 `[SESSION_ID]`，用 `--session` 回复：

```bash
bash <skill_dir>/scripts/oc_run.sh \
    --session "<上一步返回的 SESSION_ID>" \
    --query "确认上传" \
    --model "<MODEL>" \
    --log "<WORK_DIR>/round-<ROUND>/sync-upload.log"
```

### 2.3 故障注入

```bash
bash <skill_dir>/scripts/fault_inject.sh --config iter-config.yaml --action inject \
    > <WORK_DIR>/round-<ROUND>/fault-inject.log 2>&1
```

未配置 `fault_injection` 时自动跳过。

### 2.4 执行测试任务（需要你判断）

这是你需要深度参与的步骤。

**第一次执行：**

测试任务的 query 必须**严格使用配置文件中 `tasks.query` 的原始内容**。oc_run.sh 会自动在 query 前面添加"不要调用 question 工具"的提示，不会修改你传入的任务内容本身：

```bash
bash <skill_dir>/scripts/oc_run.sh \
    --query "<TASK_EXECUTE>" \
    --model "<MODEL>" \
    --log "<WORK_DIR>/round-<ROUND>/execution.log"
```

**判断 oc_run.sh 返回的文本：**

1. **这是最终回答吗？** 如果内容是完整的分析报告、排查结果、解决方案，本步骤结束。

2. **这是在向用户提问吗？** 如果在询问信息，你需要：
   - 在交互预设中匹配对应条目（通过 trigger 关键词）
   - 用 `--session` 携带上一步返回的 sessionID，回复对应的 response（严格使用交互预设中的原始文字）：
   ```bash
   bash <skill_dir>/scripts/oc_run.sh \
       --session "<上一步返回的 SESSION_ID>" \
       --query "<匹配到的 response>" \
       --model "<MODEL>" \
       --log "<WORK_DIR>/round-<ROUND>/execution.log"
   ```

3. **重复判断**，直到获得最终回答或交互次数超过 10 次。

**判断技巧：**

- 包含明确问句（"请问...？"、"您的...是什么？"）→ 在等交互
- 输出是完整的分析报告或操作步骤列表 → 最终回答
- 拿不准 → 偏向最终回答（避免死循环）

### 2.5 故障清理

测试任务执行完毕后，**无论成功失败**，都必须执行：

```bash
bash <skill_dir>/scripts/fault_inject.sh --config iter-config.yaml --action cleanup \
    > <WORK_DIR>/round-<ROUND>/fault-cleanup.log 2>&1
```

### 2.6 评估结果

```bash
bash <skill_dir>/scripts/evaluate_result.sh \
    --round <ROUND> \
    --skill-name "<SKILL_NAME>" \
    --score-threshold "<SCORE_THRESHOLD>"
```

脚本会以 30 秒间隔轮询 Insight API，最多 20 次（10 分钟），等待评分生成。

**根据退出码判断：**

- 退出码 `0`：达标。记入版本记录表，结束循环。
- 退出码 `1`：未达标或超时无数据。记入版本记录表，继续优化。
- 退出码 `2`：错误。告知用户，由用户决定是否继续。

向用户报告：当前轮次、得分、达标阈值、评判理由。

### 2.7 优化 Skill

```bash
bash <skill_dir>/scripts/oc_run.sh \
    --query "<TASK_OPTIMIZE>" \
    --model "<MODEL>" \
    --log "<WORK_DIR>/round-<ROUND>/optimization.log"
```

阅读返回文本，如果有交互请求则提取 `[SESSION_ID]` 用 `--session` 回复。 执行后会直接修改原始 skill 文件。由于你在 2.1 已备份旧版本，不会丢失。

### 2.8 上传优化后的 Skill

```bash
bash <skill_dir>/scripts/oc_run.sh \
    --query "<TASK_SYNC>" \
    --model "<MODEL>" \
    --log "<WORK_DIR>/round-<ROUND>/sync-optimized.log"
```

阅读返回文本，如果有交互请求则提取 `[SESSION_ID]` 用 `--session` 回复。

### 2.9 回到 2.0

进入下一轮。`opencode run` 每次都是独立进程，自动加载最新 skill。

---

## 第三步：结束 & 汇报

循环结束后，向用户输出完整的**迭代优化报告**：

```
========================================
迭代优化报告
========================================
Skill 名称:     openeuler-docker-fault
Skill 原始路径:  /user/work/.opencode/skills/openeuler-docker-fault
优化目标:        准确率达到 0.9 以上
使用模型:        qwen-max-latest
终止原因:        达成优化目标 / 达到最大轮次

----------------------------------------
各轮次详情:
----------------------------------------
第 1 轮:
  使用 Skill 版本:  ./iteration-logs/round-1/skill-snapshot/
  执行得分:         0.62
  达标:             否
  评判摘要:         排查步骤缺少 cgroup 限制检查

第 2 轮:
  使用 Skill 版本:  ./iteration-logs/round-2/skill-snapshot/
  执行得分:         0.85
  达标:             否
  评判摘要:         缺少网络 namespace 排查

第 3 轮:
  使用 Skill 版本:  ./iteration-logs/round-3/skill-snapshot/
  执行得分:         0.93
  达标:             是
  评判摘要:         覆盖率达标，报告结构清晰

----------------------------------------
得分趋势:  0.62 → 0.85 → 0.93
----------------------------------------
最终生效 Skill:  /user/work/.opencode/skills/openeuler-docker-fault
历史版本保留在:  ./iteration-logs/round-N/skill-snapshot/ 目录下
完整日志:        ./iteration-logs/
========================================
```
