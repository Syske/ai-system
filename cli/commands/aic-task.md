---
description: 日常任务 - 执行一次性杂务（写脚本/分析数据/转换/小工具），可作 chain 积木
---

Execute a one-off daily chore directly in conversation or as a chain block:
one-off scripts, data analysis, small conversions or tools. No OpenSpec chain,
no gate pipeline.

**Inputs**: Task description (required, free text); optional workspace/project
context.

**Steps**

1. **Clarify the goal** — a vague request → ask one question at a time
   (karpathy); ambiguity or contradiction → STOP and ask; never silently pick
   a side.
2. **Execute directly** — no plan gate (the A1 Plan Gate targets develop Task
   Cards, not chores). BUT design-decision tasks (cross-file design,
   contract-relevant choices, multi-step pipelines) get a short plan confirmed
   first; deviations STOP.
3. **Deliverables** land under the run context
   `outputs/chain/{yyMMdd}-{descriptor}/` per governance/outputs-convention.md:
   when launched as an `adhoc-task` chain block, register the produced artifact
   into chain-manifest.yaml (`record_artifact`) so downstream blocks locate it;
   standalone runs create the same one-block directory structure.
4. **Report briefly** — what was done, where the deliverables live, how to
   verify. Optionally record one line in the per-run diagnostic log.

**Outputs**

- Deliverable files under `outputs/chain/{yyMMdd}-{descriptor}/`
- Short completion note in the conversation (what / where / how to verify)

**Guardrails**

- Do NOT start an OpenSpec chain, do NOT create task cards, do NOT require a
  project container for chores.
- Contradictions / ambiguity → STOP and ask (one question at a time).
- Reuse existing implementations (action-semantic scan) over self-building
  (karpathy / P49; T-009 evidence 2026-09-09).
- As a chain block: register the artifact into the chain-manifest so
  downstream blocks can read it from the manifest, never guess paths.