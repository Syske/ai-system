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

## Self-Evaluation (Optional Quality Score)

For non-trivial work, supplement the checklist with a 5-axis self-rating.
This is a deliberate reflection step that catches omissions and flags
overconfidence before the user has to.

| Axis | Question | What it catches |
|---|---|---|
| **Accuracy** | Are the facts, claims, and outputs correct? | Hallucinations, wrong names, incorrect syntax, false statements |
| **Completeness** | Did it cover everything the user asked for? | Missed edge cases, unhandled errors, forgotten requirements |
| **Clarity** | Is the explanation understandable and well-structured? | Confusing explanations, jargon, missing context |
| **Actionability** | Can the user act on the output immediately? | Vague suggestions, missing steps, no verification path |
| **Conciseness** | Did it use the minimum words/tokens needed? | Redundancy, over-explanation, filler |

Scale: 5 = exceptional, 4 = good, 3 = adequate, 2 = weak, 1 = poor.

**Evidence rule:** every score below 5 MUST cite specific evidence — show the
gap, don't just name it. A score of 3 cannot say "could be better"; it must say
exactly what is missing or wrong.

Self-evaluation is optional and does not replace the mandatory Reflection
checklist above.

---

## Rules

- Reflection outputs **recommendations only**
- Reflection **never** modifies code
- Reflection **never** blocks Workflow completion
- Recommendations may be acted on in a future task or dismissed by the user
- Reflection is recorded in the Completion Report
- Reflection MUST be persisted to `logs/` as a per-run diagnostic record
  (template `templates/runtime/runtime-diagnostic-log.md`) before the run is declared
  done — the on-disk copy makes any past run traceable after the session ends.

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
