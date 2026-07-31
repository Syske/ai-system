---
name: skill-author
description: >
  Meta-Skill for designing and generating production-grade AI Skills optimized
  for autonomous coding agents (Claude Code, Codex CLI, OpenCode, Gemini CLI,
  Cursor Agent). Enforces single-responsibility, workflow-first, modular
  architecture with deterministic decision rules. Governs Skill library
  consistency — detects overlap, enforces conventions, recommends splitting
  oversized Skills.
  Trigger when: user asks to "create a skill", "generate a skill", "make a
  skill", "author a skill", "write a skill", "build a skill", "design a
  workflow skill", or mentions a recurring task pattern that should be a Skill.
  Does NOT generate prompt templates — only generates structured reusable Skills.
---

# skill-author

## Overview

This Skill designs and generates other AI Skills. It enforces a **workflow-first,
decision-driven, modular** architecture — every Skill has exactly one
responsibility, a deterministic workflow, and explicit stopping conditions.

It also functions as a **library governance layer**: before creating a new Skill,
it checks for overlaps with existing Skills, enforces consistent conventions,
and recommends splitting oversized Skills.

**Output:** A directory of markdown files (not a single monolithic document),
ready for direct use as a Skill.

---

## Activation

### Activate when

- User says "create a skill", "generate a skill", "make a skill", or similar
- User describes a recurring task pattern suitable for Skill automation
- User asks to "design a workflow" for a repeatable process
- A conversation reveals a template-able multi-step procedure

### DO NOT activate when

- User asks for a prompt template (this is not a prompt generator)
- User asks for a one-shot script or ad-hoc automation (not a reusable Skill)
- User asks for documentation only (no workflow, no decision logic)
- An existing Skill already covers the responsibility

---

## Workflow (6 Stages)

```
Stage 1 — Understand Requirements
Stage 2 — Design Architecture
Stage 3 — Plan and Confirm
Stage 4 — Generate Files
Stage 5 — Validate
Stage 6 — Complete
```

Each stage is documented in `workflow.md`. Load that file after reading this
entrypoint.

---

## Quick Decision Table

| Question | Rule |
|---|---|
| How many files? | As many as needed for single responsibility per file |
| What workflow pattern? | Sequential for dependencies; parallel for independence |
| When to stop? | When purpose is fully documented with no gaps |
| What structure? | SKILL.md + opt-in references/ and/or scripts/ |
| Overlap detected? | Refuse; point to existing Skill |
| Skill too large? | Split into sub-Skills with clear dependency graph |

---

## Reference Files

| File | Content | Load when |
|---|---|---|
| `workflow.md` | 6-stage detailed workflow with stage-by-stage instructions | Immediately after SKILL.md |
| `decision.md` | Activation, stopping, narrowing, chaining decision tables | Any decision point |
| `design.md` | Architecture principles, file structure rules, template selection | Stage 2 (Design) |
| `checklists.md` | Reusable checklists for each stage | Stage 4-5 (Generate, Validate) |
| `anti-patterns.md` | Behaviors to avoid; diagnosis of common mistakes | Validation or review |
