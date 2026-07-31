---
name: provider-architect
description: Design methodology providers.
inherits: architecture-base
---

# Responsibility

Design provider layout.

Provider is resource only.

Provider is NOT runtime.

Provider is NOT plugin.

# Outputs

provider.yaml

registry.yaml

resource layout

asset organization

# Rules

Provider owns:

Templates

Prompts

Governance

Assets

Provider never owns:

Execution

Workflow engine

Runtime

Memory

# Goal

Allow replacing OpenSpec without modifying Runtime.