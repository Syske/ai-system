# AI Runtime Engine 架构评估报告（2026-07）

## 一、评估范围与方法

- 对象：ai-workspace 全套 AI Runtime Engine（ai-system/ 各层 + 工作区根目录布局 + ai-runtime/ 平台层）
- 方法：platform-governor 治理维度 + runtime-analysis 六维（结构 / 职责 / 依赖 / 一致性 / 上下文效率 / 演进治理）
- 基线：本月已完成的 workflow 层优化（八段契约）与 runtime 层修复（R1-R5）、变更控制规则（Operating Rules v1.2）

## 二、总体判断

**分层骨架健康，不需要推倒式重构；需要一次"收敛治理"。**

依赖方向正确（Workflow → Runtime → Rules → Standards → Skills，无反向依赖），各层职责单一，治理资产（policy / lint / contract / rfc / metrics）齐备。问题集中在**定义多源分裂、平台层游离、文档-现实漂移**三类"漂移型"问题，均可增量修复，符合 Evolution over rewrite。

## 三、逐层健康度

| 层 | 状态 | 说明 |
|---|---|---|
| Workflow（workflows/） | 健康 | 八段契约、链路闭合、README 索引（本月已优化） |
| Runtime（templates/runtime/） | 健康 | base 契约完备（生命周期/状态/错误处理），R1-R5 已修复 |
| Operating Rules（governance/） | 健康 | v1.2：变更控制、工作区纪律、平台技能边界齐备 |
| Standards（governance/standards/） | 良好 | 目录已正名；7 个语言/框架预留位空缺（已知搁置） |
| Skills（skills/） | 良好 | 31 个技能 + architecture 系列；有 skill-policy 与 lint 工具治理 |
| Loaders（loaders/） | 健康 | 按需加载策略明确，引用已修复 |
| Routing（routing/） | 健康 | 缩表 v2：11 个 workflow 全部有路由 + 3 旧别名 + 2 standalone skill 入口；skill/pipeline/hooks 移除（SSOT） |
| Config（config/） | 健康 | A1 已完成收敛：yaml 退化为注册表三字段 |
| Frameworks（frameworks/） | 雏形 | context7/serena/grilling 适配器多为 README+version 占位 |
| ~~平台层（../ai-runtime/）~~ | **已归档** | 内容为单项目 hook 配置 + npm 残留（不可重用）；移入 archived/，引用从 AGENTS.md/合同/bootstrap 全部移除 |
| CLI（cli/） | 正常 | Python 薄入口 + opsx 命令提示词，符合合同"CLI 保持薄" |

## 四、架构级发现（按优先级）

### A1 — Workflow 定义三源分裂（高 · 违背 SSOT）

同一 workflow 存在三处定义：

```text
workflows/develop.md            入口契约（人读，本月更新）
config/workflows/develop.yaml   机器配置（inputs/outputs/next/stop_conditions）
templates/runtime/runtime-develop.md  执行细节
```

实测漂移（develop 为例）：

| 维度 | md | yaml |
|---|---|---|
| 必填输入 | Project ID, Task ID | workspace, project, task_id（多一个 workspace，命名体系不同） |
| 停止条件 | L2/L3 分级 + Plan not approved | workspace_missing…build_failed/test_failed（粒度不同） |
| 输出 | 5 项（含 Updated Workspace Context） | 4 项（implementation_report 等，名称不同） |

风险：消费 yaml 的引擎与读 md 的 agent 行为分叉 → 直接威胁"稳定产出"。

建议（二选一，推荐前者）：
- **md 为唯一语义源**：yaml 退化为注册表所需的最小字段（name / workflow / runtime 路径），删除 inputs/outputs/next/stop_conditions 重复段
- yaml 为唯一机器源：md 中 Inputs/Outputs/Next 声明改为"由 yaml 生成"，需要生成工具支撑（成本高）

### A2 — 平台适配层游离于治理之外（高）

`ai-bootstrap.yaml` 的 layers 引用 `../../ai-runtime`（含 claude/ 配置、opencode/ 包、openspec/），是真实活跃的第四实体；但 AGENTS.md 与 AI_DEVELOPMENT_CONTRACT 的架构图**均未提及**。未治理的层 = 不受契约保护、无职责边界声明。

建议：先文档承认（AGENTS.md 增补 ai-runtime/ 职责行 + 合同架构图补一节"Platform Adapters"），物理迁移（如并入 ai-system/adapters/）列入演进路线图，不急于搬家。

### A3 — 架构文档与现实漂移（中）

- AI_DEVELOPMENT_CONTRACT 架构图写 `runtime/`，实际为 `templates/runtime/`；未列 loaders/ frameworks/ maintainers/ metrics/ rfc/ archived/
- AGENTS.md 工作区结构图 `projects/` 出现两次（第二处应为 `specs/`），未提 workspaces/ repositories/ methodologies/ ai-runtime/
- 工件位置三套约定并存：AGENTS.md 的 `projects/<project>/openspec/` vs runtime 的 `workspaces/{project_id}/` vs `specs/`

风险：文档误导 agent 的路径解析与上下文加载 → 威胁"注意力效率"与新会话冷启动质量。

建议：以现实为准修订两份文档（成本低）；工件位置约定统一为 runtime 实际使用的一套，其余标注 deprecated。

### A4 — 工作区根目录卫生（低）

`nul`（重定向事故文件）、`ai-system.zip`、`ai-system-architecture-spec-v1/v2.yaml`（未归档）、`temp/`、`mvnw.cmd`、`sql/` 等散落根目录。

建议：删除事故文件与压缩包；spec yaml 移入 ai-system/archived/ 或 rfc/；根目录只保留 AGENTS.md + 四大实体目录。

## 五、健康面（明确不动）

- 分层依赖方向与职责划分（骨架正确，重构反而引入风险）
- runtime-base 执行契约（完备）
- skill-policy + repo-lint 治理链
- frameworks/ 适配器模式（方向正确，允许慢慢填充）
- 11 个 workflow 集合（上月评估结论：无合并需求）

## 六、结论与路线图

**是否需要架构层面调整？骨架不需要，收敛需要。**

| 阶段 | 动作 | 服务目标 |
|---|---|---|---|
| 近期 | A1 定义收敛（yaml 退化为注册表） | 稳定产出 |
| 近期 | A2 平台层处置：ai-runtime/ 归档 + 引用清理 | 控制效果 |
| 近期 | A3 两份治理文档对齐现实 | 注意力效率 |
| 随手 | A4 根目录清理 | 卫生 |
| 远期 | frameworks/ 适配器填充 | 演进 |

原则：全部为增量修正，无需求变更冻结期，不影响在途任务。

## 七、处置结果（同期执行）

| 项 | 状态 | 处置 |
|---|---|---|
| A1 | 已修复 | 前置核查确认 cli/services/prompt_builder.py 仅消费 name/workflow/runtime 三字段；11 个 config/workflows/*.yaml 全部退化为注册表最小形态（version/name/workflow/runtime），删除 display_name/description/inputs/outputs/next/stop_conditions 重复段；workflows/*.md 成为唯一语义源；实测 11/11 注册项路径有效 |
| A2 | 已修复 | ai-runtime/ 内容确认（单项目 hook 配置 + npm 残留，无引擎代码）；移入 ai-system/archived/ai-runtime/；AGENTS.md、AI_DEVELOPMENT_CONTRACT、ai-bootstrap.yaml 三处引用全部移除；磁盘物理清除 |
| A3 | 已修复 | AGENTS.md：修正 projects/ 重复行、删除虚构的根级 specs/ 行、补 methodologies/repositories/workspaces/、Project Workspace Structure 与 Conventions 更正为实际布局（workspaces/{project_id}/openspec/ = OpenSpec 权威源与运行期上下文所在地，经负责人确认）；合同架构图 runtime/ 改 templates/runtime/ 并补齐 loaders/frameworks/maintainers/rfc/archived；MEMORY_GUIDELINES 同步修正 2 处工件路径 |
| A4 | 已修复 | 删除 nul 事故文件、ai-system.zip、package*.json、link.txt、node_modules；两份 arch-spec yaml 归档；mvw.cmd 改造 |
| R6 | 已修复 | 路由表缩表 v2：version 1→2；移除 skill/pipeline/hooks（SSOT）；11 个 workflow 路由 + 3 别名 + 2 skill 入口 |
| 远期项 | 待办 | frameworks/ 适配器填充 |

关键事实修正（负责人确认）：评估时称"三套工件位置约定并存"，实际唯一权威位置为 `workspaces/{project_id}/openspec/`（openspec-cn 工具布局：changes/ + specs/，如 workspaces/pywechat-live-2608/openspec）；AGENTS.md 原写的 `projects/<project>/openspec/` 与根级 `specs/` 均为过时描述，已修正。
