# ADR-0009: AI-Operation-First Design

Status: Accepted

Date: 2026-08-13

---

## Context

ai-system is the AI Runtime Engine, and its own maintenance depends on AI.
The user is the decision-maker and does not participate in execution
details. Observed usage:

- The user triggers workflows and commands through `aic` (`python -m cli.main`),
  and the AI executes them.
- The AI performs routine maintenance (`maintain` command), initialization
  (`extensions-init`), and fixes.
- The user only decides: confirming plans, approving changes, choosing
  directions.

Candidate design orientations:

1. **Human-operation-first**: assets target human readability and manual
   execution; AI is only a helper.
2. **AI-operation-first (this ADR)**: assets target AI self-operation and
   self-maintenance; humans only decide. CLI, config, and docs are
   first-class
   for AI discoverability, executability, and verifiability.
3. Mixed: classified per asset type.

This ADR confirms what has already happened (P16 state guard, P17 maven
delegation, P20 publish-chain guards, bugfix hotfix modes, extensions-init
all target AI self-operation) and establishes the default orientation for
**future design**.

## Decision

**Adopt AI-Operation-First (Option 2) as the default principle for future
ai-system design.**

### Principles

1. **AI executes, user decides**: every automatable execution step is done
   by AI; the user only confirms, approves, and chooses direction.
2. **Capabilities must be AI-discoverable**: new capabilities provide an
   `aic-` command entry by default (menu.yaml registration + step-based
   command doc). AI discovers and triggers them via the wizard /
   `python -m cli.main`. Docs-without-AI-entry are not acceptable.
3. **Capabilities must be AI-executable**: command docs are step-based
   (Steps are executable commands with explicit inputs/outputs/guardrails);
   the AI can run them directly without user translation.
4. **Capabilities must be AI-verifiable**: each capability is tied to a
   gate or check (check.py item / `--check` self-test / contract test); the
   AI verifies the result itself after execution.
5. **Config-driven, AI-readable**: process differences converge into config
   (e.g. bugfix-modes.yaml); config structure is gate-validated (typos and
   dead references cannot pass silently); the AI does not rely on doc
   ratification.
6. **Generic/specific two-layer separation**: contracts live in ai-system
   (stable); implementations live in extensions (company-specific). The AI
   scaffolds skeletons via tools and providers fill implementations
   (e.g. branch-parser-scaffold / extensions-init).
7. **Idempotent and safe**: AI-executed tools must be idempotent and
   non-destructive (re-runnable, never overwrite existing content); failures
   must be diagnosable (exit code + explicit output).

### User Interaction Boundary

- User triggers: via `aic` (`python -m cli.main`) selecting workflows and
  commands
- User decision points: fix-plan confirmation (approval_gate), L2/L3 change
  approval, direction choice, providing sensitive inputs (remote URLs,
  credentials)
- User does NOT participate in: routine maintenance inspection, init,
  validation, commit, publish, and other automatable steps

### Acceptance Checklist (new capability acceptance criteria)

New capabilities/assets must satisfy:

- [ ] AI-discoverable entry (aic- command or registered workflow)
- [ ] Command doc is step-based; AI can execute directly
- [ ] Associated check/gate; AI can self-verify
- [ ] Tool is idempotent and non-destructive
- [ ] No hardcoded environment-specific values (paths/addresses/identity
      resolved from config or environment context)

## Rationale

Why AI-Operation-First was chosen:

1. **The system is an AI Runtime Engine by nature**: ai-system exists to
   orchestrate AI execution; depending on AI for its own maintenance is
   consistent with its essence, not an aberration.
2. **Maintenance cost concentrates at the decision layer**: user time is
   the most expensive resource. Automating inspection/init/validation/
   commit/publish hands to AI leaves the user to intervene only at plan
   confirmation, change approval, and direction choice — the lowest total
   maintenance cost (verified this cycle: weekly maintenance + architecture
   changes were all executed by AI; the user only made decisions).
3. **Consistency is dependable**: gates + config-driven design + contract
   tests make AI behavior deterministic and reproducible, independent of
   human memory of process details. Under human-first, process knowledge
   lives in people's heads and is lost when the person changes.
4. **Reproducibility**: on a new company/environment, the AI rebuilds the
   whole system via initializers + scaffolds + config without human recall
   (extensions-init / branch-parser-scaffold / setup.py are all
   AI-triggerable).
5. **Verified**: P16/P17/P20, bugfix hotfix modes, and extensions-init
   since ADR-0008 were all delivered with AI self-operation as the target
   and passed real use. This ADR formally confirms the already-correct
   direction.

Rejected alternatives:

- Human-operation-first: fits traditional software repositories, but the
  consumer of ai-system IS the AI; human-first introduces translation loss
  between AI and docs/processes.
- Mixed: adds classification overhead and costs more than a single
  orientation (each asset type must re-ask "who operates it").

## Consequences

Positive:

- ai-system becomes self-maintaining: AI inspects, fixes, and evolves;
  human cost drops to the decision layer.
- Fast replication across environments/companies: init, scaffolding, and
  config-driven flows are automated.
- Consistency: gates keep config and contracts from drifting; the AI can
  rely
  on deterministic behavior.

Negative/constraints:

- Higher cost per new capability: must also provide command doc + gate +
  scaffold (not just the logic).
- Docs prioritize AI readability, which may sacrifice some human reading
  comfort.
- Over-automation risk: balance with the Evolution Principle (real-issue
  driven); do not automate for automation's sake.

## Relationship to Existing Principles

- Does not replace AI_OPERATING_RULES (behavior rules) or
  AI_DEVELOPMENT_CONTRACT (layering contract); it establishes the design
  orientation.
- Reinforces the Evolution Principle: when real use exposes a maintenance
  pain point → automate (this ADR provides the judgment standard: can it
  be AI self-operated/self-maintained).
- Consistent with extensions/README.md layering: the generic layer
  (ai-system) owns automatable contracts and tools; the extension layer
  owns company-specific implementations.
