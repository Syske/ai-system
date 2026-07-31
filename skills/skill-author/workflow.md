# Workflow

## Stage 1: Understand Requirements

**Goal:** Extract the four dimensions of the Skill to be created.

### Dimensions

| Dimension | Question | Output |
|---|---|---|
| Purpose | What task does this Skill automate? | One-sentence purpose |
| Trigger | When should the AI activate this Skill? | Trigger pattern list |
| Audience | Who writes / invokes this Skill? | Developer type |
| Scope | What is explicitly NOT in scope? | Exclusion list |

### Information gathering rules

- If user provided 3+ of 4 dimensions → proceed, infer the rest
- If fewer than 2 dimensions → ask: "Can you describe the task this Skill should automate?"
- If the task sounds like an existing Skill → run Stage 0 governance check first

### Output

```
purpose:     <one sentence>
triggers:    [<list of trigger phrases>]
exclusions:  [<list of out-of-scope activities>]
```

---

## Stage 2: Design Architecture

**Goal:** Determine the optimal file structure and workflow pattern.

### Step 2.1 — Choose file structure

| Scenario | Structure |
|---|---|
| Simple workflow, <3 sub-tasks | `SKILL.md` only (single file) |
| Complex workflow, checklists, examples | `SKILL.md` + `workflow.md` + `checklists.md` |
| Many decision rules | Add `decision.md` |
| Many architecture rules | Add `design.md` |
| Many anti-patterns | Add `anti-patterns.md` |
| 10+ examples | Extract to `examples.md` |
| Background knowledge > 5 lines | Extract to `references/` |
| Executable script needed | Add `scripts/` directory |

### Step 2.2 — Choose workflow pattern

| Scenario | Pattern |
|---|---|
| Steps have strict dependencies | Sequential (numbered stages) |
| Different inputs take different paths | Conditional branches |
| Execute → verify → fix → re-execute | Validation loop |
| Multiple independent sub-tasks | Parallel execution |
| Multi-stage across sessions | Checkpoint-based |

### Step 2.3 — Check library governance

- Search for overlapping Skills in the same directory
- If overlap found: refuse, point to existing Skill
- If Skill exceeds ~500 lines across all files: plan split into sub-Skills

### Output

```
files:        [SKILL.md, workflow.md, ...]
pattern:      sequential | conditional | loop | parallel | checkpoint
governance:   pass | refuse (reason) | split (plan)
```

---

## Stage 3: Plan and Confirm

**Goal:** Present a concise outline to the user for confirmation.

### Template

```
Skill: <name>
Purpose: <one sentence>

Files:
  SKILL.md              — <summary>
  workflow.md           — <summary>
  ...

Workflow:
  Stage 1: <name> — <one line>
  Stage 2: <name> — <one line>
  ...

Governance: <existing Skills checked / pass>
```

### Rules

- Keep the outline under 15 lines
- Do not describe the content of each file in detail at this stage
- If the user says "ok", "confirm", "yes", "proceed", or "--auto" → Stage 4
- If the user requests changes → update, re-present
- If the user rejects → stop

---

## Stage 4: Generate Files

**Goal:** Create every file in the planned structure.

### File generation rules

1. **SKILL.md first** — always start with the entrypoint
2. **YAML frontmatter required** — `name`, `description`
3. **Description wins activation** — include realistic trigger phrases, slightly
   over-trigger rather than under-trigger
4. **No background knowledge** — if a concept needs >5 lines to explain, extract
   to `references/`
5. **No duplication** — if a checklist appears in multiple stages, define it once
   in `checklists.md` and reference it
6. **No project-specific assumptions** — use generic terminology (e.g., "the
   service" not "UserService")
7. **Each file has one responsibility** — SKILL.md: entrypoint; workflow.md:
   stage instructions; decision.md: decision tables; etc.
8. **Workflow is observable** — every stage has a defined output that can be
   checked

### Content requirements per file

**SKILL.md (all required):**
- Frontmatter
- Overview (3-5 lines)
- Activation (trigger + anti-trigger)
- Workflow summary (stage list)
- Quick decision table (5-10 rows)
- Reference file map

**workflow.md (if exists):**
- One section per stage
- Each stage: goal, steps, output
- Clear conditional paths within stages

**decision.md (if exists):**
- Decision tables (5-10 rows each)
- Stopping conditions
- Scope narrowing rules
- Skill chaining rules

**checklists.md (if exists):**
- One section per checklist
- Checklist items as bullet points or checkboxes
- Mechanical, not interpretive

**anti-patterns.md (if exists):**
- One section per anti-pattern
- Pattern → why it fails → what to do instead

### Generation order

```
1. SKILL.md
2. workflow.md (if planned)
3. decision.md (if planned)
4. design.md (if planned)
5. checklists.md (if planned)
6. anti-patterns.md (if planned)
7. examples.md (if planned)
8. references/ files (if planned)
9. scripts/ files (if planned)
```

---

## Stage 5: Validate

**Goal:** Verify the generated Skill meets all quality standards.

### Validation checks

| Check | Pass condition |
|---|---|
| Frontmatter | `name:` and `description:` present |
| Description | 100-1024 chars, includes trigger phrases |
| Name format | kebab-case, ≤ 64 chars |
| SKILL.md lines | ≤ 500 lines |
| Total lines (all files) | ≤ 800 unless split justified |
| No project assumptions | No hardcoded paths, service names, org names |
| No duplication | Across all files, no repeated checklists or rules |
| Activation defined | When to use AND when NOT to use |
| Workflow defined | Stages are numbered, have outputs |
| Decision rules exist | At least stopping conditions and scope narrowing |
| Stops gracefully | Defined what happens when conditions aren't met |
| Single responsibility | The Skill does one thing |
| No prompt templates | The Skill defines workflow, not prompts |
| Composability | Can be used alongside other Skills without conflict |

### Fix rules

- Any ❌ → fix, re-validate, repeat
- Only ⚠️ → report, ask user if they want to fix

---

## Stage 6: Complete

**Goal:** Finalize and report.

### Completion checklist

- [ ] All planned files exist
- [ ] Validation passed (no ❌)
- [ ] User has been shown the output path
- [ ] User has been told how to activate the Skill
- [ ] Any ⚠️ warnings communicated

### Reporting template

```
Generated: <path>
Files:     <file list>
Purpose:   <purpose>
Governance: <overlap checks / pass>

The Skill is ready. The AI will activate it when the user
says "<trigger phrase>".
```
