# Documentation Standard

## Goal

Documentation helps maintainers understand:

Why.

Not:

What it does.

---

## Language Convention

Per `governance/LANGUAGE_CONVENTION.md`:

- **Code comments and Javadoc**: Chinese（业务逻辑说明、复杂算法注释、字段含义说明）
- **Identifiers**: English（class names, method names, variable names, package names）— 标识符（含**测试方法名**）必须为 ASCII 英文（`[A-Za-z0-9_$]` 字符集），**禁止中文/Unicode 标识符**（Java 虽允许 Unicode 标识符且能编译，但破坏 Javadoc/反射/测试报告/IDE 重构与跨团队可读性）。反例：`syncToBeisen_enterpriseId空_抛参数异常` → `syncToBeisen_enterpriseIdNull_shouldThrowIllegalArgument`；场景/中文描述只能写入方法注释或 `@DisplayName`，不进方法名。
- **Commit messages**: Chinese（遵循 Conventional Commits 中文版）
- **Error messages in production**: English（避免编码问题）

---

## Javadoc Format（Javadoc 格式规范）

All Javadoc（类 / 方法 / 字段 / 枚举常量）uses the **standard multi-line block**,
aligned with IDE default formatting and existing codebase style:

```java
/**
 * 描述
 */
private String someField;
```

- **禁止单行块** `/** xxx */` —— 即使描述只有一行，也必须使用三行结构
  （`/**` 独立行 / ` * 描述` / ` */` 独立行）。反例（AI 生成时可系统性出现）：
  `/** 补偿数据同步（既有链路） */`、`/** 企业级全量同步锁前缀 */`。
- 单行注释仅允许使用 `//` 行注释（非 Javadoc），不参与文档生成。

---

## Comment Content（注释内容规范）

Code comments and Javadoc are written for **repository readers** — teammates and
other teams who read the code without access to internal task context.

- Comments describe **business semantics / intent**（业务语义、Why、复杂算法、字段含义）。
- **禁止携带内部流程标识**：Task Card 编号（`T-001` 等）、Change ID、ai-system 内部变更集引用
  **不得写入代码注释**（类 Javadoc / 方法注释 / 行内注释 / 测试注释）。
- 需求 ↔ 实现的可追溯性由 **Task Card**（Spec 引用 / 完成定义 / 实现说明）维护，不落在代码注释里。
- 引用需求时应写业务语义（如「BOSS 主管理员触发单企业全量同步到北森」），而非编号（`（T-001）`）。

## Commit Content（提交信息内容规范）

- Subject 以**业务语义**开头（动词宾语短语），**禁止以任务编号开头**
  （`feat(platform-api): T-001 …` 应写为 `feat(platform-api): 新增同步到北森的 REST 端点 syncToBeisen`；
  `fix(订单): 修复并发超卖`）。
- 需要关联内部任务时，任务编号仅可放 **body 尾部作关联注记**（`关联 T-002`），不进 subject。

---

## Commit Convention

Commit messages follow Conventional Commits, adapted for Chinese teams.

**Type** (English keyword, tooling-compatible):

| Type | Meaning | Example |
|---|---|---|
| `feat` | new feature | 添加用户注册模块 |
| `fix` | bug fix | 修复登录页白屏问题 |
| `docs` | documentation | 更新 API 接口文档 |
| `style` | formatting (no logic change) | 调整缩进、补充分号 |
| `refactor` | refactor (not new, not fix) | 拆分过长的服务类 |
| `perf` | performance | 优化首页列表查询速度 |
| `test` | testing | 补充用户模块单元测试 |
| `chore` | build/tooling/deps | 升级 webpack 到 v5 |
| `ci` | CI config | 修改 GitHub Actions 流程 |
| `revert` | revert | 回滚 v2.1.0 的登录重构 |

**Template**:

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Rules**:
- `type` required, from the table above
- `scope` optional, Chinese module name (用户模块 / 订单 / 支付)
- `subject` required, Chinese, ≤ 50 chars, verb-object phrase（「添加 xxx」「修复 xxx」），no trailing period, never vague（"修了一个 bug"）
- `body` Chinese, explains motivation, solution, and impact
- `footer` references issues (Closes #128)

Example:

```
fix(订单): 修复并发下单导致库存超卖的问题

在高并发场景下，原有的库存扣减逻辑存在竞态条件。
改用 Redis 分布式锁 + 数据库乐观锁双重保障。

Closes #256
```

---

# Class

All new business classes must:

Include Class Javadoc.

Describe:

Responsibility

Upstream / downstream

Core flow

---

# Method

Public methods must:

Document:

Purpose

Parameters

Return value

Exceptions

Side effects

---

# Fields

VO

DTO

Entity

MQ Message

Config

All fields must:

Include descriptive comments.

Field comment quality criteria（字段注释质量准则，2026-09-02 补充）:
- Describe **business meaning / value semantics**（业务含义与取值语义），not a verbatim
  translation of the field name.
- **禁止名字直译/与字段名重复**：反例——字段 `bsCompensationDataTag` 配注释
  `/** 补偿数据通道 tag */` 零信息增量，不合格。
- 配置注入字段（Apollo 等）注明**来源与对齐关系**（如 tag 由 `…bsCompensationDataProductChannel.tag`
  注入、需与消费端 `bsCompensationDataConsumerChannel` 一致）。
- 类注释已覆盖关键信息时，字段注释**指向类注释**（如「见类注释：对齐关系与注入来源」）而非复制。
- 写不出业务语义的平凡字段（如无特殊约束的自解释字段）可省略注释——注释只在对读者
  有价值时存在（Value-Burden 同样适用于注释）。

Example:

/**
 * WeCom live broadcast ID
 */
private Long liveId;

---

# Complex Logic

Complex logic must explain:

Why it was designed this way.

Forbidden:

Repeating what the code already says.

---

# TODO

Forbidden:

Adding new TODOs.

Unless:

Explicitly required by the Task Card.

---

# Deprecated

When removing old capabilities:

Prefer:

@Deprecated

Bridge pattern

Remove only after confirming no remaining references.

---

# API

When integrating with third-party systems:

Must:

Include:

Link to official documentation.

Example:

WeCom:

https://developer.work.weixin.qq.com/

---

# Update

When modifying shared capabilities:

Synchronously update:

README

Design docs

Contracts

Spec (if required)
