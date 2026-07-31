# Decision Rules

## Activation Decisions

| Condition | Decision |
|---|---|
| User says "create a skill" | Activate |
| User says "generate a skill" | Activate |
| User describes a repeatable multi-step procedure | Activate |
| User asks to "formalize" or "standardize" a process | Activate |
| User provides documentation and wants a Skill from it | Activate |
| User asks for a prompt template | DO NOT activate |
| User asks for a one-shot script | DO NOT activate |
| User asks for documentation-only output | DO NOT activate |
| User's task is already covered by an existing Skill | DO NOT activate; point to existing |

## Stopping Conditions

| Condition | Action |
|---|---|
| Purpose cannot be determined after 2 rounds of clarification | Stop, report "unable to determine purpose" |
| User rejects the outline | Stop |
| Validation fails after 3 fix cycles | Stop, report unresolved issues |
| User cancels | Stop |
| Overlapping Skill exists | Stop, point to existing Skill |
| Skill would exceed reasonable size without clear split plan | Stop, recommend splitting |

## Scope Narrowing

| Situation | Narrowing rule |
|---|---|
| User describes 3+ unrelated tasks | Split into 3+ Skills; ask for priority |
| Skill workflow has 8+ stages | Check if stages can be grouped or split |
| Multiple workflow patterns needed | Split; each Skill gets one pattern |
| Both script + documentation + background needed | Create scripts/, references/, keep SKILL.md clean |
| Skill references another Skill | Document the dependency in both Skills' descriptions |

## Skill Chaining

| Scenario | Action |
|---|---|
| New Skill needs to invoke Maven | Reference `java-maven` in description, not in workflow |
| New Skill needs test maintenance | Reference `mock-test` in description |
| New Skill shares checklists with an existing Skill | Extract shared checklists to a shared references/ file |
| New Skill should run after another Skill | Document ordering in both Skills' descriptions |

## Library Governance

| Scenario | Action |
|---|---|
| New Skill name matches an existing directory | Refuse; rename or merge |
| New Skill purpose overlaps 60%+ with existing | Refuse; extend existing instead |
| New Skill purpose overlaps 30-60% | Document relationship; may coexist with clear boundaries |
| New Skill dependencies form a cycle | Redesign; cycles are not allowed |
| All existing Skills use one directory format | New Skill must match exactly |
