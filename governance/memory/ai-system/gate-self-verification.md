# Gate Self-Verification Memory

Lessons from establishing the Phase Contract gate (P76 S1, 2026-09-29). These
are the **evidence** behind the rules in
`governance/policies/quality-gates.md` § "Writing a Gate That Can Be Proven to
Fail"; the rules live there, the instances live here.

---

## [AI System] A Gate That Has Never Failed Is Indistinguishable From a Broken One

Context:

Adding `tools/checks/phase_contract.py` (8 checks) with
`cli/tests/test_phase_contract.py` (15 cases). All 15 passed on the first
green run, including 6 negative fixtures — one per ERROR-level check.

Problem:

Passing output proves the fixtures are well-formed. It proves nothing about
whether the gate enforces anything. This is not hypothetical: three gates in
this repository had been enforcing nothing while reporting clean —
`proposal-audit` globbing `P*.md` where `rglob` was needed (so 66 proposals
would have become invisible to Status / index / open-item checks),
`path-audit` never checking references inside `reports/`, and
`check_outputs_consistency` returning early when its extracted list was empty
(so deleting a runtime's whole `# Outputs` section silently disabled the
workflow↔runtime artifact contract).

Scope:

Any new or modified check under `tools/checks/`.

Lesson:

A gate is unverified until it has been observed to fail. Pass-only test suites
cannot distinguish a working gate from a broken one.

Solution:

Short-circuit each gate individually and confirm the matching negative test
fails. Observed results for this gate:

| Neutered check | Negative tests failing |
|---|---|
| C1 unknown phase ref | 1 |
| C2 `.passed` without `pass_criterion` | 1 |
| C3 wild artifact | 1 |
| C5 contract/runtime id-set mismatch | 1 |
| C6 duplicate id | 1 |
| C7 unparseable activation | 1 |

---

## [AI System] The Short-Circuit Mutation Must Itself Be Verified

Context:

Attempting to prove the C3 check (a Phase must not declare an artifact outside
the workflow's `## Outputs`) by neutering it.

Problem:

The first mutation was
`outputs = _workflow_outputs(body) or ["*"]` — with a wildcard standing in for
"everything is allowed". Every test still passed, which looked like a broken
negative test. It was the opposite: the predicate being checked is
"is this artifact among the declared outputs", and `"*"` as an output entry
made `any(...)` match **every** artifact. The mutation had inverted the gate
rather than disabled it.

A short-circuit that leaves the suite green has two possible causes — a gate
with no negative test, or a mutation that does not actually remove the check —
and they need different fixes. Real neutering means removing the branch
(`for pid, entry in ():`), not feeding it data that makes it pass.

Scope:

Any gate mutation used as evidence of test coverage.

Lesson:

A short-circuit that leaves the suite green is ambiguous — it means either the
gate has no negative test, or the mutation did not actually disable the gate.
Check which before changing the test.

Solution:

When a short-circuit leaves tests green, re-read the mutation and confirm it
removes the branch before concluding the negative test is missing.

---

## [AI System] Gate Bugs Are Detail Assumptions About the File Format

Context:

First run of the new gate reported 18 errors — every workflow claiming all of
its Phases did not exist in its runtime.

Problem:

Three independent detail assumptions, none of them logic errors:

1. `_PHASE_HEADING` was compiled **without `re.M`**. Against multi-line file
   content `^` anchors only at the string start, so zero headings matched. The
   gate then reported every contract Phase as absent from the runtime.
2. The runtime path was read from the workflow's **frontmatter**. The
   authoritative source is `config/workflows/<name>.yaml`; the frontmatter has
   no `runtime:` key at all, so the lookup fell through to a fallback that
   never matched.
3. `_parse_phases` stripped the surrounding quotes of a YAML double-quoted
   scalar but left the backslash escapes inside it, so an expression stored as
   `phase(\"6.5\").completed` was compared as `phase(\"6.5\")...` and never
   matched its own grammar.

Pattern:

| Assumption | Symptom |
|---|---|
| Regex flags vs. the subject's actual shape | Every row unmatched; gate reports nothing |
| Resolving a value from a guessed source instead of the authority | Whole check reports false results, or none |
| Reading a structured scalar without decoding it | Values with embedded metacharacters never match |

Scope:

Gates that extract data from files (frontmatter, YAML, markdown, CSV).

Lesson:

Most gate bugs are wrong assumptions about the file format, not wrong logic.
Implausible output means suspect the extraction first.

Solution:

When a new gate produces implausible output — every row failing, or none —
suspect its **extraction** before suspecting the data it reads. A gate that has
never run against the real repository is unverified no matter how many fixtures
pass. The first real-repo run of this gate found two genuine content defects
that no fixture would have:

- A runtime's Phase 1 and Phase 2 headings had **no title at all**, so the
  prompt skeleton's heading pattern (which requires an em dash) did not match
  them and those phases were **invisible in the agent's prompt**.
- A third heading used a space instead of the em dash, failing the same pattern.

Both were invisible until a machine check compared declared ids against actual
headings.
