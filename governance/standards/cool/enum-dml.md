# Enum-to-DML Mapping Convention

## Purpose

Ensure every new, modified, or removed enum value has a corresponding DML operation in the database mapping table.

## Scope

- `runtime-release` — release readiness validation
- Cool College projects involving database changes

## Validation

1. Identify all new/modified/removed enum values
2. Scan code for enum-to-database-table mapping patterns:
   - `parseValue(value)` method
   - `Map<String, Enum> map = ...` static mapping
   - Enum value passed as a parameter to a DAO method
3. If a mapping exists, determine the operation type:
   - New enum value → provide INSERT SQL
   - Modified enum value → provide UPDATE SQL
   - Deprecated enum value → evaluate whether DELETE is needed

## Output Requirements

- Generated SQL scripts MUST be included in the SQL Checklist as executable SQL code blocks
- Every forward SQL MUST have a corresponding rollback SQL

## BLOCKER Conditions

- A mapping exists but no corresponding SQL script is provided
- SQL script has no rollback plan

## Example

```sql
-- Forward
INSERT INTO `audit_event_types` (`event_type`, `event_name`)
VALUES ('create_live_course', 'Create WeCom Live Course');

-- Rollback
DELETE FROM `audit_event_types`
WHERE `event_type` = 'create_live_course';
```
