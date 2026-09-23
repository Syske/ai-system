# Worker / Subagent Output Contract

Binding for **every dispatched worker**: pi-worker style subagent, isolated research
agent, parallel per-module analysis, any delegated scan/audit.

This is a **hard boundary, not a style preference** — a worker that violates it
produces output the caller cannot act on.

## MUST

1. Return **conclusions** — the main context stays flat (CONTEXT_LOADING §subagent isolation).
2. Attach **evidence** to every conclusion: `file:line` + a ≤1-line quote, or the numeric result.
3. State explicitly what **could not be determined**, as `UNDETERMINED: <what is missing>` +
   `needs: <evidence that would settle it>`.
4. Distinguish **fact** from **inference** whenever confidence differs.
5. Use the fixed sections below, in this order.

## MUST NOT

- Repeat the task or restate the question.
- Paste source files or raw tool output — quote **at most one line**, as evidence.
- Narrate the process ("first I searched, then I read…").
- Add a closing summary that repeats the findings above it.
- Assert unsupported conclusions. **Never turn "not enough evidence" into "probably X".**

> The caller is a development system: a fabricated certainty propagates into code, specs and
> commits. An explicit `UNDETERMINED` is a **result**, not a failure. A wrong confident claim
> costs far more than one extra line of uncertainty.

## Output sections

```text
## Conclusions
- <conclusion> — evidence: <file:line / ≤1-line quote / number>

## Undetermined
- <what could not be verified> — needs: <evidence that would settle it>

## Notes (optional)
- <risks, side findings, blockers that affect the caller's decision>
```

## Relationship to other rules

- Output discipline (what may be dropped / must never be dropped): `governance/standards/common/output-discipline.md`
- Dispatch and isolation policy: `governance/CONTEXT_LOADING.md` §subagent isolation
- Multi-judge blind review has its own stricter format: `templates/prompts/external-blind-review.md`