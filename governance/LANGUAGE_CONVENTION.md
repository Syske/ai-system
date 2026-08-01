# Language Convention

Version: 1.0

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
USER-FACING REPORTS → CHINESE
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
| Coding Memory | Lesson entries, memory indexes (governance/memory/) | Loaded by agents at execution time; must be deterministic |
| Config files | YAML keys, routing rules | Machine-parsed |

---

## Chinese (User-Facing)

The following outputs SHOULD use Chinese:

| Output | Scope | Reason |
|---|---|---|
| Completion reports | Summary, findings, recommendations | Read by Chinese-speaking developers |
| Review reports | Design review, code review, quality review | Read by Chinese-speaking reviewers |
| Release reports | Release checklist, risk report, branch review | Read by release manager and team |
| Verification reports | Spec/contract/scenario verification results | Read by QA and developers |
| Task Cards | Task descriptions, acceptance criteria | Read by implementing developers |
| **Interactive prompts** | Questions and choices presented to the user during a Runtime (confirmation requests, clarification questions, branch selection, next-action choices) | Read by the user at the moment of interaction |
| **Code comments & Javadoc** | Business logic explanations, algorithm notes, field descriptions | Read by Chinese-speaking maintainers |

Rule: interactive prompts follow the system-specified language (`config/menu.yaml → locale`).

Code comment convention (per `governance/standards/common/documentation.md`):
- Comments, Javadoc, field descriptions → Chinese
- Identifiers (class names, method names, variables) → English
- Commit messages → Chinese (Conventional Commits)
- Production error messages → English (encoding safety)

---

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
