---
description: 梳理分析 - 在指定范围（workspace/projects/分支）内检索关键词或代码块，支持逻辑对比/链路确认/影响范围/手动分析
---

在指定范围内对关键词或代码块做梳理分析。范围由 Workspace、Projects、Branch 限定；分析方式由 Operation 决定；结果可选保留到 scans/ 目录，并可在发现问题后衔接 develop/fix 等流程。

**输入**：
- Operation（可选，默认 search）：`search` 梳理检索 / `diff` 逻辑对比 / `chain` 逻辑链路 / `impact` 影响范围 / `manual` 手动自定义
- Workspace（可选，skip=不在 workspace 中搜索）
- Projects（可选，多选，skip=在所有项目中梳理）
- Branch（可选，默认 master）
- Code Reference：关键词（逗号分隔）或代码块；manual 时为用户的分析指令
- Compare With（仅 diff：第二段待对比代码）
- Keep Results（yes=结果保留到 scans/ 目录；no=仅会话内输出）
- Scan Directory（保留结果时的目标目录）

**步骤**

1. **定位范围**
   - Workspace 已选 → 搜索范围含 `workspaces/{workspace_id}/`
   - Projects 已选 → 对应 `projects/{service_id}/`；skip → 所有 `projects/*`
   - 每个 project 检出目标分支（Branch，默认 master；不存在的分支跳过并记录）
   - 范围为空（未选 workspace 且无可用项目）→ 报告无可用范围并停止

2. **按 Operation 执行**

   - **search（梳理检索）**：在范围内检索 Code Reference（关键词按逗号拆分，逐条检索；代码块按精确片段检索），整理每个命中位置与上下文
   - **diff（逻辑对比）**：对比 Code Reference 与 Compare With 两段代码的逻辑差异（输入输出、分支条件、边界处理、异常路径），产出差异清单
   - **chain（逻辑链路）**：沿 Code Reference 的调用/依赖关系梳理逻辑链路（函数调用链、数据流向、依赖模块），标注断点与死路
   - **impact（影响范围）**：分析 Code Reference 改动/引用会波及的模块、接口、契约、调用方，按影响面分级
   - **manual（手动自定义）**：把 Code Reference 中的用户指令作为分析任务执行；若提供了范围/分支则在其内执行，否则按指令自包含分析

3. **梳理结论**
   - 命中清单：位置（文件:行）、代码块摘录、上下文说明
   - 分析结论：按 operation 产出对应结论（检索结果/差异/链路/影响面/用户指令结论）

4. **结果落盘（Keep Results=yes 时）**
   - 写入 Scan Directory：
     - `scan-report.md`：梳理报告（范围、命中、结论）
     - `snippets/`：命中的代码块摘录
     - `metadata.yaml`：Operation、Workspace、Projects、Branch、Code Reference、时间
   - Keep Results=no → 仅会话内输出，不写文件

5. **下一步动作（完成后必问）**

   使用 **AskUserQuestion tool** 让用户选择下一步：

   - **fix**（发现可修复问题时，推荐）：按问题定位启动修复流程——加载 `workflows/develop.md`（或 `bugfix` 契约），为每个问题推导变更并生成任务卡
   - **review**（需要质量复核时）：加载 review 契约执行，之后可 verify
   - **verify**（需验证改动正确性时）：加载 `workflows/verify.md` 与 `templates/runtime/runtime-verify.md`
   - **finish**：仅保留 Scan Report 结束

   用户选择后立即执行所选动作，不要自行决定。

**输出**

## Scan Report

- 范围与分支说明
- 命中清单（文件:行、代码块、上下文）
- 分析结论（按 operation）
- 发现问题清单与建议下一步

**护栏**

- 只读操作：检索/分析绝不修改代码、绝不 checkout 切换工作区（只在 `git ls-files`/`git grep`/`git show <branch>:<file>` 只读方式下工作）
- 最小加载：按命中定位加载，禁全仓通读
- 每一批修复前必须确认（Change Control 纪律）
- 结果目录只追加，不覆盖已有 scan 报告
