---
name: iterative-optimizer
description: 自动化迭代优化 skill 的完整流程。当用户希望通过反复执行测试任务、收集结果、优化 skill 来持续提升 skill 质量时，使用此技能。触发场景包括：用户提到"迭代优化"、"自动优化 skill"、"批量测试并改进"、"循环优化"、"多轮优化"等。即使用户只是说"帮我优化这个 skill 的效果"，也应触发此技能。此技能编排了 skill-sync、skill-optimizer 以及测试框架（如 opencode）之间的完整自动化循环。
---

# Iterative Optimizer

你是迭代优化的编排者。你的职责是驱动 skill 的"执行 → 评估 → 优化 → 再执行"循环，直到达成优化目标或达到最大轮次。

以下脚本工具可以自动完成**不需要模型判断**的步骤，你负责**需要理解和判断**的部分。

详细执行流程见 `workflow.md`（第一步：引导用户 & 初始化；第二步：迭代循环；第三步：结束 & 汇报）。

## 工具清单

所有脚本位于本 skill 的 `scripts/` 目录下。

| 脚本 | 功能 | 需要模型？ |
|------|------|-----------|
| `oc_run.sh` | opencode run 封装，解析 JSON 流，返回纯文本结果 | 否（但返回内容需要你判断） |
| `init_workspace.sh` | 解析配置、创建日志目录、生成 `.iter-state.env` | 否 |
| `update_round.sh` | 递增轮次计数，创建本轮日志目录 | 否 |
| `snapshot_skill.sh` | 备份当前版本 skill 到本轮日志目录 | 否 |
| `fault_inject.sh` | 执行故障注入或故障清理命令 | 否 |
| `evaluate_result.sh` | 调用 Insight API 轮询获取 answer_score，与阈值对比 | 否 |
| `parse_config.py` | 解析 iter-config.yaml，输出摘要或提取单字段 | 否 |

### oc_run.sh 说明

所有 opencode run 调用都通过 `oc_run.sh` 执行，不要直接调用 `opencode run`。

该脚本会：

1. 使用 `opencode run --format json` 执行，获取流式 JSON 输出
2. 过滤出 `type=text` 的文字内容（agent 回复的正文）
3. 检测到 `type=step_finish` 且 `reason=stop` 时结束（表示执行完毕）
4. 忽略 thinking、tool_use 等中间信息
5. 将过滤后的纯文本返回给你阅读和判断
6. 自动在每个 query **前面**添加"不要调用 question 工具"的提示，不修改原始任务内容
7. 默认超时 15 分钟

**新会话执行：**

```bash
bash <skill_dir>/scripts/oc_run.sh \
    --query "<任务内容>" \
    --model "<MODEL>" \
    --log "<日志文件路径>"
```

**继续指定会话（通过 sessionID）：**

```bash
bash <skill_dir>/scripts/oc_run.sh \
    --session "<SESSION_ID>" \
    --query "<回答内容>" \
    --model "<MODEL>" \
    --log "<日志文件路径>"
```

**关于 sessionID：** oc_run.sh 每次执行后，输出的最后一行格式为 `[SESSION_ID] ses_xxxx`。你需要提取这个 sessionID，在后续需要继续同一会话时通过 `--session` 传入。这比 `-c` 模式更稳定，能精准定位到具体的会话。

需要你（模型）参与判断的环节：

- oc_run.sh 返回的文本是"最终回答"还是"在向用户提问"
- 如果是提问，根据交互预设选择回答，用 `--session` 携带 sessionID 继续对话
- 每轮结束后向用户报告进展

## 流程摘要

1. **第一步 引导 & 初始化**：检查/生成 `iter-config.yaml`，选择模型，初始化工作空间（详见 `workflow.md`）
2. **第二步 迭代循环**：备份 → 上传 → 故障注入 → 测试 → 清理 → 评估 → 优化 → 上传 → 下一轮
3. **第三步 结束 & 汇报**：输出迭代优化报告

## 注意事项

1. **[最重要] bash 工具超时设置**：你在调用 bash 工具执行 scripts 目录下的任何脚本时，**必须将 bash 工具的超时时间设置为足够长（至少 900 秒 / 15 分钟）**，不要使用默认的 2 分钟超时。这些脚本的执行时间远超 2 分钟：oc_run.sh 单次可能运行 10-15 分钟，evaluate_result.sh 轮询可能持续 10 分钟。如果你的 bash 工具有超时参数，请设为 900 或更大。如果 bash 工具不支持自定义超时，请确保不会在脚本运行过程中主动中断它。

2. **所有脚本一定会返回结果**。每个脚本在任何情况下（成功、失败、超时）都保证向 stdout 输出内容。你只需要等待命令执行完毕、读取返回的输出内容，然后根据内容决定下一步。**不要因为等待时间长就中断、跳过或重试。**

3. **不要直接调用 opencode run**。所有 opencode 调用统一通过 `oc_run.sh` 执行。

4. **测试任务的 query 必须严格保持原样**。`oc_run.sh` 会自动在所有 query 前面（而非后面）添加"不要调用 question 工具"的提示，不会修改你传入的任务内容。你只需确保传给 `--query` 的内容与配置文件一致即可。

5. **所有 oc_run.sh 返回后都必须检查文本内容**。不仅是测试任务，上传、优化等步骤也可能产生交互。交互预设中的条目适用于所有步骤。

6. **超时设置**：oc_run.sh 内部默认 15 分钟超时，如需调整可用 `--timeout` 参数。

7. **版本备份在优化之前**。Step 2.1 必须在 Step 2.7 之前执行。

8. **优化 prompt 要带完整路径**。skill-optimizer 需要知道要操作哪个目录。

9. **评估轮询**：evaluate_result.sh 以 30 秒间隔轮询，最多 20 次（10 分钟）。

10. **容错**：oc_run.sh 或其他脚本失败时不要直接终止，记录错误并告知用户。

11. **透明沟通**：每轮的开始和结束都向用户简要汇报进展。

12. **日志完整性**：oc_run.sh 通过 `--log` 参数自动将原始 JSON 流写入日志文件。

## 参考文件

- `workflow.md` — 完整分步执行流程
- `examples/iter-config-template.yaml` — 配置文件模板
- `examples/docker-fault-iter-config.yaml` — 完整配置示例
