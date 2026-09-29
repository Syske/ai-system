#!/usr/bin/env python3
"""Phase Contract gate tests (check.py item 16, P76).

Every gate ships with a **negative test**: a fixture that violates it and
asserts the gate fires. A gate that cannot be proven to fail may silently
stop working — this repository has hit that class of defect three times in
2026-09 alone:

- `proposal-audit` globbing `P*.md` instead of `rglob` (P74 §5.2-7)
- `path-audit` not checking references inside `reports/` (P74 §1.2 F4)
- `check_outputs_consistency` returning early when `rt_items` is empty

Covers:
- C1 activation references an undeclared phase
- C2 `phase("X").passed` where X has no pass_criterion
- C3 a Phase declares an artifact absent from `## Outputs`
- C4 a workflow Output declared by no Phase → NOT reported
- C5 contract ids != runtime Phase heading ids (both directions)
- C6 duplicate id / empty name
- C7 activation not parseable (natural language, unknown mode key)
- real repository has zero findings

Run:
    python -m unittest cli.tests.test_phase_contract
"""

import shutil
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "tools"))
sys.path.insert(0, str(REPO_ROOT))

from checks.base import Checker  # noqa: E402
from checks.phase_contract import check_phase_contract  # noqa: E402

RUNTIME_HEAD = """# Runtime: Demo

Extends:

- runtime-base.md

---

## Purpose

Demo runtime for the phase-contract gate tests.

# Phase 1 — First
Do the first thing.

# Phase 2 — Second
Do the second thing.
"""


def _workflow(phases_yaml, outputs, runtime="templates/runtime/runtime-demo.md"):
    return f"""---
name: demo
description: Demo workflow.
workflow:
  inputs:
    required: []
{phases_yaml}  outputs:
    base: "outputs/demo/{{yyMMdd}}-x/"
---
# Workflow: Demo

## Purpose

Demo.

## Runtime

- {runtime}

## Outputs

{outputs}

## Exit Criteria

Success:

- done

## Next

- None
"""


class PhaseContractFixture(unittest.TestCase):
    """Build a throwaway repo root with one workflow + its runtime."""

    def setUp(self):
        self._td = tempfile.TemporaryDirectory()
        self.root = Path(self._td.name)
        (self.root / "workflows").mkdir()
        (self.root / "templates" / "runtime").mkdir(parents=True)
        (self.root / "config" / "workflows").mkdir(parents=True)
        (self.root / "templates" / "runtime" / "runtime-demo.md").write_text(
            RUNTIME_HEAD, encoding="utf-8"
        )
        (self.root / "config" / "workflows" / "demo.yaml").write_text(
            "version: 1\nname: demo\n"
            "workflow: workflows/demo.md\n"
            "runtime: templates/runtime/runtime-demo.md\n",
            encoding="utf-8",
        )

    def tearDown(self):
        self._td.cleanup()

    def run_gate(self):
        c = Checker()
        check_phase_contract(c, root=self.root)
        return c

    def write(self, phases_yaml, outputs="- report.md"):
        (self.root / "workflows" / "demo.md").write_text(
            _workflow(phases_yaml, outputs), encoding="utf-8"
        )


class TestBaseline(PhaseContractFixture):
    def test_valid_contract_passes(self):
        self.write(
            "  phases:\n"
            '    - id: "1"\n      name: "First"\n'
            '    - id: "2"\n      name: "Second"\n'
            '      activation: "WHEN mode.phases ∋ second"\n'
        )
        c = self.run_gate()
        self.assertEqual(c.errors, [], c.errors)

    def test_real_repo_is_clean(self):
        """Real repository currently satisfies the contract."""
        c = Checker()
        check_phase_contract(c, root=REPO_ROOT)
        self.assertEqual(c.errors, [], f"真实仓库不应有 phase 契约错误: {c.errors}")


class TestC1UnknownPhaseRef(PhaseContractFixture):
    def test_reference_to_undeclared_phase_errors(self):
        self.write(
            "  phases:\n"
            '    - id: "1"\n      name: "First"\n'
            '    - id: "2"\n      name: "Second"\n'
            '      activation: "WHEN phase(\\"9.9\\").completed"\n'
        )
        c = self.run_gate()
        self.assertTrue(
            any("9.9" in e and "not declared" in e for e in c.errors),
            c.errors,
        )


class TestC2PassedRequiresCriterion(PhaseContractFixture):
    def test_passed_without_pass_criterion_errors(self):
        self.write(
            "  phases:\n"
            '    - id: "1"\n      name: "First"\n'
            '    - id: "2"\n      name: "Second"\n'
            '      activation: "WHEN phase(\\"1\\").passed"\n'
        )
        c = self.run_gate()
        self.assertTrue(
            any("pass_criterion" in e for e in c.errors), c.errors
        )

    def test_passed_with_pass_criterion_passes(self):
        self.write(
            "  phases:\n"
            '    - id: "1"\n      name: "First"\n'
            '      pass_criterion: "Status = PASS"\n'
            '    - id: "2"\n      name: "Second"\n'
            '      activation: "WHEN phase(\\"1\\").passed"\n'
        )
        c = self.run_gate()
        self.assertEqual(c.errors, [], c.errors)


class TestC3WildArtifact(PhaseContractFixture):
    def test_declared_artifact_outside_outputs_errors(self):
        self.write(
            "  phases:\n"
            '    - id: "1"\n      name: "First"\n'
            '      declares: ["wild-artifact.md"]\n'
            '    - id: "2"\n      name: "Second"\n'
        )
        c = self.run_gate()
        self.assertTrue(
            any("wild-artifact" in e for e in c.errors), c.errors
        )

    def test_declared_artifact_inside_outputs_passes(self):
        self.write(
            "  phases:\n"
            '    - id: "1"\n      name: "First"\n'
            '      declares: ["report.md"]\n'
            '    - id: "2"\n      name: "Second"\n'
        )
        c = self.run_gate()
        self.assertEqual(c.errors, [], c.errors)


class TestC4ReverseNotChecked(PhaseContractFixture):
    def test_output_declared_by_no_phase_is_not_an_error(self):
        """Many workflows are 'many Phases -> few Outputs'; the reverse
        direction is intentionally unchecked (policy §5.2)."""
        self.write(
            "  phases:\n"
            '    - id: "1"\n      name: "First"\n'
            '    - id: "2"\n      name: "Second"\n',
            outputs="- report.md\n- extra-summary.md",
        )
        c = self.run_gate()
        self.assertEqual(c.errors, [], c.errors)


class TestC5IdSetMismatch(PhaseContractFixture):
    def test_runtime_phase_missing_from_contract_errors(self):
        self.write(
            "  phases:\n"
            '    - id: "1"\n      name: "First"\n'
        )
        c = self.run_gate()
        self.assertTrue(
            any("'2'" in e and "missing from the frontmatter" in e
                for e in c.errors),
            c.errors,
        )

    def test_contract_phase_missing_from_runtime_errors(self):
        self.write(
            "  phases:\n"
            '    - id: "1"\n      name: "First"\n'
            '    - id: "2"\n      name: "Second"\n'
            '    - id: "7"\n      name: "Ghost"\n'
        )
        c = self.run_gate()
        self.assertTrue(
            any("'7'" in e and "do not exist in runtime" in e
                for e in c.errors),
            c.errors,
        )


class TestC6IdUniqueness(PhaseContractFixture):
    def test_duplicate_id_errors(self):
        self.write(
            "  phases:\n"
            '    - id: "1"\n      name: "First"\n'
            '    - id: "1"\n      name: "First Again"\n'
            '    - id: "2"\n      name: "Second"\n'
        )
        c = self.run_gate()
        self.assertTrue(
            any("duplicate phase id" in e for e in c.errors), c.errors
        )

    def test_empty_name_errors(self):
        self.write(
            "  phases:\n"
            '    - id: "1"\n      name: "First"\n'
            '    - id: "2"\n      name: ""\n'
        )
        c = self.run_gate()
        self.assertTrue(any("empty name" in e for e in c.errors), c.errors)


class TestC7UnparseableActivation(PhaseContractFixture):
    def test_natural_language_errors(self):
        self.write(
            "  phases:\n"
            '    - id: "1"\n      name: "First"\n'
            '    - id: "2"\n      name: "Second"\n'
            '      activation: "WHEN MR is enabled and the branch was committed'
            ' in Phase 1"\n'
        )
        c = self.run_gate()
        self.assertTrue(
            any("not parseable" in e or "must be" in e for e in c.errors),
            c.errors,
        )

    def test_unknown_mode_key_errors(self):
        self.write(
            "  phases:\n"
            '    - id: "1"\n      name: "First"\n'
            '    - id: "2"\n      name: "Second"\n'
            '      activation: "WHEN mode.no_such_key"\n'
        )
        c = self.run_gate()
        self.assertTrue(
            any("unknown mode key" in e for e in c.errors), c.errors
        )

    def test_conjunction_of_two_atoms_passes(self):
        self.write(
            "  phases:\n"
            '    - id: "1"\n      name: "First"\n'
            '    - id: "2"\n      name: "Second"\n'
            '      activation: "WHEN mode.phases ∋ second ∧'
            ' phase(\\"1\\").completed"\n'
        )
        c = self.run_gate()
        self.assertEqual(c.errors, [], c.errors)


if __name__ == "__main__":
    unittest.main()
