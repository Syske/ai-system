# ADR-0002: Playbook as Separate Knowledge Layer

| Field | Value |
|---|---|
| Status | **Accepted** |
| Decided | 2026-07-02 |

## Context

Skills across the repository were embedding the same engineering knowledge
(Maven commands, Mockito patterns, ReflectionTestUtils usage) independently.
This caused:
1. Duplicated content — fixing a pattern required editing 5 files
2. Inconsistent guidance — skills said different things about the same topic
3. Skill bloat — skills contained knowledge they didn't own

## Decision

Extract all reusable engineering knowledge into Playbooks. Each playbook is a standalone reference document that Skills reference by path.

## Consequences

**Positive:**
- Single source of truth for each engineering topic
- Skills become thinner (focused on workflow, not knowledge)
- Playbooks can be updated independently

**Negative:**
- Indirect reference — Skills must load playbooks separately
- Risk of playbooks becoming stale if skills stop referencing them

## Rationale

The "reference by path" pattern keeps the dependency explicit. A Skill that
references `playbooks/maven.md` makes its dependency visible. The linter can
detect orphaned playbooks (playbooks that no Skill references).

> Status note: the `playbooks/` directory is **planned** (RFC-0001/ADR-0002
> target architecture); it does not exist yet. References to `playbooks/*.md`
> in this RFC are forward references, not broken links.

## Related

- `RFC-0001` — Repository Architecture (Playbook definition)
- `RFC-0002` — Skill Specification (prohibition of duplicate content)
- `skills/implement/planning.md` — Playbook content absorbed here
- `tools/repo-lint.py` — orphaned playbook detection
