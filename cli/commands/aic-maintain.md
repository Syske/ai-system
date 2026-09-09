---
description: AI 系统维护 - repo-lint 校验 + repository-maintainer 巡检 + 治理一致性抽查
---

Run routine maintenance on ai-system and the workflow system: tool checks, mode-based inspection, contract consistency spot checks, producing a maintenance report.

**Inputs**: Mode (weekly / monthly / quarterly / on-demand, default weekly); optional Scope (for on-demand, limits the range, e.g. workflows / runtime / skills / governance / cli).

**Interaction language (mandatory):** All user-facing text (questions, choices, confirmations, completion/review reports) MUST follow the system language per `AI_OPERATING_RULES` §Language Boundary + `governance/LANGUAGE_CONVENTION.md` (current `config/menu.yaml → locale` = `zh`). AI control flow stays English; only the text shown to the user is localized.

**AI scheduling** (ADR-0009):
- Session start: run `python3 tools/quick-check.py` (read-only), record issues
  to metrics/quick-check-{date}.json.
- Check `config/maintenance.yaml → next_maintenance`; when due, prompt the
  user for authorization before running. User decides only whether to run and Mode/Scope.

**Steps**

0. **Pre-check (AI auto, read-only)**

   ```bash
   python3 tools/quick-check.py            # lint + path + extensions, records findings
   python3 tools/quick-check.py --history  # recent snapshots (trend for report)
   python3 tools/maintain-delta.py --check # delta verdict: NO_CHANGES -> skip full audits
   ```

   - `maintain-delta.py --check` verdicts: FIRST_RUN → full audit; NO_CHANGES
     (no commits since last full run) → skip heavy audits (quick-check + state
     hygiene + report); CHANGED → affected-area subset (`suggested` line)

1. **Tool checks** (run in the ai-system directory)

   ```bash
   python3 tools/repo-lint.py --repo-root .
   python3 tools/repo-metrics.py --repo-root . --snapshot metrics/maintain-{date}.json
   python3 tools/path-audit.py
   ```

   Do not proceed to later steps until BLOCKER / ERROR are fixed (report only, do not fix on your own).
   After the full run completes, record the delta baseline:

   ```bash
   python3 tools/maintain-delta.py --record   # record current HEAD as the next delta baseline
   ```

2. **Mode-based inspection** (per skills/repository-maintainer and OPERATIONS.md section 9)
   - weekly: duplication / dependency graph / orphan assets / health score
   - monthly: architecture review / capability matrix / lifecycle report / evolution
   - quarterly: workflow redesign / capability restructuring / Playbook / knowledge cleanup
   - on-demand: run the corresponding items above per Scope
   - Scope=extensions: `extensions-lint.py` (+ `--fix-missing-log`), verify repo sync (`git -C <workspace>/extensions status`), report per-extension health (SKILL.md / OPTIMIZATION_LOG coverage)

2.5 **AI system health (analysis workflow, internal)** — run its checks
   (structure/quality/consistency) as an internal stage; not a menu entry.

2.6 **Knowledge lifecycle (internal)** — per OPERATIONS 1.7: collect (after
   release/retrospective), review (monthly: de-dup/contradiction/stale),
   archive (quarterly). Managed by AI in the maintenance cycle.
   - **logs recycle**: scan `logs/` for **recurring (≥2x)** observations never
     captured to Coding Memory / env.yaml / a proposal → decide capture /
     machine-config / proposal (Issue Capture triage). Skip single-shot
     transient observations.

3. **Governance consistency spot check** (always, to prevent recurrence of past issues)
   - workflows/*.md: all eight sections present and in order (Purpose/Runtime/Preconditions/Inputs/Context/Outputs/Exit Criteria/Next); terminology matches workflows/README.md selection table; Runtime reference files exist; Preconditions/Next chain closes
   - config/workflows/*.yaml: registry stays minimal (name/workflow/runtime), no re-bloating into inputs/outputs/next (prevent A1 recurrence)
   - Referenced paths exist (governance/standards/, loaders/, templates/prompts/, cli/commands/); link health: junction/symlink targets like projects/ accessible (`Get-Item -Force` for LinkType/Target)
   - Doc-vs-reality: AGENTS.md workspace structure diagram, AI_DEVELOPMENT_CONTRACT architecture diagram, OPERATIONS entry sections match the actual directory layout
   - State hygiene: project/change references in workspaces/.aic-state.yaml still exist
   - **Run-log coverage**: cross-check uncommitted git changes vs logs/ diagnostic records — changes with no corresponding run log (e.g. tracked files modified outside a logged run) are flagged for attribution before commit (2026-09-01 maintain finding)
   - **Proposal leftovers**: run `python3 tools/proposal-audit.py` — evaluate open proposals (Status ≠ Implemented/Approved/Rejected/Archived) and unclosed `- [ ]` action items in reports/; refresh the index (`--refresh-index`) and report each leftover's disposition (approve / implement / reject / defer)

4. **Persist report**
   - Generate the skeleton first: `python3 tools/maintain-report.py --date {date}`,
     then fill narrative sections (findings / consistency / fix list).
     Non-destructive: existing file is not overwritten.
   - Write to ai-system/reports/MAINTENANCE-{date}.md: findings (by severity), fix
     suggestions, metric comparison (vs previous snapshot).
   - Run the language gate on the report before presenting (P45 pilot chain,
     runtime-base Complete step): `python3 tools/language-gate.py reports/MAINTENANCE-{date}.md`
   - Minor issues (typos, broken links, doc drift) may be fixed in place after
     confirmation and recorded; structural changes **output suggestions only**
     (OPERATIONS §11: Analyze → Propose → Review → Approve)

**Output**

## Maintenance Report

报告字段、`config/maintenance.yaml` 更新与 last_findings 纪律见
`skills/repository-maintainer/health.md` §Maintenance State Update（aic-maintain Output）。

**Guardrails**

- Follow AI_DEVELOPMENT_CONTRACT (no redesign / no responsibility moves / structural changes → suggestions only); confirm before each batch of fixes (Change Control)
- Inspection is read-first; modifications limited to confirmed minor fixes
- This command maintains ai-system ARCHITECTURE only; aic-tool health runs separately via quick-check (OPERATIONS 1.8.1)
- Maintenance experience (CI env, pyc cache, repo layout) is recorded in reports/ — consult the index, not this file
- CI without the extensions repo: parser/mr.provider checks degrade to WARN, not ERROR
