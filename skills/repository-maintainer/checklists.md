# Checklists

---

## Pre-Execution Quality Gates

Before recommending any change, verify:

- [ ] No duplicated responsibility across Skills
- [ ] No unnecessary Skill that could be merged or archived
- [ ] No orphaned assets (Playbook, Template, Checklist with zero references)
- [ ] No circular dependencies in the dependency graph
- [ ] No duplicated engineering knowledge (content that belongs in a Playbook)
- [ ] No duplicated checklist items (checklists that duplicate `.opencode/checklists/`)
- [ ] No duplicated templates (templates that duplicate `.opencode/templates/`)
- [ ] No naming convention violations
- [ ] No backward compatibility violations
- [ ] Each recommendation has: action, asset, reason, effort, risk, impact

---

## Repository Structure Checklist

- [ ] All Skills in `.opencode/skills/`
- [ ] All Workflows in `.opencode/workflows/`
- [ ] All Playbooks in `.opencode/playbooks/`
- [ ] All Knowledge in `.opencode/knowledge/`
- [ ] All Templates in `.opencode/templates/`
- [ ] All Checklists in `.opencode/checklists/`
- [ ] All RFCs in `.ai/rfc/`
- [ ] All governance docs in `.ai/governance/`
- [ ] All tools in `tools/`

---

## Skill Review Checklist

- [ ] Purpose is clear (one sentence)
- [ ] Single responsibility (no "and")
- [ ] Trigger conditions defined
- [ ] Workflow has ≥ 3 stages with Goal/Steps/Output
- [ ] Decision rules include stopping conditions
- [ ] Delegation references exist and are correct
- [ ] No Maven commands (unless java-maven)
- [ ] No project-specific paths
- [ ] No duplicated checklist content
- [ ] Total lines ≤ 1000
- [ ] Frontmatter has name + description
- [ ] name: matches directory name

---

## Workflow Review Checklist

- [ ] Orchestration-only (no implementation logic)
- [ ] All referenced Skills exist
- [ ] Execution order is clear
- [ ] Handoff conditions defined
- [ ] Stopping conditions defined
- [ ] No embedded knowledge or Playbook content
- [ ] File size ≤ 100 lines

---

## Playbook/Knowledge/Template/Checklist Review Checklist

- [ ] Single topic / theme
- [ ] No execution instructions
- [ ] No project-specific content (hardcoded paths, org names)
- [ ] Referenced by at least one Skill
- [ ] Not orphaned

---

## Maintenance Report Checklist

- [ ] Asset overview included
- [ ] Metrics included with trends
- [ ] Skill reviews included
- [ ] Risks identified and classified
- [ ] Recommendations prioritized (P0-P3)
- [ ] Each recommendation has: action, asset, reason, effort, risk, impact
- [ ] User approval requested
- [ ] No changes made without approval
