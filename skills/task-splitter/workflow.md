# Task Splitter Workflow

本文件定义 task-splitter 的能力执行指令（T1-T5）。SKILL.md 为入口摘要、能力表与工作流总览，本文件为分步执行细节。所有 Task Card 必须与 `methodologies/providers/openspec-cn/templates/tasks-template.md` 字段结构一致，位置为 `tasks/cards/T-{id}.md`。

---

## Task Card 字段

每张 Task Card（写 `tasks/cards/T-{id}.md`）必须包含以下字段，与 tasks-template.md 对齐：

```
# T-{编号}: {任务标题}

**服务**: {服务名}

**branch**: {分支名模板，如 cc{date}_ipd_{desc}_{service}，由需求确认时定死}

**Spec引用**: {spec文件} § {需求/场景}

**契约约束**:
- {条目ID / 调用方→被调用方 / 协议 / 请求响应字段 / 错误码}

**场景约束**: {switch_scenarios.yml 场景ID 或 "无"}

**完成定义**:
- [ ] {完成项}

**验收标准**:
- Given {前提} When {动作} Then {预期}

## 代码质量检查

### 基线清单（引用，不逐项展开）
- [ ] 通用 / 安全性 / 语言检查：已按 ai-system/governance/standards/common/task-quality-checklist.md 逐项自检通过（review 将按该清单逐项核验）

### <按条件展开的检查节>
```

- **branch**：来自 runtime-spec 6.Y 分支命名模板（默认 `cc{date}_ipd_{desc}_{service}`），dev-setup 据此创建/校验服务分支并冻结。同一服务的多张卡共享同一分支名。
- **代码质量检查推导**：按 runtime-spec 6.X 规则——基线清单仅引用一行（Single Source of Truth，不逐项展开）；条件检查仅在某条件命中时逐项展开（REST 接口 / MQ / RPC / 影响数据访问或远程调用的性能 / 新增功能 / 修改既有代码 / 删除）。
- 卡片中出现的每个文件引用须为完整仓库相对路径。

---

## T1: 单服务任务拆分

执行步骤：

1. 确认当前变更目录 `openspec/changes/<change-name>/` 存在。
2. 读取 `openspec/changes/<change-name>/specs/<service-name>/` 下的所有 Spec 文件。
3. 读取 `openspec/changes/<change-name>/contracts/interop_contract.yml` 中所有 **调用方或被调用方** 包含 `<service-name>` 的条目。
4. 读取 `repositories/<service_id>.yaml` 获取技术栈（用于代码质量检查推导）。
5. 按以下原则拆分任务：
   - 每个任务只做一件事，可直接映射到 Spec 的特定需求或验收场景（单一职责）。
   - 每个任务可独立实现、独立测试、独立验证。
   - 每步可执行粒度（bite-sized）：任务内部步骤 2-5 分钟。
   - 必须标注依赖提示（如"依赖 T-XXX 的被调用方接口就绪"），但不在此步骤排序。
   - 若任务涉及企业库切库，必须引用 `switch_scenarios.yml` 中的场景 ID。
   - 单任务工时 4h ≤ t ≤ 8h；超 8h 继续拆分。
6. 为每个任务分配唯一 ID `T-{3位序号}`，写入 `tasks/cards/T-{id}.md`（使用上面的 Task Card 字段结构 + 代码质量检查推导 + branch）。
7. 扩展 `tasks/<service-name>-tasks.md` 索引（列出本服务卡 ID 与标题）。

Verify by: 每张卡可溯源到唯一 Spec 需求 + 契约条目；无遗漏需求；粒度不超过 8h 工时；卡片含 branch / 完成定义 / 代码质量检查。

拆分对象：

```
{{PASTE_SERVICE_NAME_HERE}}
```

---

## T2: 批量服务拆分

```
需拆分的服务列表：{{SERVICE_LIST}}
输出位置：tasks/cards/*.md（每个任务一张卡）+ tasks/<service>-tasks.md（每服务索引）
```

规则：

1. 从用户上下文或 `spec-updater` 获取受影响服务列表。
2. 对每个服务执行 T1。
3. 若列表为空，提示先运行 `spec-updater` 完成需求录入。

---

## T3: 全局任务编排

执行步骤：

1. 读取 `tasks/cards/` 下所有 Task Card。
2. 分析所有任务间的 RPC 和 MQ 依赖关系（参考 `interop_contract.yml` 与卡片 `契约约束`）。
3. 按"被调用方/生产者先实现，调用方/消费者后实现"原则排序。
4. 无依赖的任务归入"并行开发池"。
5. 为每个任务标注 **blocking 边**：必须在其之前完成的其他任务（引用 `T-{id}`）。

**垂直切片原则**（借鉴 tracer-bullet 方法）：

- 每个任务切一条 **完整路径**——穿越 schema/API/业务逻辑/测试各层，而非某一层的水平切片。
- 完成后的切片**可独立演示或验证**（有自己的验收标准）。
- 切片大小适配单个上下文窗口；宽重构（机械性全局改动）例外，按 **expand-contract** 编排：先加新形态不破坏 → 按 blast radius 分批迁移（每批一个任务）→ 最后删除旧形态。

**用户确认**：

任务清单 + blocking 边就绪后，以编号列表呈现给用户，逐项确认：

- 粒度是否合适（太粗/太细）
- blocking 边是否正确（每个任务只依赖真正 gate 它的任务）
- 是否有应合并/拆分的任务

用户批准后才写入 `tasks/global-plan.md`。

输出格式（一行一卡，引用 `T-{id}`，不重复卡片内容格式）：

```
Phase 1: 基础接口与契约实现（被调用方）
  - [isv-api] T-001 任务描述（blocked by: 无；branch: cc{date}_ipd_desc_isv-api）
Phase 2: 核心逻辑（调用方）
  - [knowledge-api] T-002 任务描述（blocked by: T-001）
Phase 3: 集成与验证
  - [live-api] T-003 任务描述（blocked by: T-002）
并行开发池（无依赖）：
  - [teacher-manage-api] T-004 任务描述（blocked by: 无）
```

6. 写入 `tasks/global-plan.md`。global-plan 仅为**排序视图**（引用卡 ID + blocking 边），任务内容仍以 `tasks/cards/` 为准。

---

## T4: 契约片段注入（自动执行，不单独触发）

在 T1/T2 的每张 Task Card 中，自动追加契约上下文到 `**契约约束**` 字段：

```
- 条目 {{ENTRY_ID}}
  - 调用方: {{caller}} → 被调用方: {{callee}}
  - 协议: {{protocol}}
  - 请求字段: {{request_schema}}
  - 响应字段: {{response_schema}}
  - 错误码: {{errors}}
  - 切库场景: {{switch_scenario_id}}
```

---

## T5: 验收标准生成

为每张 Task Card 补充可测试的验收标准（写入卡片 `**验收标准**` 字段）：

```
验收标准:
- Given [前提] When [动作] Then [预期结果]
- 直接引用 Spec 中的验收场景（## 场景: 块）
- 覆盖契约中的错误处理规则
```
