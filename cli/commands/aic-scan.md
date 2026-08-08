---
description: 梳理分析 - 在指定范围（workspace/projects/分支）内检索关键词或代码块，支持逻辑对比/链路确认/影响范围/手动分析
---

Analyze keywords or code blocks within a specified scope. Scope is limited by Workspace, Projects, Branch; the analysis method is chosen by Operation; results may be kept in the scans/ directory, and can feed into develop/fix flows when issues are found.

**Inputs**:
- Operation (optional, default search): `search` keyword scan / `diff` logical compare / `chain` call-chain / `impact` impact scope / `manual` custom instructions
- Workspace (optional, skip = do not search in workspace)
- Projects (optional, multi-select, skip = scan across all projects)
- Branch (optional, default master)
- Code Reference: keywords (comma-separated) or a code block; for manual, the user's analysis instruction
- Compare With (diff only: the second code block to compare)
- Keep Results (yes = keep results in scans/ dir; no = session-only output)
- Scan Directory (target dir when keeping results)

**Steps**

1. **Resolve scope**
   - Workspace selected → search scope includes `workspaces/{workspace_id}/`
   - Projects selected → corresponding `projects/{service_id}/`; skip → all `projects/*`
   - For each project, check out the target Branch (default master; skip and record if missing)
   - Empty scope (no workspace and no usable project) → report no usable scope and stop

2. **Execute per Operation**

   - **search**: search Code Reference in scope (keywords split by comma, each searched; code block matched as exact fragment), collect each hit location and context
   - **diff**: compare logical differences between Code Reference and Compare With (inputs/outputs, branch conditions, boundary handling, error paths), produce a difference list
   - **chain**: trace the call/dependency chain of Code Reference (call chains, data flow, dependent modules), mark breakpoints and dead ends
   - **impact**: analyze modules, interfaces, contracts, and callers affected by Code Reference changes/references, graded by blast radius
   - **manual**: execute the user's instruction in Code Reference as an analysis task; within scope/branch if provided, otherwise self-contained

   > **Delegation (binding)**: `chain` and `impact` operations are deep
   > impact/risk analysis — run the **change-impact workflow**
   > (`workflows/change-impact.md`) for these, which produces the full
   > impact report (blast radius, risks, modification plan). `scan` keeps
   > `search` / `diff` / `manual` for lightweight keyword and comparison
   > scans; `chain` / `impact` here are thin triggers that hand off to the
   > workflow rather than re-implementing impact analysis in the command.

3. **Conclude**
   - Hit list: location (file:line), code excerpt, context note
   - Analysis conclusion: per operation (search results / differences / chain / impact / instruction result)

4. **Persist results (when Keep Results=yes)**
   - Write to Scan Directory:
     - `scan-report.md`: scan report (scope, hits, conclusions)
     - `snippets/`: matched code excerpts
     - `metadata.yaml`: Operation, Workspace, Projects, Branch, Code Reference, timestamp
   - Keep Results=no → session-only output, no files written

5. **Next action (always ask after completion)**

   Use the **AskUserQuestion tool** to let the user choose the next step, presenting options in the system language:

   - **fix**（推荐，发现可修复问题时）：按问题定位启动修复流程——加载 `workflows/develop.md`（或 `bugfix` 契约），为每个问题推导变更并生成任务卡
   - **review**（需要质量复核时）：加载 review 契约执行，之后可 verify
   - **verify**（需验证改动正确性时）：加载 `workflows/verify.md` 与 `templates/runtime/runtime-verify.md`
   - **finish**：仅保留 Scan Report 结束

   Execute the chosen action immediately; do not decide on your own.

**Output**

## Scan Report

- 范围与分支说明
- 命中清单（文件:行、代码块、上下文）
- 分析结论（按 operation）
- 发现问题清单与建议下一步

**Guardrails**

- Read-only operation: search/analysis never modifies code, never checks out or switches workspaces (work only via read-only `git ls-files` / `git grep` / `git show <branch>:<file>`)
- Minimal loading: load only by hit location, never read the whole repo
- Each batch of fixes requires confirmation (Change Control discipline)
- Result dir is append-only; never overwrite existing scan reports
