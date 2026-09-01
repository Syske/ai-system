# Language Convention

Version: 1.2

---

## Purpose

Define which parts of the AI Runtime use English and which use Chinese.

This convention ensures:
- Flow control is deterministic, unambiguous, and globally portable
- User-facing reports are readable for the target team

---

## Principle

```
AI FLOW CONTROL → ENGLISH
USER-FACING OUTPUT → SYSTEM LANGUAGE (config/menu.yaml → locale; currently zh → Simplified Chinese)
```

---

## English (AI-Internal)

The following layers MUST use English:

| Layer | Scope | Reason |
|---|---|---|
| Workflow definitions | Purpose, Preconditions, Inputs, Outputs, Exit Criteria, Next | Machine-consumed; must be deterministic |
| Command definitions | Steps, decision rules, guardrails (cli/commands/aic-*.md) | Execution logic; must not have ambiguity |
| Runtime templates | Phase names, step instructions, decision rules | Execution logic; must not have ambiguity |
| Skills | Implementation instructions, validation rules, anti-patterns | Reusable across teams |
| Governance | Rules, standards, policies | Authoritative; English is less ambiguous |
| RFC / ADR | rfc/ 下的规范与决策记录 | Authoritative records; English is less ambiguous |
| Coding Memory | Lesson entries, memory indexes (governance/memory/) | Loaded by agents at execution time; must be deterministic |
| Config files | YAML keys, routing rules | Machine-parsed |

---

## Chinese (User-Facing)

The following user-facing outputs MUST follow the system language
(`config/menu.yaml → locale`; currently Simplified Chinese):

| Output | Scope | Reason |
|---|---|---|
| Completion reports | Summary, findings, recommendations | Read by Chinese-speaking developers |
| Review reports | Design review, code review, quality review | Read by Chinese-speaking reviewers |
| Release reports | Release checklist, risk report, branch review | Read by release manager and team |
| Verification reports | Spec/contract/scenario verification results | Read by QA and developers |
| Task Cards | Task descriptions, acceptance criteria | Read by implementing developers |
| **Interactive prompts** | Questions and choices presented to the user during a Runtime (confirmation requests, clarification questions, branch selection, next-action choices) | Read by the user at the moment of interaction |
| **Code comments & Javadoc** | Business logic explanations, algorithm notes, field descriptions | Read by Chinese-speaking maintainers |

Rule (binding): ALL user-facing text — interactive prompts, completion / review / release /
verification reports, task cards, menu copy — MUST be presented in the system language
(`config/menu.yaml → locale`). Repository assets are machine-checked by
`repo-lint.py check_language`; runtime report output is subject to the completion-time
language self-check below. AI control flow stays English; only the text shown to the user
is localized.

Code comment convention (per `governance/standards/common/documentation.md`):
- Comments, Javadoc, field descriptions → Chinese
- Identifiers (class names, method names, variables) → English
- Commit messages → Chinese (Conventional Commits)
- Production error messages → English (encoding safety)

### 简体要求 (Simplified Chinese Only)

All Chinese output — report bodies and tables, code comments/Javadoc, command-line
(CLI/bash) explanations, interactive prompts, commit messages, and in-session process
notes — MUST use **Simplified Chinese (简体)**. Traditional/variant wording (繁体) is
not permitted in any Chinese output, including transient bash comments and process
captions; it breaks convention consistency (e.g. `检查/脚本/传参/转义`, not
`檢查/腳本/傳參/轉義`) and can leak into final deliverables.

Self-check (report/completion time, per AI_OPERATING_RULES gate function):
1. **Language-selection check (runtime gate, P45)**: BEFORE presenting any
   user-facing report, run `python3 tools/language-gate.py <report-file>`.
   PASS → present; WARN → review suspicious lines (`--list-suspicious`), fix or
   accept with a note; FAIL → rewrite the user-facing text in the system language
   and re-run the gate. Gate outcome is recorded in the per-run diagnostic log.
   (Mechanism defined in `templates/runtime/runtime-base.md` 语言自检 steps and
   proposal P45.)
2. **Simplified-Chinese check**: all Chinese output MUST use 简体 (no 繁体/变体).

---

## System Language (Single Source of Truth)

The system language has exactly one source: `config/menu.yaml → locale` (currently `zh`).
Any component that presents user-facing text (runtimes, commands, wizard, menu, reports)
resolves the language from this key — never hardcodes it, never derives it elsewhere.
Exceptions: technical identifiers, file/structure names, and AI control flow stay English
and are language-independent by definition.

## Hybrid (Bilingual Headings)

Reports that contain technical identifiers use bilingual headings:

```markdown
## 实现总结 / Implementation Summary

## 发现清单 / Findings

## 风险 / Risks
```

The Chinese heading comes first for readability. The English heading follows for searchability.

---

## Reference

This convention is binding for all Workflows and Runtimes.

Referenced from:
- `governance/AI_OPERATING_RULES.md`
- `loaders/standards-loader.md` (Always Load)

## Changelog

- v1.2 (2026-09-01): language-selection self-check升级为运行门禁（P45 实施）——
  呈现前运行 `tools/language-gate.py`，PASS/WARN/FAIL 三态闭环；机制定义于
  runtime-base 语言自检步骤 + P45。
- v1.1 (2026-09-01): user-facing outputs upgraded SHOULD → MUST (follow the system
  language, not hardcoded Chinese); explicit single-source-of-truth anchor
  (`config/menu.yaml → locale`, new section); self-check extended to language-selection;
  interactive-prompt rule restated as binding for all user-facing text (converges the
  pilot A interaction-language constraint from ai-commands back into the convention;
  L1 Language-Boundary batch, confirmed 2026-09-01).
- v1.0: initial.
