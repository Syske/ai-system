# Runtime: Release

Extends:

- runtime-base.md

---

# Purpose

Prepare a complete release readiness package.

The Release Runtime ensures all required release activities are identified before deployment.

The Runtime does not execute deployment.

---

## Governance

This Runtime is bound by:

- AI Operating Rules: governance/AI_OPERATING_RULES.md
- Source of Truth: governance/SOURCE_OF_TRUTH.md
- Context Loading: governance/CONTEXT_LOADING.md
- Repository First: governance/REPOSITORY_FIRST.md
- Reflection Rules: governance/REFLECTION_RULES.md

Context is loaded according to governance/CONTEXT_LOADING.md.
Standards are loaded according to loaders/standards-loader.md.

---

# Responsibilities

The Runtime is responsible for:

- Release Scope Analysis
- Change Impact Analysis
- Database Change Review
- Data Migration Planning
- Configuration Review
- Dependency Verification
- Deployment Checklist Generation
- Release Risk Assessment

---

# Runtime Context

Provided by Bootstrap Runtime:

- Environment Context (repository_root, workspaces_root, methodologies_root)

Provided by Dev Setup Runtime:

- Project Context

Provided by Dev Setup Runtime:

- Workspace Context

Provided by Runtime Base:

- Runtime Configuration
- Operating Rules
- Applied Standards

Provided by Specification Runtime:

- Specification
- Contracts
- Scenarios

Provided by Development Runtime:

- Code Changes
- Test Results

Resolved by Release Runtime:

- Release Scope
- Release Checklist
- Migration Plan
- Configuration Plan

---

# Phase 1 — Release Scope Analysis

Identify all projects/services in the release scope.

For EACH project:

- Locate repository root and active branch from workspace metadata (`.aic-workspace.yaml`) or repository config (`repositories/{service}.yaml`)
- Collect:
    - Completed tasks associated with this project
    - New dependencies (pom.xml, build.gradle, package.json changes)

- Run per-project branch diff:
    ```bash
    git fetch origin master
    git diff origin/master...HEAD --stat
    ```
- Classify changed files into:
    - **Application Code** — Java/Kotlin/TS sources, controllers, services, facades
    - **Database** — DDL, DML, migration scripts, Liquibase/Flyway files
    - **Configuration** — Apollo namespaces, MQ channels, environment variables, feature flags
    - **Infrastructure** — Canal adapter configs, CI/CD pipelines, Dockerfiles, deployment manifests
    - **Documentation** — README, API docs, changelogs
    - **Cross-Project Duplicated Definitions** — enums, constants, shared types mirrored across modules

    Check cross-project duplicates against:
    - governance/standards/common/cross-project-sync.md

Aggregate all per-project diffs into:

Release Scope Report

Output example:

| Project | Branch | Files Changed | App | DB | Config | Infra | Docs |
|---------|--------|--------------|-----|-----|--------|-------|------|
| live-api | task/T-022-wecom-live | 24 | 18 | 2 DDL | 19 | 0 | 1 |
| knowledge-api | task/T-025-wecom-live | 31 | 22 | 1 DDL+1 DML | 13 | 0 | 1 |

---

### 1.Y — Branch Diff Quality Review

Review each completed Task Card in the release scope against the aggregated diff.

#### Execution Mode

**Default**: Review one Task → output report → wait for user confirmation → next Task.

**Skip-confirm**: When user passes `--skip-confirm`, review all Tasks sequentially,
output aggregated summary at the end for one-time confirmation.

| Mode | Trigger | Behavior |
|---|---|---|
| Per-Task Confirm (default) | no extra argument | each Task → report → ⏸️ → next |
| Batch Skip-Confirm | `--skip-confirm` | all Tasks → aggregated report → one-time confirmation |

#### Per-Task Review

For each completed Task Card:

**1. Scope check**
- Do the files changed for this task match the Task Card's declared scope?
- Standard: `governance/SOURCE_OF_TRUTH.md` — Task Card scope

**2. Residue scan**
- In the files changed for this task, scan for:
  - `System.out.println` / `printStackTrace` / `e.printStackTrace()`
  - Commented-out code blocks (≥3 consecutive commented lines)
  - `TODO` / `FIXME` / `HACK` markers
  - Debug-level logging left at INFO or above in production paths
- Standards: `governance/standards/common/task-quality-checklist.md` (no residue) + `governance/standards/common/clean-code.md`

**3. Registration check**
- If this task introduces new MQ / RPC / Apollo config:
  - MQ Consumer → Spring bean registered?
  - MQ Producer → producer config declared?
  - RPC Facade → method declared in interface with version?
  - Apollo key → appears in configuration checklist?
- Standards: `governance/standards/cool/rpc-conventions.md` + `governance/standards/cool/rocketmq-conventions.md`

**4. Quality baseline**
- Lightweight scan of the task's changed files:
  - Hardcoded values (URL / Token / Secret) → should be from config center
  - Missing Javadoc on new public classes/methods
  - Silent exception swallowing (empty catch blocks)
  - Log statements containing potential PII or secrets
- Standard: `governance/standards/common/task-quality-checklist.md` (baseline check)

**5. Cross-project check**
- Only if this task touches shared definitions:
  - Enum values / constants / types consistent across sibling projects?
  - Any definition present in one project but missing in sibling projects?
- Standard: `governance/standards/common/cross-project-sync.md`

#### Per-Task Output

Generate one report per task:

```markdown
# Branch Diff Review: {task-id}

**任务**: {task-id} — {title}
**服务**: {service_id}
**分支**: {branch} → master
**变更文件**: N files (+X, -Y, ~Z)

---

## 审查标准

| 维度 | 依据 |
|---|---|
| 范围一致性 | governance/SOURCE_OF_TRUTH.md |
| 迭代残留 | governance/standards/common/task-quality-checklist.md |
| 注册完整性 | governance/standards/cool/rpc-conventions.md / rocketmq-conventions.md |
| 代码质量基线 | governance/standards/common/task-quality-checklist.md |
| 跨服务一致性 | governance/standards/common/cross-project-sync.md |

---

## 发现清单

### BLOCKER（必须修复）

| # | 维度 | 文件:行 | 问题 | 修复建议 |
|---|---|---|---|---|

### WARNING（建议修复）

| # | 维度 | 文件:行 | 问题 | 修复建议 |
|---|---|---|---|---|

### INFO（参考）

| # | 维度 | 文件:行 | 问题 | 说明 |
|---|---|---|---|---|

---

## 统计

| 级别 | 数量 |
|---|---|
| BLOCKER | 0 |
| WARNING | 0 |
| INFO | 0 |

**状态**: ⏸️ 待用户确认
**审查时间**: {timestamp}
```

Save to: `workspaces/{project_id}/openspec/changes/{change_id}/release/review-{task-id}.md`

#### Findings Classification

Per `governance/policies/quality-gates.md`:

| Level | Criteria | Action |
|---|---|---|
| **BLOCKER** | Security, data loss, broken integration, missing registration | Must fix before release |
| **WARNING** | Dead code, missing doc, style violation | Should fix; may defer with documented reason |
| **INFO** | Minor duplication, naming suggestion | Advisory only |

#### Confirmation Flow

**Per-Task Mode (default):**

```
T-001 → report → ⏸️ "T-001 审查完成（0B 2W 1I）。继续审查 T-002？[Y/n/skip-all]"
    Y → next task
    n → stop, return to develop
    skip-all → enter skip-confirm mode
```

**Skip-confirm Mode:**

```
T-001 → T-002 → T-003 → ... → aggregate → ⏸️
    "全部 N 个 Task 已审查。BLOCKER 1 个，WARNING 3 个。是否查看详情？[Y/n]"
```

#### Aggregated Output

After all tasks reviewed, generate `release-branch-review.md`:

```markdown
# Release Branch Review Summary

**发布版本**: {version}
**审查范围**: N tasks / M services
**审查时间**: {timestamp}

---

## 总览

| Task | 服务 | 文件 | BLOCKER | WARNING | INFO | 状态 |
|---|---|---|---|---|---|---|
| {task-id} | {service} | N | 0 | 2 | 1 | ⏸️ 待确认 |
| **合计** | | **N** | **B** | **W** | **I** | |

---

## BLOCKER 汇总
（仅在存在 BLOCKER 时出现）

## WARNING 汇总
（仅在存在 WARNING 时出现）

## INFO 汇总
（仅在存在 INFO 时出现）

---

## 审查标准引用

| 维度 | Governance |
|---|---|
| 范围一致性 | governance/SOURCE_OF_TRUTH.md |
| 迭代残留 + 基线质量 | governance/standards/common/task-quality-checklist.md + clean-code.md |
| 注册完整性 | governance/standards/cool/rpc-conventions.md + rocketmq-conventions.md |
| 跨服务一致性 | governance/standards/common/cross-project-sync.md |
| 发现分级 | governance/policies/quality-gates.md |

---

## 决策

| 条件 | 动作 |
|---|---|
| 存在 BLOCKER | Release Readiness = BLOCKED → 回退 develop 修复 |
| 全部 BLOCKER 清零 | Release Readiness = READY → 继续 release Phase 2 |
```

Save to: `workspaces/{project_id}/openspec/changes/{change_id}/release/release-branch-review.md`

If any BLOCKER finding exists: Release Readiness = BLOCKED, stop and return findings to user for resolution.

---

# Phase 2 — Database Change Analysis

Analyze all database-related changes.

Check:

- New Tables
- Table Alterations
- Index Changes
- Column Changes
- Data Migration
- Data Cleanup
- Enum Value Changes (check enum→database table DML requirements)
- Enum Value Naming (validate against naming convention)

Check against:
- governance/standards/cool/enum-naming.md
- governance/standards/cool/enum-dml.md

Generate:

## SQL Checklist

Include:

- SQL File
- Purpose
- Execution Order
- Execution Environment
- Risk
- Rollback SQL

Each SQL item MUST include the executable script in a code block:

```sql
-- Forward
INSERT INTO `table` (`col1`, `col2`) VALUES ('val1', 'val2');

-- Rollback
DELETE FROM `table` WHERE `col1` = 'val1';
```

Example:

| ID | Purpose | Order | Env | Risk |
|---|---|---|---|---|
| 1 | Insert audit event types | 1 | Prod | Low |

```sql
-- Forward (ID: 1)
INSERT INTO `audit_event_types` (`event_type`, `event_name`)
VALUES ('example_type', 'Example Type');

-- Rollback (ID: 1)
DELETE FROM `audit_event_types` WHERE `event_type` = 'example_type';
```

---

# Phase 3 — Data Migration Analysis

Identify required data operations.

Check:

- Historical Data Migration
- Data Correction
- Data Backfill
- Batch Processing Scripts

For every script:

Require:

- Purpose
- Input
- Output
- Execution Method
- Estimated Time
- Rollback Strategy

Generate:

Data Migration Plan

---

# Phase 4 — Configuration Analysis

Analyze configuration changes.

Check:

- Apollo Configuration
- Environment Variables
- Feature Flags
- Secrets
- Runtime Parameters

MQ configuration changes MUST follow the RocketMQ Convention:
- governance/standards/cool/rocketmq-conventions.md

Check: producer/consumer channel naming, Consumer 4-field spec, group-id prefix, environment isolation, message body documentation.

For every configuration:

Require:

- Key
- Value Change
- Environment
- Effective Time
- Rollback Method

Generate:

## Configuration Checklist

Include:

- Key
- Change Type (add/modify/delete)
- Old Value
- New Value
- Environment
- Effective Method (hot reload/restart)
- Rollback Method

Each configuration change MUST include the entry in a `.properties` code block:

```properties
# Apollo Configuration Changes — Environment: production

# [add] Enable feature X
xxx.feature.enabled=true

# [modify] Timeout increased
yyy.service.timeout=5000
---

# [delete] Deprecated flag (will be removed)
# zzz.old.flag=
```

---

# Phase 5 Dependency Validation

Verify:

□ Facade version updated

□ SNAPSHOT replaced

□ Downstream dependency impact evaluated

Check against RPC Convention:
- governance/standards/cool/rpc-conventions.md

# Phase 6 — Dependency Analysis

Analyze:

- Service Dependencies
- RPC Dependencies
- MQ Topics
- Scheduled Jobs
- External Systems

Check:

- Deployment Order
- Compatibility
- Version Requirements

Generate:

Dependency Checklist

---

# Phase 7 — Deployment Preparation

Generate:

Deployment Checklist

Include:

Before Release:

- Database Preparation
- Configuration Preparation
- Dependency Check

During Release:

- Deployment Order
- Verification Steps

After Release:

- Smoke Test
- Monitoring Check

---

# Phase 8 — Risk Assessment

Identify:

- Database Risk
- Data Risk
- Compatibility Risk
- Performance Risk
- Rollback Risk

Generate:

Risk Report

---

# Phase 9 — Release Readiness

Verify:

✓ Code Verified

✓ SQL Reviewed

✓ Data Scripts Prepared

✓ Apollo Config Reviewed

✓ Dependencies Identified

✓ i18n Resources Complete (all locale files have entries for new enum values)

✓ Copy/Content Reviewed (product confirmed display names for new types)

✓ Rollback Plan Available

✓ Monitoring Plan Available

Result:

READY

or

BLOCKED

---

# Outputs

Generate:

- release-checklist.md             # Overall release readiness per service
- release-change-report.md          # Per-project branch diff summary with change classification
- release-branch-review.md          # Aggregated branch diff quality review
- review-{task-id}.md               # Per-task branch diff review (one per Task Card)
- sql-checklist.md                  # DDL/DML/Scripts with order, rollback, risk
- sql/                              # Executable SQL files organized by execution order
  - {service}-{type}.sql
- data-migration-plan.md            # Data migration scripts with execution plan
- configuration-checklist.md        # Summary checklist for all configuration changes
- configuration-apollo.md           # Apollo per-namespace .properties blocks
- configuration-mq-topics.md         # MQ topic table with producer/consumer matrix + message body schemas
- configuration-canal.md            # Canal/binlog config changes for new/renamed fields
- dependency-checklist.md           # Service dependencies, RPC, MQ, deploy order
- risk-report.md                    # Risk registry with severity and mitigation

# Reflection

Before declaring completion, execute Reflection according to governance/REFLECTION_RULES.md.

Evaluate:
1. Simpler implementation possible?
2. Code duplication introduced?
3. Standards violated?
4. Over-engineering present?
5. Anything incomplete?

Record the Reflection Report in the Completion output.
Do NOT modify code during Reflection.

---

# Completion

Return:

## Release Summary

## Release Readiness

## Required Actions

## Risks

If READY:

Next Step:

Deployment Workflow

If BLOCKED:

Resolve Missing Items