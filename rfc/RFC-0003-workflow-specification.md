# RFC-0003: Workflow Specification

| Field | Value |
|---|---|
| Status | **Approved** |
| Type | Specification |
| Author | Repository Governance |
| Created | 2026-07-02 |
| Supersedes | None |

---

## Abstract

This RFC defines the specification for Workflows — the orchestration layer
of this repository. Workflows coordinate multiple Skills to complete
higher-level processes. They must not implement capabilities themselves.

---

## 1. Definition

A **Workflow** is a directed sequence of Skill invocations that completes a
repository-level process. It is the "how" that connects multiple Skills.

**A Workflow orchestrates. It does not implement.**

---

## 2. Mandatory Components

### 2.1 Purpose

A one-sentence statement of the process this workflow orchestrates.

```
Good: "Orchestrates feature development from task card to merged code."
Bad:  "Runs implement, then mock-test, then java-maven, then review."
```

### 2.2 Trigger

When this workflow should be invoked.

Examples:
- "User wants to implement a new feature"
- "User reports a bug that needs fixing"
- "Code review approval is needed"

### 2.3 Skills Orchestrated

Every Skill that this workflow invokes, listed with:
- Skill name (matches directory in `ai-system/skills/`)
- Trigger condition (when the Skill is invoked)
- Handoff condition (what must be true before the next Skill)

### 2.4 Execution Order

The sequence in which Skills are invoked. Must be represented as a directed
graph or numbered list.

### 2.5 Stopping Conditions

When this workflow terminates. Must include:
- Normal completion (all Skills succeeded)
- Failure at each Skill (what happens if a Skill fails)

---

## 3. File Structure

```
ai-system/workflows/<name>/
  workflow.md          # Required: the workflow specification
                       # Max: 100 lines
```

Workflows must have exactly one file. If a workflow exceeds 100 lines,
it is orchestrating too many Skills and should be split.

---

## 4. Workflow Specification Format

```markdown
# Workflow: <name>

## Purpose
<one sentence>

## Trigger
<when this workflow runs>

## Skills Orchestrated

| # | Skill | Trigger | Handoff |
|---|---|---|---|
| 1 | `implement` | Task card ready | Plan approved by user |
| 2 | `mock-test` | Production signatures changed | Fixtures synchronized |
| 3 | `java-maven` | Code ready for validation | Build succeeds |
| 4 | `review` | Validation passed | Review approved |

## Execution Order

```
implement → mock-test? → java-maven → review → finish
                                                          
? = conditional: only if production signatures changed
```

## Stopping Conditions

| Condition | Action |
|---|---|
| All Skills pass | Report completion |
| implement fails | Stop, report planning issue |
| java-maven fails | Return to implement for fix |
| review rejects | Return to implement for revision |
| User cancels | Stop |
```

---

## 5. Workflow Rules

### 5.1 Orchestration-Only

A Workflow must not contain:

| Prohibited content | Example | Why |
|---|---|---|
| Maven commands | `mvn -pl service -am test` | Belongs in java-maven |
| Test fixture logic | `ReflectionTestUtils.setField(...)` | Belongs in mock-test |
| Bug diagnosis | "Check the stack trace for NPE" | Belongs in bugfix |
| Implementation logic | "Add null check in process()" | Belongs in implement |
| Engineering knowledge | "Mockito supports lenient stubbing" | Belongs in playbooks |
| Report templates | "## Implementation Report" | Belongs in templates |
| Checklist items | "- [ ] Test passes" | Belongs in checklists |

### 5.2 Skill Reference Only

A Workflow must reference Skills only by their directory name (which matches
their `name:` frontmatter field). It must not re-implement any part of a
Skill's workflow.

```
Correct: "Invoke `implement` with the task card."
Incorrect: "Read the task card. Check acceptance criteria. Plan changes."
```

### 5.3 Conditional Execution

A Workflow may include conditional branches:

```
implement → mock-test?
  │           │
  │           ├─ (signatures changed) → mock-test → java-maven → review
  │           └─ (no change)          → java-maven → review
  │
  └─ (plan rejected) → stop
```

Each condition must reference a Skill's output, not implement logic.

### 5.4 Stopping Conditions

A Workflow must define what happens when each Skill fails:

| If Skill | Fails because | Action |
|---|---|---|
| implement | Plan rejected | Stop, report |
| implement | Conflict detected | Stop, report conflict |
| mock-test | Fixture cannot be updated | Fix manually, retry |
| java-maven | Compilation error | Return to implement |
| java-maven | Test failure | Return to implement |
| review | Changes requested | Return to implement |

---

## 6. Quality Gates

Every Workflow must pass these gates:

| Gate | Check |
|---|---|
| References only existing Skills | All Skill names match directories in `ai-system/skills/` |
| No implementation logic | No Maven commands, no test code, no fix patterns |
| No engineering knowledge | No playbook-level content |
| No templates | No report structures |
| No checklists | No verification item lists |
| Skills orchestrated ≤ 6 | If more, split the workflow |
| File length ≤ 100 lines | Workflow should be concise |
| Stopping conditions defined | For normal completion AND each failure path |

---

## 7. Prohibited Workflow Patterns

| Pattern | Why |
|---|---|
| "Mega-workflow" orchestrating 10+ Skills | Should be split into sub-workflows |
| Workflow containing embedded documentation | Documentation belongs in playbooks or knowledge |
| Workflow containing conditional logic that duplicates Skill logic | The Skill already handles that decision |
| Workflow hardcoding project-specific paths | Workflows must be reusable |
| Workflow referencing Skills that don't exist | Broken orchestration |
