---
name: archive-openspec
description: Archive an OpenSpec change with spec-sync awareness. Use when running aic-archive, or when the user asks to archive a completed OpenSpec change. Carries the full archive procedure (select → status check → task check → spec sync prompt → move) so the aic-archive command stays a thin trigger.
---

# OpenSpec Change Archive

Procedure for archiving a completed OpenSpec change. Loaded by the
`aic-archive` command; can also be invoked directly.

## Steps

1. **Select the change** (if not provided)

   Run `openspec-cn list --json`. Use the AskUserQuestion tool to let the
   user choose. Show only active (unarchived) changes, with schema if
   available. Do not guess or auto-select.

2. **Check artifact completion**

   `openspec-cn status --change "<name>" --json` →
   `schemaName`, `artifacts` (status per artifact).

   If any artifact is not `done`: warn with the incomplete list, prompt to
   continue.

3. **Check task completion**

   Read the Task Cards under `tasks/cards/*.md`（若无 cards 目录，回退读 `tasks.md`）；逐卡统计 `- [ ]` vs `- [x]`.

   If incomplete tasks: warn with count, prompt to continue.
   If no task file / no cards directory: continue.

4. **Evaluate incremental spec sync**

   Check `openspec/changes/<name>/specs/`. If absent, continue (no sync
   prompt needed).

   If present: compare each incremental spec against the main spec at
   `openspec/specs/<capability>/spec.md`; determine add/modify/delete/rename;
   show a merge summary before prompting.

   Prompt options:
   - If changes needed: "Sync now (recommended)" / "Archive without syncing"
   - If already synced: "Archive now" / "Sync anyway" / "Cancel"

   If the user chooses sync: `openspec-cn archive <name> -y` merges
   incremental specs into `openspec/specs/` (verified 2026-08-06). Continue
   archiving regardless of choice.

5. **Perform the archive**

   ```bash
   mkdir -p openspec/changes/archive
   ```
   Target name: `YYYY-MM-DD-<change-name>`.

   If target exists: fail, suggest renaming or a different date.
   Otherwise: `mv openspec/changes/<name> openspec/changes/archive/YYYY-MM-DD-<name>`.

6. **Show summary**

   Change name / schema / archive location / spec sync status
   (synced | skipped | no incremental) / warnings (incomplete artifacts/tasks).

## Validation

- Archive directory exists and change moved into it
- Summary reflects the sync choice actually made
- Warnings reflect actual incomplete state, not assumed
