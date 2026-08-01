---
name: grilling
description: Stress-test a plan, design, or idea through a relentless decision-tree interview before implementation. Use when the user wants to pressure-test a proposed design or plan, or mentions "grill", "stress-test this plan", "challenge this design", "walk through the decisions". Walks each branch of the decision tree one question at a time, provides recommended answers, and does NOT act until the user confirms shared understanding. Does NOT apply to reviewing completed code (use review workflow) or to bug fixing.
---

# Grilling

Interview the user relentlessly about a plan, design, or idea until reaching a shared understanding. This is a **design pressure test** used between prepare (Architecture Summary) and spec (Design), before implementation begins.

## When to Use

**Use when:**
- The user has a plan, design, or proposal with soft spots to surface
- A design decision tree needs to be walked branch by branch before coding
- The user explicitly asks to "grill", "stress-test", or "challenge" an idea
- Preparing a Design artifact after an Architecture Summary exists

**Do NOT use when:**
- Reviewing already-implemented code (use the `review` workflow, whose runtime-review Grilling Method applies)
- Fixing a bug (use `bugfix`)
- Clarifying ambiguous requirements (use prepare/spec Discovery Method)

## Method

### 1. Model the decision tree

Map the plan as a **decision tree**: every plan branches into decisions, and decisions depend on each other. Descend the tree one node at a time, so an early answer reshapes which questions come next.

### 2. Walk each branch in dependency order

Resolve dependencies between decisions one by one. Do not skip. An early answer can unblock or reshape later branches.

### 2.5 Challenge domain terminology

When the user uses a term that conflicts with existing language in specs, contracts,
or knowledge, call it out immediately and propose a precise canonical term. Stress-test
domain relationships with concrete scenarios that probe edge cases. If the code,
spec, or contract contradicts what the user says, surface the contradiction — decide
which side is the truth rather than silently assuming.

### 3. Ask one question at a time

Ask a single question, provide your **recommended answer**, and wait for feedback before the next. Asking multiple questions at once is bewildering and loses the tree structure.

### 4. Look up facts, ask only decisions

If a *fact* can be found by exploring the environment (filesystem, tools, codebase, existing specs), look it up rather than asking the user. The *decisions* are the user's — put each one to them and wait for their answer.

### 5. Do not act until confirmed

Do not implement, write the spec, or change files until the user confirms a shared understanding has been reached.

## Interaction

- Present every question and choice in the system language (`config/menu.yaml → locale`).
- Provide a recommended answer with each question to make the interview converge.
- If a question can be answered by exploring the codebase, explore instead of asking.

## Output

- A confirmed, shared understanding of the plan/design with every decision resolved
- No implementation until confirmation

## Related

- `templates/runtime/runtime-review.md` — Grilling Method (review-phase variant)
- `templates/runtime/runtime-spec.md` — Discovery Method (requirement clarification)
- Workflow chain: prepare → spec → dev-setup → develop
