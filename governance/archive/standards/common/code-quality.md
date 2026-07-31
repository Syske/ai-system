# Code Quality Goal (DEPRECATED)

**Status**: Deprecated. Replaced by:
- `task-quality-checklist.md` — per-task quality verification baseline
- `clean-code.md` — code structure and style standards

This file is kept for reference only and is no longer loaded by any Runtime.

---

## Overall Goal

代码应达到：

可长期维护，而不仅仅是可运行。

---

# Readability

优先：

读代码的人。

不是：

写代码的人。

任何新增代码，应在几分钟内理解。

---

# Maintainability

新增代码必须：

容易修改

容易定位问题

容易扩展

避免：

隐藏逻辑

大量条件分支

重复实现

---

# Simplicity

优先：

简单实现。

禁止：

炫技代码。

禁止：

没有价值的抽象。

---

# Consistency

必须：

保持与项目现有风格一致。

包括：

命名

日志

异常

DTO

VO

Mapper

Package

---

# Performance

禁止：

明显低效实现。

例如：

循环数据库查询

循环RPC

循环HTTP

循环MQ

优先：

批量

缓存

分页

---

# Safety

必须：

考虑：

空指针

事务

线程安全

资源释放

幂等

超时

重试

---

# Backward Compatibility

禁止：

随意修改：

接口

字段

消息体

数据库

必须：

保证兼容。

---

# Output Requirement

生成代码应达到：

可以直接提交 Merge Request。

无需再次大规模重构。