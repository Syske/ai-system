# Workflow

## Stage 1: Load Repository Structure

**Goal:** Index every component in the repository.

**Steps:**

1.1 Scan `.opencode/skills/` — list all Skill directories and their files.

1.2 Scan `.opencode/workflows/` — list all Workflow directories and their files.

1.3 Scan `.opencode/playbooks/` — list all Playbook files.

1.4 Scan `.opencode/knowledge/` — list all Knowledge files.

1.5 Scan `.opencode/templates/` — list all Template files.

1.6 Scan `.opencode/checklists/` — list all shared Checklist files.

1.7 Scan `<repo-root>/rfc` — list all RFC and ADR files.

1.8 Scan `<repo-root>/governance` — list all governance files.

1.9 Scan `<repo-root>/reports` — list all report files.

**Output:** `{skills: [...], workflows: [...], playbooks: [...], knowledge: [...],
templates: [...], checklists: [...], rfc: [...], adr: [...], governance: [...], reports: [...]}`

---

## Stage 2: Run Linter

**Goal:** Execute automated linting against the repository.

**Steps:**

2.1 Run the linter script:
```shell
python tools/repo-lint.py --repo-root .
```

2.2 Parse the JSON output:

```json
{
  "passed": true,
  "blockers": [],
  "errors": [],
  "warnings": [],
  "infos": [],
  "summary": {
    "skills_checked": 17,
    "files_checked": 52,
    "blockers": 0,
    "errors": 2,
    "warnings": 5
  }
}
```

2.3 For each BLOCKER and ERROR, read the specific rule from
`governance/policies/quality-gates.md`.

**Output:** `{linterResult, blockers: [...], errors: [...], warnings: [...]}`

---

## Stage 3: Run Metrics

**Goal:** Collect quantitative health metrics.

**Steps:**

3.1 Run the metrics script:
```shell
python tools/repo-metrics.py --repo-root .
```

3.2 Parse the JSON output.

3.3 If a previous metrics snapshot exists, compare current vs previous:

| Metric | Previous | Current | Trend |
|---|---|---|---|
| Skills | 15 | 17 | +2 |
| Average Skill size | 520 lines | 540 lines | +20 |
| Duplication index | 0.12 | 0.10 | -0.02 |
| Orphan playbooks | 0 | 0 | — |

**Output:** `{currentMetrics, previousMetrics, deltas}`

---

## Stage 4: Analyze Duplication

**Goal:** Identify duplicated content across Skills.

**Steps:**

4.1 Cross-reference each Skill's checklist headings with
`.opencode/checklists/` shared checklists.

4.2 Identify duplicate checklist items (same heading, same structure).

4.3 Cross-reference each Skill's content with playbook topics.

4.4 Identify knowledge that should be extracted to a Playbook.

4.5 Assign each finding a severity:

| Severity | Meaning | Action |
|---|---|---|
| HIGH | Exact duplication > 10 lines | Consolidate immediately |
| MEDIUM | Semantic duplication > 5 lines | Plan consolidation |
| LOW | Similar topic, different content | Monitor |

**Output:** `{duplications: [{severity, type, skills[], suggestedAction}]}`

---

## Stage 5: Analyze Dead References

**Goal:** Find orphaned and unreferenced components.

**Steps:**

5.1 For each Playbook, check if any Skill references it.

5.2 For each shared Checklist, check if any Skill references it.

5.3 For each Template, check if any Skill references it.

5.4 For each Skill, check if any Workflow or other Skill references it.

5.5 For each Workflow, check if all referenced Skills exist.

5.6 Categorize findings:

| Category | Meaning | Action |
|---|---|---|
| Orphaned Playbook | No Skill references it | Archive or promote |
| Orphaned Checklist | No Skill references it | Archive or promote |
| Broken reference | Workflow references non-existent Skill | Fix workflow |
| Unused Skill | No Workflow references it | Consider deprecation |

**Output:** `{deadRefs: [{category, component, severity}]}`

---

## Stage 6: Generate Evolution Report

**Goal:** Produce actionable recommendations.

**Steps:**

6.1 Aggregate findings from Stages 2-5.

6.2 Prioritize recommendations:

| Priority | Criteria |
|---|---|
| P0 | BLOCKER linter issues |
| P1 | HIGH duplication, broken references |
| P2 | MEDIUM duplication, orphaned components |
| P3 | WARNING linter issues, LOW duplication |
| P4 | INFO, suggestions, improvements |

6.3 Generate the report using this template:

```
Repository Evolution Report
───────────────────────────
Date:       <yyyy-mm-dd>
Skills:     <N> active
Workflows:  <N> active
Health:     <PASS|DEGRADED|CRITICAL>

BLOCKERS (must fix):
  - <description>

ERRORS (should fix):
  - <description>

DUPLICATIONS:
  - <severity>: <description>

DEAD REFERENCES:
  - <category>: <component>

RECOMMENDATIONS:
  1. <priority> — <action>
  2. <priority> — <action>

TREND:
  <metric>: <prev> → <curr> (<direction>)
```

**Output:** Evolution report.

---

## Stage 7: Finish

**Goal:** Report and stop.

**Steps:**

7.1 Present the evolution report to the user.

7.2 If there are P0/P1 items, recommend addressing them.

7.3 If the report is clean, confirm repository health.

7.4 Do not make any changes. This Skill only analyzes and reports.

**Output:** Completion.
