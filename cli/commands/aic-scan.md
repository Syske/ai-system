---
description: 梳理分析 - 在指定范围（workspace/projects/分支）内检索关键词或代码块，支持逻辑对比/链路确认/影响范围/手动分析
---

Analyze keywords or code blocks within a specified scope. Scope is limited by Workspace, Projects, Branch; the analysis method is chosen by Operation; results may be kept in the scans/ directory, and can feed into develop/fix flows when issues are found.

**Inputs**:
- Operation (optional, default search): `search` keyword scan / `diff` logical compare / `chain` call-chain / `manual` custom instructions
- Workspace (optional, skip = do not search in workspace)
- Projects (optional, multi-select, skip = scan across all projects)
- Branch (optional, default master)
- Code Reference: keywords (comma-separated) or a code block; for manual, the user's analysis instruction
- Compare With (diff only: the second code block to compare)
- Logs (optional; manual bug analysis): log excerpts to analyze
- Stack Trace (optional; manual bug analysis): exception stack trace to analyze
- Keep Results (yes = keep results in scans/ dir; no = session-only output)

> `Scan Directory` 由 CLI 自动填充（Keep Results=yes 时指向
> `outputs/scan/{yyMMdd}-{descriptor}/`），用户无需输入。

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
   - **manual**: execute the user's instruction in Code Reference as an analysis task; within scope/branch if provided, otherwise self-contained. For **bug analysis without a project** (e.g. diagnose a defect from logs/stack trace against a baseline branch): put the analysis instruction in Code Reference, paste the log excerpt in Logs and the exception trace in Stack Trace; Branch selects the baseline to inspect (default master).

   > **Boundary (2026-08-18)**: impact analysis is NOT part of `scan`.
   > To assess the impact, risks, and modification plan of a code target
   > before changing it, run the **change-impact workflow**
   > (`workflows/change-impact.md`, 「代码分析」menu group), which produces
   > the full impact report (blast radius, risks, modification plan).
   > `scan` keeps `search` / `diff` / `chain` / `manual` for lightweight
   > locating and comparison; `chain` here is a call-chain locator, not an
   > impact assessment.

3. **Conclude**
   - Hit list: location (file:line), code excerpt, context note
   - Analysis conclusion: per operation (search results / differences / chain / instruction result)

4. **Persist results (when Keep Results=yes)**
   - Write to Scan Directory:
     - `scan-report.md`: scan report (scope, hits, conclusions)
     - `snippets/`: matched code excerpts
     - `metadata.yaml`: Operation, Workspace, Projects, Branch, Code Reference, timestamp
   - Keep Results=no → session-only output, no files written

5. **Next action (always ask after completion)**

   Use the **AskUserQuestion tool** to let the user choose the next step, presenting options in the system language:

   - **fix** (recommended when fixable issues found): load `workflows/develop.md` (or the bugfix contract), derive changes per issue and generate task cards
   - **review** (when quality review needed): load the review contract, then verify
   - **verify** (when change correctness needs validation): load `workflows/verify.md` and `templates/runtime/runtime-verify.md`
   - **finish**: keep the Scan Report only

   Execute the chosen action immediately; do not decide on your own.

**Output**

## Scan Report

- 范围与分支说明
- 命中清单（文件:行、代码块、上下文）
- 分析结论（按 operation）
- 发现问题清单与建议下一步

产出写入 `outputs/scan/{yyMMdd}-{descriptor}/`（workspace 根），
`descriptor` 为本次扫描主题（kebab-case，≤30 字符，如 `thread-leak`），
同日同主题重跑追加 `-N` 后缀：

```
outputs/scan/260813-thread-leak/
  └── scan-report.md        # 主报告（含 日期/范围/结论/建议）
  └── scan-report.json      # 可选：机器可读命中清单
```

**Guardrails**

- Read-only operation: search/analysis never modifies code, never checks out or switches workspaces (work only via read-only `git ls-files` / `git grep` / `git show <branch>:<file>`)
- Minimal loading: load only by hit location, never read the whole repo
- Each batch of fixes requires confirmation (Change Control discipline)
- Result dir is append-only; never overwrite existing scan reports
