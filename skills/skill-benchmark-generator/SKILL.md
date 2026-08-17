---
name: skill-benchmark-generator
description: 当需要针对某个具体 skill 一次性生成 routing 和 outcome 两类测试集时使用。默认必须同时补齐这两类测试集；它负责生成路由命中样本（routing）与效果评测样本（outcome），并将结果整理成可入库的数据项。不适用于评估模型通用能力或路由无关的通用查询。
---

# Skill Benchmark Generator

这是 benchmark generation 的总编排 skill。对单个目标 skill，它同时补齐两类测试集：

- **routing benchmark** — 应命中该 skill 的 query、语义意图、语义锚点（验证路由准确性）
- **outcome benchmark** — 该 skill 成功执行后应交付的标准答案、根因、关键动作（验证输出质量）

（历史版本曾将 routing / outcome 拆为独立 skill `routing-benchmark-generator`、
`outcome-benchmark-generator`，2026-08-17 合并入本 skill 为两大章节；二者无独立
执行体，仅为纯 prompt 说明，合并不影响任何调用。）

## 何时使用

当用户表达以下意图时使用：

- "给这个 skill 自动生成测试集"
- "补齐这个 skill 的 routing 和 outcome benchmark"
- "给 skill-optimizer 提供更系统的路由/效果评测样本"
- "把 benchmark generation 沉淀成 skill"

## 输入

- 目标 skill 名称
- 目标 skill 版本
- 目标版本 `SKILL.md`
- 当前已有 configs（用于去重）
- 可选：本次希望生成的 routing 条数、skill 描述、change log、辅助文件摘要、已有 routing queries

## 输出

输出一个完整的 benchmark generation 结果，至少包含：

- 新生成的 routing dataset items
- 新生成的 outcome dataset items
- 重复项跳过情况
- 当前 skill 的 routing / outcome benchmark 库存统计

## 编排原则

- 对单个目标 skill，默认必须同时生成 routing 与 outcome 两类测试集
- routing 与 outcome 必须分开生成，不能混成一个 combined 语义
- **routing 只关心"该不该命中这个 skill"**；**outcome 只关心"该 skill 成功执行后应交付什么"**
- 入库前必须去重
- 版本必须绑定到目标 skill version，不能悄悄丢成无版本

只有在内部调试、回填或局部修复时，才允许单独生成其中一类；这不是默认产品语义。

## 工作流程

1. 解析目标 skill 与目标版本
2. 读取 `SKILL.md` 和辅助文件摘要
3. 生成 routing benchmarks（见下节）
4. 生成 outcome benchmark（见下节）
5. 对现有 config 做去重与版本绑定检查
6. 输出可直接入库的 benchmark generation 结果

## 验收标准

- 用户能针对单个 skill 一键补齐两类 benchmark
- 生成结果能直接进入项目的数据集管理链路
- 最终可以清楚说明"哪些是 routing benchmark，哪些是 outcome benchmark"

---

## 章节 A — Routing Benchmark

面向 `routing evaluation`：为某个 skill 生成"应命中该 skill"的 query 测试集，
**验证路由准确性**；不负责结果质量评测，也不适用于无明确触发条件的通用查询。

### 适用场景

- 新 skill 刚导入，需要快速补齐 routing benchmark
- 某个 skill 的 routing hit rate 数据不足
- 需要为 skill optimizer 提供更系统的路由命中样本

### 输出（routing dataset item）

每条数据必须包含：

- `query`
- `expectedSkills`
- `routingIntent`
- `routingAnchors`

### 核心约束（routing）

- 只回答"应该命中哪个 skill"，不混入 outcome 层的完成质量判断
- 生成的是 query，不是执行报告，不是标准答案，不是优化建议
- 每条 query 都必须真实落在目标 skill 的职责边界内
- 不要通过简单改写重复生成同一语义
- 不要发明 skill 定义之外的能力
- 不依赖完整 prompt 逐字匹配

### 工作流程（routing）

1. 读取目标 skill 的 `SKILL.md`，提取它真正负责的任务边界
2. 识别该 skill 的能力面，而不是抄写原文
3. 生成一组语义上有区分度的用户 query，覆盖不同职责切面
4. 为每条 query 绑定目标 `expectedSkills`
5. 再从 query 提取 `routingIntent` 与 `routingAnchors`
6. 检查与现有 routing 数据是否重复后再入库

---

## 章节 B — Outcome Benchmark

面向 `outcome evaluation`：为某个 skill 生成"成功执行后应该产出什么"的效果评测集，
**验证输出质量**；不负责路由命中样本生成，且不适用于评估模型通用能力。

### 适用场景

- 某个 skill 没有 outcome benchmark
- 需要为准确率和执行效果提供标准答案
- 需要补齐 `root_causes` 与 `key_actions`

### 输出（outcome dataset item）

输出为一个 skill-bound outcome dataset item，包含：

- `skill`
- `skillVersion`
- `standardAnswer`
- `rootCauses`
- `keyActions`
- 可选：`sourceScenario`

### 核心约束（outcome）

- 评测的是"这个 skill 执行成功后应交付什么"
- 不要把 routing 是否命中混进 outcome 层
- `standardAnswer` 必须足够具体，后续才能稳定抽出 `rootCauses` 和 `keyActions`
- `sourceScenario` 只是来源场景，不是 outcome 的主键
- 不要生成 skill 定义之外的交付物
- `rootCauses` 表达回答中必须出现的关键信息；`keyActions` 表达执行中必须发生的关键动作

### 工作流程（outcome）

1. 读取目标 skill 的 `SKILL.md`，识别它负责的最终交付物
2. 生成一个代表性成功场景或来源场景
3. 为该场景生成可复核的 `standardAnswer`
4. 再从 `standardAnswer` 抽取 `rootCauses`
5. 从同一份 `standardAnswer` 抽取 `keyActions`
6. 绑定到目标 skill 与目标版本，形成 outcome dataset
