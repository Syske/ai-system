# ADR-0007: Governance Independence

Status: Accepted

Date: 2026-07-24

---

## Context

The AI Runtime needs a set of global rules, quality standards, and decision frameworks. Where should they live and how should they be enforced?

## Decision

Governance is an independent layer, separate from Runtimes and Skills.

1. **Governance documents** define global behavior rules, not implementation logic
2. **Operating Rules** apply to every Workflow regardless of task type
3. **Standards** define quality expectations for implementation
4. **Runtimes reference Governance**, not the reverse
5. **Governance is never copied** into Runtimes or Skills — it is referenced

## Rationale

- **Single Source of Truth**: If a rule changes, only one file changes
- **Separation of Concerns**: Runtimes orchestrate, Governance constrains
- **Extensibility**: New standards (e.g., `governance/standards/go/go-style.md`) can be added without modifying Runtimes
- **No Duplication**: Multiple Runtimes sharing the same rule reference the same file

## Why Governance is NOT in Runtime

If Governance were embedded in Runtimes:

- Every Runtime would duplicate the same rules
- Changing a rule would require updating every Runtime file
- Rules would drift between Runtimes

If Governance were embedded in Skills:

- Skills would become coupled to specific rules
- Adding a new standard would require updating every Skill
- Skills would no longer be reusable

## How Skills and Governance Interact

Skills contain "how to do it" (implementation methodology).
Governance contains "what rules to follow" (behavioral constraints).

A Skill says: "Write tests. Validate. Mark complete."
Governance says: "No completion claims without fresh verification evidence."

The Skill is the method. Governance is the constraint.

## Consequences

- Governance documents must remain independent of any specific Runtime or Skill
- Runtime Templates reference Governance by path, never by inline copy
- The Standards Loader (`loaders/standards-loader.md`) is the single configuration point for Governance loading order

## References

- `governance/AI_OPERATING_RULES.md`
- `governance/SOURCE_OF_TRUTH.md`
- `governance/REPOSITORY_FIRST.md`
- `governance/CONTEXT_LOADING.md`
- `governance/REFLECTION_RULES.md`
- `loaders/standards-loader.md`
