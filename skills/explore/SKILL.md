---
name: explore
description: OpenSpec-aware exploration support for the aic-explore command. Use when running aic-explore in OpenSpec workspace to check active changes, reference artifacts naturally, and offer to capture decisions. Loaded by the aic-explore command; not for standalone use.
---

# OpenSpec Exploration Support

Supports the `aic-explore` command: thinking-partner exploration with
OpenSpec awareness. This skill carries the OpenSpec-specific methodology;
the command carries the stance.

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
   - `openspec/changes/<name>/tasks.md`
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
   | New work identified | `tasks.md` |
   | Assumption invalidated | relevant artifact |

   Example offers:
   - "This is a design decision. Want to record it in design.md?"
   - "This is a new requirement. Want to add it to specs?"
   - "This changes the scope. Want to update the proposal?"

4. **User decides** — offer and continue. Don't pressure. Don't auto-capture.
