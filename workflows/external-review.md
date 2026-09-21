---
name: external-review
description: Run an independent external blind review of an artifact with cross-vendor judges, verify every finding against the repository, and curate the durable report.
workflow:
  inputs:
    required: []
    optional:
      - name: Artifact
        default: ai-system
      - name: Scope
        default: all layers
      - name: Judges
        default: cross-vendor pair
  next: [None]
  outputs:
    base: "reports/"
---
# Workflow: External Review

## Purpose

Run an **independent external blind review** of an artifact: hand the artifact to
third-party models that get *no internal context*, collect their findings, verify each one
against the repository, and curate the durable report.

External conclusions are **unverified inputs**: nothing enters this system before it passes
per-claim verification and the inbound gate
(`templates/prompts/external-ai-review.md`, KEEP / REVISE / REJECT / UNVERIFIABLE).
This workflow is a **complement** to the internal gates, never a replacement.

## Runtime

- templates/runtime/runtime-external-review.md

## Preconditions

- The artifact under review exists and is **git-tracked** (bundles are built from tracked files only).
- Judge models are available through an existing provider, and they are **independent from the
  artifact's authoring model family** (same-family judges reintroduce self-preference bias).
- The review is **read-only** on the artifact: it never modifies the reviewed repository.
- The artifact's internal conclusions (`reports/`, `logs/`, `metrics/`) are **not** part of the bundle.

## Inputs

Required:

- None

Optional:

- Artifact (default: ai-system)
- Scope (default: all layers)
- Judges (default: cross-vendor pair)

## Context

Load only:

- The bundle packages produced in this run (document layer / code layer packages).
- The judge model list, the blind-review discipline and the per-pass prompts.
- The verification evidence gathered for each finding (grep / git log / runtime checks).

Never load:

- The artifact's `reports/`, `logs/`, `metrics/`, `workspaces/` or `archived/` content into a
  bundle — internal conclusions and self-assessments anchor an external reviewer.
- Repository identity (remote URL, commit sha, machine user names) — it lets a networked model
  identify the repository and read its internal history, which defeats the blind review.

### Blind-review protocol (summary — details in the runtime)

1. **Split the artifact into layers** and build one bundle per layer (doc layer; code layers).
2. **Run each bundle in an isolated session** with tools disabled and context files disabled.
3. **Two cross-vendor judges**: a primary judge and a cross judge, each on the same bundles.
4. **Reconcile**: findings reported by both judges are high-confidence; single-judge findings must
   be located in the repository before they count (judges may rewrite file paths).
5. **Adjudicate through the inbound gate** before anything is recorded or fixed.

## Outputs

- reports/EXTERNAL-BLIND-REVIEW-{date}.md
- findings-index.md

**Placement (two-tier — deliberate, see P61)**: the durable record
`EXTERNAL-BLIND-REVIEW-{date}.md` is written to `reports/` in the reviewed system repository,
registered in the reports index, and is the only carrier that becomes part of the system's
history. The run-time evidence (`findings-index.md`, bundles, raw judge outputs, run logs) is
written to `outputs/code-review/{yyMMdd}-external-blind-review/` under the workspace root and is
**not committed and not indexed** — so no committed document may point at it with a path
reference (`outputs/` is outside the path-audit scope, so such references would never fail
loudly). The report is written in the system language (config/menu.yaml → locale, per
governance/LANGUAGE_CONVENTION.md).

## Exit Criteria

Success:

- Both judges ran on every bundle in the planned scope, every failure mode was handled
  (shape check + bounded retry), and the durable report was curated, verified per finding and
  registered in the reports index.

Stop:

- No independent judge model is available → report and stop (do not fall back to a same-family model).
- Bundle hygiene cannot be proven (identity leak or internal-conclusion leak detected) → stop and fix the bundle.
- The artifact is not git-tracked → stop (bundles would be unauditable).

## Next

- None