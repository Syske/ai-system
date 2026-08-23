# Runtime: Bootstrap

Extends:

- runtime-base.md

---

# Purpose

Load environment configuration and derive all base paths.

Bootstrap Runtime prepares the environment context that all downstream runtimes depend on.

Bootstrap Runtime does not manage workspace state, resolve project configuration, or implement business logic.

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

The Bootstrap Runtime is responsible for:

- Provision Environment (run tools/setup.py when configuration is missing)
- Load Environment Configuration
- Derive Workspace Root
- Derive Repository Root
- Derive Workspaces Root
- Derive Methodologies Root
- Initialize Workspace Directory
- Build Environment Context
- Persist Environment State

---

# Runtime Context

## Provided by Runtime Base

- Runtime Configuration
- Operating Rules

## Resolved by Bootstrap Runtime

- Environment Name
- Workspace Root
- Repository Root
- Workspaces Root
- AI System Root
- Methodologies Root
- Workspace ID
- Workspace Path
- Project ID

---

# Phase 1 — Load Environment Configuration

Locate:

- ai-system/config/environments/{environment}.yaml

Resolve:

- workspace.repository_root

If environment configuration is missing:

1. Guide the user to run `python tools/setup.py [--environment {environment}]`:
   - Generates `config/environments/{environment}.yaml` interactively
   - Scaffolds workspace base directories (workspaces/ projects/ repositories/ methodologies/ extensions/)
   - Ensures ai-system runtime dirs (metrics/ logs/)
   - Links detected code repositories into projects/
   - Records the metrics baseline snapshot (metrics/baseline-{date}.json, if missing)
   - Runs `tools/path-audit.py` to verify paths
2. Re-load the environment configuration.

If the configuration still cannot be loaded:

STOP.

Report missing environment configuration.

---

# Phase 2 — Derive Base Paths

Derive all base paths from the environment configuration and bootstrap location.

Config source order (merged by `cli/services/environment.py`):

```
machine layer   ~/.config/ai-system/env.yaml   # 首启按系统生成，优先；用户可改（如 WSL 路径）
workspace layer config/environments/{env}.yaml  # 工作区共享项（bugfix.mode 等）+ 旧版兼容
fallback        自动推导（见下）                # 布局路径无需配置
```

Derivation:

```
workspace_root    = {machine layer → workspace.root} or {local.yaml → workspace.root} or {ai-system directory parent}
repository_root   = {local.yaml → workspace.repository_root}
repositories_root = {workspace_root}/repositories
workspaces_root      = {workspace_root}/workspaces
ai_system_root       = {workspace_root}/ai-system
methodologies_root   = {workspace_root}/methodologies
```

Do not hardcode absolute paths.

Paths are derived once and shared across all downstream runtimes.

---

---

# Phase 3 — Build Environment Context

Generate:

```yaml
environment:
  name: local
  workspace_root:
  repository_root:
  repositories_root:
  workspaces_root:
  ai_system_root:
  methodologies_root:
```

---

# Phase 4 — Persist

Store:

- environment_context

Location:

```
ai-system/config/environments/context.yaml
```

Note: environments/context.yaml should be added to .gitignore.

---

# Phase 5 — Initialize Workspace

Create workspace directory:

```
{workspaces_root}/{workspace_name}/
```

Workspace name is derived from the environment name or provided input.

Initialize:

- Workspace ID
- Workspace Status (initialized)
- Workspace Metadata

The workspace metadata includes:

```yaml
workspace:
  id: {workspace_name}
  status: initialized
  path: "{workspaces_root}/{workspace_name}"
  environment: {environment_name}
```

Do not bind project context or resolve repositories here.

Project binding and repository resolution belong to Dev Setup Runtime.

---

# Outputs

Generate:

- Environment Context (workspace_root, repository_root, workspaces_root, ai_system_root, methodologies_root)
- Workspace Metadata (initialized, no project binding)

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

## Environment Context

Contains:

- Workspace Root
- Repository Root
- Methodologies Root
- Workspaces Root
- AI System Root
- Workspace ID
- Workspace Path
- Workspace Status

The Environment Context can be consumed by:

- Dev Setup Runtime
- All downstream runtimes



