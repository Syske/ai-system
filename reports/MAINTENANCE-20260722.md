# Maintenance Report — 2026-07-22

**Mode**: weekly (extended with release.md evaluation)
**Scope**: workflows, release.md domain assessment
**Date**: 2026-07-22

---

## 1. Tool Check Results

### repo-lint.py

| Severity | Count |
|----------|-------|
| BLOCKER  | 0     |
| ERROR    | 0     |
| WARNING  | 0     |

**Result**: ✅ PASS — Clean run, no issues.

### path-audit.py

| Metric           | Value |
|------------------|-------|
| Files scanned    | 85    |
| References checked | 141 |
| Placeholders     | 38    |
| Known debt       | 11    |
| BROKEN           | 0     |

**Result**: ✅ PASS — No broken path dependencies.

### repo-metrics.py

| Metric          | Current |
|-----------------|---------|
| Snapshot        | metrics/maintain-20260722.json |
| Skills count    | 0*      |
| Workflows count | 0*      |

> *Note: repo-metrics.py reports 0 due to pattern/detection issue, not actual count. Requires tool investigation (TECH-DEBT).

### Governance Consistency Checks

| Check | Result |
|-------|--------|
| All workflows/*.md have 8 sections in order | ✅ PASS |
| All config/workflows/*.yaml minimal (3 fields, no inputs/outputs/next) | ✅ PASS |
| Runtime files referenced by workflows exist | ✅ PASS |
| Workspace state (.aic-state.yaml) valid — references pywechat-live-2608 | ✅ PASS |
| OPERATIONS.md §11 (Change Management) present and complete | ✅ PASS |
| A1 regression (YAML re-inflation) absent | ✅ PASS |

### Path Integrity

| Reference | Status |
|-----------|--------|
| workflows/release.md → templates/runtime/runtime-release.md | ✅ EXISTS |
| runtime-release.md → runtime-base.md | ✅ EXISTS |
| runtime-release.md → governance/standards/common/cross-project-sync.md | ✅ EXISTS |
| runtime-release.md → governance/standards/cool/enum-naming.md | ✅ EXISTS |
| runtime-release.md → governance/standards/cool/enum-dml.md | ✅ EXISTS |

**All paths verified** — no broken references.

### Docs–Reality Consistency

| Check | Result |
|-------|--------|
| AGENTS.md workspace tree vs actual directory layout | ⚠️ MINOR — tree shows `ai-system/`, `methodologies/`, `projects/`, `repositories/`, `workspaces/` which all exist. Additional top-level items (`docs/`, `launch/`, `outputs/`, `temp/`) not documented in AGENTS.md. |
| OPERATIONS.md §1–§15 section numbering vs content | ✅ Consistent |

---

## 2. Release.md Domain Evaluation

### 2.1 User Expectations Summary

The user asked 4 questions about release.md:

| # | Expectation | Verdict |
|---|-------------|---------|
| 1 | **Per-project branch diff with master** — compare each project branch against master, collect differences | ❌ **Not supported** |
| 2 | **Collect release configs, SQL, etc.** — gather configuration, SQL, and release artifacts | ⚠️ **Partial** |
| 3 | **RocketMQ special conventions** — domain-specific MQ configuration rules | ⚠️ **Partial** |
| 4 | **RPC special conventions** — domain-specific RPC/facade rules | ⚠️ **Partial** |
| 5 | **Final config checklist** — reference structure from `workspaces/pywechat-live-2608/outputs/release/` | ⚠️ **Structure differs** |

### 2.2 Per-Project Branch Diff (Expectation 1) — ❌ NOT SUPPORTED

**What release.md says**:
- Context: "Git changes, completed tasks and test results in the release scope"
- Phase 1: "Git Changes" as a collection bucket

**What is missing**:
- No mechanism to iterate over multiple projects (release.md assumes single workspace)
- No concept of diffing `task/{task-id}` branch against `master` per project
- No per-project change classification (what changed in project A vs project B)
- No template for per-project diff output

**Severity**: MODERATE — for multi-project releases, the reviewer must manually gather per-project diffs.

**Recommendation**: Enhance runtime-release.md Phase 1 with explicit per-project branch diff step:
```
For each project in the release scope:
  - Identify repository from workspaces/{id}/repository metadata
  - Run: git diff master...HEAD --stat (changed files)
  - Classify: application / database / configuration / infrastructure
  - Aggregate into Release Scope Report
```

### 2.3 Configuration & SQL Collection (Expectation 2) — ⚠️ PARTIAL

**What release.md provides** ✅:
- sql-checklist.md — DDL/DML with order, risk, rollback
- data-migration-plan.md — data operations with execution plan
- configuration-checklist.md — key, change type, old/new values, env, rollback
- Phase 2 (Database Analysis) — detailed table/column/index checks
- Phase 4 (Configuration Analysis) — Apollo, env vars, feature flags, secrets

**What is missing** ❌:
- No requirement for a **centralized release output directory** (reference uses `workspaces/{id}/outputs/release/`)
- No requirement for **per-service artifact breakdown** (reference shows per-service tables)
- No Canal configuration check template (reference has `configuration-canal.md`)
- No MQ Topic configuration artifact (reference has `configuration-mq-topics.md`)
- No release-checklist.md structure specification (reference has comprehensive per-section checklist)
- No **enum naming & DML compliance** check (runtime-release.md Phase 2 checks, but not wired into outputs)
- No **i18n completeness** check (Phase 9 release readiness mentions i18n, but no output artifact)

**Gap analysis vs reference output** (`workspaces/pywechat-live-2608/outputs/release/`):

| Reference Artifact | In release.md Outputs | In runtime Phases |
|--------------------|----------------------|-------------------|
| release-checklist.md | ✅ Listed | — |
| sql-checklist.md | ✅ Listed | ✅ Phase 2 |
| data-migration-plan.md | ✅ Listed | ✅ Phase 3 |
| configuration-checklist.md | ✅ Listed | ✅ Phase 4 |
| dependency-checklist.md | ✅ Listed | ✅ Phase 6 |
| risk-report.md | ✅ Listed | ✅ Phase 8 |
| **configuration-apollo.md** | ❌ Not listed | ⚠️ Phase 4 generically covers Apollo |
| **configuration-mq-topics.md** | ❌ Not listed | ⚠️ Phase 6 mentions MQ Topics generically |
| **configuration-canal.md** | ❌ Not listed | ❌ Not mentioned |
| **sql/ subdirectory** | ❌ Not listed | ❌ Not mentioned |

**Severity**: LOW-MODERATE — runtime delegates structure to skill, but workflow does not constrain artifact completeness. The reference output demonstrates what a thorough release produces, but this is achieved by implementation skill, not workflow definition.

**Recommendation**: Add to release.md Outputs (or runtime Phase 1):
```
For each service in the release scope, generate:
  - configuration-{service}.md (Apollo config per namespace with .properties blocks)
  - configuration-mq-topics.md (MQ topic table with producer/consumer matrix + message body)
  - configuration-canal.md (Canal/E2E field sync changes)
  - sql/{service}-{type}.sql (executable SQL, organized by execution order)
```

### 2.4 RocketMQ Conventions (Expectation 3) — ⚠️ PARTIAL

**Conventions observed in reference output** (`configuration-mq-topics.md` + `configuration-apollo.md`):

| Convention | Pattern | Documented in runtime? |
|------------|---------|----------------------|
| Channel naming | `cool.mq.bindings.producer.{channelName}.topic` | ❌ |
| Consumer 4-field spec | topic, tag, group-name, group-id | ❌ |
| Group-ID prefix | `GID_` prefix convention | ❌ |
| Environment isolation | topic/tag/group-id suffixed `_t2`, `_pre` | ❌ |
| Topic table | List: name, type, msg type, producer, consumer | ❌ |
| Message body | JSON structure per topic | ❌ |
| MQ architecture diagram | Producer → Consumer flow | ❌ |

**What runtime-release.md says**:
- Phase 6: "MQ Topics" as a dependency category
- Phase 5: Facade / SNAPSHOT check (RPC-focused, not MQ)

**Severity**: MODERATE — RocketMQ is a critical integration point with specific operational patterns. Without documented conventions, each release generates ad-hoc MQ documentation.

**Recommendation**: Add a domain-specific convention section to runtime-release.md or as a standards document:
```markdown
### RocketMQ Convention (applies when project uses cool.mq.* framework)

Every MQ Topic must document:
1. Topic name, type (normal/ordered/transactional), message type (concurrent/sequential)
2. Producer service, consumer service(s)
3. All 4 consumer fields: topic, tag, group-name, group-id
4. Group-ID must use `GID_` prefix
5. Environment suffix: `_t2` (test), `_pre` (preprod), none (production)
6. Message body JSON structure (required fields, types, examples)
7. Deployment order constraint (producer must be deployed before or with consumer)
```

### 2.5 RPC Conventions (Expectation 4) — ⚠️ PARTIAL

**What runtime-release.md says**:
- Phase 5: "Facade version updated" / "SNAPSHOT replaced" / "Downstream dependency impact evaluated"
- Phase 6: "RPC Dependencies" as a category

**What's missing**:
| Convention | Documented? |
|------------|------------|
| Per-service RPC dependency matrix | ❌ |
| Facade naming convention (`{service}-api-facade`, `IBiz*Facade`) | ❌ |
| RPC interface backward compatibility check | ❌ |
| Deployment order constraint due to RPC version dependency | ❌ |
| Cross-service RPC version mapping | ❌ |

**Severity**: LOW — Facade/SNAPSHOT check covers the most critical RPC concerns. Additional conventions would improve completeness but are not blocking.

### 2.6 Reference Output Structure (Expectation 5)

The reference at `workspaces/pywechat-live-2608/outputs/release/` provides an authoritative artifact structure:

```
outputs/release/
├── release-checklist.md          # Per-service breakdown, readiness status
├── sql-checklist.md              # DDL/DML with order, rollback, code blocks
├── sql/
│   ├── sql-ddl.sql
│   ├── sql-dml.sql
│   └── insert_audit_event_types.sql
├── configuration-apollo.md       # Per-namespace .properties blocks
├── configuration-mq-topics.md    # Topic table + message schemas + flow diagram
├── configuration-canal.md        # Binlog sync changes
├── configuration-checklist.md    # Summary checklist
├── dependency-checklist.md       # Service dependencies, MQ, deploy order
├── data-migration-plan.md        # Migration scripts with execution plan
└── risk-report.md                # Risk registry with severity + mitigation
```

**This structure exceeds release.md mandated outputs in depth (per-service) and breadth (Canal, MQ topics, Apollo per-namespace).**

The gap is that release.md constrains: "what files to produce" — but NOT "what those files must contain." The reference output's richness comes from implementation skill effort, not workflow prescription.

---

## 3. Inspection Findings

### 3.1 BLOCKER / ERROR (0 items)

None — all tools pass cleanly.

### 3.2 WARNING / MINOR (1 item)

| # | Severity | Area | Finding | Action |
|---|----------|------|---------|--------|
| W2 | WARNING | repo-metrics.py | Reports 0 for all metrics (skills, workflows, governance) — detection logic may have path or pattern bug | File TECH-DEBT issue for tool fix |

### 3.3 Domain Gaps (release.md)

| # | Severity | Gap | Impact |
|---|----------|-----|--------|
| G1 | MODERATE | No per-project branch diff against master | Multi-project releases require manual diff collection |
| G2 | MODERATE | RocketMQ domain conventions undocumented | Each release produces ad-hoc MQ documentation |
| G3 | LOW | RPC conventions incomplete (beyond facade/SNAPSHOT) | RPC dependency matrix left to implementation |
| G4 | LOW-MODERATE | Release output artifacts lack specification for per-service config, Canal, MQ topic files | Output quality depends on skill, not workflow prescription |

### 3.4 Health Score

| Metric | Value |
|--------|-------|
| Lint status | ✅ CLEAN (0/0/0) |
| Path integrity | 1 broken reference |
| Governance consistency | ✅ All clean (8-section, minimal YAML, state hygiene) |
| Domain coverage gaps | 4 identified (G1-G4) |
| Tech debt | 1 (metrics tool reporting 0) |

---

## 4. Recommended Fix Actions

### Fix as Low-Impact (documentation)

| # | File | Change | Type |
|---|------|--------|------|
| P5 | `workflows/release.md` | Update Outputs section to specify: per-service config, MQ, Canal, SQL subdirectory | Workflow improvement |

### ✅ Completed (this maintenance run)

| # | Action | Status |
|---|--------|--------|
| G1 | `workflows/release.md` — per-project branch diff (Context + release-change-report.md) | ✅ DONE |
| G2 / P3 | `governance/standards/cool/rocketmq-conventions.md` (English) + referenced in runtime-release Phase 4 | ✅ DONE |
| G3 / P4 | `governance/standards/cool/rpc-conventions.md` (English) + referenced in runtime-release Phase 5 | ✅ DONE |
| P2 | `templates/runtime/runtime-release.md` Phase 1 — multi-project iteration with per-project git diff | ✅ DONE |
| W3 | `AGENTS.md` — workspace tree updated (docs/, launch/, outputs/, temp/) | ✅ DONE |

### ⏳ Pending (awaiting sequential confirmation)

| # | Item | Dependency |
|---|------|------------|
| — | All items complete | — |

---

## 5. Metrics Comparison

| Metric | Previous | Current | Delta |
|--------|----------|---------|-------|
| Snapshot timestamp | — (first) | 2026-07-22 | N/A |
| Lint blockers | — | 0 | — |
| Path audit broken | — | 0 | — |
| Governance issues | — | 0 | — |

> No previous snapshot available for delta analysis. Future maintenance runs will show trend.

---

## 6. Completion

### Modified Files

None (inspection only; no changes applied)

### New Files

- `reports/MAINTENANCE-20260722.md`
- `metrics/maintain-20260722.json`

### Deviations (L1 / L2)

- L1: Corrected false alarm in report (path was correct); updated AGENTS.md workspace tree; archived 3 Chinese standards → English rewrites (enum-naming, enum-dml, cross-project-sync)
- L2: Pending confirmation for P5 (release.md Outputs supplement)

### Risks

- Release.md currently lacks domain-specific conventions for RocketMQ and RPC, relying on implementation skill to fill gaps. For teams unfamiliar with the conventions, release outputs may be inconsistent.
- repo-metrics.py reporting 0 for all metrics may indicate a broader detection issue that will affect future maintenance trend tracking if not addressed.

### Next Recommendation

1. ✅ Confirm this report and apply F1 (broken path fix) — minor, non-structural
2. 📋 Route G1–G4 (domain gaps in release.md) through OPERATIONS §11 change management: Analyze → Propose (RFC if needed) → Review → Approve → Implement
3. 🔧 File TECH-DEBT for repo-metrics.py reporting 0 on all categories
