# ADR-0001: OpenSpec Integration as Planning Layer

| Field | Value |
|---|---|
| Status | **Accepted** |
| Decided | 2026-07-02 |

## Context

The repository needed a structured way to go from requirements to code.
Without a planning layer, agents would jump directly into implementation,
producing inconsistent results.

## Decision

Integrate OpenSpec-CN as the standard planning layer. The OpenSpec workflow
(explore → propose → apply → archive) governs all feature development.

## Consequences

**Positive:**
- Requirements are traceable from proposal to task card to code
- Changes are documented in a standard format
- Contracts are generated automatically from specs

**Negative:**
- Adds overhead for trivial changes (one-line fixes)
- Requires OpenSpec-CLI to be installed

## Rationale

OpenSpec provides a mature, schema-driven planning workflow that covers
the full lifecycle: exploration, proposal, task decomposition, implementation,
and archival. No other planning tool in the ecosystem provides this
completeness.

## Related

- `RFC-0001` — Repository Architecture
- `cli/commands/aic-explore.md`
- `cli/commands/aic-propose.md`
- `cli/commands/aic-apply.md`
- `cli/commands/aic-archive.md`
