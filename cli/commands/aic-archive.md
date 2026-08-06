---
description: 归档实验性工作流中已完成的变更
---

Archive a completed change in the experimental workflow.

**Inputs**: Optionally specify the change name after `/aic-archive` (e.g. `/aic-archive add-auth`). If omitted, check whether it can be inferred from conversation context. If ambiguous or unclear, you must prompt for the available changes.

**Steps**

1. **If no change name provided, prompt for selection**

   Run `openspec-cn list --json` to get available changes. Use the **AskUserQuestion tool** to let the user choose.

   Show only active (unarchived) changes.
   Include the schema used by each change, if available.

   **Important**: Do not guess or auto-select a change. Always let the user choose.

2. **Check artifact completion status**

   Run `openspec-cn status --change "<name>" --json` to check artifact completion.

   Parse JSON to understand:
   - `schemaName`: the workflow schema in use
   - `artifacts`: list of artifacts and their status (`done` or other values)

   **If any artifact is not `done`:**
   - Show a warning listing the incomplete artifacts
   - Prompt the user to confirm whether to continue
   - If the user confirms, continue

3. **Check task completion status**

   Read the task file (usually `tasks.md`) to check for incomplete tasks.

   Count tasks marked `- [ ]` (incomplete) vs `- [x]` (complete).

   **If incomplete tasks are found:**
   - Show a warning with the number of incomplete tasks
   - Prompt the user to confirm whether to continue
   - If the user confirms, continue

   **If no task file exists:** continue without a task-related warning.

4. **Evaluate incremental spec sync status**

   Check for incremental specs in `openspec/changes/<name>/specs/`. If absent, continue without prompting for sync.

   **If incremental specs exist:**
   - Compare each incremental spec against its corresponding main spec in `openspec/specs/<capability>/spec.md`
   - Determine which changes would apply (add, modify, delete, rename)
   - Show a merge summary before prompting

   **Prompt options:**
   - If changes needed: "Sync now (recommended)", "Archive without syncing"
   - If already synced: "Archive now", "Sync anyway", "Cancel"

   If the user chooses to sync, run `openspec-cn archive <name> -y`, whose built-in sync
   merges incremental specs into `openspec/specs/` (verified 2026-08-06: archive merges
   without a separate command). Continue archiving regardless of choice.

5. **Perform the archive**

   Create the archive directory if it does not exist:
   ```bash
   mkdir -p openspec/changes/archive
   ```

   Generate the target name using the current date: `YYYY-MM-DD-<change-name>`

   **Check whether the target already exists:**
   - If yes: fail with an error, suggest renaming the existing archive or using a different date
   - If no: move the change directory to the archive

   ```bash
   mv openspec/changes/<name> openspec/changes/archive/YYYY-MM-DD-<name>
   ```

6. **Show summary**

   Show an archive completion summary, including:
   - Change name
   - Schema used
   - Archive location
   - Spec sync status (synced / skipped sync / no incremental specs)
   - Notes on any warnings (incomplete artifacts/tasks)

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
