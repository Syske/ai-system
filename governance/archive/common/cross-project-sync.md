# 跨项目重复定义同步规范

## 目的

确保多个项目中存在的同名类、枚举、常量被修改时，所有副本保持同步，避免因漏改导致的不一致。

## 适用范围

`runtime-release`

## 检查方式

1. 在 Release Scope Analysis 中识别修改列表中属于「跨项目重复定义」的文件
2. 搜索仓库中是否存在同名文件（如 `**/AuditTypeEnum.java` 等在多个模块中出现）
3. 对比各副本内容，确认是否需要同步修改
4. 若某副本本次无需修改，需确认该副本已标记为 `@deprecated` 或有明确的业务隔离理由

## BLOCKER 条件

- 重复定义被修改后，存在未同步的副本且无合理说明

## 示例

```
修改: enterprise-manage-api/.../AuditTypeEnum.java
遗漏: knowledge-api/.../AuditTypeEnum.java
     offline-course-api/.../AuditTypeEnum.java
```

检查所有副本一致后再进入下一阶段。
