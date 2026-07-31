# ADR-0005: Runtime Architecture

Status: Accepted

Date: 2026-07-24

---

## Context

The AI Runtime Engine needs a layered orchestration architecture where responsibilities are separated into independent layers: Workflows, Runtimes, Operating Rules, Standards, and Skills.

## Decision

Adopt a layered Runtime architecture where:

1. **Workflows** define what process should be executed (entry point, preconditions, inputs, outputs, exit criteria, next step)
2. **Runtimes** orchestrate the execution lifecycle (phases, context loading, skill invocation)
3. **Operating Rules** constrain AI behavior globally
4. **Standards** define implementation quality
5. **Skills** provide reusable implementation capabilities

## Rationale

- **Single Responsibility**: Each layer owns exactly one responsibility, preventing coupling
- **Independent Evolution**: Layers can evolve without affecting others
- **Deterministic Execution**: Clear boundaries enable predictable behavior
- **Replaceability**: Any layer can be swapped without redesigning the system

## Consequences

- Adding a new Workflow requires touching only the workflow definition and its runtime template
- Runtime Templates reference Governance documents, not copy their content
- Skills are stateless and reusable across Runtimes
- The architecture can scale to support new languages, frameworks, and domains without structural changes

## References

- `governance/AI_OPERATING_RULES.md`
- `templates/runtime/runtime-base.md`
