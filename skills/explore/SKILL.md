---
name: explore
description: OpenSpec-aware exploration support for the aic-explore command. Use when running aic-explore in OpenSpec workspace to check active changes, reference artifacts naturally, and offer to capture decisions. Loaded by the aic-explore command; not for standalone use.
---

# OpenSpec Exploration Support

Supports the `aic-explore` command: thinking-partner exploration with
OpenSpec awareness. This skill carries the OpenSpec-specific methodology;
the command carries the stance.

## Relationship with explore-codebase

This skill is the **OpenSpec workspace exploration** capability — it is
loaded by the `aic-explore` command to check active changes, reference
artifacts, and offer to capture decisions. It is **not** for standalone
codebase-structure analysis.

For knowledge-graph driven codebase structure understanding (mapping
modules, tracing usage, finding entry points before a change), use the
**`explore-codebase`** skill (`skills/explore-codebase/SKILL.md`) instead —
it is a standalone skill that navigates the code graph directly.

**Which to use:**

| 场景 | 用哪个 |
|------|--------|
| 被 `aic-explore` 命令调用（OpenSpec 工作区导航/澄清需求） | **explore**（本技能） |
| 独立理解代码库结构（模块映射、调用追踪、入口点查找） | **explore-codebase** |
| 变更前的结构概览（不涉及 OpenSpec 变更导航） | **explore-codebase** |
| 变更提案/澄清需求时的工作区上下文（proposal/design/tasks） | **explore**（本技能） |

## Check the context

At the start, quickly check what exists:
```bash
openspec-cn list --json
```

This tells you:
- Whether there are active changes
- Their names, schemas, and statuses
- What the user might be working on

If the user mentions a specific change name, read its artifacts for context.

## When no change exists

Think freely. When an insight crystallizes, you might offer:

- "This feels solid enough to start a change. Want me to create one?"
  → can transition to `/aic-propose` or `/aic-apply`
- Or keep exploring — no formal pressure

## When a change exists

If the user mentions a change or you detect a relevant one:

1. **Read existing artifacts for context**
   - `openspec/changes/<name>/proposal.md`
   - `openspec/changes/<name>/design.md`
   - `openspec/changes/<name>/tasks/cards/` (task cards)
   - etc.

2. **Reference them naturally in conversation**
   - "Your design mentions Redis, but we just realized SQLite might be better..."
   - "The proposal scopes this to power users, but we're now considering everyone..."

3. **Offer to capture when a decision is made**

   | Insight type | Capture location |
   |---|---|
   | New requirement discovered | `specs/<capability>/spec.md` |
   | Requirement changed | `specs/<capability>/spec.md` |
   | Design decision made | `design.md` |
   | Scope changed | `proposal.md` |
   | New work identified | `tasks/cards/` |
   | Assumption invalidated | relevant artifact |

   Example offers:
   - "This is a design decision. Want to record it in design.md?"
   - "This is a new requirement. Want to add it to specs?"
   - "This changes the scope. Want to update the proposal?"

4. **User decides** — offer and continue. Don't pressure. Don't auto-capture.

## Things You Might Do

Depending on what the user brings, you might:

**Explore the problem space**
- Ask clarifying questions about what they said
- Challenge assumptions
- Reframe the problem
- Look for analogies

**Investigate the codebase**
- Map the existing architecture relevant to the discussion
- Find integration points
- Identify patterns already in use
- Surface hidden complexity

**Compare options**
- Brainstorm multiple approaches
- Build comparison tables
- Sketch trade-offs
- Recommend a path (if asked)

**Visualize**
```
┌─────────────────────────────────────────┐
│        Use ASCII diagrams liberally     │
├─────────────────────────────────────────┤
│                                         │
│      ┌────────┐         ┌────────┐      │
│      │ state  │────────▶│ state  │      │
│      │   A    │         │   B    │      │
│      └────────┘         └────────┘      │
│                                         │
│   system maps, state machines, data     │
│   flows, architecture sketches,        │
│   dependency graphs, comparison tables  │
│                                         │
└─────────────────────────────────────────┘
```

**Surface risks and unknowns**
- Identify what could go wrong
- Discover gaps in understanding
- Suggest probes (spikes) or investigations

## Things You Don't Have to Do

- Follow a script
- Ask the same questions every time
- Produce specific artifacts
- Reach a conclusion
- Stay on topic if a digression has value
- Be brief (this is thinking time)

## Ending Exploration

No required ending. Exploration might:

- **Flow into action**: "Ready to start? `/aic-propose` or `/aic-apply`"
- **Result in artifact updates**: "Updated design.md with these decisions"
- **Provide clarity only**: the user got what they needed, moved on
- **Continue later**: "We can pick this thread up anytime"

When things feel clear, you can summarize - but it's optional. Sometimes the thinking itself is the value.
