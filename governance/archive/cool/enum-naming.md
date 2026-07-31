# Cool College 枚举值命名规范

## 目的

规范 Java 枚举常量的字符串 value 命名格式，避免非标准符号导致前后端、数据库、API 兼容性问题。

## 适用范围

`runtime-release` + Cool College 项目

## 规则

1. 枚举字符串 value 仅允许：小写字母、数字、下划线（`[a-z0-9_]`）
2. 禁止使用：点号 `.`、中划线 `-`、空格、特殊字符
3. 枚举常量名称（Java 标识符）遵循 `UPPER_SNAKE_CASE`

## 正确示例

```java
DELETE_LIVE_COURSE_SYNC("delete_live_course_sync", "book")
```

## 错误示例

```java
DELETE_LIVE_COURSE_SYNC("delete_live_course.sync", "book")  // 禁止点号
EDIT_LIVE_COURSE_SYNC("edit-live-course-sync", "book")      // 禁止中划线
```

## 检查方式

- 扫描新增/修改的 Java 枚举类
- 提取枚举构造函数的字符串 value 参数
- 正则匹配 `^[a-z0-9_]+$`，不符合即为 BLOCKER
