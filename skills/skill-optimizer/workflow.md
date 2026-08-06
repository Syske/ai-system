# Skill Optimizer Workflow

本文件定义 skill-optimizer 的分步执行流程。SKILL.md 为入口摘要、模式说明与参考清单，本文件为执行细节。

---

## 步骤 1：优化前引导

收到用户优化请求后，Agent **先从用户消息中提取已明确的信息，仅对缺失项进行追问**。如果用户的意图已经足够明确，则跳过问答直接进入步骤 2。

**1.1 确认目标**：确认目标 Skill 路径（包含 `SKILL.md` 的目录）。

**1.2 确定优化方式**：询问用户想怎么优化，从回答中确定模式：

```
Agent: 收到！在开始优化前想先确认，你想怎么优化这个 Skill？（可多选）
      a) 我有具体想改的地方（feedback）
      b) 帮我跑一轮自动诊断（static）
      c) 结合运行日志来分析实际问题（dynamic）
      d) 结合 trace 数据来针对性优化（trace）
```

**选项组合到模式的映射：**

| 用户选择  | 模式                        | 后续动作                           |
| :---- | :------------------------ | :----------------------------- |
| a     | `feedback`                | 收集反馈内容后执行                      |
| b     | `static`                  | 直接执行                           |
| c     | `dynamic`                 | 检查 Insight 平台可用性后执行            |
| d     | `trace`                   | 检查 trace 数据可用性后执行             |
| b + c | `static` → `dynamic`      | 检查 Insight 平台可用性后执行            |
| a + b | `static` → `feedback` 顺序编排 | 先跑静态诊断，再根据反馈调整                 |
| a + c | `dynamic` → `feedback` 顺序编排 | 先跑动态优化，再根据反馈调整                |
| a + d | `trace` → `feedback` 顺序编排 | 先跑 trace 优化，再根据反馈调整             |
| b + d | `static` → `trace`        | 先跑静态优化，再根据 trace 数据优化        |
| a + b + d | `static` → `trace` → `feedback` 顺序编排 | 先跑静态优化，再根据 trace 优化，再根据反馈调整 |
| a + c + d | `trace` → `dynamic` → `feedback` 顺序编排 | 先跑 trace 优化，再根据运行日志优化，再根据反馈调整 |
| a + b + c | `static` → `dynamic` → `feedback` 顺序编排 | 先跑静态诊断，再根据运行日志优化，再根据反馈调整            |
| a + b + c + d | `static` → `trace` → `dynamic` → `feedback` 顺序编排 | 先跑静态优化，再根据 trace 优化，再根据运行日志优化，再根据反馈调整 |

- 当涉及 c（运行日志）时：确认 Agent Insight 平台可用（`~/.agent-insight/.env` 或环境变量中有配置 `AGENT_INSIGHT_HOST` 和 `AGENT_INSIGHT_API_KEY`），不可用则提前告知用户并降级。
- 当涉及 d（trace 数据）时：确认 trace 数据来源可用（本地 trace 文件、Foundry traces 或其他 trace 数据源），不可用则提前告知用户并降级。

**意图已明确时跳过问答**：

如果用户在初始请求中已经表达清楚了优化方式，Agent 直接确定模式并进入步骤 2，不再重复提问。

```
用户: 用静态优化优化 xx skill，没有反馈意见。
Agent: 好的，对 xx skill 执行静态优化。开始准备环境……
```

```
用户: 结合运行日志优化一下 troubleshooter skill。
Agent: 好的，对 troubleshooter skill 执行动态优化。先检查 Insight 平台连接……
```

```
用户: xx skill 的描述太长了，帮我精简一下。
Agent: 收到，针对反馈"描述太长需精简"来优化 xx skill。开始准备环境……
```

**复杂场景**（多模式顺序编排）：

当用户同时需要多种模式时，Agent 编排为顺序流程，每步之间显示 Diff 并确认：

```
用户：全部要改，skill中还需增加关于硬件问题的排查和处理。
Agent: 我会分步执行：
      1. 先执行自动诊断做静态优化
      2. 再根据运行日志做动态优化
      3. 最后根据你的反馈来调整
      每步完成后你都可以看到优化点，不满意随时停。继续吗？
```

---

## 步骤 2：环境准备 (Setup)

**所有命令必须在** **`skill-optimizer`** **目录下执行。**

```bash
cd /path/to/.opencode/skills/skill-optimizer
./scripts/opt.sh --help                                    # 检查环境、自动创建 .opt 虚拟环境并安装依赖
uv run python scripts/model_config_detector.py             # 自动检测模型配置并写入 .env
uv run python scripts/test_model_connectivity.py --env-file .env  # 连通性测试（必须通过才可继续）
```

**⚠️ 连通性测试失败时必须进入环境异常交互流程**：

当 `opt.sh` 输出包含 `__CONNECTIVITY_FAILED__` 标记或以 exit code 2 退出时，Agent **必须停止**，不得继续执行优化，而是立即进入环境异常交互流程：

```
Question: "模型连通性测试未通过，请重新配置以确保后续流程顺利进行："
Options: "获取 DeepSeek 的 api_key", "获取符合 OpenAI 规范的 LLM 的 base_url、api_key、model_name", "取消"
```

用户提供信息后，更新 `.env` 文件，然后**重新执行连通性测试**。只有测试通过后才可进入步骤 3。

其他异常场景的交互处理见 [references/setup-interactions.md](references/setup-interactions.md)。

---

## 步骤 3：执行优化

> **⚠️ 运行框架重要提示 (Framework Notice)**：
> 本 Skill 的执行涉及深度的静态分析、LLM 调用以及代码变异与验证。**完整优化流程的运行时长极有可能超过 10 分钟**。请调度本 Skill 的运行框架（Agent/Plugin）务必放宽调用超时限制（建议设置为 20 分钟或以上），以防因超时导致优化中断。

根据步骤 1 确定的计划，依次执行对应模式。如果是多模式顺序编排，每个子步骤完成后都要执行步骤 3.3（Review），用户确认后再进入下一个子步骤。

**⚠️ 动态优化的前置检查**：

`dynamic` 模式的核心依赖是执行日志中 `skill_issues` 列表里的 **`improvement_suggestion`**（优化建议）。在执行优化前会自动检查是否具备可用的优化建议，如果没有则**不进行后续优化**，直接停止并提示：

| 检查项 | 不通过时的行为 |
| :--- | :--- |
| Agent Insight 平台不可用 | **停止**，提示用户配置平台连接 |
| 未获取到执行日志（空列表） | **停止**，提示用户先运行 Skill 产生日志，或改用 `static` 模式 |
| 日志中 `skill_issues` 无 `improvement_suggestion` | **停止**，提示用户改用 `static` 模式 |

检查通过后，会输出获取到的优化建议统计：`📊 获取到 X 条执行日志，共 Y 条优化建议。`

Agent 收到停止提示后，应向用户说明情况并建议下一步操作（如改用 `static` 模式、先运行 Skill 等）。

**⚠️ trace 优化的前置检查**：

`trace` 模式的核心依赖是运行时 trace 数据中的 **`improvement_suggestion`**（优化建议）。在执行优化前会自动检查是否具备可用的优化建议，如果没有则**不进行后续优化**，直接停止并提示：

| 检查项 | 不通过时的行为 |
| :--- | :--- |
| trace 数据不可用 | **停止**，提示用户提供 trace 数据 |
| 未获取到 trace（空列表） | **停止**，提示用户提供 trace 数据，或改用 `static` 模式 |
| trace 中无 `improvement_suggestion` | **停止**，提示用户改用 `static` 模式 |

检查通过后，会输出获取到的优化建议统计：`📊 获取到 X 条 trace，共 Y 条优化建议。`

Agent 收到停止提示后，应向用户说明情况并建议下一步操作（如改用 `static` 模式、提供 trace 数据等）。

**3.1 执行优化命令**（示例）：

根据步骤 1 确定的模式执行，例如：

```bash
./scripts/opt.sh --action optimize --mode static   --input /path/to/skill_dir --project-dir /path/to/project
./scripts/opt.sh --action optimize --mode dynamic  --input /path/to/skill_dir --project-dir /path/to/project
./scripts/opt.sh --action optimize --mode trace    --input /path/to/skill_dir --project-dir /path/to/project --trace /path/to/trace_data
./scripts/opt.sh --action optimize --mode feedback --input /path/to/skill_dir --project-dir /path/to/project --feedback "用户反馈的具体内容"
./scripts/opt.sh --action optimize --mode feedback --input /path/to/skill_dir --project-dir /path/to/project --feedback /path/to/feedback.txt
```

- `--project-dir`（`-p`）：项目根目录，优化后的工作区将在此目录下创建。**必须由 Agent 传入当前项目的根目录路径**。
- `--feedback` 参数接受字符串，可以是反馈内容本身，也可以是文件路径（自动识别）。

**3.2 显示 Diff**：

优化命令执行完成后，系统会自动生成并打开 Diff 页面（浏览器），Agent **无需手动执行**任何命令来显示 Diff。

**3.3 引导用户 Review**：

Diff 页面打开后，Agent **不能沉默**，必须主动引导用户：

- 告知用户已打开 Diff 页面，可以查看优化前后的具体变化。
- 请用户看完后反馈感受：满意就说 Accept，有想改的地方直接告诉 Agent 修改意见。
- 提示用户也可以使用 Diff 页面上的 Accept / Revise / Revert 按钮快捷操作。
- **如果是多步顺序流程**：确认用户满意当前步骤后再执行下一步，用户随时可以停止。

**单模式示例**：

```
Agent: ✅ 优化完成！已打开 Diff 页面，你可以看看优化前后的变化。
      看完后告诉我：
      - 满意的话我就确认保存
      - 有想调整的地方直接说，我继续改
      - 也可以用 Diff 页面上的按钮快捷操作
```

**多步流程示例**：

```
Agent: ✅ 静态优化完成！已打开 Diff 页面，你可以看看变化。
      看完后告诉我：
      - 满意的话我继续执行下一步（动态优化）
      - 有想调整的地方直接说，我先改完再往下走
      - 也可以到此为止，不继续后面的步骤了
```

**3.4 重复 3.1-3.3**：如果有多个模式待执行，循环直到所有模式完成或用户选择停止。

**3.5 附加 Action（P11 吸收，可选）**：按需在优化后执行候选优先的辅助动作——均只写入新快照、不自动采纳，采纳走既有 accept：

| Action | 命令 | 用途 |
| :----- | :--- | :--- |
| augment | `./scripts/opt.sh --action augment --input <skill_dir> --demos <demos.json>` | 将成功执行示例沉淀为 `## Examples` 区（DSPy BootstrapFewShot 思想） |
| validate | `./scripts/opt.sh --action validate --input <skill_dir> --benchmark <benchmark.json>` | held-out 门控：候选 vs 基线通过率对比，输出 accept/reject 建议（SkillOpt 思想） |
| tune-description | `./scripts/opt.sh --action tune-description --input <skill_dir> [--routing-report <routing.json>]` | description 路由触发质量评估与改写建议（Claude skill-creator 思想） |

交互流程与快照版本结构详见 [references/diff-review-loop.md](references/diff-review-loop.md)。

---

## 步骤 4：加载到本地

所有优化步骤完成后，询问用户是否将优化后的 Skill 加载到当前项目：

```
Question: "✅ Skill 优化完成！(位于 <inner-skill-path>)。是否将此技能加载到当前项目的 .opencode/skills 目录下以便立即使用（需要重启）？"
Options: "是，加载到 .opencode/skills 目录", "否，保持当前位置"
```

**用户同意**：

使用 `load_skill.sh` 脚本一键完成归档旧 Skill + 加载新 Skill。Agent 只需提供两个参数，无需关注内部细节：

```bash
./scripts/load_skill.sh --new <优化后的skill文件夹绝对路径> --old <待替换的旧skill文件夹绝对路径>
```

- `--new`：优化后的纯 Skill 目录绝对路径（即外层工作区中的内层 `<skill-name>/` 子目录）
- `--old`：当前 `.opencode/skills/` 下待替换的旧 Skill 目录绝对路径

示例：

```bash
./scripts/load_skill.sh \
  --new /Users/xxx/project/offline-disk-fault-diagnosis-optimized-20260414_114917/offline-disk-fault-diagnosis \
  --old /Users/xxx/project/.opencode/skills/offline-disk-fault-diagnosis
```

脚本会自动完成：

1. 将旧 Skill 归档到 `~/.agent-insight/skill-history/<skill-name>-<timestamp>`（重名自动追加序号）
2. 将优化后的 Skill 复制到旧 Skill 的原位置
3. 提示用户重启 opencode 生效

**用户不同意**：告知 Skill 保持在当前位置，后续可手动调用 `load_skill.sh` 加载。

---

## 步骤 5：上传至 Insight 平台

**如果检测到 `skill-sync` 技能可用，则主动询问用户是否上传；否则仅在用户明确要求时执行。**

**5.1 检测 skill-sync 是否可用**：

```bash
# 检查 skill-sync 是否存在于 .opencode/skills 或项目 skills 目录
ls .opencode/skills/skill-sync/SKILL.md 2>/dev/null || ls skills/skill-sync/SKILL.md 2>/dev/null
```

**5.2 如果 skill-sync 可用，主动询问**：

```
Question: "检测到 skill-sync 技能可用。是否将优化后的 Skill 上传到 Agent Insight 平台？"
Options: "是，上传到 Insight 平台", "否，仅保存在本地"
```

**5.3 用户同意上传时，调用 skill-sync 技能**：

```bash
node <skill-sync-path>/scripts/push.js <优化后的skill绝对路径>
```

> **注意**：上传路径应指向内层纯 Skill 目录（`<output-path>/<skill-name>/`），而非外层工作区目录。

**5.4 如果 skill-sync 不可用**：仅当用户明确要求"上传/同步/保存到 Insight"时，提示用户需要先安装 skill-sync 技能。
