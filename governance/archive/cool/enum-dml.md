# Cool College 枚举-DML 映射规范

## 目的

确保新增、修改、删除的枚举值在数据库映射表中有对应的 DML 操作。

## 适用范围

`runtime-release` + Cool College 项目 + 涉及数据库变更

## 检查方式

1. 识别所有新增/修改的枚举值
2. 扫描代码中是否存在枚举 value → 数据库表的映射模式：
   - `parseValue(value)` 方法
   - `Map<String, Enum> map = ...` 静态映射
   - 枚举值作为参数传入 DAO 方法
3. 若存在映射，判断操作类型：
   - 新增枚举值 → 提供 INSERT SQL
   - 修改枚举值 → 提供 UPDATE SQL
   - 废弃枚举值 → 评估是否需要 DELETE

## 输出要求

- 生成的 SQL 脚本必须包含在 SQL Checklist 中，以 SQL 代码块呈现
- 必须提供可回滚的 SQL（反向操作）

## BLOCKER 条件

- 存在映射但无对应 SQL 脚本
- SQL 脚本无回滚方案

## 示例

```sql
-- 正向
INSERT INTO `audit_event_types` (`event_type`, `event_name`)
VALUES ('create_live_course', '创建企微直播课');

-- 回滚
DELETE FROM `audit_event_types`
WHERE `event_type` = 'create_live_course';
```
