# Governance

Quality gates, policies, naming conventions, and review standards for the AI repository.

## Core Rules

| File | Purpose |
|------|---------|
| `AI_OPERATING_RULES.md` | Global AI behavior rules (v1.3). Binding for all Workflows. |
| `SOURCE_OF_TRUTH.md` | Authoritative priority hierarchy of all information sources. |
| `CONTEXT_LOADING.md` | Minimal, deterministic context loading strategy. |
| `CONTEXT_RETENTION.md` | Cross-tool context retention: Keep/Drop priorities + handoff template. |
| `ATTENTION_MANAGEMENT.md` | Attention decay signals, mid-task checkpoints, interruption rules. |
| `REPOSITORY_FIRST.md` | Search-before-create principle. Reuse over rewrite. |
| `REFLECTION_RULES.md` | Mandatory reflection at every Workflow completion. |
| `LANGUAGE_CONVENTION.md` | English for AI flow control, Chinese for user-facing reports. Enforced by `repo-lint.py check_language` (Rule 1-3). |
| `AI_USER_RESPONSIBILITY_CONTRACT.md` | AI/user division of labor, decision rights matrix (D1-D10), escalation ladder, interaction protocol (per ADR-0009). |

## Quality & Review

| File | Purpose |
|------|---------|
| `repo-lint.md` | Structural naming rules for all components |
| `review-standard.md` | Skill review workflow and checklists |
| `violation-rules.md` | Violation severity classification |
| `karpathy-guidelines.md` | Coding guidelines to reduce LLM mistakes |
| `DIRECTORY-RESPONSIBILITY.md` | Per-directory responsibilities, new-asset decision tree, violation handling |

## Policies

| File | Purpose |
|------|---------|
| `policies/quality-gates.md` | BLOCKER/ERROR/WARNING/INFO quality definitions |
| `policies/skill-policy.md` | Skill creation and contribution guide |
| `policies/skill-lifecycle.md` | Skill lifecycle stages (Draft → Proposed → Active → Deprecated → Archived) |
| `policies/security-policy.md` | Security practices and review gates |

## Adding Governance Documents

New governance documents (policies, standards, rules) follow this structure:

```markdown
# <Topic> <Type>            # e.g. Cache Policy / SQL Standard
## Purpose                  # one sentence: what this document enforces
## Scope                    # which runtimes, workflows, or components it applies to
## <Rules>                  # numbered rules or tables (the binding content)
## Enforcement              # automated checks, tools, or review that enforce it
## Violations               # severity + handling (referencing violation-rules.md)
```

Rules:
- File name is kebab-case and reflects the content (`repo-lint.md`).
- Written in English (AI-internal governance layer, per `LANGUAGE_CONVENTION.md`).
- Register the file in this index (`governance/README.md`).
- Active standards only; obsolete standards move to `governance/archive/`.

## Language Enforcement (LANGUAGE_CONVENTION)

Language rules are enforced automatically by `repo-lint.py check_language`,
run by `tools/check.py` after every change:

| Rule | Scope | Requirement |
|---|---|---|
| 1 | `cli/commands/aic-*.md` Steps/Guardrails | English (flow control) |
| 2 | `cli/**/*.py` + `tools/*.py` comments | Chinese (documentation.md) |
| 3 | `governance/*.md` (excl. archive/, standards/, README, policies) | English (AI-internal) |

When adding a new governance document, keep it English and expect Rule 3 to
verify it on the next `check.py` run. See `tools/README.md` for the tool
coverage note.
