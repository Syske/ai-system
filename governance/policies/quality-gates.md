# Quality Gates

This document defines the quality gates that every component in the
repository must pass. These gates are enforced by `tools/repo-lint.py`
and by the repository-governor Skill.

> **Naming disambiguation (G5)**: this file governs the **asset-repo lint
gates** (SKILL.md structure / duplication / dependencies, enforced by
repo-lint.py). It is **NOT** the workflow runtime readiness gate — that one
lives in each `workflows/*.md` Exit Criteria and the runtime phase gates
(e.g. prepare Phase 7 Readiness Assessment). Same word, different meaning;
do not conflate them.

---

## Gate 1: Structural Integrity

| Check | Scope | Failure |
|---|---|---|
| SKILL.md exists | Every Skill | Missing entrypoint |
| YAML frontmatter present | Every SKILL.md | Missing frontmatter |
| `name:` matches directory name | Every SKILL.md | Name mismatch |
| `description:` present | Every SKILL.md | Missing description |
| workflow.md exists (if SKILL.md > 80 lines) | Skills > 80 lines | Missing workflow |
| No orphaned files (files not referenced by any SKILL.md) | All files | Orphan detected |

## Gate 2: Content Quality

| Check | Scope | Failure |
|---|---|---|
| No single file exceeds 1000 lines (aggregated reference files exempt) | Per Skill | Skill exceeds limit |
| No Maven commands (`mvn ` strings) | Non-java-maven skills | Prohibited command |
| No absolute paths (`C:\`, `/home/`, `/usr/`) | All files | Hardcoded path |
| No hardcoded project names | All files | Non-generic content |
| Description 100-1024 characters | Every SKILL.md | Invalid length |
| At least 3 trigger phrases in description | Every SKILL.md | Insufficient triggers |

## Gate 3: Dependency Integrity

| Check | Scope | Failure |
|---|---|---|
| All Skill references exist in `ai-system/skills/` | All files referencing skills | Broken reference |
| No circular dependencies | Skill dependency graph | Cycle detected |
| Foundation Layer (L1) depends only on L1 | java-maven, codegraph-helper, karpathy | Layer violation |
| Test Layer (L2) depends only on L1-Foundation | mock-test | Layer violation |

## Gate 4: Duplication

| Check | Scope | Failure |
|---|---|---|
| No checklist duplication with `ai-system/skills/*/checklists.md` | All checklists.md | Duplicate detected |
| No playbook content duplication | All skill files | Duplicate detected |
| No template content duplication | All skill files | Duplicate detected |

## Gate 5: Documentation

| Check | Scope | Failure |
|---|---|---|
| Stopping conditions defined | Every SKILL.md | Missing stop conditions |
| Delegation documented | Every SKILL.md | Missing delegation |
| At least 3 workflow stages | Every workflow.md | Insufficient stages |

---

## Gate Severity

| Severity | Meaning | Action |
|---|---|---|
| **BLOCKER** | Must fix before merge | Linter exit code 2 |
| **ERROR** | Should fix before merge | Linter exit code 1 |
| **WARNING** | Should fix, but not blocking | Linter exit code 0 with report |
| **INFO** | Suggestion for improvement | Linter reports only |

---

## Writing a Gate That Can Be Proven to Fail

A gate that has never been observed to fail is indistinguishable from a gate
that is silently broken. **Passing output is not evidence that a gate works** —
only a *deliberately violated* fixture is.

ai-system has hit this failure class repeatedly (three times in 2026-09 alone:
`proposal-audit` globbing `P*.md` instead of `rglob`, `path-audit` not checking
references inside `reports/`, `check_outputs_consistency` returning early when
its extracted list was empty). Each looked green while enforcing nothing.

### Rule 0 — Audit the coverage before trusting it

Count how many test files reference each check under `tools/checks/`. A check
with **zero** references has never been observed to fire, regardless of how
clean the real repository looks.

Measured 2026-09-29: `checks/adr.py` (numbering / status / date / required
sections / continuity / README registration, six rules) had no test at all —
and was structurally untestable, because it hardcoded its directory instead of
accepting an injectable `root` like every other check. A gate that cannot be
pointed at a broken fixture cannot be proven to work.

### Rule 1 — Every gate ships with a negative test

For each check, construct a fixture that violates **only** that rule and assert
the gate fires. A test suite with only positive cases proves nothing about the
gate; it proves the fixture is well-formed.

Cover both directions where the rule is directional: if `A ⊆ B` is an error,
assert that an `A` outside `B` errors **and** that an uncovered `B` is
**not** reported. The second half is what stops someone "fixing" a deliberately
one-way check into a stricter, wrong one.

### Rule 2 — Prove each gate by short-circuiting it, one at a time

Mutation-check the gate: disable exactly one check, re-run the negative tests,
and confirm the corresponding test **fails**. Then restore and confirm the suite
is green again. Do this per gate, not once for the module.

```bash
# 1. neuter one check
#    e.g. `if ref not in by_id:` → `if False and ref not in by_id:`
# 2. the matching negative test MUST fail
python3 -m unittest cli.tests.test_phase_contract   # expect FAILED
# 3. restore, expect green
```

**The short-circuit itself must be verified.** A mutation that still leaves the
suite green means either the gate has no negative test, or the mutation did not
actually disable it. A real instance: neutering a check via
`outputs = _workflow_outputs(body) or ["*"]` left every test passing, because
the wildcard made the "is this artifact declared?" predicate match everything.
The mutation looked like it disabled the gate; it actually inverted it. Real
neutering means removing the branch, not feeding it data that makes it pass.

### Rule 3 — Gate code needs the same specification rigor as the code it checks

Most gate bugs are **detail assumptions**, not logic errors. Observed classes:

| Assumption | Symptom |
|---|---|
| A regex without `re.M` where the subject is multi-line | Every row silently unmatched; the gate reports nothing |
| Resolving a path from the wrong source (guessing instead of reading the authority) | Whole check reports false positives, or none |
| Reading a YAML scalar without unescaping it | Values with embedded quotes never match their own grammar |

When a new gate reports implausible results — every row failing, or none —
suspect its extraction before suspecting the data it reads. A gate that has
never been run against the real repository is unverified regardless of how many
fixtures pass.

### Checklist before shipping a gate

- [ ] Each check has a negative fixture that violates only that rule
- [ ] Directional rules assert the non-error direction too
- [ ] Each gate short-circuited individually, confirming the matching test fails
- [ ] Gate run against the real repository (a "real repo is clean" assertion)
- [ ] Extraction logic verified against the real file format, not an idealised one

