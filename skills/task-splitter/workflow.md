# Task Splitter Workflow

本文件定义 task-splitter 的能力执行指令（T1-T5）。SKILL.md 为入口摘要、能力表与工作流总览，本文件为分步执行细节。

---

## T1: 单服务任务拆分

执行步骤：

1. 确认当前变更目录 `openspec/changes/<change-name>/` 存在。
2. 读取 `openspec/changes/<change-name>/specs/<service-name>/` 下的所有 Spec 文件。
3. 读取 `openspec/changes/<change-name>/contracts/interop_contract.yml` 中所有 **调用方或被调用方** 包含 `<service-name>` 的条目。
4. 按以下原则拆分任务：
   - 每个任务只做一件事，可直接映射到 Spec 的特定需求或验收场景。
   - 必须标注依赖提示（如"依赖 T-XXX 的被调用方接口就绪"），但不在本步骤排序。
   - 若任务涉及企业库切库，必须引用 `switch_scenarios.yml` 中的场景 ID。

每个原子任务包含：

```
T-<编号> <任务标题>
- 引用 Spec: [文件名]:[章节/需求ID]
- 契约约束: [interop_contract.yml 条目 ID] [关键约束点]
- 切库场景: [switch_scenarios.yml 场景 ID]（如有）
- 验收标准: [如何验证]
```

5. 写入 `tasks/<service-name>.md`。

Verify by: 每个任务可溯源到唯一 Spec 需求 + 契约条目；无遗漏需求；任务粒度不超过 8h 工时。

拆分对象：

```
{{PASTE_SERVICE_NAME_HERE}}
```

---

## T2: 批量服务拆分

```
需拆分的服务列表：{{SERVICE_LIST}}
输出位置：tasks/*.md（每个服务一个文件）
```

规则：

1. 从用户上下文或 `spec-updater` 获取受影响服务列表。
2. 对每个服务执行 T1。
3. 若列表为空，提示先运行 `spec-updater` 完成需求录入。

---

## T3: 全局任务编排

执行步骤：

1. 读取 `tasks/` 下所有任务文件。
2. 分析所有任务间的 RPC 和 MQ 依赖关系（参考 `interop_contract.yml`）。
3. 按"被调用方/生产者先实现，调用方/消费者后实现"原则排序。
4. 无依赖的任务归入"并行开发池"。

输出格式：

```
Phase 1: 基础接口与契约实现（被调用方）
  - [服务名] T-XXX 任务描述
Phase 2: 核心逻辑（调用方）
  - [服务名] T-XXX 任务描述
Phase 3: 集成与验证
  - [服务名] T-XXX 任务描述
并行开发池（无依赖）：
  - [服务名] T-XXX 任务描述
```

5. 写入 `tasks/global-plan.md`。

---

## T4: 契约片段注入（自动执行，不单独触发）

在 T1/T2 的每个任务中，自动追加契约上下文：

```
契约条目: {{ENTRY_ID}}
- 调用方: {{caller}} → 被调用方: {{callee}}
- 协议: {{protocol}}
- 请求字段: {{request_schema}}
- 响应字段: {{response_schema}}
- 错误码: {{errors}}
- 切库场景: {{switch_scenario_id}}
```

---

## T5: 验收标准生成

为每个原子任务补充可测试的验收标准：

```
验收标准:
- Given: [前提条件] When: [操作] Then: [预期结果]
- 直接引用 Spec 中的验收场景（## 场景: 块）
- 覆盖契约中的错误处理规则
```
