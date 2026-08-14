---
description: AI 系统维护 - repo-lint 校验 + repository-maintainer 巡检 + 治理一致性抽查
---

Run routine maintenance on ai-system and the workflow system: tool checks, mode-based inspection, contract consistency spot checks, producing a maintenance report.

**Inputs**: Mode (weekly / monthly / quarterly / on-demand, default weekly); optional Scope (for on-demand, limits the range, e.g. workflows / runtime / skills / governance / cli).

**AI scheduling** (ADR-0009):
- At session start the AI runs `python tools/quick-check.py` (read-only,
  seconds); issues are reported and recorded to
  metrics/quick-check-{date}.json.
- The AI checks workspaces/.aic-state.yaml → maintenance.next_maintenance;
  when due, it prompts the user for authorization before running this command.
- The user decides only whether to run and which Mode/Scope.

**Steps**

0. **Pre-check (AI auto, read-only)**

   ```bash
   python tools/quick-check.py            # lint + path + extensions, records findings
   python tools/quick-check.py --history  # recent snapshots (trend for report)
   ```

1. **Tool checks** (run in the ai-system directory)

   ```bash
   python tools/repo-lint.py --repo-root .
   python tools/repo-metrics.py --repo-root . --snapshot metrics/maintain-{date}.json
   python tools/path-audit.py
   ```

   Do not proceed to later steps until BLOCKER / ERROR are fixed (report only, do not fix on your own).

2. **Mode-based inspection** (per skills/repository-maintainer and OPERATIONS.md section 9)
   - weekly: duplication report, dependency graph, orphan assets, health score
   - monthly: architecture review, capability matrix, lifecycle report, evolution suggestions
   - quarterly: workflow redesign assessment, capability restructuring, Playbook consolidation, knowledge cleanup
   - on-demand: run the corresponding items above per Scope
   - Scope=extensions (any mode): run the extensions domain inspection —
     `python tools/extensions-lint.py` (conventions + tracked artifacts),
     `python tools/extensions-lint.py --fix-missing-log` (scaffold logs),
     verify extensions repo sync (`git -C <workspace>/extensions status`),
     and report per-extension health (SKILL.md / OPTIMIZATION_LOG coverage)

2.5 **AI system health (analysis workflow, internal)** — run the analysis
   workflow's checks (structure/quality/consistency) as an internal stage;
   the analysis workflow is not a standalone menu entry.

2.6 **Knowledge lifecycle (internal)** — per OPERATIONS 1.7: collect (after
   release/retrospective), review (monthly: de-dup/contradiction/stale),
   archive (quarterly). Managed by AI as part of the maintenance cycle.

3. **Governance consistency spot check** (always, to prevent recurrence of past issues)
   - workflows/*.md: all eight sections present and in order (Purpose/Runtime/Preconditions/Inputs/Context/Outputs/Exit Criteria/Next); terminology matches workflows/README.md selection table; Runtime reference files exist; Preconditions/Next chain closes
   - config/workflows/*.yaml: registry stays minimal (name/workflow/runtime), no re-bloating into inputs/outputs/next (prevent A1 recurrence)
   - Referenced paths exist: files referenced in governance/standards/, loaders/, templates/prompts/, cli/commands/ all exist (prevent stangards / runtime-workspace style broken links)
   - Link health: junction/symlink target dirs like projects/ exist and are accessible (`Get-Item -Force` to check LinkType and Target)
   - Doc-vs-reality: AGENTS.md workspace structure diagram, AI_DEVELOPMENT_CONTRACT architecture diagram, OPERATIONS entry sections match the actual directory layout
   - State hygiene: project/change references in workspaces/.aic-state.yaml still exist
   - **Proposal leftovers**: run `python tools/proposal-audit.py` — evaluate open proposals (Status ≠ Implemented/Approved/Rejected/Archived) and unclosed `- [ ]` action items in reports/; refresh the index (`--refresh-index`) and report each leftover's disposition (approve / implement / reject / defer)

4. **Persist report**
   - Write to ai-system/reports/MAINTENANCE-{date}.md: findings list (by severity), fix suggestions, metric comparison (vs previous snapshot)
   - Minor issues (typos, broken links, doc drift) may be fixed in place after confirmation and recorded
   - Structural changes (directory adjustments, module merges, contract modifications) **output suggestions only**, go through the OPERATIONS section 11 change management flow (Analyze → Propose → Review → Approve)

**Output**

## Maintenance Report

- 工具校验结果（lint BLOCKER/ERROR/WARN 计数、指标变化）
- 巡检发现（按严重度分级）
- 一致性抽查结论（逐项通过/失败）
- 修复动作与建议清单
- quick-check 趋势（近 N 日快照对比）

完成后更新 workspaces/.aic-state.yaml:

```yaml
maintenance:
  last_run: {date}
  mode: {mode}
  next_maintenance: {date + interval}   # weekly:+7d monthly:+30d quarterly:+90d
  last_findings: [...]                    # 本次问题摘要
```

**Guardrails**

- Follow AI_DEVELOPMENT_CONTRACT: no architecture redesign, no moving responsibilities across modules, structural changes prohibited from direct implementation
- Confirm before each batch of fixes (Change Control)
- Inspection is read-first; modifications limited to confirmed minor fixes
- This command maintains ai-system ARCHITECTURE only; aic-tool health runs separately via quick-check (OPERATIONS 1.8.1)
- Maintenance experience (CI env, pyc cache, repo layout) is recorded in reports/ — consult the index, not this file
- CI without the extensions repo: parser/mr.provider checks degrade to WARN, not ERROR
