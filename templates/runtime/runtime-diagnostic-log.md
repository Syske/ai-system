# Runtime: Diagnostic Log

## Purpose

Persist a per-run diagnostic record for every command / workflow completion, so
any past run can be traced and audited after the session ends. Fields mirror the
Completion Report (AI_OPERATING_RULES §Completion) + Reflection checklist
(REFLECTION_RULES) exactly — this is the Completion Report's durable on-disk copy,
not a second, divergent schema.

## Where Writes Land

```
ai-system/logs/
└── <command|workflow>-<YYYYMMDD-HHMMSS>.md   # one record per run
```

- Filename begins with the run object (e.g. `aic-scan-20260817-183000.md`,
  `develop-20260817-190000.md`); timestamp prevents overwrite.
- Plain-text Markdown; greppable / diffable / searchable. No external dependency.

## Field Template

```markdown
# <command|workflow> 运行诊断 — <timestamp>

## 运行对象
<command/workflow name + input essentials: scope / project / change id>

## 结果
<exit code / artifact path / completed or failed>

## 验证 (gate)
<diff shown / grep hit count / test output 0 failures — must carry independent
evidence; never "should succeed">

## 修改文件
<list>

## 新建文件
<list>

## 偏差 (L1/L2)
<recorded or None>

## 风险
<list>

## 下一步建议
<Next Recommendation>

## Reflection (五问)
<Simpler impl / Duplication / Standards / Over-engineering / Completeness — one line each>
```

## Split-Out Detail (on-demand)

A run's full walkthrough (raw命令输出、复现步骤、长 stack trace、完整逐文件 diff)
SHOULD NOT be inlined into the main diagnostic record — it bloats grep/read. Instead:

- Write the detail to a sibling file: `logs/…-<timestamp>.detail.md`
- The main record keeps one **reference line**: `## 详细日志: logs/…-<timestamp>.detail.md`
- Rule of thumb: if a section would exceed ~30 lines, split it out and reference it.

This keeps every main record a one-page summary + a pointer, and lets full detail
be kept or discarded independently (matching CONTEXT_RETENTION: keep P0 decision,
drop exploration noise).

## Archival Layering & Version Control

- `logs/` (the per-run record files) is a **runtime state** directory and is
  git-ignored (see ROOT .gitignore, "Runtime state" group) — records live on the
  local machine only; they do not ride the repository/PR evolution.
- This template + the governance references are the **versioned**, tracked
  specification of the archival convention (not the records themselves).
- If cross-environment or history-long tracing is ever required, revisit whether to
  version `logs/` (whitelist scheme) — do not pre-empt it (Evolution Principle).

## Write Discipline

- **When**: every command/workflow writes its record during the REPORT / Completion phase.
- **Fails are detailed**: a failed/abnormal run MUST include root cause + reproduction steps.
- **Normal runs are one page**: a summary + reference, not a full dump.
- **Evidence first**: only record fresh output of actually-run commands (exit code,
  diff, grep count); forbidden to write "should succeed" claims.
- **Runtime-file reads (R1)**: if the run's prompt skeleton referenced a full runtime
  template (`Full runtime template: <path>`), note in one line whether the agent
  actually read the referenced file per phase — this feeds the skeletonization
  cost/benefit measurement (prompt-metrics / Q2-R1). Absence of the line means
  "not read".
- **Gradual field growth**: only add fields when a real "cannot trace back this run"
  case shows up (Evolution Principle) — do not pre-inflate.

## Boundary

- Does NOT replace `OPTIMIZATION_LOG.md` (skill实战优化) — that is per-skill and
  written only on optimization.
- Does NOT replace `metrics/*.json` (system health snapshots) — those are quantitative;
  this is textual per-run diagnostics.
- Does NOT introduce background collection / third-party logging / a database.
