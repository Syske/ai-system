# Reusable Checklists

---

## Preparation Checklist (Stage 1)

- [ ] Purpose extracted (one sentence)
- [ ] Trigger phrases identified (3-7 patterns)
- [ ] Anti-triggers identified (what NOT to do)
- [ ] Audience identified (who uses this Skill)
- [ ] Exclusions documented (what is explicitly out of scope)
- [ ] Existing Skills checked for overlap
- [ ] Overlap result: pass | refuse | coexist

---

## Design Checklist (Stage 2)

- [ ] File structure chosen (single vs. modular)
- [ ] Workflow pattern chosen (sequential/conditional/loop/parallel/checkpoint)
- [ ] SKILL.md entrypoint planned
- [ ] workflow.md planned (if needed)
- [ ] decision.md planned (if needed)
- [ ] checklists.md planned (if needed)
- [ ] anti-patterns.md planned (if needed)
- [ ] references/ planned (if needed)
- [ ] scripts/ planned (if needed)
- [ ] Governance check completed
- [ ] Split plan documented (if needed)

---

## Generation Checklist (Stage 4)

- [ ] Frontmatter written (`name`, `description`)
- [ ] Description includes trigger phrases AND anti-triggers
- [ ] Description is 100-1024 characters
- [ ] Name is kebab-case, ≤ 64 characters
- [ ] Workflow stages are numbered and have clear outputs
- [ ] Decision rules include stopping conditions
- [ ] No project-specific assumptions
- [ ] No duplicated content across files
- [ ] Each file has one responsibility
- [ ] SKILL.md ≤ 500 lines
- [ ] If references/ used, SKILL.md references them explicitly
- [ ] If scripts/ used, scripts are idempotent

---

## Validation Checklist (Stage 5)

- [ ] Frontmatter valid (name + description)
- [ ] Description has triggers AND anti-triggers
- [ ] Description length 100-1024 chars
- [ ] Name is kebab-case (e.g., `my-skill-name`)
- [ ] Name ≤ 64 chars
- [ ] SKILL.md ≤ 500 lines
- [ ] Total files ≤ 800 lines
- [ ] No hardcoded paths
- [ ] No hardcoded org or service names
- [ ] No duplicated checklists or rules
- [ ] Activation section defines when-to-use AND when-NOT-to-use
- [ ] Workflow stages have defined outputs
- [ ] Stopping conditions exist (graceful failure)
- [ ] Single responsibility (one-sentence test passes)
- [ ] No prompt templates (only workflow, decisions, checklists)
- [ ] Composable with other Skills (no circular deps)

---

## Completion Checklist (Stage 6)

- [ ] All planned files exist
- [ ] All validation checks passed
- [ ] User informed of output path
- [ ] User informed of trigger phrase
- [ ] Any warnings communicated to user
- [ ] No open questions
