---
description: 归档实验性工作流中已完成的变更
---

Archive a completed change in the experimental workflow.

**Inputs**: Optionally specify the change name after `/aic-archive` (e.g. `/aic-archive add-auth`). If omitted, check whether it can be inferred from conversation context. If ambiguous or unclear, you must prompt for the available changes.

**Steps**

> The full archive procedure (select change → check artifact/task
> completion → evaluate spec sync → archive) lives in the
> **`archive-openspec` skill** — load `skills/archive-openspec/SKILL.md`
> and execute it step by step. The command below is the thin trigger:
> select or confirm the change name, then follow the skill's 6 steps
> (select → status → tasks → spec-sync prompt → mv archive → summary).

**Output**

On success:

```
## 归档完成

**变更：** <change-name>
**Schema：** <schema-name>
**归档至：** openspec/changes/archive/YYYY-MM-DD-<name>/
**规范：** ✓ 已同步到主规范

所有产出物已完成。所有任务已完成。
```

On success (no incremental specs):

```
## 归档完成

**变更：** <change-name>
**Schema：** <schema-name>
**归档至：** openspec/changes/archive/YYYY-MM-DD-<name>/
**规范：** 无增量规范

所有产出物已完成。所有任务已完成。
```

On success (with warnings):

```
## 归档完成（带警告）

**变更：** <change-name>
**Schema：** <schema-name>
**归档至：** openspec/changes/archive/YYYY-MM-DD-<name>/
**规格说明：** 跳过同步（用户选择跳过）

**警告：**
- 带有 2 个未完成产出物的归档
- 带有 3 个未完成任务的归档
- 增量规格说明同步已跳过（用户选择跳过）

如果这不是故意的，请检查归档。
```

On error (archive exists):

```
## 归档失败

**变更：** <change-name>
**目标：** openspec/changes/archive/YYYY-MM-DD-<name>/

目标归档目录已存在。

**选项：**
1. 重命名现有归档
2. 如果是重复的，删除现有归档
3. 等待不同的日期再归档
```

**Guardrails**
- Always prompt for selection if no change is provided
- Use the artifact graph (`openspec-cn status --json`) for completion checks
- Do not block archiving on warnings - just inform and confirm
- Preserve `.openspec.yaml` when moving to archive (it moves with the directory)
- Show a clear operation summary
- If sync is requested, run `openspec-cn archive <name> -y` (built-in spec sync; no separate command or skill exists)
- Always run the sync evaluation if incremental specs exist, and show a consolidated summary before prompting
