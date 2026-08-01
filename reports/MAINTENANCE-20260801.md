# Maintenance Report — 2026-08-01

**Mode**: monthly
**Scope**: ai-system + workflow system
**Date**: 2026-08-01
**Environment**: Linux migration workspace (`/home/syske/net-workspace/workspace`)

---

## 1. Tool Check Results

### repo-lint.py

| Severity | Count |
|----------|-------|
| BLOCKER  | 0     |
| ERROR    | 0     |
| WARNING  | 9     |

**Result**: ✅ PASS — no blockers/errors. 9 warnings (informational only).

Warnings breakdown:
- 4× `SKILL.md` > 80 lines with no `workflow.md` (agent-debug-diagnosis, contract-maintainer, java-maven, review)
- 5× Maven command mentions inside skills (bugfix/anti-patterns, bugfix/validation, mock-test/anti-patterns, mock-test/diagnosis, mock-test/mockito)

### repo-metrics.py

| Metric | Current |
|--------|---------|
| Snapshot | metrics/maintain-20260801.json |
| Skills    | 27 (incl. `architecture/` container) |
| Workflows | 11 |
| RFCs      | 12 |
| Governance| 56 |
| Templates | 16 |
| Frontmatter | 26 valid / 1 missing |

**Result**: ✅ PASS — tool now reports real metrics (fixed since 2026-07-22 snapshot which reported all zeros).

> Note: metrics tool counts `architecture/` (a container of 7 sub-skills with no own SKILL.md) as 1 skill → 27. repo-lint excludes it → 26. Discrepancy of 1; both behaviors are internally consistent.

### path-audit.py

| Metric | Value |
|--------|-------|
| Files scanned | 114 |
| References checked | 400 |
| Placeholders | 60 |
| Known debt | 3 |
| BROKEN | **0** |

**Result**: ✅ PASS — no broken path dependencies.

### check.py (System Integrity Gate)

| Result | Detail |
|--------|--------|
| PASS | 11 workflows, 9 commands discovered |
| WARN  | `workflows/release.md` Next: self-reference (re-run loop) |

**Result**: ✅ PASS — exits 0. 1 warning (see finding F2).

---

## 2. Monthly Inspection

### 2.1 Architecture Review

| Check | Result |
|-------|--------|
| Layer structure matches AI_DEVELOPMENT_CONTRACT | ✅ Consistent (cli / workflows / templates / loaders / skills / config / governance / rfc / tools / reports / metrics / logs / archived) |
| No new top-level directories | ✅ None added |
| Backward compatibility (no modules renamed/moved) | ✅ Confirmed |
| Workflows orchestrate without implementing | ✅ Runtime templates carry lifecycle detail; workflows declare contracts only |
| Skills reference correct paths | ✅ 0 broken references |

The architecture is stable and matches the contract. No redesign needed.

### 2.2 Capability Matrix (Maven Execution)

| Capability | Primary Owner | Also present in | Assessment |
|---|---|---|---|
| Maven execution | `java-maven` | bugfix (anti-patterns, validation), mock-test (anti-patterns, diagnosis, mockito) | DUPLICATED — command mentions in skills; per analysis.md these are reference examples, not delegation. Extraction to playbook is optional, low priority |
| Mockito test generation | `mock-test` | bugfix | PARTIALLY DUPLICATED — acceptable |
| Code review | `review` | review-changes, review workflow | PROPERLY OWNED |
| Iterative skill optimization | `skill-optimizer` | `iterative-optimizer` (orchestrates it) | PROPERLY OWNED (orchestration layer) |
| Contract maintenance | `contract-maintainer` | — | PROPERLY OWNED |

No capability without an owner. Maven mentions in bugfix/mock-test are the only duplication signal, already surfaced by lint warnings.

### 2.3 Lifecycle Report

| Stage | Assets |
|-------|--------|
| Active | 26 skills + 7 architecture sub-skills |
| Deprecated | `refactor-safely` (status: deprecated; replaced_by review workflow + review-changes; no references in workflows/cli/config/menu) |
| Archived | archived/workflows (project, workspace), archived/config/workflows (project, workspace), archived/ai-runtime, archived/templates/runtime, archived/frameworks, archived/routing, archived/maintainers |

`refactor-safely` meets the Deprecated → Archived transition (superseded + no references) — candidate for archiving.

### 2.4 Skill Size (RFC-0002 limit: ≤ 1000 lines total)

| Skill | Lines (md only) | Status |
|-------|-----------------|--------|
| implement | 2375 | ⚠️ EXCEEDS |
| mock-test | 1325 | ⚠️ EXCEEDS |
| bugfix | 1314 | ⚠️ EXCEEDS |
| repository-maintainer | 1117 | ⚠️ EXCEEDS |
| skill-optimizer | 2482 (md) / 9552 incl. scripts | ⚠️ EXCEEDS (largest) |

Four skills exceed the RFC-0002 1000-line budget. Candidates for future splitting.

### 2.5 Evolution Suggestions

1. **Archive `refactor-safely`** — deprecated, unreferenced; move to `archived/` after confirmation.
2. **Split oversized skills** (implement, mock-test, bugfix, repository-maintainer) — extract knowledge to playbooks/shared assets.
3. **Reconcile metrics vs lint skill counting** — `architecture/` container counted by metrics, excluded by lint; decide whether sub-skills should be counted individually.
4. **Remove local `.venv`** (39M) under `skills/skill-optimizer/` — gitignored but on-disk cruft.
5. **Run `tools/setup.py`** on this machine to scaffold workspace roots (see F4/F5).

---

## 3. Governance Consistency Spot Check

### Workflow Contract Structure

| Check | Result |
|-------|--------|
| All 11 `workflows/*.md` have 8 sections in order (Purpose/Runtime/Preconditions/Inputs/Context/Outputs/Exit Criteria/Next) | ✅ PASS |
| Terminology matches workflows/README.md glossary | ✅ PASS |
| Runtime reference files exist (11/11) | ✅ PASS |
| Preconditions/Next chain closes (prepare→spec→dev-setup→develop→review→verify→release; bugfix→review→verify; bootstrap→prepare; analysis→knowledge/prepare; knowledge→None) | ✅ PASS |

### YAML Registry Minimality (A1 recurrence prevention)

| Check | Result |
|-------|--------|
| All 11 `config/workflows/*.yaml` stay minimal (version/name/workflow/runtime only) | ✅ PASS |
| No re-inflation into inputs/outputs/next | ✅ PASS |
| `config/workflow-registry.yaml` chain (config → workflow → runtime) resolves | ✅ PASS |

### Referenced Paths Exist

| Area | Result |
|------|--------|
| governance/standards/** (all standards referenced by runtimes) | ✅ PASS (0 broken via path-audit) |
| loaders/** (standards-loader.md) | ✅ PASS |
| templates/prompts/** | ✅ PASS |
| cli/commands/** | ✅ PASS |

### Link Health & Doc-vs-Reality

| Check | Result |
|-------|--------|
| Junction/symlink target dirs (projects/) exist & accessible | ⚠️ WARN — `projects/` absent in this workspace (Linux migration; scaffold not yet run). See F4 |
| AGENTS.md workspace structure diagram vs actual layout | ⚠️ WARN — no workspace-root `AGENTS.md` present here (only `person-learning-note/AGENTS.md`); scaffold dirs `workspaces/ projects/ methodologies/ repositories/` not created. See F4 |
| AI_DEVELOPMENT_CONTRACT architecture diagram vs ai-system/ layout | ✅ PASS — matches |
| OPERATIONS entry sections (1.x) match workflow registry | ✅ PASS |
| config/environments ready for this machine | ⚠️ WARN — only `local.yaml.template` exists (Windows paths); needs `local.yaml` for this host. See F5 |

### State Hygiene

| Check | Result |
|-------|--------|
| project/change references in `workspaces/.aic-state.yaml` exist | ⚠️ N/A — no `workspaces/` dir / state file on this machine (scaffold pending). Not a regression; environment not yet initialized |

---

## 4. Findings (by severity)

| # | Severity | Area | Finding | Recommended Action |
|---|----------|------|---------|--------------------|
| F1 | LOW | tools | `tools/dependency-graph.py` crashes when run from workspace root (`ValueError: list.index(x): x not in list` in `detect_cycles`) due to recursion_stack not cleaned after early `return True`; also hardcodes `ai-system/skills` subdir, so it returns empty when run inside ai-system | Fix cycle detection cleanup + make skills subdir consistent with repo-lint/repo-metrics |
| F2 | LOW | workflows | `release.md` Next lists `release — on BLOCKED (missing release items: resolve and re-run)` — flagged as self-reference re-run loop by check.py | Intentional re-run; reword to make loop-exit explicit or add note |
| F3 | LOW | skills | 4-5 skills exceed RFC-0002 1000-line budget (implement 2375, mock-test 1325, bugfix 1314, repository-maintainer 1117, skill-optimizer 2482/9552) | Route splitting via OPERATIONS §12 change management |
| F4 | WARN | workspace | Workspace scaffold not initialized on this host: `workspaces/ projects/ repositories/ methodologies/` missing; no workspace-root AGENTS.md; no `workspaces/.aic-state.yaml` | Run `python ai-system/tools/setup.py --workspace /home/syske/net-workspace/workspace` (bootstrap) |
| F5 | WARN | config | `config/environments/` has only `local.yaml.template` with `D:\...` paths; no `local.yaml` for this Linux host | Generate `local.yaml` via setup.py; verify workspace.root/repository_root |
| F6 | INFO | tools | metrics (27) vs lint (26) skill count differ due to `architecture/` container handling | Decide policy: count container vs sub-skills |
| F7 | INFO | skills | Deprecated `refactor-safely` remains in `skills/` (unreferenced, superseded) | Archive to `archived/` after confirmation |

---

## 5. Fix Actions

### ✅ Completed (after user confirmation)

| # | Action | Status |
|---|--------|--------|
| P2 | F1 — Fixed `tools/dependency-graph.py`: added `resolve_root` (consistent with repo-lint, works from ai-system/ or workspace root); fixed `detect_cycles` cleanup (recursion_stack no longer left stale after early return, eliminating `ValueError`); updated usage docstring | ✅ DONE |
| P5 | F2 — Reworded `workflows/release.md`: moved "resolve and re-run" loop instruction to Exit Criteria (Stop); removed machine-readable self-edge from Next. check.py now reports 0 warnings | ✅ DONE |
| P3 | F4 — Ran `tools/setup.py --workspace /home/syske/net-workspace/workspace`: scaffolded `workspaces/ projects/ repositories/ methodologies/`, linked `projects/person-learning-note` | ✅ DONE |
| P4 | F5 — Generated `config/environments/local.yaml` for this host (build paths left empty for user to fill) | ✅ DONE |
| P1 | F7 — Archived `skills/refactor-safely` → `archived/skills/refactor-safely`; removed from `skills/README.md` index; recorded in `archived/ARCHIVE.md` | ✅ DONE |
| P6 | F3 — Resolved via OPERATIONS §12 (Option A, approved): reconciled RFC-0002 size rule to per-file limit (matching linter enforcement); synced RFC-0001, quality-gates, skill-lifecycle, review-standard, repository-maintainer criteria, README. See `reports/P6-SKILL-SIZE-PROPOSAL.md` | ✅ DONE |

### 📋 Still open — structural, routed through OPERATIONS §12 (not implemented)

| # | Item | Type |
|---|------|------|
| — | F6 — Decide metrics vs lint skill counting policy (`architecture/` container) | Policy |
| — | Maven capability de-duplication (bugfix/mock-test references) | Optional, low priority |

---

## 6. Metrics Comparison

| Metric | Previous (2026-07-22) | Current (2026-08-01) | Delta | Trend |
|--------|------------------------|-----------------------|-------|-------|
| Skills | 0* (tool bug) | 26 (after archive; incl. container) | +26 | — |
| Workflows | 0* | 11 | +11 | — |
| RFCs | 0* | 12 | +12 | — |
| Governance | 0* | 56 | +56 | — |
| Templates | 0* | 16 | +16 | — |
| Lint BLOCKER | 0 | 0 | 0 | ✅ stable |
| Lint ERROR | 0 | 0 | 0 | ✅ stable |
| Lint WARNING | 0 | 9 | +9 | ↑ needs review |
| Path-audit BROKEN | 0 | 0 | 0 | ✅ stable |
| Frontmatter missing | 0* | 1 (architecture container) | +1 | info |

> *Previous snapshot reported all zeros due to the metrics-tool detection bug (now fixed). First meaningful snapshot. Baseline established from this run.

---

## 7. Completion

### Modified Files

- `tools/dependency-graph.py` — root resolution + cycle-detection cleanup fix
- `workflows/release.md` — Next self-reference loop moved to Exit Criteria
- `skills/README.md` — removed refactor-safely from index
- `archived/ARCHIVE.md` — recorded refactor-safely archival
- `config/environments/local.yaml` — generated for this host (new)
- `rfc/RFC-0002-skill-specification.md` — size rule reconciled to per-file limit (P6/Option A)
- `rfc/RFC-0001-repository-architecture.md` — prohibited-pattern wording synced (P6)
- `governance/policies/quality-gates.md` — Gate 2 size row synced (P6)
- `governance/policies/skill-lifecycle.md` — Split decision synced (P6)
- `governance/review-standard.md` — checklist item synced (P6)
- `skills/repository-maintainer/{checklists,governance,review}.md` — review criteria synced (P6)
- `README.md` — key-rule row synced (P6)

### Moved Files

- `skills/refactor-safely/` → `archived/skills/refactor-safely/`

### New Files

- `reports/MAINTENANCE-20260801.md`
- `reports/P6-SKILL-SIZE-PROPOSAL.md`
- `metrics/maintain-20260801.json`
- `config/environments/local.yaml`
- Workspace scaffold: `workspaces/ projects/ repositories/ methodologies/` (+ `projects/person-learning-note` link)

### Deviations (L1 / L2)

- L1: Applied P1/P2/P3/P4/P5 per user confirmation (`确认修复`).
- L1: P6 resolved via OPERATIONS §12 (Analyze → Propose → Review → **Approve: Option A** → Implement → Validate); approved by user. No L2/L3.

### Risks

- Maven command mentions in bugfix/mock-test remain as lint warnings (informational; optional de-duplication).
- `config/environments/local.yaml` build paths (java_home/maven_home/maven_settings) are empty; user must fill before Java/Maven builds on this host.
- RFC-0002 total-size rule was reconciled to per-file limit; skills with many reference files (implement 2368, skill-optimizer scripts) are no longer flagged as violations — deliberate, matches linter enforcement.

### Next Recommendation

1. ✅ Done — P1/P2/P3/P4/P5/P6 applied and validated (repo-lint 0/0/9, check.py 0 warnings, path-audit 0 broken, dependency-graph.py functional).
2. 📋 Fill `local.yaml` build paths when Java/Maven are installed on this host.
3. 📋 Next maintenance run: weekly (2026-08-08) for trend vs this baseline.
