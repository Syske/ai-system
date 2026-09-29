---
description: AI 系统维护 - repo-lint 校验 + repository-maintainer 巡检 + 治理一致性抽查
---

Run routine maintenance on ai-system and the workflow system: tool checks, mode-based inspection, contract consistency spot checks, producing a maintenance report.

**Inputs**: Mode (weekly / monthly / quarterly / on-demand, default weekly); optional Scope (for on-demand, limits the range, e.g. workflows / runtime / skills / governance / cli).

**Interaction language (mandatory):** All user-facing text (questions, choices, confirmations, completion/review reports) MUST follow the system language per `AI_OPERATING_RULES` §Language Boundary + `governance/LANGUAGE_CONVENTION.md` (current `config/menu.yaml → locale` = `zh`). AI control flow stays English; only the text shown to the user is localized.

**AI scheduling** (ADR-0009):
- Session start: run `python3 tools/quick-check.py` (read-only), record issues
  to <workspace>/metrics/quick-check-{date}.json (outside the repo).
- Check `config/maintenance.yaml → next_maintenance`; when due, prompt the
  user for authorization before running. User decides only whether to run and Mode/Scope.

**Steps**

0. **Pre-check (AI auto, read-only)**

   ```bash
   python3 tools/quick-check.py            # lint + path + extensions, records findings
   python3 tools/quick-check.py --history  # recent snapshots (trend for report)
   python3 tools/maintain-delta.py --check # prints verdict + suggested subset; follow it
   ```

1. **Tool checks** (run in the ai-system directory)

   ```bash
   python3 tools/repo-lint.py --repo-root .
   python3 tools/repo-metrics.py --repo-root . --snapshot ../metrics/maintain-{date}.json
   python3 tools/prompt-metrics.py; python3 tools/context-audit.py   # P70 trend obs, never a token target
   python3 tools/path-audit.py
   python3 tools/maintain-delta.py --record   # after the full run: baseline current HEAD
   ```

   Do not proceed to later steps until BLOCKER / ERROR are fixed (report only, do not fix on your own).

2. **Mode-based inspection** (per skills/repository-maintainer and OPERATIONS.md section 9)
   - weekly: duplication / dependency graph / orphan assets / health score
   - monthly: architecture review / capability matrix / lifecycle report / evolution
   - quarterly: workflow redesign / capability restructuring / Playbook / knowledge cleanup; on-demand: the above per Scope
   - Scope=extensions: `extensions-lint.py` (+ `--fix-missing-log`), verify repo sync (`git -C <workspace>/extensions status`), report per-extension health (SKILL.md / OPTIMIZATION_LOG coverage)

2.5 **AI system health (analysis workflow, internal)** — run its checks as an
   internal stage; not a menu entry.

2.6 **Knowledge lifecycle (internal)** — per OPERATIONS 1.7: collect (after
   release/retrospective), review (monthly: de-dup/contradiction/stale),
   archive (quarterly). Managed by AI in the maintenance cycle.
   - **logs recycle**: scan `logs/` for **recurring (>=2x)** observations never
     captured to Coding Memory / env.yaml / a proposal → decide capture /
     machine-config / proposal (Issue Capture triage). Skip single-shot
     transients.
   - **Experience Inbox triage** (P71) — procedure and the read-only hard rule live
     in `MEMORY_GUIDELINES.md` "Experience Inbox"; do not restate them here. Runs even
     when empty. **Verify each `Source` before promoting**; discard needs a reason per
     candidate; no candidate is a legitimate result. Commit promotions, delete drafts.
   - **Record the five counts, always** (P71 5.9): generated / triaged / promoted /
     redirected / discarded + per-discard reasons + `<machine>`, into the report and
     `last_findings`. No counts = run incomplete.
   - **Snapshot the run denominator** (P71 5.9) — never read the rate back off `logs/`,
     it has been wiped before (INCIDENT-2026-09-24): count the four instrumented
     workflow logs, append `{ts, watermark, develop, review, bugfix, change-impact,
     files}` to `metrics/by-machine/<machine-id>/knowledge-runs.jsonl` (newer than
     `watermark` only; keep `files` verbatim so the count stays auditable).

3. **Governance consistency spot check** (always — these recur otherwise)
   - workflows/*.md: eight sections in order; terminology matches workflows/README.md; Runtime refs exist; Preconditions/Next chain closes
   - config/workflows/*.yaml: registry stays minimal (name/workflow/runtime), no re-bloating into inputs/outputs/next (prevent A1 recurrence)
   - Referenced paths exist (governance/standards/, loaders/, templates/prompts/, cli/commands/); junction/symlink targets like projects/ resolve
   - Doc-vs-reality: AGENTS.md + AI_DEVELOPMENT_CONTRACT diagrams, OPERATIONS sections vs actual layout
   - State hygiene: project/change references in workspaces/.aic-state.yaml still exist
   - **Run-log coverage**: uncommitted changes vs logs/ records — changes with no run log are flagged for attribution before commit (2026-09-01)
   - **Proposal leftovers**: `python3 tools/proposal-audit.py --refresh-index`; report each open proposal / `- [ ]` item's disposition (approve / implement / reject / defer)

4. **Persist report**
   - Skeleton first: `python3 tools/maintain-report.py --date {date}`, then fill
     findings / consistency / fix list. Non-destructive.
   - Write reports/MAINTENANCE-{date}.md: findings by severity, fix suggestions, metric
     comparison (vs previous snapshot), P71 5.9 counts + run-denominator snapshot path.
   - Language-gate the report (P45): `python3 tools/language-gate.py reports/MAINTENANCE-{date}.md`
   - Minor issues fixed in place after confirmation and recorded; structural
     changes **suggestions only** (OPERATIONS 11: Analyze → Propose → Review → Approve)

**Output**

## Maintenance Report

报告字段、`config/maintenance.yaml` 更新与 last_findings 纪律见 `skills/repository-maintainer/health.md` §Maintenance State Update。

**Guardrails**

- Follow AI_DEVELOPMENT_CONTRACT (no redesign / no responsibility moves / structural changes → suggestions only); confirm before each batch of fixes (Change Control)
- Inspection is read-first; modifications limited to confirmed minor fixes
- Maintains ai-system ARCHITECTURE only; tool health runs via quick-check (OPERATIONS 1.8.1)
- Maintenance experience is recorded in reports/ — consult the index, not this file
- CI without the extensions repo: parser/mr.provider checks degrade to WARN, not ERROR
- The Inbox is triage-read only; never cite a candidate as knowledge (P71 4.10)
