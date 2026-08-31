---
name: task-splitter
description: 基于 OpenSpec 规范和《服务间交互契约》生成原子开发任务（Task Card），按服务依赖编排为全局执行计划。当用户提及"拆分任务""生成原子任务""任务清单""全局任务排序""开发计划"等关键词时触发。
version: 1.1.0
---

# task-splitter

## 核心职责

将已确认的 OpenSpec 规范和 `interop_contract.yml` 契约转化为**可独立执行、可验证、严格遵循契约约束**的原子开发任务（Task Card），并按服务依赖关系编排为全局有序的执行计划。Task Card 是主链 develop/dev-setup 的统一消费单位，必须与 `methodologies/providers/openspec-cn/templates/tasks-template.md` 格式一致。

## 依赖

| 依赖 | 说明 |
|------|------|
| `spec-updater` Skill (methodologies/providers/openspec-cn/skills/spec-updater/) | 提供更新后的 Spec 文件路径和本次迭代涉及的服务列表 |
| `contract-maintainer` Skill | 提供最新 `interop_contract.yml`（由 `generate_contract.py` 保证一致性） |
| `repositories/{service_id}.yaml` | 服务技术栈（用于 Code Quality 推导：protocol → MQ/RPC 检查项） |
| `openspec/changes/<change-name>/` | 项目规范源文件目录结构 |

## 触发条件

本 Skill 绑定 spec runtime（见 `skills/README.md`），在 **Phase 6 — Task Planning** 阶段由 AI 推荐或自主决策触发，无需单独的触发流程。前提：`specs/` 与 `contracts/interop_contract.yml` 就绪。

用户消息包含以下关键词之一时，作为**显式请求**可直接触发（对应人工指定拆分场景）：
- "拆分任务" / "生成原子任务" / "任务清单"
- "全局任务排序" / "全局排序" / "整合任务"
- "开发计划" / "实现计划" / "迭代任务"
- "为 [服务名] 拆分" / "为 [服务名] 生成任务"

## 核心能力

| ID | 能力 | 触发词 | 描述 |
|----|------|--------|------|
| T1 | 单服务任务拆分 | "拆分 [服务名] 的任务" | 读取指定服务的 Spec 和契约中相关条目，生成 Task Card（`tasks/cards/T-{id}.md`） |
| T2 | 批量服务拆分 | "拆分所有受影响服务" | 对迭代涉及的所有服务依次执行 T1，并为每服务生成 `{service}-tasks.md` 索引 |
| T3 | 全局任务编排 | "全局排序"、"整合任务" | 分析所有 Task Card 间的服务调用依赖（RPC/MQ），输出 `tasks/global-plan.md`（按"被调用方先实现"排序 + blocking 边） |
| T4 | 契约片段注入 | （自动执行） | 拆分时为每个 Task Card 自动粘贴关联的契约条目 ID 和关键约束，确保实现不偏离 |
| T5 | 验收标准生成 | "验收标准"、"验收条件" | 基于 Spec 的验收场景和契约的错误处理规则，为每个 Task Card 生成 Given-When-Then 验收标准 |

## 工作流

```mermaid
graph TD
    A[用户提出拆分请求] --> B[激活 task-splitter]
    B --> C{请求类型?}

    C -->|单服务| D[定位变更目录 openspec/changes/&lt;change-name&gt;/]
    C -->|批量| E[从 spec-updater 获取受影响服务列表]

    D --> F[读取服务 Spec + interop_contract.yml 相关条目]
    E --> G[遍历服务列表，循环执行 T1]

    F --> H[按 tasks-template.md 生成 Task Card → tasks/cards/T-{id}.md]
    G --> H

    H --> I[T4: 注入契约片段 + 6.X 代码质量检查推导 + branch 字段]
    I --> J{是否需要验收标准?}
    J -->|是| K[T5: 补全验收标准]
    J -->|否| L

    K --> L{是否需要全局排序?}
    L -->|是| M[T3: 分析 RPC/MQ 依赖，输出 tasks/global-plan.md 引用 card ID]
    L -->|否| N[输出 Task Card 清单]
    M --> N
    N --> O[写入 tasks/ 目录，询问用户确认]
```

## 输出目录结构

```
openspec/changes/<change-name>/
├── tasks/
│   ├── cards/                     # Task Card（task-splitter 输出，每任务一卡，tasks-template.md 格式）
│   │   ├── T-001.md
│   │   ├── T-002.md
│   │   └── ...
│   ├── <service-name>-tasks.md   # （可选）单服务任务索引，引用 cards/ 中的 T-id
│   └── global-plan.md            # 全局排序后的执行计划（T3 输出，引用 card ID + blocking 边）
├── specs/                         # spec-updater 维护
├── contracts/                     # contract-maintainer 维护
└── design.md
```

> **tasks.md 已淘汰**：任务权威源是 `tasks/cards/*.md`，不再生成变更根目录的 `tasks.md` 用户入口索引（避免与 cards/ 双源）。归档时完成度以 `tasks/cards/*.md` 为准（见 `archive-openspec` skill）。

> **Task Card 位置约定**：CLI 提供方按 `*/tasks/cards/*.md` 枚举任务 ID（`cli/services/providers.py:task_ids`），develop/dev-setup 从这些卡片读取 `branch` / `Completion Definition` / 代码质量检查。因此每张任务卡必须落在 `tasks/cards/T-{id}.md`。

## 内嵌指令模板

各能力的详细执行指令见 `workflow.md`：

- T1: 单服务任务拆分
- T2: 批量服务拆分
- T3: 全局任务编排
- T4: 契约片段注入（自动执行）
- T5: 验收标准生成

Task Card 采用 `methodologies/providers/openspec-cn/templates/tasks-template.md` 的字段结构与代码质量检查清单（见 workflow.md「Task Card 字段」）。

## 与 spec-updater 和 contract-maintainer 的协作

| 层面 | spec-updater | contract-maintainer | task-splitter |
|------|-------------|-------------------|--------------|
| 职责 | 写源文件（Spec + 场景清单） | 读源文件，生成契约 | 读源文件+契约，生成 Task Card |
| 产物 | specs/*.md, switch_scenarios.yml | interop_contract.yml | tasks/cards/T-*.md, global-plan.md |
| 触发 | 用户提需求 | spec-updater 完成 | spec-updater + contract-maintainer 就绪 |
| 关系 | 最上游 | 中游 | 最下游 |

协作流程：
`spec-updater` (S1-S3) → `openspec-cn validate` → `contract-maintainer` (生成契约) → `openspec-cn validate` → **task-splitter** → 输出 Task Card + global-plan

## 初始化检查

首次激活时自动确认：

1. `openspec/changes/<活跃变更名>/specs/` 目录存在且包含至少一个服务子目录。
2. `openspec/changes/<活跃变更名>/contracts/interop_contract.yml` 文件存在且格式有效。
3. 若 1/2 缺失，提示用户先运行 `spec-updater` 完成需求录入和 `contract-maintainer` 契约生成。
4. 若 `tasks/cards/` 目录不存在，自动创建。

## 与 AGENTS.md 的关系

- Task Card 位于 `openspec/changes/<change-name>/tasks/cards/` 下，与其他源文件并列。
- 任务拆分时引用 AGENTS.md 中的"关键设计决策"约束，确保任务不偏离已确认的设计。
- 单任务工时遵循 AGENTS.md 规范（4h ≤ 单任务 ≤ 8h），超 8h 必须拆分。
