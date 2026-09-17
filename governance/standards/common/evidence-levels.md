# Evidence Levels (证据等级)

Version: 1.0

---

## Purpose

Every technical conclusion in main-chain artifacts must carry an explicit
evidence level, so readers (human or AI) can distinguish verified facts from
inferences and assumptions. This is the anti-fabrication discipline for the
main chain (Task Cards, review findings, design/spec conclusions).

Adopted from the TR5 extension discipline (`extensions/tr5/references/
coolspec-behavior-discipline.md`, originally absorbed from SenSpec's
backend-ai-behavior-rules) and promoted to the main chain (2026-09-17).

---

## Levels

| Level | Meaning | Must be backed by |
|---|---|---|
| **E1 — 代码事实** (code fact) | The claim is directly verifiable in code | Concrete file + line / symbol reference |
| **E2 — 文档事实** (doc fact) | The claim is explicitly stated in a document | Document name + section (TR2/Wiki/spec/contract/config) |
| **E3 — 推断** (inference) | Reasoned conclusion from E1/E2 evidence | The E1/E2 facts it is derived from |
| **E4 — 假设** (assumption) | Not yet verifiable; pending confirmation | Owner + deadline (see placeholder format) |

## Rules

1. **Every technical conclusion carries a level.** Facts, impact claims,
   root causes and compatibility statements in Task Card 完成定义/验收标准,
   review findings, and design/spec conclusions are annotated `E1`-`E4`.
2. **Downgrade when unsure.** If the evidence does not support the claimed
   level, state the lower level — never claim a higher level than the
   evidence allows.
3. **Unverifiable → placeholder, not fabrication.** When the evidence is
   missing and the conclusion is needed, write a placeholder instead of
   inventing:
   ```
   ⚠️ 待确认: {owner} / {deadline} — what must be confirmed and why
   ```
   A placeholder blocks completion of the item; it is resolved before the
   artifact is accepted.
4. **Code search before inference.** Prefer E1 (code fact) via the
   three-tier code search (CodeGraph → ast-grep → grep); only fall back to
   E3/E4 when search cannot resolve the question.

## Application Points

- **Task Cards** (`tasks/cards/T-{id}.md`) — each card carries an
  `**证据等级**` field; 完成定义/验收 items annotate factual claims with a
  level (see `skills/task-splitter/workflow.md` and the template
  `templates/prompts/tasks-template.md`).
- **Review findings** — findings in review reports annotate their basis with
  a level (`skills/review/SKILL.md`); a finding without an evidence level is
  treated as E4 until verified.
- **Design / spec conclusions** — technical decisions and impact statements
  in design.md / spec conclusions carry levels where a reader could not
  otherwise tell fact from inference.

## Reference

- `governance/SOURCE_OF_TRUTH.md` — priority of information sources
- `governance/CONTEXT_LOADING.md` — read discipline (search before read)
- `extensions/tr5/references/coolspec-behavior-discipline.md` — TR5-side
  evidence discipline (same levels)
