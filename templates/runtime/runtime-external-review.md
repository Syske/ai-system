# Runtime: External Review

## Purpose

Execute an external blind review end to end: bundle → isolated judge runs → shape check →
cross-model reconciliation → per-finding verification → curated report → inbound gate.

The value of this runtime is **independence**: the judges see the artifact without its internal
conclusions, without our framing and without repository identity. Everything else (verification,
adjudication, fixes) stays inside this system.

## Governance

- `governance/AI_OPERATING_RULES.md` — confirmation, stop conditions, Issue Capture.
- `governance/policies/proposal-policy.md` + `OPERATIONS.md §12` — any structural follow-up
  becomes a proposal; nothing structural is changed inside a review run.
- `templates/prompts/external-ai-review.md` — the **inbound gate**: every external claim is
  KEEP / REVISE / REJECT / UNVERIFIABLE before it may enter the system.
- `governance/REFLECTION_RULES.md` — Reflection before completion.

## Responsibilities

- Build bundle packages that are **hygienic** (no identity, no internal conclusions, no binaries).
- Run judges in **isolated sessions** (no workspace context, no tools).
- Treat every judge output as an **unverified input**; verify before counting a finding.
- Produce a **durable, curated report** plus non-committed run-time evidence.
- Never modify the reviewed artifact during the review.

## Runtime Context

Load only:

- `tools/blind-bundle.py`, `templates/prompts/external-blind-review.md` (prompts + discipline).
- The judge model list from the local model store, and the provider that serves it.
- The artifacts produced by this run (bundles, raw outputs, verification evidence).

Never load the artifact's `reports/`, `logs/`, `metrics/` or `archived/` into a bundle.

## Phase 1 — Scope and Judge Selection

1. Confirm the artifact root and that it is git-tracked (`git ls-files` non-empty).
2. Choose the layer split. Default for a layered repo: **doc layer** (prose, specs, templates,
   loaders, governance) + **code layers** (one bundle per code area, each ≤ 200K tokens).
3. Choose judges: one **primary** and one **cross** judge from **different vendors**, both
   **different from the artifact's authoring model family**. Verify availability with the local
   model listing before running; do not fall back to a same-family model.
4. Record the plan (artifact, layers, judges, model ids/versions) — it goes into the report.

## Phase 2 — Bundle Preparation (hygiene first)

1. Build bundles with `python3 tools/blind-bundle.py --repo <artifact-root> --out <dir>`.
2. The builder **must** apply, and the run **must** prove:

| Hygiene rule | Proof |
|---|---|
| No identity leak (remote URL, commit sha, machine user name, repo name) | sanitization pass + `--check` reports 0 |
| No internal-conclusion files (`reports/` `logs/` `metrics/` `workspaces/` `archived/`) | `--check` reports 0 excluded file headers |
| No binary content | builder skips binaries; `--check` reports 0 |
| Placeholders in prose are not mistaken for paths | sanitizer keeps `<owner>` / `<user>` forms |

3. `--check` failing means **stop**: fix the builder or the exclusion list; never run judges on an
   unproven bundle.

## Phase 3 — Isolated Judge Runs

Run each bundle against each judge in a **fresh session**, from a neutral directory, with tools and
context files disabled. Two decisions matter for reproducibility:

1. **Isolation** — disable all tools, all context-file discovery, all extensions, skills and prompt
   templates, and session persistence; run from an empty directory outside the reviewed repository.
   Otherwise the judge can read the local tree and the review stops being blind.
2. **Determinism** — prefer the lowest sampling temperature the provider accepts; if the client
   cannot set it, run the bundle twice with the same judge and compare, and report the observed
   variance. Record model id + version for every run.

Run long bundles in the background with a hard timeout per pass, and poll the run log instead of
blocking — a single bundle takes minutes, and a blocking shell call will time out first.

## Phase 4 — Shape Check and Retry

A judge output is only usable if it has the expected shape. Known failure: a judge that wants tools
but has none emits **tool-call syntax as text** and returns almost immediately.

- Fail signals: run finished in well under a minute, or the output contains tool-call markup, or the
  output is far below the expected size.
- Action: re-run that bundle/judge pair once. If it fails again, record it as a failed pass and
  continue with the other judge (report the gap explicitly).
- Never hand a failed pass to reconciliation.

## Phase 5 — Cross-Model Reconciliation

1. Parse severity-tagged findings from every successful pass into one machine-readable index
   (`findings-index.md`).
2. Classify by agreement:
   - reported by **both** judges → **high confidence**;
   - reported by **one** judge → **needs verification** (locate it in the artifact first);
   - **conflicting** claims (e.g. "docs promise X / code does not implement X") → adjudicate.
3. Watch for judge-specific distortion: judges may **rewrite file paths** while keeping the
   substance correct. Treat the path column as a hint, never as evidence — re-locate every
   single-judge finding by searching the artifact.
4. Expect and record judge false positives; a shared misreading is also signal (it usually means the
   document is genuinely ambiguous → rewrite it).

## Phase 6 — Verification Before Counting

For every finding that will enter the report:

1. Locate it in the artifact (grep / read the cited file).
2. Reproduce the claimed behaviour where it is executable (run the check, count the collected
   tests, evaluate the regex, re-run the gate) — a finding without reproduction is reported as
   unverified, not as a defect.
3. Record the disposition: verified-real / misread / not-a-defect / unverified, with the evidence
   that decided it.

Fixes are **not** part of this phase; verified defects are handed to the normal change process
(minor fix with confirmation, or a proposal for structural work).

## Phase 7 — Curated Durable Report

Write `EXTERNAL-BLIND-REVIEW-{date}.md` into `reports/` (committed, registered in the reports
index). Curate, do not dump:

- one-page conclusion (judges, bundle scope, finding counts, cost, effort);
- method + blind-review discipline (so the next run does not have to re-derive it);
- **verified findings** with evidence and (if fixed) the commit;
- cross-model intelligence (agreement, distortion, false positives);
- derived conclusions / follow-up proposals;
- leftovers that were not adjudicated;
- explicit statement of what the report does **not** cover.

Run-time evidence (index, bundles, raw outputs, logs) stays in the workspace run directory and is
**not** committed; the committed report must not contain path references into it.

## Phase 8 — Inbound Gate and Follow-up

1. Take every conclusion through `templates/prompts/external-ai-review.md`
   (KEEP / REVISE / REJECT / UNVERIFIABLE) with its evidence.
2. Route the KEEPs: in-place minor fix (with confirmation) or a proposal per
   `governance/policies/proposal-policy.md §1.1`.
3. Register the report in `reports/README.md`; register proposals in `reports/PROPOSALS.md`.
4. Record the run in the per-run diagnostic log (per `runtime-diagnostic-log.md`).

## Outputs

- reports/EXTERNAL-BLIND-REVIEW-{date}.md
- findings-index.md

## Output Placement

The durable record goes to `reports/` in the reviewed system repository (committed, registered in
the reports index). The run-time evidence (`findings-index.md`, bundles, raw judge outputs, run
logs) goes to `outputs/code-review/{yyMMdd}-external-blind-review/` and is **not** committed: the
durable report must not carry path references into non-committed run-time evidence.

## Execution notes (operational discipline)

| Topic | Practice |
|---|---|
| Isolation flags | tools disabled, context files disabled, extensions + skills + prompt templates disabled, no session persistence, neutral working directory |
| Prompting | one prompt per pass (doc layer / code layer / cross adjudication), no extra hints — do not steer the judge toward expected findings |
| Long runs | background + hard per-pass timeout + poll the log; never block a single call for the whole set |
| Failed pass | shape check → single retry → record as gap if it fails again |
| Cost | prefer an existing provider/plan; record tokens and cost per run; if the plan is unavailable degrade to the smallest useful scope (doc layer, single judge) and say so |
| Blind integrity | if a bundle cannot be proven hygienic, stop — a leaked bundle is worse than no review |
| Model independence | never judge with the artifact's authoring model family; record model id + version |

## Reflection

Before declaring completion, execute Reflection according to governance/REFLECTION_RULES.md.

Evaluate:

- Did the bundles stay hygienic (proof, not assumption)?
- Was every counted finding verified, and is every unverified item labelled as such?
- Did any judge distort evidence, and was that recorded?
- Is the durable report self-contained (no paths into non-committed run-time evidence)?
- What did this run teach that belongs in the discipline above?

## Completion

Report to the user: judges + models used, bundle scope and sizes, finding counts by severity,
verified-vs-misread split, what was fixed, what is left unadjudicated, and the report path.