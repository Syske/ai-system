# RFC-0002: Skill Specification

| Field | Value |
|---|---|
| Status | **Approved** |
| Type | Specification |
| Author | Repository Governance |
| Created | 2026-07-02 |
| Supersedes | None |

---

## Abstract

This RFC defines the exact specification that every Skill in this repository
must satisfy. It covers mandatory components, file structure, frontmatter
requirements, workflow rules, prohibitions, and quality gates.

---

## 1. Mandatory Components

Every Skill must include the following components. A Skill is not considered
complete if any component is missing.

### 1.1 Purpose

A one-sentence statement of the Skill's single responsibility.

**Test:** Can you describe the Skill without using "and"?

```
Good: "Automatically maintains Java unit tests after production code changes."
Bad:  "Automatically maintains Java unit tests and executes Maven builds."
```

### 1.2 Trigger

A list of conditions that cause the AI agent to activate this Skill.

Must include:
- At least 3 trigger phrases (what the user might say)
- At least 1 anti-trigger phrase (when NOT to activate)

### 1.3 Input

A description of what information the Skill expects before it can begin.

Examples: task card, git diff, exception stack trace, contract file.

### 1.4 Output

A description of what the Skill produces.

Examples: implementation plan, repaired code, test fixtures, completion report.

### 1.5 Workflow

A numbered sequence of stages. Each stage must have:
- A goal (one sentence)
- Steps (numbered, actionable)
- An output (what this stage produces)

### 1.6 Decision Rules

Rules that guide the AI's choices during execution. Must include:
- At least one stopping condition
- At least one delegation rule (when to invoke another Skill)
- At least one scope-narrowing rule

### 1.7 Stop

An explicit condition that ends the Skill's execution. Must include:
- Normal completion (success)
- Failure modes (insufficient evidence, user cancel, unrecoverable error)

### 1.8 Delegation

A list of other Skills this Skill may invoke, and under what circumstances.

---

## 2. File Structure

### 2.1 Required Files

```
<skill-name>/
  skill.md              # Entrypoint — contains Purpose, Trigger, Input,
                        #   Output, Workflow summary, Decision summary,
                        #   Delegation summary, Reference file map.
                        #   Max: 80 lines.
```

### 2.2 Optional Files

```
  workflow.md           # Detailed stage-by-stage workflow.
                        #   Required when skill.md's workflow summary
                        #   exceeds 15 lines.
                        #   Max: 250 lines.

  decision.md           # Extended decision tables.
                        #   Required when skill.md's decision summary
                        #   exceeds 10 decision points.
                        #   Max: 80 lines.

  analysis.md           # Extended analysis workflows (evidence collection,
                        #   hypothesis generation, root cause analysis).
                        #   Max: 200 lines.

  repair.md             # Extended repair strategies and fix patterns.
                        #   Max: 150 lines.

  validation.md         # Extended validation and regression checking.
                        #   Max: 150 lines.

  planning.md           # Extended planning and understanding phase.
                        #   Max: 150 lines.

  checklists.md         # Skill-specific checklist items (not shared ones).
                        #   Shared checklists live in each Skill's checklists.md.
                        #   Max: 100 lines.

  examples.md           # Complete end-to-end workflow examples.
                        #   Max: 250 lines.

  anti-patterns.md      # Behaviors to avoid.
                        #   Max: 100 lines.

  scripts/              # Executable scripts (Python, shell, etc.)
                        #   Each script must be idempotent.
```

### 2.3 Prohibited Files

| File | Reason |
|---|---|
| `README.md` inside a Skill | Not needed — skill.md serves as documentation |
| `SKILL.md` (uppercase) | Must be lowercase `skill.md` |
| `index.md` | Not needed — single entrypoint is sufficient |

---

## 3. Frontmatter Specification

Every `skill.md` must begin with a valid YAML frontmatter:

```yaml
---
name: <kebab-case-name>
# Must match the directory name exactly.

description: >
  <concise description of the Skill's purpose, trigger conditions,
  and anti-trigger conditions. Must be 100-1024 characters.
  Must include trigger phrases that the AI agent will match against
  user input. Include "Does NOT" for anti-triggers.>
---
```

### Frontmatter Rules

| Rule | Enforcement |
|---|---|
| `name:` must match directory name | Linter checks directory == name |
| `description:` must be 100-1024 characters | Linter checks length |
| `description:` must contain at least 3 trigger phrases | Linter checks for common patterns |
| `description:` must contain "Does NOT" or "not responsible for" | Linter checks for anti-trigger |
| No additional keys unless documented in an RFC | Linter rejects unknown keys |

### Invocation Design

Choose how a Skill is invoked based on context-load vs cognitive-load trade-off:

| Invocation | Mechanics | Cost | When |
|---|---|---|---|
| **Model-invoked** | Keep a model-facing `description` (rich triggers); the agent fires it autonomously | Context load: description sits in the window every turn | The agent must reach it on its own, or another Skill must reference it |
| **User-invoked** | Set `disable-model-invocation: true`; description becomes a human-facing one-liner, triggers stripped | Cognitive load: the user must remember it exists | It only ever fires by hand; keep context lean |

Rules:

- Pick **model-invocation** only when the agent must reach the Skill on its own or another Skill must. Otherwise make it user-invoked and pay no context load.
- **Description does two jobs**: state what the Skill is, and list the branches that trigger it. Every word adds context load, so prune harder than the body.
- **One trigger per branch.** Synonyms that rename a single branch are duplication — collapse them; keep only genuinely distinct branches.
- When user-invoked Skills multiply past what a user can remember, add a **router** Skill that names the others and when to reach for each.

---

## 4. Workflow Stage Specification

Every workflow stage must follow this exact structure:

```markdown
### Stage N: [Stage Name]

**Goal:** <one sentence describing what this stage produces>

**Steps:**

N.1 <actionable command or decision>
N.2 <actionable command or decision>

**Output:** <what this stage produces for the next stage>
```

### Stage Rules

| Rule | Enforcement |
|---|---|
| Stages must be numbered sequentially | Linter checks for gaps |
| Each stage must have a Goal | Linter checks for "**Goal:**" |
| Each stage must have Steps | Linter checks for numbered steps |
| Each stage must have an Output | Linter checks for "**Output:**" |
| Stages must not contain unchecked commands | Linter warns on bare command blocks |
| Stages must explain before executing | Linter warns on execute-first patterns |

---

## 5. Prohibitions

### 5.1 Content Prohibitions

| Prohibition | Reason | Linter check |
|---|---|---|
| Must not have any single file exceeding 1000 lines | Maintainability | Check per-file line count |
| Must not duplicate content from a shared checklist | Duplication | Compare checklist headings |
| Must not duplicate content from `ai-system/governance/standards/` | Duplication | Compare governance headings |
| Must not embed report templates | Belongs in `ai-system/templates/` | Check for template patterns |
| Must not hardcode Maven commands | Must delegate to java-maven | Grep for `mvn ` patterns |
| Must not hardcode project paths | Must be reusable | Grep for absolute paths |
| Must not hardcode project/organization names | Must be reusable | Grep for org names |

### 5.2 Dependency Prohibitions

| Prohibition | Reason | Linter check |
|---|---|---|
| Must not create circular dependencies | Acyclic graph | Build dependency graph, check for cycles |
| Foundation Layer skills must not depend on Orchestration Layer | Layer rule | Check which skills reference which |
| Must not depend on a Skill that does not exist | Broken reference | Check all `delegates to` references |

---

## 6. Quality Gates

Every Skill must pass these gates before being accepted:

| Gate | Check |
|---|---|
| Frontmatter valid | `name:` exists, `description:` 100-1024 chars |
| Single responsibility | One-sentence test passes |
| No prohibited content | No Maven commands, no project paths |
| No duplication | No shared checklist/playbook duplication |
| Dependency acyclic | Dependency graph has no cycles |
| No single file exceeds 1000 lines (aggregated reference files are exempt) | Per-file line count (see §5.1) |
| Workflow has stages | At least 3 stages with Goal/Steps/Output |
| Stopping conditions defined | At least one normal stop + one failure stop |
| Delegation documented | At least "delegates to: none" if standalone |

---

## 7. Skill Lifecycle

| Stage | Description | Gate |
|---|---|---|
| **Draft** | Skill is being designed | RFC-0002 compliance plan |
| **Proposed** | Skill has an approved RFC | Passes all quality gates |
| **Active** | Skill is available for use | Linter passes, metrics recorded |
| **Deprecated** | Skill is replaced or superseded | ADR documents deprecation reason |
| **Archived** | Skill is removed from active use | Moved to `archive/` directory |
