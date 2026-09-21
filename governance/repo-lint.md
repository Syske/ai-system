# Naming Conventions

This document defines naming conventions for all components in the repository.

---

## Directories

| Component | Pattern | Examples |
|---|---|---|
| Skill | `kebab-case`, one or two words | `bugfix`, `java-maven`, `mock-test` |
| Workflow | `kebab-case`, one word preferred | `develop`, `bugfix`, `release` |
| Command | `kebab-case` after `aic-` | `aic-scan`, `aic-trace` |
| Playbook | `kebab-case` | `spring-boot-test`, `reflection-test-utils` |
| Knowledge | `kebab-case` | `domain-terms`, `coding-conventions` |
| Template | `kebab-case` | `implementation-report`, `bug-report` |
| Checklist | `kebab-case` | `validation`, `completion`, `retry` |
| RFC | `kebab-case` after `RFC-NNNN-` | `RFC-0001-repository-architecture` |
| ADR | `kebab-case` after `NNNN-` | `0001-openspec-integration` |

## Files

| Component | Entrypoint | Pattern |
|---|---|---|
| Skill entrypoint | `SKILL.md` (also accepted: `skill.md`) | Case-insensitive |
| Workflow entrypoint | `workflows/<name>.md` | Lowercase, kebab-case |
| Skill-internal workflow (optional) | `workflow.md` inside the skill dir | Lowercase only |
| Command entrypoint | `aic-<name>.md` in `cli/commands/` | Lowercase, kebab-case |
| Playbook | `<topic>.md` | Lowercase only |
| Knowledge | `<topic>.md` | Lowercase only |
| Template | `<purpose>(-report)?.md` | Lowercase only |
| Checklist | `<theme>.md` | Lowercase only |
| RFC | `RFC-NNNN-<kebab-title>.md` | Uppercase RFC prefix |
| ADR | `NNNN-<kebab-title>.md` | Numeric prefix |
| Python tool | `*.py` | kebab-case or snake_case |
| Script | `*.sh` or `*.cmd` | kebab-case |

## Names

| Component | Rule | Good | Bad |
|---|---|---|---|
| Skill name | Describe what it does | `bugfix`, `java-maven`, `mock-test` | `my-skill`, `utils`, `helper` |
| Workflow name | Describe the process | `develop`, `bugfix`, `release` | `dev-workflow`, `process` |
| Command name | Describe the operation | `scan`, `trace` | `cmd`, `tool`, `do-stuff` |
| Playbook name | Describe the topic | `mockito`, `maven`, `spring-boot-test` | `testing-tips`, `random` |
| RFC title | Describe the specification | `repository-architecture`, `skill-specification` | `new-idea`, `stuff` |

## Frontmatter

The `name:` field in every `skill.md` must exactly match the directory name.

```yaml
# Directory: ai-system/skills/bugfix/
name: bugfix    # Must match

# Directory: ai-system/skills/java-maven/
name: java-maven  # Must match
```

## YAML Keys

| Key | Convention |
|---|---|
| `name:` | kebab-case, matches directory |
| `description:` | Starts with verb, includes trigger phrases, ends with anti-trigger |
| `status:` | One of: `active`, `deprecated`, `draft` |

## Enforcement

Naming conventions are enforced by `tools/repo-lint.py` and must pass at
BLOCKER or ERROR level before any component is accepted.

## Gate Self-Verification (P60)

A gate that silently stops working is worse than no gate: it manufactures false
confidence. The 2026-09-21 external blind review found five such failures at once
(silently uncollected tests, a dead exemption regex, an uncollected `[BLOCKER]`
severity, a fail-open registry check, an unreachable dangerous-command branch) —
none of which produced any signal in the existing gates.

Three rules apply to every gate, guard, regex, whitelist and registry check:

1. **Fail loud.** A gate must never degrade into "pass" when its own rule cannot
   be evaluated (missing key, empty pattern, unreadable target). Missing input is
   an ERROR, not a skip.
2. **Declarative rules need positive *and* negative cases.** Every regex /
   whitelist / keyword exemption carries a self-test asserting what it must match
   **and what it must not** — see `cli/tests/test_gate_self_verification.py`
   (repo-lint keyword exemption, dangerous-command guard, path-audit relative
   reference rule, tests-collected checker).
3. **Declared and effective must be reconciled.** What a file *declares* and what
   the runtime *collects* are two different worlds; they are compared by
   `tools/checks/tests_collected.py` (declared `def test_` vs unittest collection),
   wired into `tools/check.py`.

Boundary: `tools/path-audit.py` audits explicit relative references (a dot-slash
prefixed path, written in placeholders as `./<file>.md`) against the referring
file's directory; *bare* relative forms (for example `references/x.md`, no
dot-slash prefix) are intentionally out of scope (false-positive risk in prose).
Note: because prose examples are audited too, documentation must write such
references with a placeholder segment (`./<file>.md`) rather than a concrete path.
