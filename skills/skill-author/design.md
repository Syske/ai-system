# Skill Design Rules

## Architecture Principles

### Single Responsibility

A Skill must do exactly one thing. If a Skill's `workflow.md` has stages
that belong to different domains, split it.

**Test:** Can you describe the Skill in one sentence without using "and"?

- "Maintains Java unit tests" → single responsibility ✓
- "Maintains tests and deploys artifacts" → split ✗
- "Executes Maven builds" → single responsibility ✓
- "Executes Maven builds and generates documentation" → split ✗

### Modularity

One markdown file per concern:

| Concern | File |
|---|---|
| Entrypoint + triggers | `SKILL.md` |
| Workflow stages | `workflow.md` |
| Decision tables | `decision.md` |
| Design rules | `design.md` |
| Checklists | `checklists.md` |
| Anti-patterns | `anti-patterns.md` |
| Examples | `examples.md` |
| Background knowledge | `references/` |
| Executable scripts | `scripts/` |

### Composability

Skills are composable when:

- Each Skill's description includes trigger phrases that another Skill can
  reference (e.g., `java-maven` includes "build" triggers, `mock-test`
  includes "test failure" triggers)
- No circular dependencies between Skills
- Shared logic lives in shared `references/` files, not duplicated across
  Skills
- A Skill can be activated mid-workflow of another Skill

## File Structure

### Standard directory layout

```
skill-name/
  SKILL.md              # Required: entrypoint
  workflow.md           # Recommended: detailed stages
  decision.md           # Recommended: decision tables
  checklists.md         # Recommended: reusable checklists
  anti-patterns.md      # Recommended: behaviors to avoid
  design.md             # Optional: design rules
  examples.md           # Optional: end-to-end examples
  references/           # Optional: background knowledge
    index.md
    <topic>.md
  scripts/              # Optional: executable scripts
    <action>.sh
```

### When to add files

| You need... | Add... |
|---|---|
| More than 5 stage steps | `workflow.md` |
| More than 5 decision points | `decision.md` |
| More than 3 checklists | `checklists.md` |
| Defined undesirable behavior | `anti-patterns.md` |
| Architecture justification | `design.md` |
| 5+ complete examples | `examples.md` |
| Background >5 lines | `references/` |
| Runnable commands | `scripts/` |

### When to keep it simple

| You only need... | Structure |
|---|---|
| A single workflow, <200 lines | `SKILL.md` only |
| Simple, one-stage process | `SKILL.md` only |
| A checklist for a known process | `SKILL.md` + `checklists.md` |

## Workflow Design

### Stage structure

Every stage must have:

```
### Stage N: [Name]

**Goal:** <one sentence>

**Steps:**
N.1 <action>
N.2 <action>
...

**Output:** <what this stage produces>
```

### Condition branches within a stage

```
**Branch logic:**
- Scenario A (condition X) → execute path A
- Scenario B (condition Y) → execute path B
- Fallback: <default behavior>
```

### Workflow rules

1. Every stage produces an output consumed by the next stage
2. Stages are ordered so earlier stages narrow down the problem space
3. Conditional paths are explicit — not hidden in prose
4. Don't describe what — describe how (commands, checks, decisions)

## Frontmatter Rules

### Description writing

A good `description:` follows this template:

```
> [Action the Skill performs].
> [Specific techniques or tools it handles].
> [Trigger patterns — when the AI should load this Skill].
> [Anti-trigger — what the Skill does NOT do].
```

**Example (mock-test):**
```
> Automatically maintains Java unit tests after production code changes.
> Handles JUnit 4/5, Mockito, Spring Boot Test, ReflectionTestUtils.
> Trigger when: production Java changes, test compilation fails, test
> execution fails, user asks to "update tests".
> Does NOT generate new tests — only maintains existing ones.
```

### Trigger pattern rules

- List 3-7 realistic trigger phrases
- Include both developer language ("fix tests") and agent language
  ("compilation failure in test")
- Slightly over-trigger rather than under-trigger
- Include anti-trigger patterns to prevent false activation

### Invocation design

Choose model-invoked vs user-invoked based on the load trade-off
(see RFC-0002, Frontmatter → Invocation Design):

| Choice | When | Cost |
|---|---|---|
| Model-invoked (keep description) | Agent must reach the Skill on its own, or another Skill references it | Context load each turn |
| User-invoked (`disable-model-invocation: true`) | Only fires by hand; description becomes a human one-liner | Cognitive load on the user |

- **One trigger per branch.** Synonyms renaming a single branch are duplication — collapse them.
- When user-invoked Skills multiply, add a **router** Skill that names the others and when to reach for each.

## Validation Rules

### Always validate

1. **Frontmatter check** — `name` and `description` present and valid
2. **Description check** — 100-1024 chars, includes triggers and anti-triggers
3. **Name check** — kebab-case, ≤ 64 chars
4. **Size check** — SKILL.md ≤ 500 lines, total ≤ 800 lines
5. **No project assumptions** — no hardcoded paths or org names
6. **No duplication** — no repeated content across files
7. **Responsibility check** — single responsibility test passes
8. **Activation check** — both when-to-use and when-NOT-to-use defined
9. **Stopping check** — graceful failure paths defined
10. **Composability check** — no circular dependencies with other Skills
