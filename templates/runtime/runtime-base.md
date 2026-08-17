# Runtime: Base

## Purpose

Runtime Base defines the common execution contract for all Runtime implementations.

Every Runtime MUST inherit the behavior defined in this document.

Runtime Base itself is bound by:

- AI Operating Rules: governance/AI_OPERATING_RULES.md
- Source of Truth: governance/SOURCE_OF_TRUTH.md
- Context Loading: governance/CONTEXT_LOADING.md
- Repository First: governance/REPOSITORY_FIRST.md
- Reflection Rules: governance/REFLECTION_RULES.md

Examples:

- Dev Setup Runtime
- Specification Runtime
- Development Runtime
- Review Runtime
- Verification Runtime

---

# Runtime Responsibilities

Every Runtime MUST:

- Validate input
- Load execution context
- Execute assigned responsibilities
- Persist execution state
- Generate runtime artifacts
- Handle failures consistently
- Return execution result

---

# Runtime Lifecycle

Every Runtime MUST follow this lifecycle:

Validate

↓

Initialize

↓

Load Context

↓

Execute

↓

Persist

↓

Complete

On Complete, every Runtime MUST persist a per-run diagnostic record to
`ai-system/logs/` per `templates/runtime/runtime-diagnostic-log.md` (Completion
Report + Reflection fields; fails carry root cause + reproduction; normal runs one
page + pointer). Filename `<workflow>-<YYYYMMDD-HHMMSS>.md`.

---

# Runtime Context

Each Runtime owns a Runtime Context.

Runtime Context may include:

- Configuration
- Runtime State
- Active Workspace
- Active Specification
- Active Project
- Loaded Skills
- Loaded Frameworks
- Execution Variables

Runtime Context is read/write during execution.

---

# Runtime Configuration

Runtime MUST load configuration before execution.

Configuration sources may include:

- Runtime Templates
- Global Configuration
- Project Configuration
- Workspace Configuration

Runtime-specific configuration overrides global configuration.

---

# Runtime State

Every Runtime maintains an execution state.

Minimum states:

Initialized

Running

Paused

Failed

Completed

State changes MUST be persisted.

---

# Runtime APIs

Every Runtime SHOULD expose common capabilities.

Required:

Load Context

Resolve Resource

Execute Skill

Execute Workflow

Record Artifact

Update State

Persist

Return Result

---

# Artifact Management

Every Runtime may generate artifacts.

Examples:

Reports

Logs

Generated Documents

Temporary Cache

Artifacts MUST be written to the current execution context.

Runtime MUST NOT overwrite source artifacts.

---

# Persistence

Runtime MUST persist:

Current State

Generated Reports

Execution Metadata

Execution Logs

Runtime Cache MAY be discarded.

---

# Error Handling

Recoverable Error

Retry if possible

Record warning

Continue execution

Fatal Error

Stop execution

Persist runtime state

Generate failure report

Return failure result

---

# Logging

Every Runtime SHOULD generate execution logs.

Minimum information:

Runtime Name

Execution Start Time

Execution End Time

Current Stage

Current Task

Execution Result

---

# Runtime Result

Every Runtime MUST return:

Status

Summary

Generated Artifacts

Warnings

Errors

Next Recommended Action

---

# Runtime Principles

A Runtime MUST:

Be deterministic

Be resumable

Be idempotent whenever possible

Persist state before exit

Never modify resources outside its responsibility

Never duplicate source data

Always record execution history