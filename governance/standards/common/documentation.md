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
