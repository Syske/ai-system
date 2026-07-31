# Workflow 层优化报告（2026-07）

## 一、背景与目标

本次优化对象为 `ai-system/workflows/`（11 个 workflow 入口文件），驱动目标为四项：

1. 稳定产出（确定性转移、显式退出）
2. 输出质量（产出物与完成判据显式化）
3. 控制效果（前置条件、停止条件、链路衔接）
4. 上下文与注意力效率（最小上下文声明、禁止全仓加载）

依据技能：`skills/architecture/workflow-architect`（继承 architecture-base）、`context-architect`、`design-review`。

范围约束：仅修改 `workflows/`；runtime、routing 层不动，相关发现记录于本报告"后续演进建议"。

---

## 二、变更摘要

| 变更 | 说明 |
|---|---|
| 11 个 workflow 文件统一为八段模板 | Purpose / Runtime / Preconditions / Inputs / Context / Outputs / Exit Criteria / Next |
| 新增 `workflows/README.md` | 场景选择表、主链路图、术语表、模板规范（约束未来新增 workflow） |
| 原有字段语义全部保留 | Purpose、Runtime 指针、Inputs 仅做术语统一，无破坏性变更 |

八段与目标的映射：

- Preconditions + Exit Criteria(Stop) → 控制效果
- Outputs + Exit Criteria(Success) → 稳定产出、输出质量
- Context（按 Task → Spec → Contract → Standards → Repository 顺序声明最小集）→ 注意力效率
- Next → 链路控制（确定性转移）

主链路（已与负责人确认）：

```text
bootstrap → prepare → spec → dev-setup → develop → review → verify → release
条件回路：review(Changes Required) → develop；verify(FAIL) → develop
独立入口：bugfix → review → verify
独立辅助：analysis、knowledge
```

---

## 三、术语统一映射

| 文件 | 旧 | 新 |
|---|---|---|
| develop.md | Project | Project ID |
| review.md | Project | Project ID |
| bugfix.md | Project | Project ID |
| release.md | Workspace | Workspace ID |
| spec.md | Change Name | Change ID |
| prepare.md | —（新增） | Change ID（必填，用于跨 workflow 工件寻址） |
| verify.md | Specification | Specification Reference；补充 Project ID（对齐 review） |

规则：身份字段一律带 `ID` 后缀；内容字段（Bug Description、Logs、Requirement Documents 等）保持描述性命名。

---

## 四、设计自检结论（design-review 八阶段）

| 阶段 | 结论 |
|---|---|
| 1 Scope | 目标与范围明确 ✓ |
| 2 Responsibility | workflow=入口契约；runtime=执行生命周期；Context 段声明"加载什么"，runtime 决定"如何加载"，无职责重叠 ✓ |
| 3 Coupling | workflow→runtime 为既有路径引用；workflow→workflow 仅通过 Preconditions/Next 声明既存真实依赖，无隐藏依赖、无循环执行 ✓ |
| 4 Complexity | 无新增抽象层；每文件约 50–70 行；README 为索引非引擎 ✓ |
| 5 Evolution | 模板已在 README 固化；新增 workflow 按模板扩展，不需改 runtime ✓ |
| 6 Compatibility | 原字段语义保留；重命名为受控变更（见第三节映射表）；routing 层不引用输入字段名，无影响 ✓ |
| 7 Context | 全部 11 个文件声明最小加载集并显式禁止全仓加载 ✓ |
| 8 Readiness | 内容全部从 12 个 runtime 模板事实推导 ✓ |

**Verdict: Approved。** Complexity 2/5，Evolution 4/5，Maintainability 4/5。

---

## 五、重组评估（仅评估，未实施）

| 候选 | 结论 | 理由 |
|---|---|---|
| prepare 与 spec 合并？ | **保留分离** | prepare 做上下文/影响/风险收集（不产规格），spec 产规格工件，职责边界清晰。真正的重叠在 runtime 层：`runtime-prepare` Phase 3 与 `runtime-spec` Phase 2 各自调用 architecture-analysis，存在重复分析 → 建议 runtime 层让 spec 复用 prepare 的 Architecture Summary（见第六节 R3） |
| bootstrap 与 dev-setup 合并？ | **保留分离** | bootstrap 管环境路径推导与工作区初始化（一次性、项目无关）；dev-setup 管项目绑定、分支确认、标准装载（项目相关、可重复）。合并将破坏"环境与项目解耦" |
| analysis / knowledge 是否保留？ | **保留** | 定位清晰（系统体检 / 知识资产），与主链正交，且各有独立 runtime 支撑 |

结论：11 个 workflow 集合保持不变，无合并/删除需求。

---

## 六、runtime 层发现与后续演进建议（不在本次范围）

| 编号 | 发现 | 建议 | 优先级 |
|---|---|---|---|
| R1 | 5 个 runtime 声明 `Extends: runtime-workspace.md`，该文件不存在（runtime-prepare / review / verify / release / bugfix） | 新建 runtime-workspace.md 或统一改为 extends runtime-base.md | 高 |
| R2 | 上下文循环疑点：runtime-prepare 声明消费 Dev Setup 的 Project/Workspace Context，但主链中 dev-setup 位于 spec 之后（需要 Task ID），prepare 阶段这些上下文通常不存在 | 将 runtime-prepare 中该依赖改为可选（workflow 层本次已按"如存在则加载"处理） | 中 |
| R3 | architecture-analysis 在 prepare 与 spec 两个 runtime 中重复执行 | runtime-spec Phase 2 优先复用 Prepare 的 Architecture Summary，仅增量分析 | 中 |
| R4 | runtime-spec Completion 推荐 Next = Development Runtime，跳过了 dev-setup，与实际链路 spec → dev-setup → develop 不一致 | 修正为 Dev Setup Runtime | 中 |
| R5 | runtime-release 两处引用 `governance/stangards/...`，拼写错误（应为 standards），会导致标准文件解析失败 | 修正拼写 | 高 |
| R6 | routing/ai-routing.yaml 的 `workflow` 路由仅有 `workflow: true`，未定义如何映射到 workflows/*.md | 补充路由到 workflow 文件的解析规则 | 低 |

### 处置结果（同期修复）

| 编号 | 状态 | 处置 |
|---|---|---|
| R1 | 已修复 | 依据 archived/ARCHIVE.md（runtime-workspace 已被 runtime-dev-setup 取代），5 个 runtime 的 Extends 统一改为 runtime-base.md，与 runtime-develop 模式一致，不复活已归档抽象 |
| R2 | 已修复 | runtime-prepare 中 Dev Setup 上下文改为可选，并注明 Prepare 位于主链 Spec / Dev Setup 之前、不得依赖其产物 |
| R3 | 已修复 | runtime-spec Phase 2 改为优先复用 Prepare 的 Architecture Summary 与 Impact Report，仅对缺口增量调用 architecture-analysis |
| R4 | 已修复 | runtime-spec Completion 推荐链改为 Dev Setup Runtime → Development Runtime |
| R5 | 已修复 | 实际根因是目录本身拼写错误：`governance/stangards/` 重命名为 `governance/standards/`；修正 standards-loader.md（5 处）与 runtime-release.md（3 处）拼错引用；testing.md、review-checklist.md 移入 common/ 与引用对齐。重命名同时修复了 19 处按正确拼写书写、此前指向不存在路径的引用（standards-loader 18 处 + MEMORY_GUIDELINES 1 处） |
| R6 | 搁置 | 路由层、消费者未知，自创 schema 违背稳定产出目标；保留待办 |

补充说明：standards-loader 中仍有 9 处引用指向从未创建的标准文件（python/pep8.md、go/go-style.md、java/spring.md、java/mybatis.md ×2、mq/rocketmq.md、api/rest.md、database/sql.md），判定为语言/框架扩展预留位，保持不动。

---

## 七、验证结果

| 检查项 | 结果 |
|---|---|
| 八段齐全且顺序一致（11 文件） | 11/11 通过 |
| Runtime 引用有效（11 处） | 11/11 存在 |
| 术语残留（Project / Workspace / Change Name 裸用） | 0 处（spec.md Outputs 中 `Specification` 为工件名，合法） |
| 链路闭合（Next 目标均为存在的 workflow 或显式 None/external） | 通过 |
| Preconditions 与上游 Outputs 对应 | 通过（逐条来自 runtime 模板 Outputs 事实） |

---

## 八、兼容性说明

- 本次为增量补齐：原 Purpose / Runtime / Inputs 三段语义完整保留。
- 重命名仅限第三节映射表所列字段；workflows 之外无文件引用这些字段名（routing 层已核实）。
- 生命周期细节（checkpoints、恢复、持久化）未上移，仍由 Runtime 层唯一拥有（Single Source of Truth）。
