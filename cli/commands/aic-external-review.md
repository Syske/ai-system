---
description: 外部盲检 - 把制品交给跨厂商第三方模型做独立盲检，逐条核实后拣选为可入库报告
---

Run an **independent external blind review** of an artifact: build hygienic bundle packages, hand
them to cross-vendor third-party models that receive **no internal context**, reconcile and verify
every finding, and curate the durable report into `reports/`.

This is a **complement** to internal gates, not a replacement: internal gates and the author share
the same blind spots, so a fresh outside view is the only way to surface the class of defect where
"the gate itself silently stopped working".

**Inputs**:
- Artifact (optional, default ai-system): the repository under review (must be git-tracked)
- Scope (optional, default all layers): which layers to bundle — `all layers` / `doc layer only` /
  named code areas
- Judges (optional, default cross-vendor pair): primary + cross judge models

> Judge models must come from **different vendors** and must **not** be the artifact's authoring
> model family (same-family judges reintroduce self-preference bias). Model ids/versions are
> recorded in the report for reproducibility.

**Steps**

1. **Scope and judges**
   - Confirm the artifact root is git-tracked (`git ls-files` non-empty); otherwise stop
   - Split into layers: doc layer (prose, specs, templates, loaders, governance) + one bundle per code
     area, each ≤ 200K tokens
   - Verify judge availability against the local model list; never fall back to a same-family model

2. **Build bundles (hygiene is a gate, not a hope)**
   - `python3 tools/blind-bundle.py --repo <artifact-root> --out <run-dir>`
   - The builder excludes internal conclusions (`reports/`, `logs/`, `metrics/`, `workspaces/`,
     `archived/`) and binaries, and **sanitizes identity** (remote URL, machine user name)
   - Prove it: `--check` must report 0 identity leaks and 0 excluded file headers; if not, **stop**

3. **Run judges in isolation**
   - Fresh session per bundle × judge, from a neutral directory outside the artifact
   - Disable tools, context files, extensions, skills, prompt templates and session persistence so the
     judge cannot read the local tree (otherwise the review is not blind)
   - Use the per-pass prompts from `templates/prompts/external-blind-review.md`; add no extra hints
   - Long bundles: run in the background with a hard per-pass timeout and poll the log

4. **Shape check**
   - Fail signals: finished far too fast, contains tool-call markup, or far below expected size
   - Retry once; if it fails again record the pass as a gap and continue with the other judge
   - Failed passes never enter reconciliation

5. **Reconcile and verify**
   - Both judges → high confidence; single judge → must be located in the artifact before counting
   - Judges may rewrite file paths: re-locate every finding by search, never trust the path column
   - Reproduce executable claims (run the check / count the tests / evaluate the regex / re-run the
     gate); record verified-real / misread / not-a-defect / unverified with evidence

6. **Curate the durable report**
   - Write `EXTERNAL-BLIND-REVIEW-{date}.md` to `reports/` (committed + registered in the reports
     index); run-time evidence stays in the workspace run dir and is **not** committed
   - The committed report must not contain path references into non-committed run-time evidence

7. **Inbound gate (mandatory)**
   - Every conclusion goes through `templates/prompts/external-ai-review.md`
     (KEEP / REVISE / REJECT / UNVERIFIABLE) with evidence before it may enter the system
   - KEEPs route to an in-place minor fix (with confirmation) or a proposal
     (`governance/policies/proposal-policy.md §1.1`)

**Output**

- Durable report: `reports/EXTERNAL-BLIND-REVIEW-{date}.md` (committed, indexed)
- Run-time evidence: `outputs/code-review/{yyMMdd}-external-blind-review/` — `findings-index.md`,
  bundles, raw judge outputs, run logs (not committed, not indexed)

**Guardrails**

- Read-only on the reviewed artifact: this workflow never modifies the artifact under review
- No internal conclusions in bundles; no repository identity in bundles — if hygiene cannot be
  proven, stop instead of reviewing a leaked bundle
- No same-family judge; record model id + version for every pass
- External conclusions are unverified inputs: never adopt verbatim, never auto-fix without
  confirmation, and never let them override `governance/SOURCE_OF_TRUTH.md`
- Structural follow-up discovered by the review becomes a proposal (OPERATIONS §12); a review run
  does not change structure itself