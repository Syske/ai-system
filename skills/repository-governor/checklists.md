# Checklists

---

## Repository Structure Checklist

Use during Stage 1.

- [ ] All Skill directories listed
- [ ] All Workflow directories listed
- [ ] All Playbook files listed
- [ ] All Knowledge files listed
- [ ] All Template files listed
- [ ] All shared Checklist files listed
- [ ] All RFC files listed
- [ ] All ADR files listed
- [ ] All Governance files listed

---

## Linter Checklist

Use during Stage 2.

- [ ] `scripts/repo-lint.py` executed
- [ ] BLOCKER count: 0
- [ ] ERROR count: reported
- [ ] WARNING count: reported
- [ ] All BLOCKER items understood
- [ ] All ERROR items understood

---

## Metrics Checklist

Use during Stage 3.

- [ ] `scripts/repo-metrics.py` executed
- [ ] Previous snapshot found? (yes / no / first run)
- [ ] Current metrics recorded
- [ ] Trend computed (↑ / ↓ / —)
- [ ] Any metric degraded? (size ↑, duplication ↑, health ↓)

---

## Duplication Checklist

Use during Stage 4.

- [ ] All checklist files compared against shared checklists
- [ ] All skill files scanned for playbook-level knowledge
- [ ] HIGH duplication items identified
- [ ] MEDIUM duplication items identified
- [ ] LOW duplication items identified

---

## Dead Reference Checklist

Use during Stage 5.

- [ ] All playbooks checked for references
- [ ] All shared checklists checked for references
- [ ] All templates checked for references
- [ ] All workflow Skill references verified
- [ ] All Skill delegation references verified
- [ ] Orphaned components identified
- [ ] Broken references identified

---

## Evolution Report Checklist

Use during Stage 6.

- [ ] All findings aggregated
- [ ] Recommendations prioritized (P0 → P4)
- [ ] Each recommendation has: type, component, reason, action, effort, risk
- [ ] Report generated using standard template
- [ ] No changes made (analysis-only)
