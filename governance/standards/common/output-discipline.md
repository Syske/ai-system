# Output Discipline

## Scope

Governs **agent replies only** — not artifacts, not code, not reports.

One question only: once the business/process contracts are already satisfied
(Completion report fields, Runtime Result, Task Card, decision format),
**how to avoid low-value output**.

It never replaces those contracts. Artifacts stay complete; replies stay lean.

## Priority

**Correctness > Completeness > Auditability > Conciseness**

Conciseness ranks **last**: when in doubt, keep the information and cut the words.
A short reply that drops evidence, constraints or uncertainty is a **defect**, not conciseness.

## May be dropped

- What the user already knows: their request, their document, decisions just confirmed
- What already lives in an artifact: reports, task cards, diagnostic logs, commit messages
- Raw tool output: grep / find / scan / test dumps — keep the judged conclusion plus the line that proves it
- Process narration: "I will now…", "Let me analyse…", step-by-step self-commentary
- Filler and courtesy: praise, restating the question, "as mentioned above" / 「如前所述」式重复
- Summaries that repeat content already given earlier in the same reply

## Must never be dropped

- Conclusion / decision
- Evidence: `file:line`, the numbers or the output actually needed to judge the claim
- Constraints, contracts, thresholds
- Risks and uncertainty — including "I could not verify this"
- Verification results: what was run, what passed / failed
- The request for the user's decision (options + tradeoffs)

## Where reply shape is owned

- Per-stage reply shape: the runtime (`templates/runtime/*.md`)
- Worker / subagent replies: `templates/prompts/worker-contract.md`
- Artifact content: **unchanged** by this standard

## Observation, not a target

Never use a token-reduction percentage as an acceptance metric — a target invites
deleting evidence to hit it. Observe **trends** instead: `tools/prompt-metrics.py`
(prompt size, prefix stability) and `tools/context-audit.py` (session tokens),
read together with information completeness and repetition rate.