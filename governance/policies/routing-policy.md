# Routing Policy

This document defines how user intents are routed to workflows and skills.

The authoritative routing configuration lives in `routing/ai-routing.yaml`.

This policy describes the routing model and its execution rules.

---

## Purpose

Route lookup is the only entry point for workflow dispatch.

When a user intent arrives, the router maps it to exactly one workflow or skill via the route table, then dispatches.

---

## Route Types

| Type | Meaning | Example |
|---|---|---|
| `workflow` | Direct dispatch to a registered workflow | `prepare: workflow: prepare` |
| `skill` | Direct dispatch to a standalone skill shortcut | `explore: skill: explore-codebase` |
| `alias` | Re-route to another workflow name | `implement: alias: develop` |

---

## Route Table

All registered workflows are routable by name:

```text
prepare, spec, bootstrap, dev-setup, develop, bugfix,
review, verify, release, analysis, knowledge
```

Standalone skill shortcuts:

```text
explore → explore-codebase
browse  → agent-browser
```

Aliases:

| Alias | Resolves to |
|---|---|
| implement | develop |
| openspec | spec |
| debug | bugfix |

---

## Execution Rules

1. **Route lookup is the only entry point for workflow dispatch.** Do not bypass the route table.
2. **Fallback to the default route for unknown intents.** Unmatched intents resolve to the default route (`explore-codebase`).
3. **Workflows define their own execution chain** (Preconditions, Next); never hardcode pipelines in the routing configuration.
4. **Skills are invoked by runtimes, not directly by route**, unless listed as a standalone skill shortcut.
5. **Aliases resolve before dispatch.** An aliased name dispatches to its target workflow, not a new route.

---

## Configuration Reference

- Routing configuration: `routing/ai-routing.yaml`
- Registered workflows: `config/workflow-registry.yaml`
- Workflow contracts: `workflows/README.md`
