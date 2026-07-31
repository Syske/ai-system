---
name: contract-maintainer
description: 基于 OpenSpec 和 switch_scenarios.yml 自动生成、校验、引用《服务间交互契约》。当用户提到"契约""contract""切库""服务间交互""任务拆分""合同"等关键词时触发。也适用于跨服务调用的规范性文档生成和维护。
---

# Contract Maintainer

## 核心能力

| 能力 | 方式 | 说明 |
|------|------|------|
| 生成契约 | `scripts/generate_contract.py` | 解析 Spec YAML 块 + switch_scenarios.yml，输出 interop_contract.yml |
| 校验一致性 | 脚本内置交叉校验 | 检查 Spec 与场景清单的覆盖关系、字段一致性 |
| 注入任务上下文 | 预置提示词模板 | 任务拆分时自动引用契约中相关条目 |
| 迁移辅助 | 内置指引 | 帮助将存量 Markdown 交互描述逐步转为 YAML 块 |

## 源文件结构

```
specs/                          # OpenSpec 源文件
├── mq-event/spec.md           # 增量规范（可含 YAML 块）
├── live-core/spec.md
├── progress/spec.md
└── switch_scenarios.yml       # 切库场景清单（唯一源）
contracts/
├── interop_contract.yml       # 生成的契约文件（只读，头部标记 AUTO-GENERATED）
└── contract_manual.yml        # 存量手动补充条目（逐步废弃）
scripts/
└── generate_contract.py       # 生成脚本
```

## 双轨运行策略

- **新交互**：在 Spec 中以 YAML 代码块编写，脚本自动提取
- **存量交互**：保留纯文本描述，手动维护 `contract_manual.yml` 作为补充
- **迁移触发**：当存量交互被需求迭代触动时，顺手重构为 YAML 块
- **合并规则**：YAML 块优先于手动条目；重复时输出警告提示清理手动条目

## 工作流

### 1. 生成契约

```
scripts/generate_contract.py --spec-dir specs/ --switch specs/switch_scenarios.yml --manual contracts/contract_manual.yml --output contracts/interop_contract.yml
```

生成后，检查输出文件底部的 `# VALIDATION_WARNINGS` 区块，处理所有警告和错误。

### 2. 校验一致性

脚本自动执行三项检查：

| 检查项 | 严重度 | 动作 |
|--------|--------|------|
| Spec RPC/MQ 缺少对应场景条目 | 警告 | 提醒补充 switch_scenarios.yml |
| 场景条目在 Spec 中找不到对应交互 | 警告 | 可能场景过期 |
| 切库字段名与 Spec schema 不一致 | 报错 | 阻断生成 |

### 3. 任务拆分时注入契约

当用户说"拆分任务"时，先读取 `contracts/interop_contract.yml` 中所有与目标服务相关的条目，将契约约束写入每个原子任务的"必须遵守的契约"部分。

### 4. 存量迁移辅助

当一个交互从纯文本迁移为 YAML 块时：

1. 在 Spec 对应章节添加 YAML 代码块（参考下方 YAML 块模板）
2. 运行 `generate_contract.py` 确认自动条目已覆盖
3. 从 `contract_manual.yml` 中移除对应手动条目
4. 重新生成 `interop_contract.yml`

## Spec YAML 块模板

```yaml
rpc:
  - name: CreateOrder
    caller: api-gateway
    callee: order-service
    description: 创建订单的场景说明
    protocol: SOFA RPC
    request:
      enterprise_id: string
      user_id: string
      items: list
    response:
      order_id: string
      status: string
    errors:
      - code: INVALID_ITEM
        status: 400
```

```yaml
mq:
  - topic: order.enterprise.created
    producer: order-service
    consumer: inventory-service
    description: 企业订单创建后通知库存服务预占
    schema:
      enterprise_id: string
      order_id: string
      items: list
    error_handling: 死信队列，最多重试 3 次
```

## switch_scenarios.yml 格式

```yaml
scenarios:
  - id: SW-01
    service: order-service
    feature: 创建企业团购订单
    description: 消费企业订单创建消息，切换到对应企业库执行库存扣减
    source_of_enterprise_id: 订单参数
    trigger: REST create_order API
    error_handling: 切库失败 → 事务回滚，返回 500
```

## 提示词模板

### 生成契约提示词

> 请基于以下源文件运行 `scripts/generate_contract.py` 生成最新契约：
> - Spec 目录：`specs/`
> - 场景清单：`specs/switch_scenarios.yml`
> - 手动补充：`contracts/contract_manual.yml`（如有）
>
> 生成后，列出变更摘要（新增/修改/删除的条目），并附上校验警告。

### 拆分任务时注入契约提示词

> 当前任务涉及 `{服务名}`，请先读取 `contracts/interop_contract.yml` 中所有与该服务相关的条目。
> 将这些条目作为硬约束，写入每个原子任务的"必须遵守的契约"部分。
> 不得遗漏，不得偏离。
