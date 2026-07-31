# Analysis

This document defines duplication detection and dead reference analysis
rules. Use during Stages 4-5 of the workflow.

---

## Duplication Detection

### Checklist Duplication

For each `checklists.md` file in a Skill, compare each heading with
shared checklists in `.opencode/checklists/`:

| Shared checklist | Skill checklist | Overlap | Action |
|---|---|---|---|
| `validation.md` | `## Validation Checklist` | > 80% items identical | Replace with reference |
| `completion.md` | `## Completion Checklist` | > 80% items identical | Replace with reference |
| Any shared | Any skill-specific | > 50% items | Extract, keep skill-specific items |

**Detection method:**
1. Extract all checklist item texts from both files
2. Compute Jaccard similarity: `intersection / union`
3. If similarity > 0.5, flag as duplication candidate

### Knowledge Duplication

For each file in a Skill, compare against Playbook topics:

| Playbook | Skill file | Detection |
|---|---|---|
| `maven.md` | Any file with `mvn` commands | Direct match (grep) |
| `mockito.md` | Any file with Mockito patterns | Direct match (grep) |
| `reflection-test-utils.md` | Any file with `ReflectionTestUtils` | Direct match (grep) |
| `spring-boot-test.md` | Any file with `@SpringBootTest` | Direct match (grep) |

---

## Dead Reference Detection

### Reference Patterns

A reference from one component to another follows these patterns:

| Source | Reference pattern | Target |
|---|---|---|
| Skill skill.md | `delegates to: <name>` | Skill directory |
| Skill workflow.md | `invoke <name>` | Skill directory |
| Workflow workflow.md | `` `<name>` `` | Skill directory |
| Skill any file | `playbooks/<name>.md` | Playbook file (in `ai/playbooks/`) |
| Skill any file | `templates/<name>.md` | Template file (in `ai/templates/`) |
| Skill any file | `checklists/<name>.md` | Checklist file (in `ai/checklists/`) |
| Skill any file | `knowledge/<name>.md` | Knowledge file (in `ai/knowledge/`) |

### Orphan Detection Algorithm

```
For each playbook in D:\workspace\ai-workspace\ai-system\playbooks:
  grep all skill files for "playbooks/<playbook_name>"
  if count == 0 → flag as ORPHAN

For each checklist in D:\workspace\ai-workspace\ai-system\checklists:
  grep all skill checklists.md for headings matching checklist name
  if count == 0 → flag as UNREFERENCED

For each template in .opencode/templates/:
  grep all skill files for "templates/<template_name>"
  if count == 0 → flag as UNREFERENCED

For each workflow in .opencode/workflows/:
  grep workflow.md for "`<skill_name>`" patterns
  for each match, verify skill directory exists
  if not → flag as BROKEN_REFERENCE
```

---

## Severity Classification

| Finding | Severity | Auto-recommendation |
|---|---|---|
| Checklist duplication > 80% | HIGH | Extract to shared checklist |
| Checklist duplication 50-80% | MEDIUM | Consider partial extraction |
| Knowledge duplication > 10 lines | HIGH | Extract to playbook |
| Knowledge duplication 5-10 lines | MEDIUM | Consider extraction |
| Orphaned playbook | MEDIUM | Archive or add references |
| Orphaned checklist | LOW | Archive or add references |
| Broken workflow reference | HIGH | Fix workflow |
| Unused Skill | LOW | Consider deprecation |
| Linter BLOCKER | P0 | Fix immediately |
| Linter ERROR | P1 | Fix this cycle |
| Linter WARNING | P2 | Fix when possible |
