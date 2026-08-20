# External AI Conclusion Review (第三方 AI 结论核查)

You are verifying a conclusion produced by an external AI (or an external analyst /
share link) before it may enter this system. External conclusions are **unverified
inputs**, not sources of truth. They never override the
`governance/SOURCE_OF_TRUTH.md` hierarchy and are never adopted verbatim.

## When to Use

Trigger words: `外部 AI 结论`, `第三方结论`, `DeepSeek/其他 AI 的结论`, `帮我核对/复核某结论`,
`这份分析对不对`. Use whenever a user hands over a conclusion from another AI/share
(e.g. a DeepSeek share link) and asks to adopt, verify, or "核对" it.

## Procedure

1. **Fetch the raw source text** — for share links use the local export path
   (`skills/deepseek-share-to-md`）to pull the exact conversation into Markdown;
   do NOT treat the summary as the source.

2. **Claim-by-claim evidence check** — split the external conclusion into discrete
   claims. For each claim, ask:
   - What evidence would prove it? (log line, config, stack trace, code, metric)
   - Does the evidence actually appear in the raw source / repository? (gate function)
   - Is the claim consistent with the repository / real symptom?

3. **Adjudicate each claim** — mark one of:
   - **KEEP** (evidence-backed, adopt)
   - **REVISE** (direction right, details corrected) — record the correction + why
   - **REJECT** (unfounded or contradicted) — record the reason + counter-evidence
   - **UNVERIFIABLE** (no evidence obtainable) — do not adopt; surface to user (per
     AI_USER_RESPONSIBILITY_CONTRACT D10 / E2 contradiction arbitration → user)

4. **Annotate the output** — produce a structured verdict table:
   ``| # | 外部结论 | 判定 | 证据 | 修正/理由 |``

5. **Never auto-admit** — unless a claim is KEEP with evidence, it does not enter
   reports / memory / wiki. Rejection and revision decisions are recorded.

## Guardrails

- Do not trust the external conclusion's framing; verify each claim independently.
- External conclusions are NOT sources of truth (SOURCE_OF_TRUTH).
- If the external conclusion conflicts with repository/evidence, present both sides
  and let the user arbitrate — never decide silently.
- Prior real example: an external conclusion stated `-Xmx ~3G`; verification against
  the actual JMX/capture data showed a different value — miscounted values would have
  led the root cause astray.

## Self-check

- Every KEEP claim cites a specific verifiable source (not "the AI said").
- REJECT / REVISE carry explicit reason + counter-evidence.
- Nothing was adopted without the user seeing the verdict table.
