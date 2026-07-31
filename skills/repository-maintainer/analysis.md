# Analysis

This document defines dependency analysis and capability analysis rules.
Use during Stages 5 and 8 of the workflow.

---

## Dependency Analysis

### Cycle Detection

A dependency cycle exists when Skill A depends on B, B depends on C, and
C depends on A. This creates an unresolvable loop.

**Detection:**
```python
# tools/dependency-graph.py detects cycles via DFS
cycles = dependency_graph.detect_cycles(skills, edges)
```

**Resolution recommendations:**

| Cycle type | Resolution |
|---|---|
| Direct (A↔B) | Extract shared logic to a Foundation Skill |
| Indirect (A→B→C→A) | Redesign one dependency; promote shared capability |
| Self (A→A) | Remove self-reference |

### Deep Chain Detection

A dependency chain is "deep" when a Skill transitively depends on > 3 Skills.

**Resolution recommendations:**

| Depth | Recommendation |
|---|---|
| 4-5 hops | Consider introducing intermediate abstraction |
| 6+ hops | Restructure; Foundation Skills should not need deep chains |

### Isolation Detection

An asset is "isolated" when nothing references it.

| Asset type | Impact of isolation |
|---|---|
| Skill | No Workflow or other Skill invokes it. May be unused. |
| Workflow | No user references it. May be unused. |
| Playbook | No Skill references it. Orphaned knowledge. |
| Template | No Skill references it. Unused format. |
| Checklist | No Skill references it. Unused verification. |

---

## Capability Analysis

### Capability Matrix Generation

For each Skill, extract capabilities from:
- `skill.md` description
- `workflow.md` stages
- Delegation references

Then cross-reference across all Skills:

```
Capability: Maven execution
  Primary owner: java-maven
  Also present in: bugfix (3 files), implement (2 files), mock-test (2 files)
  Assessment: DUPLICATED — should be extracted to playbooks/maven.md

Capability: Mockito fixture maintenance
  Primary owner: mock-test
  Also present in: bugfix (analysis.md)
  Assessment: PARTIALLY DUPLICATED — bugfix should reference mock-test

Capability: Stack trace triage
  Primary owner: bugfix
  Also present in: (none)
  Assessment: PROPERLY OWNED
```

### Capability Redistribution Rules

| Finding | Action |
|---|---|
| Capability owned by 1 Skill | Keep |
| Capability owned by 2+ Skills, one is primary | Extract knowledge to Playbook, keep primary owner |
| Capability owned by 2+ Skills, no primary | Designate primary owner, redistribute |
| Capability in wrong Layer | Move to correct Layer |
| Capability with no owner | Create new Skill or assign to existing |

### Unused Capability Detection

A capability is "unused" when:
- The Skill that owns it is orphaned (no Workflow invokes it)
- The capability is in a deprecated Skill
- No test or user scenario exercises it

**Recommendation:** Deprecate or archive the owning Skill.
