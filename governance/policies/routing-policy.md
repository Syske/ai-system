# Routing Policy

This document defines how user intents are routed to workflows and skills.

The AI System does not maintain a separate runtime route table. Routing is
derived from the workflow contracts themselves.

---

## Purpose

A user intent resolves to exactly one workflow. The resolver is the CLI
wizard (`cli/services/wizard.py`): after the user selects a target, it
recommends the next workflow by parsing each workflow's `## Next` section
(`_parse_next`) and pre-selecting it in the menu.

---

## How Routing Works

1. **Target selection.** The user picks a workflow or command from the
   config-driven menu (`config/menu.yaml`).
2. **Next recommendation.** The wizard reads the selected workflow's
   `## Next` section from `workflows/<name>.md` and recommends the downstream
   workflow.
3. **Dispatch.** The chosen workflow runs its own runtime template
   (`config/workflows/<name>.yaml` → `templates/runtime/runtime-<name>.md`).

---

## Rules

1. **Workflow contracts own the chain.** The `## Next` section in each
   workflow defines its downstream transitions (see `workflows/README.md`,
   Workflow Template). Never hardcode a pipeline in code.
2. **Next must be machine-readable.** Each `## Next` bullet starts with the
   downstream workflow name (kebab-case), `None`, or a known external target
   (`deployment`). Enforced by `tools/checks/workflow.py` (check_next_sections).
3. **Workflow registry is the single source of workflow identity.**
   `config/workflow-registry.yaml` lists every workflow; the menu and wizard
   resolve against it.
4. **Skills are invoked by runtimes**, not by a top-level router.

---

## Configuration Reference

- Workflow contracts: `workflows/README.md` + `workflows/<name>.md`
- Workflow registry: `config/workflow-registry.yaml`
- Menu: `config/menu.yaml`
- Wizard: `cli/services/wizard.py`
