# Naming Conventions

This document defines naming conventions for all components in the repository.

---

## Directories

| Component | Pattern | Examples |
|---|---|---|
| Skill | `kebab-case`, one or two words | `bugfix`, `java-maven`, `mock-test` |
| Workflow | `kebab-case`, one word preferred | `develop`, `bugfix`, `release` |
| Playbook | `kebab-case` | `spring-boot-test`, `reflection-test-utils` |
| Knowledge | `kebab-case` | `domain-terms`, `coding-conventions` |
| Template | `kebab-case` | `implementation-report`, `bug-report` |
| Checklist | `kebab-case` | `validation`, `completion`, `retry` |
| RFC | `kebab-case` after `RFC-NNNN-` | `RFC-0001-repository-architecture` |
| ADR | `kebab-case` after `NNNN-` | `0001-openspec-integration` |

## Files

| Component | Entrypoint | Pattern |
|---|---|---|
| Skill entrypoint | `skill.md` | Lowercase only |
| Workflow entrypoint | `workflow.md` | Lowercase only |
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
