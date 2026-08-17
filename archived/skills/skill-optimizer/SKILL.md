---
name: skill-optimizer
description: Use when optimizing Agent Skill definitions via static compliance checks, LLM quality evaluations, runtime trace crystallization, or direct user revision requests. Supports static/dynamic/trace/feedback modes with snapshot versioning and interactive review loops.
---

# Skill 优化器 (Skill Optimizer)

## Overview

本技能用于优化 Agent Skill 定义（`SKILL.md` 及其辅助文件）。支持四种原子优化模式，可单独执行或由 Agent 编排为顺序流程。

DiagnosticMutator 可修改目标 Skill 目录下的 `SKILL.md` 及辅助文件（脚本、references 等），也可新建缺失的辅助文件。修改范围仅限目标 Skill 目录，不会触及 skill-optimizer 自身或其他 Skill。

分步执行流程见 `workflow.md`（步骤 1 引导 / 步骤 2 环境准备 / 步骤 3 执行优化 / 步骤 4 加载到本地 / 步骤 5 上传至平台）。

## 三种优化模式

| 模式         | 含义                            | 适用场景             |
| :--------- | :---------------------------- | :--------------- |
| `static`   | 框架自动诊断（L1 静态合规 + L2 LLM 五维评估） | 用户无具体反馈，希望全面体检   |
| `dynamic`  | 基于 Agent Insight 运行日志优化       | 有历史运行记录，想修复实际问题  |
| `trace`    | 基于运行时 trace 结晶优化              | 有 trace 数据，想针对性优化   |
| `feedback` | 纯用户反馈驱动，不跑框架评估                | 用户有明确修改意见        |

## 附加 Action（P11 吸收）

| Action | 含义 | 对应思想 |
| :----- | :--- | :------- |
| `augment` | demo-augment：将成功执行示例（demos.json）沉淀为 SKILL.md 的 `## Examples` 区 | DSPy BootstrapFewShot |
| `validate` | held-out 验证门控：用 benchmark.json（skill-benchmark-generator 产物）对比候选快照 vs 当前基线，输出 PASS/FAIL 与 accept/reject 建议 | SkillOpt held-out gating |
| `tune-description` | description 调优：评估 frontmatter description 的路由触发质量并给出改写建议 | Claude skill-creator |

三者均为**候选优先 + 快照版本化 + 人工决策**：只写入新快照，不自动采纳；采纳走既有 `accept` action。

```bash
# 示例沉淀（demos.json: [{task, approach, result}, ...]）
./scripts/opt.sh --action augment --input /path/to/skill_dir --demos /path/to/demos.json
# held-out 验证（benchmark.json: [{task, expected_outcome}, ...]）
./scripts/opt.sh --action validate --input /path/to/skill_dir --benchmark /path/to/benchmark.json
# description 调优（可选 --routing-report 传入路由命中报告）
./scripts/opt.sh --action tune-description --input /path/to/skill_dir [--routing-report /path/to/routing.json]
```

> **模式选择注意**：当用户明确指定 `dynamic` 模式 / 动态优化 / 只使用运行日志时，执行 dynamic 而非 static+dynamic 组合。
> 当用户明确指定 `trace` 模式 / trace 优化 / 只使用 trace 数据时，执行 trace 而非 static+trace 组合。

**Review Loop 命令：**

```bash
./scripts/opt.sh --action accept --input /path/to/skill_dir
./scripts/opt.sh --action revert --target-version <version> --input /path/to/skill_dir
```

**Diff 查看器：**

```bash
uv run python scripts/diff_viewer.py --snapshots /path/to/skill-snapshots --title "skill-name"
uv run python scripts/diff_viewer.py --base /path/to/old --current /path/to/new --title "skill-name"
uv run python scripts/diff_viewer.py <old_dir> <new_dir> --static diff.html --title "skill-name"
uv run python scripts/diff_viewer.py --snapshots /path/to/skill-snapshots --title "skill-name" --no-open --output diff.html
```

## Outputs

- 默认情况下，优化器会在 `--project-dir` 指定的项目根目录下创建一个新的工作区：`{skill-name}-optimized-{时间戳}/`。
- **目录结构**：工作区采用两层结构，外层存放优化过程产物，内层存放纯 Skill 内容：

```
{skill-name}-optimized-{timestamp}/       ← 外层工作区（优化过程产物）
├── {skill-name}/                          ← 内层纯 Skill 目录（可加载到 .opencode/skills）
│   ├── SKILL.md
│   ├── scripts/
│   └── references/
├── snapshots/                             ← 版本快照（v0, v1, v1.1, ...）
│   ├── v0/
│   │   ├── SKILL.md
│   │   └── meta.json
│   └── v1/
│       ├── SKILL.md
│       ├── diagnoses.json
│       ├── OPTIMIZATION_REPORT.md
│       └── meta.json
└── OPTIMIZATION_REPORT.md                 ← 最新优化报告
```

  - **内层 `<skill-name>/`**：纯 Skill 内容，仅包含 `SKILL.md` 及其辅助文件（scripts、references 等）。加载到 `.opencode/skills/` 或上传到 Insight 平台时使用此目录。
  - **外层工作区**：包含优化过程的所有产物（snapshots、报告等），用于迭代优化和版本回溯。
  - `snapshots/`：版本快照（`v0`, `v1`, `v1.1`, ...），每个版本含 `meta.json`。
  - `diagnoses.json`：结构化诊断数据（位于对应快照版本目录内）。
  - `OPTIMIZATION_REPORT.md`：诊断结果 + 修改建议 + 版本信息（位于对应快照版本目录内及外层工作区根目录）。
- **迭代优化**：当需要针对已优化的结果继续迭代（如使用 `feedback` 模式），将 `--input` 指向**外层工作区目录**即可。

## 主要脚本 (Scripts)

- `scripts/opt.sh`: 核心入口脚本。负责环境初始化、执行不同模式的优化操作（`optimize`）、接受优化结果（`accept`）以及版本回滚（`revert`）。
- `scripts/main.py`: CLI 主入口（S1 拆分后保留）。核心辅助函数已移至 `scripts/core.py`；多 SKILL.md 时可用 `--parallel` 并行处理。
- `scripts/core.py`: 共享核心逻辑（LLM 客户端、SKILL.md 验证、辅助文件引用集成等），由 main.py 引入。
- `scripts/load_skill.sh`: Skill 加载脚本。归档旧 Skill 到 `~/.agent-insight/skill-history/` 并将优化后的 Skill 复制到指定位置。参数：`--new <优化后skill路径> --old <旧skill路径>`。
- `scripts/diff_viewer.py`: Diff 可视化工具 CLI 入口（S1 拆分后为薄入口）。计算逻辑在 `scripts/diff_core.py`，HTML 模板在 `scripts/html_report.py`。用于在浏览器中直观对比优化前后的版本差异，支持按快照目录或指定新旧目录进行比对。
- `scripts/model_config_detector.py`: 环境准备脚本。自动检测并提取当前环境的大模型配置，生成 `.env` 文件。
- `scripts/test_model_connectivity.py`: 连通性测试脚本。用于检查大模型 API 是否可用，确保后续优化流程能够正常调用 LLM。

## 参考文档 (References)

- 执行流程：[workflow.md](workflow.md)
- 架构与核心组件：[references/architecture.md](references/architecture.md)
- 评估分层与诊断：[references/evaluation.md](references/evaluation.md)
- Setup 异常交互模板：[references/setup-interactions.md](references/setup-interactions.md)
- Diff Review Loop 与快照版本：[references/diff-review-loop.md](references/diff-review-loop.md)
- 环境变量配置：[references/env-config.md](references/env-config.md)
- 故障排查：[references/troubleshooting.md](references/troubleshooting.md)
