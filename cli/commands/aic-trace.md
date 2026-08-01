---
description: 分支差异对账 - 对比需求分支与 master 的代码差异，反查 spec/任务卡并驱动补账或生成变更
---

Compare the code differences between the current feature branch and the baseline branch (default master), trace each difference back to its task card, spec scenario, and contract; for unaccounted changes, after confirmation either **backfill the existing change set** or **create a new change set**.

**Inputs**: Project ID; optional Code Reference (focus on specific files/symbols in the diff); optional Change ID (limit to a change set); optional Base Branch (default master).

**Steps**

1. **Locate workspace and repositories**
   - Change set root: `workspaces/{project_id}/openspec/changes/` (exclude archive/)
   - Related service repos: resolved from the project context services list, local path `projects/{service_id}`

2. **Collect diff (trace scope = branch diff, not the whole repo)**

   For each related service repo:

   ```bash
   git diff --name-status {base}...HEAD     # changed file list (three-dot merge-base compare)
   git log --oneline {base}..HEAD           # branch commits, extract T-xxx task ids
   ```

   - Code Reference provided → keep only matching diff files
   - Current branch equals baseline → report "no branch diff" and stop

3. **Trace each changed file**
   - Git clues: branch name `task/{T-xxx}`, T-xxx in commit messages → Task ID
   - Artifact search: grep task cards (tasks/cards/*.md), per-service splits ({service}-tasks.md), spec scenarios (specs/*/spec.md), contracts (contracts/interop_contract.yml)

4. **Trace Report (reconciliation matrix)**

   | Changed File | Commit / Branch | Task Card | Spec Scenario | Contract | Status |
   |---|---|---|---|---|---|

   Status:
   - `MATCHED` — code, task card, and spec agree
   - `TASK_STALE` — has an owning task card, but completion definition / acceptance criteria don't match the implementation (unchecked, wrongly checked, or outdated)
   - `SPEC_STALE` — implementation behavior exceeds or diverges from the spec scenario
   - `UNTRACKED` — difference belongs to no task card or spec scenario

5. **Adjudicate and fix (execute only after stop-and-confirm — Change Control discipline)**

   Output a fix plan list first, wait for user confirmation, then execute:

   - `TASK_STALE` / `SPEC_STALE` and part of an in-flight change → **backfill existing artifacts** (OPERATIONS.md 1.6):
     update in place `changes/{change_id}/` spec delta, task cards (add acceptance evidence, correct checks), contract entries
   - `UNTRACKED` and the change is approved → **create a new change set**:
     derive a kebab-case change name → `openspec-cn new change "<name>"` (/aic-propose flow), fill proposal / specs / tasks, attach implementation evidence directly to task cards
   - Unapproved drift → add to **revert recommendations** (develop corrects per spec); this command does not touch code

6. **Next action (always ask after completion)**

   After reconciliation and fixes, use the **AskUserQuestion tool** to let the user choose, presenting options in the system language:

   - **verify**（推荐，若工件已对齐）：就地执行——加载 `ai-system/workflows/verify.md` 与 `ai-system/templates/runtime/runtime-verify.md`，对每个受影响的 Task ID 按契约执行正确性核验，产出验证报告
   - **review**（若涉及实现质量复核）：加载 review 契约执行，之后再 verify（OPERATIONS.md 1.6 标准关门顺序）
   - **spec re-entry**（若对账发现需要更大范围的规格更新）：提示运行 `python -m cli.main prepare --change <change_id> --request "<变动点>" --mode re-entry`
   - **finish**：仅输出 Trace Report 结束

   Execute the chosen action immediately; do not decide on your own.

   Closing reminder: record every artifact change from this reconciliation in Deviations.

**Output**

## Trace Report

对账矩阵 + 每个非 MATCHED 项的修复方案与执行结果（或待确认状态）。

**Guardrails**

- Only modify artifacts (spec / task / contract / proposal), **never code**
- Each batch of artifact changes requires confirmation (L2/L3 discipline)
- Diff collection is read-only git; never read the whole repo; minimal load in Task → Spec → Contract → Repository order
- Never open a second change set for the same behavior while the current change is unarchived
