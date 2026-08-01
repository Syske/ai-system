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
- **Identifiers**: English（class names, method names, variable names, package names）
- **Commit messages**: Chinese（遵循 Conventional Commits 中文版）
- **Error messages in production**: English（避免编码问题）

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
