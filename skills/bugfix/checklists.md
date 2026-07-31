# Checklists

---

## Bug Understanding Checklist

Use during Stage 1.

- [ ] Symptom captured verbatim (error message, wrong output, exception)
- [ ] Environment documented (input, state, configuration)
- [ ] Reproduction steps documented
- [ ] Bug is reproducible? (yes / intermittent / unknown)

---

## Evidence Checklist

Use during Stage 2.

- [ ] Stack trace captured (first application frame identified)
- [ ] Test output captured (expected vs actual)
- [ ] Compilation error captured (file, line, symbol)
- [ ] Logs collected (10 lines before/after)
- [ ] `git diff` checked for recent changes
- [ ] `git log --oneline -10` reviewed
- [ ] `git blame` checked for affected lines
- [ ] Evidence sufficiency: sufficient / ask user

---

## Hypothesis Checklist

Use during Stages 7-8.

- [ ] At least 2 hypotheses generated
- [ ] Each hypothesis has confirm evidence prediction
- [ ] Each hypothesis has refute evidence prediction
- [ ] Hypotheses ranked by likelihood
- [ ] Cheapest validation method chosen for each
- [ ] Eliminated hypotheses documented
- [ ] Validated hypothesis has clear evidence

---

## Repair Checklist

Use during Stages 10-11.

- [ ] Root cause identified to file:line
- [ ] Repair is the smallest possible change
- [ ] Repair addresses root cause, not symptom
- [ ] No unrelated changes introduced
- [ ] Side effects checked
- [ ] Skill dependencies identified (java-maven, mock-test, etc.)
- [ ] Single commit worth of changes

---

## Validation Checklist

Use during Stage 12.

- [ ] Exact symptom no longer reproduces
- [ ] Failing test passes
- [ ] Smallest validation scope chosen
- [ ] Validation result documented (pass/fail)

---

## Regression Checklist

Use during Stage 13.

- [ ] Tests in affected module pass
- [ ] Tests in dependent modules pass
- [ ] Regression failure is pre-existing? (if failing, check before fix)
- [ ] Compilation succeeds
- [ ] No new warnings introduced

---

## Completion Checklist

Use during Stage 14.

- [ ] Root cause documented
- [ ] Repair method documented
- [ ] Evidence documented
- [ ] Validation documented
- [ ] Changes scoped to affected files only
- [ ] No follow-up issues created
