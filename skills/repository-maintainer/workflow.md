# Workflow

## Stage 1: Observe

**Goal:** Capture the context that triggered the maintenance cycle.

**Steps:**

1.1 Determine the trigger: scheduled maintenance / post-change audit /
user request.

1.2 Load the previous maintenance report (if any) from `ai-system/reports`.

1.3 Load the previous metrics snapshot from `ai-system/metrics`.

**Output:** `{trigger, previousReport, previousMetrics}`

---

## Stage 2: Analyze Repository

**Goal:** Index every asset in the repository.

**Steps:**

2.1 Scan `.opencode/skills/` — list every Skill, count files, total lines.

2.2 Scan `.opencode/workflows/` — list every Workflow.

2.3 Scan `.opencode/playbooks/` — list every Playbook.

2.4 Scan `.opencode/knowledge/` — list every Knowledge document.

2.5 Scan `.opencode/templates/` — list every Template.

2.6 Scan `.opencode/checklists/` — list every shared Checklist.

2.7 Scan `ai-system/rfc` — list all RFCs and ADRs.

2.8 Scan `ai-system/governance` — list all governance documents.

2.9 Scan `ai-system/reports` — list all reports.

2.10 Scan `tools/` — list all tools.

**Output:** `{skills: [...], workflows: [...], playbooks: [...], knowledge: [...],
templates: [...], checklists: [...], rfc: [...], adr: [...], governance: [...],
reports: [...], tools: [...]}`

---

## Stage 3: Collect Metrics

**Goal:** Gather quantitative health data.

**Steps:**

3.1 Run `python tools/repo-metrics.py --repo-root . --json` and parse output.

3.2 If a previous snapshot exists at `ai-system/metrics`, load and compare.

3.3 Record baseline metrics (see `metrics.md` for full list).

**Output:** `{currentMetrics, previousMetrics, deltas}`

---

## Stage 4: Analyze Architecture

**Goal:** Verify the repository matches the architecture defined in RFC-0001.

**Steps:**

4.1 Verify layer structure — Foundation Skills do not depend on Orchestration.

4.2 Verify naming conventions — all components match `ai-system/governance/repo-lint.md`.

4.3 Verify frontmatter — every skill.md has valid YAML frontmatter.

4.4 Verify directory conventions — all assets in correct directories.

4.5 Verify backward compatibility — `.opencode/skills/` and `.opencode/commands/` untouched.

**Output:** `{architectureViolations: [{violation, severity, component}]}`

---

## Stage 5: Analyze Dependencies

**Goal:** Generate and analyze the dependency graph.

**Steps:**

5.1 Run `python tools/dependency-graph.py --repo-root . --format json` and parse.

5.2 Identify cycles — circular dependencies between Skills.

5.3 Identify deep chains — dependency chains longer than 3 hops.

5.4 Identify isolated assets — Skills/Workflows/Playbooks with no references.

5.5 Identify orphaned references — Workflows referencing non-existent Skills.

**Output:** `{deps, cycles: [...], deepChains: [...], isolated: [...], orphanedRefs: [...]}`

---

## Stage 6: Review Skills

**Goal:** Evaluate every Skill against 15 review criteria.

**Steps:**

6.1 For each Skill, load `skill.md` and evaluate (see `review.md`):

| Criterion | Weight |
|---|---|
| Purpose clarity | HIGH |
| Single responsibility | HIGH |
| Workflow quality | HIGH |
| Decision quality | MEDIUM |
| Delegation correctness | HIGH |
| Knowledge duplication | HIGH |
| Checklist duplication | MEDIUM |
| Playbook references | MEDIUM |
| Total size | MEDIUM |
| Dependency complexity | MEDIUM |
| Evolution risk | LOW |

6.2 Assign each Skill a recommendation: Keep / Simplify / Split / Merge / Archive.

**Output:** `{skillReviews: [{name, score, recommendation, risks}]}`

---

## Stage 7: Review Workflows, Playbooks, Knowledge, Templates, Checklists

**Goal:** Evaluate all non-Skill assets.

**Steps:**

7.1 For each Workflow, verify orchestration-only, no implementation logic
(see `review.md`).

7.2 For each Playbook, evaluate reuse, duplication, coverage, outdated content.

7.3 For each Knowledge document, detect conflicts, duplicates, stale content.

7.4 For each Template, detect duplicates and unused templates.

7.5 For each Checklist, detect duplicate items and unused checklists.

**Output:** `{workflowReviews: [...], playbookReviews: [...], knowledgeReviews: [...],
templateReviews: [...], checklistReviews: [...]}`

---

## Stage 8: Analyze Capabilities

**Goal:** Build and evaluate the Capability Matrix.

**Steps:**

8.1 For each capability detected in any Skill, identify:

| Attribute | Value |
|---|---|
| Capability | e.g., "Maven execution", "Mockito fixture maintenance" |
| Owner Skill | The Skill primarily responsible |
| Shared with | Other Skills that also implement this capability |
| Duplicated in | Other Skills that duplicate this capability |
| Missing owner | Capabilities with no clear owner |

8.2 Recommend redistribution when duplication exceeds threshold.

**Output:** `{capabilityMatrix: [...], redistributionCandidates: [...]}`

---

## Stage 9: Analyze Shared Assets

**Goal:** Evaluate reuse of Playbooks, Templates, Checklists, Knowledge.

**Steps:**

9.1 For each shared asset, count references across all Skills.

9.2 Identify unreferenced (orphaned) assets.

9.3 Identify over-referenced assets (potential candidates for further splitting).

**Output:** `{sharedAssetUsage: [{asset, refCount, orphaned, overloaded}]}`

---

## Stage 10: Generate Risks

**Goal:** Identify all risks to repository health.

**Steps:**

10.1 Aggregate findings from Stages 4-9.

10.2 Classify each risk:

| Risk level | Criteria |
|---|---|
| CRITICAL | Circular dependency, backward compatibility violation |
| HIGH | Excessive duplication, orphaned Skills, broken references |
| MEDIUM | Missing frontmatter, naming violations, unused assets |
| LOW | Minor inconsistencies, improvement suggestions |

**Output:** `{risks: [{level, description, component, impact}]}`

---

## Stage 11: Prioritize Recommendations

**Goal:** Produce a ranked action list.

**Steps:**

11.1 Sort risks by level (CRITICAL → HIGH → MEDIUM → LOW).

11.2 For each risk, produce a recommendation:

| Field | Value |
|---|---|
| Action | Keep / Simplify / Split / Merge / Archive / Extract / Create |
| Asset | Component name |
| Reason | Why this action is needed |
| Effort | Small / Medium / Large |
| Risk | Low / Medium / High |
| Impact | What improves after this change |

11.3 Verify each recommendation against quality gates (see `checklists.md`).

**Output:** `{recommendations: [{action, asset, reason, effort, risk, impact}]}`

---

## Stage 12: Generate Repository Maintenance Report

**Goal:** Produce the full maintenance report.

**Steps:**

12.1 Format the report:

```
Repository Maintenance Report
─────────────────────────────
Date:       <yyyy-mm-dd>
Health:     <score>/100 — <PASS|DEGRADED|CRITICAL>

ASSET OVERVIEW:
  Skills:     <N> active, <N> deprecated
  Workflows:  <N>
  Playbooks:  <N> (<N> orphaned)
  Knowledge:  <N>
  Templates:  <N> (<N> orphaned)
  Checklists: <N> (<N> orphaned)

METRICS:
  <metric>: <value> <trend>

SKILL REVIEW:
  <name>: <recommendation> — <reason>

RISKS:
  <level>: <description>

RECOMMENDATIONS:
  <priority>. <action> <asset> — <reason>

NEXT MAINTENANCE: <date>
```

**Output:** Maintenance report.

---

## Stage 13: WAIT FOR USER APPROVAL

**Hard gate.** No structural changes without explicit approval.

**Steps:**

13.1 Present the report to the user.

13.2 Ask: "Do you approve these maintenance recommendations?"

| Response | Action |
|---|---|
| "Yes" / "Approve" / specific items | Execute approved items |
| "No" / "Modify" | Update recommendations |
| "Cancel" | Stop |

**Output:** User approval or modification.

---

## Stage 14: Execute and Finish

**Goal:** Apply approved maintenance changes.

**Steps:**

14.1 For each approved recommendation:

| Action | Execution |
|---|---|
| Simplify | Reduce Skill scope, extract knowledge to Playbooks |
| Split | Create new Skill(s), redistribute content |
| Merge | Consolidate two Skills into one, archive old |
| Extract | Move duplicated knowledge to Playbook |
| Archive | Move deprecated assets to archive/ |

14.2 After all changes, run validation:
```shell
python tools/repo-lint.py --repo-root .
```

14.3 Save metrics snapshot:
```shell
python tools/repo-metrics.py --repo-root . --snapshot ai-system/metrics/<date>.json
```

14.4 Generate change summary.

14.5 Report completion.

**Output:** Change summary, updated metrics.
