# AI Coding Workflow

## Workflow

prepare

---

# Operating Rules

Load and obey ai-system/governance/AI_OPERATING_RULES.md before execution.

Change control levels (L1 / L2 / L3) and workspace discipline apply to this run.

---

# Workflow: Prepare

## Purpose

Prepare complete implementation context before specification.

## Runtime

- templates/runtime/runtime-prepare.md

## Preconditions

- Bootstrap completed (Environment Context available)
- Change Request available

## Inputs

Required:

- Change ID
- Change Request

Optional:

- Requirement Documents
- Existing Design
- Related Issues
- Existing Specifications
- Mode

## Context

Load only:

- Environment Context (from Bootstrap)
- Change Request materials
- Target repositories identified by the Change Request (structure and entry points only)
- Project Context and Workspace Context, if a previous Dev Setup exists

Never load the entire repository tree into context.

## Outputs

- Requirement Summary
- Repository Summary
- Architecture Summary
- Dependency Report
- Impact Report
- Risk Report
- Preparation Report

## Exit Criteria

Success:

- Readiness = Ready for Specification

Stop:

- Readiness = Blocked → report missing information and stop

## Next

- spec — on ready


---

# Runtime: Prepare

Extends:

- runtime-base.md

---

## Purpose

Build a complete implementation context before Specification.

Prepare Runtime never generates Specifications.

Prepare Runtime never generates implementation code.

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

## Responsibilities

The Runtime is responsible for:

- Requirement Collection
- Context Resolution
- Repository Analysis
- Architecture Analysis
- Dependency Analysis
- Impact Analysis
- Risk Assessment
- Readiness Assessment

---

## Runtime Context

Provided by Bootstrap Runtime:

- Environment Context (repository_root, workspaces_root, methodologies_root)

Optional, only if a previous Dev Setup exists for this project:

- Project Context
- Workspace Context

Prepare runs before Spec and Dev Setup in the main chain and must not require Dev Setup outputs.

Provided by Runtime Base:

- Runtime Configuration
- Operating Rules
- Loaded Skills
- Loaded Frameworks

Resolved by Prepare Runtime:

- Requirement Context
- Architecture Context
- Dependency Context
- Impact Context

---

## Phase 1 — Requirement Collection

Collect:

- User Requirements
- Existing Documents
- Existing Specifications

Generate:

Requirement Summary

Identify:

Unknown Information

Clarification Questions

## Discovery Method

When requirements are ambiguous, apply collaborative discovery:

1. **Explore context first**: Check existing specs, docs, and recent changes before asking questions.
2. **One question at a time**: Ask a single clarifying question, provide a recommended answer, wait for feedback.
3. **Multi-approach**: When multiple interpretation paths exist, propose 2-3 with trade-offs and a recommendation.
4. **Gate**: Do NOT proceed to Phase 2 until requirements are unambiguous.

Present every question and choice to the user in the system language (config/menu.yaml → locale).

---

## Phase 2 — Repository Analysis

Invoke:

- repository-analysis

Analyze:

- Repository Structure
- Modules
- Entry Points
- Existing Tests

---

## Phase 3 — Architecture Analysis

Invoke:

- architecture-analysis

Analyze:

- Services
- APIs
- Database
- MQ
- RPC
- Scheduled Jobs
- External Systems

## Parallel Analysis

When the change spans multiple independent services or modules, dispatch one analysis per service/module in parallel.
Each analysis is independent — one per problem domain with isolated context.
Do NOT use parallel dispatch when services are tightly coupled (fix in one may affect another).

Generate:

Architecture Summary

---

## Phase 4 — Dependency Analysis

Analyze:

- Module Dependencies
- Service Dependencies
- Data Dependencies
- External Dependencies

Generate:

Dependency Report

---

## Phase 5 — Impact Analysis

Determine:

- Modified Modules
- Modified Interfaces
- Modified Contracts
- Modified Data Models

Generate:

Impact Report

---

## Phase 6 — Risk Assessment

Identify:

- Technical Risks
- Compatibility Risks
- Performance Risks
- Migration Risks

Generate:

Risk Report

---

## Phase 7 — Readiness Assessment

Verify:

✓ Requirement Understood

✓ Architecture Understood

✓ Dependencies Identified

✓ Risks Identified

✓ Impact Identified

If complete:

Status = Ready for Specification

Otherwise:

Status = Blocked

---

## Outputs

Generate:

- Requirement Summary
- Repository Summary
- Architecture Summary
- Dependency Report
- Impact Report
- Risk Report
- Preparation Report

## Reflection

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

## Completion

Return:

- Preparation Summary
- Readiness
- Recommended Next Runtime

If Ready:

Next Runtime:

Specification Runtime

---

# User Inputs

Project ID: pywechat-live-2608
Change ID: wecom-live-integration
Change Request: 钉钉推送链 LiveService.changeLiveStatus() 平铺改造：EcoLiveStatusChangedEvent 推送链与 ChangeFeedStatusSyncActionEvent 同步链共用同一 ActiveMQ 队列同一消费者，消息体统一平铺 LiveStatusChangeMqVO{platform:live_course, liveId, status, subStatus, corpId, appId}；旧 LiveStatusChangeEvent 字段包装废弃，旧 LiveStatusChangeEventHandler 下线或改平铺；企微 platform 统一 wx_live；RocketMQ 转发消息体不含 subStatus
Mode: re-entry
Keep Results: False

---

Begin execution.