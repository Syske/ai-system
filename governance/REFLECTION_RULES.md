# Reflection Rules

Version: 1.0

---

## Purpose

Every Workflow completion must include a Reflection phase.

Reflection ensures continuous quality improvement without requiring architectural changes.

Reflection outputs recommendations only. It never modifies code automatically.

---

## Iron Law

```
EVERY WORKFLOW MUST REFLECT BEFORE EXIT
```

No Workflow may declare completion without executing Reflection.

---

## Reflection Checklist

At the end of every Workflow, evaluate:

1. **Simpler Implementation**: Could this have been implemented with fewer files, fewer changes, or less complexity?

2. **Code Duplication**: Does any new code duplicate existing functionality in the project?

3. **Standards Compliance**: Did any deviation from the Applied Standards occur?

4. **Over-Engineering**: Was any unnecessary abstraction, generic framework, or future-proofing introduced?

5. **Completeness**: Are any acceptance criteria, edge cases, or documentation items incomplete?

---

## Output Format

Reflection generates a structured report:

```markdown
## Reflection Report

### Assessment

| Question | Answer | Evidence |
|---|---|---|
| Simpler implementation possible? | Yes/No | ... |
| Code duplication introduced? | Yes/No | ... |
| Standards violated? | Yes/No | ... |
| Over-engineering present? | Yes/No | ... |
| Anything incomplete? | Yes/No | ... |

### Recommendations

(Only if answers above are "Yes")

- ...
```

---

## Rules

- Reflection outputs **recommendations only**
- Reflection **never** modifies code
- Reflection **never** blocks Workflow completion
- Recommendations may be acted on in a future task or dismissed by the user
- Reflection is recorded in the Completion Report

---

## Scope

Applies to all Workflows:

- spec
- dev-setup
- prepare
- develop
- bugfix
- review
- verify
- release
- analysis
- knowledge
- bootstrap

Every Runtime Template must include a Reflection step before the Completion phase.
