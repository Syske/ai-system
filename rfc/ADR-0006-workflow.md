# ADR-0006: Workflow-First Design

Status: Accepted

Date: 2026-07-24

---

## Context

The AI system needs a clear execution model: who decides what to run, in what order, and how results flow between stages.

## Decision

Adopt a Workflow-First architecture where:

1. **Workflows are the entry point** for all user-initiated actions
2. **Workflows select the Runtime**, which orchestrates the execution lifecycle
3. **Runtimes invoke Skills**, which contain implementation knowledge
4. **Skills do NOT schedule, dispatch, or route** — they only implement

## Rationale

- **Workflow First**: Every action starts from a known workflow with defined preconditions and exit criteria
- **Skill Independence**: Skills are pure implementation units with no knowledge of scheduling or routing
- **Clear Accountability**: If something goes wrong, trace up: Skill → Runtime → Workflow
- **No Hidden State**: Workflows define explicit next steps (`Next: review`), not implicit chains

## Alternatives Considered

- **Skill-First**: Skills would auto-chain and self-route. Rejected because this creates hidden dependencies and makes debugging impossible.
- **Runtime-First**: Runtimes would self-discover tasks. Rejected because this requires a scheduler/event bus, violating the MVP principle of simplicity.

## Consequences

- Skills must never contain routing logic
- Adding a new workflow requires a workflow definition + runtime template
- The workflow registry (`config/workflow-registry.yaml`) is the single entry point for all workflows

## References

- `config/workflow-registry.yaml`
- `workflows/develop.md`
- `workflows/review.md`
