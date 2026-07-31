# RFC-0004: Playbook Specification

| Field | Value |
|---|---|
| Status | **Approved** |
| Type | Specification |
| Author | Repository Governance |
| Created | 2026-07-02 |
| Supersedes | None |

---

## Abstract

This RFC defines the specification for Playbooks — the reusable engineering
knowledge layer of this repository. Playbooks capture best practices,
diagnostic patterns, and decision guidance for specific technical topics.

---

## 1. Definition

A **Playbook** is a standalone reference document that captures reusable
engineering knowledge about a specific technical topic. It is not executable.
It is referenced by Skills when they need topic-specific guidance.

**A Playbook educates. It does not execute.**

---

## 2. Mandatory Components

### 2.1 Topic

A one-line description of the technical topic this Playbook covers.

```
Good: "Mockito argument matchers, stubbing patterns, and verification strategies."
Bad:  "How to write good tests."
```

### 2.2 Audience

Who should reference this Playbook.

Examples:
- "Skills that maintain Mockito test fixtures"
- "Skills that execute Maven builds"
- "Skills that diagnose test failures"

### 2.3 Content Sections

At minimum:
- **Best Practices** — recommended approaches
- **Common Pitfalls** — mistakes to avoid
- **Decision Guidance** — how to choose between options

### 2.4 References

If the Playbook references external sources (documentation, libraries,
specifications), list them explicitly.

---

## 3. Prohibited Content

| Prohibited | Reason |
|---|---|
| Execution instructions | "Run `mvn clean install`" → belongs in Skills |
| Project-specific paths | `/workspace/my-project/` → belongs in `knowledge/` |
| Workflow stages | "Stage 1: Analyze" → belongs in Skills |
| Checklist items | "Test passes" → belongs in `checklists/` |
| Report templates | "## Summary" → belongs in `templates/` |
| Skill-specific triggers | "When user says 'fix test'" → belongs in Skills |

---

## 4. File Structure

```
playbooks/<topic>.md
```

Single file per topic. If a topic exceeds 300 lines, split it into
sub-topics (e.g., `mockito-basics.md`, `mockito-advanced.md`).

---

## 5. Playbook Specification Format

```markdown
# <Topic>

## Overview
<one paragraph describing the topic and when to reference this playbook>

## Best Practices
- <recommended approach 1>
- <recommended approach 2>

## Common Pitfalls
- <mistake 1> — <why it fails> — <what to do instead>
- <mistake 2> — <why it fails> — <what to do instead>

## Decision Guidance

| Situation | Recommended | Not recommended |
|---|---|---|
| <condition A> | <approach> | <approach> |
| <condition B> | <approach> | <approach> |

## References
- <external reference>
```

---

## 6. Playbook Lifecycle

| Stage | Description |
|---|---|
| **Draft** | Playbook is being written; not yet referenced |
| **Active** | Playbook is referenced by at least one Skill |
| **Orphaned** | Playbook is no longer referenced by any Skill — may be archived |
| **Archived** | Playbook moved to archive; no longer maintained |

Playbooks become orphaned when all Skills that referenced them are updated.
An orphaned Playbook that remains unreferenced for 3 months is archived.

---

## 7. Quality Gates

| Gate | Check |
|---|---|
| Single topic | Covers exactly one technical area |
| No execution instructions | No commands, no workflow stages |
| No project-specific content | No paths, no org names, no project names |
| Referenced by at least one Skill | If Active stage |
| Max 300 lines | If exceeded, split into sub-topics |
