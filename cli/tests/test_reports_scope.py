#!/usr/bin/env python3
"""reports/ ownership gate tests (P74 S1, check.py item 17).

The gate exists because a business artifact once entered `reports/` and no gate
complained: `proposal-policy` §6 required a report to be *registered*, never to
*belong* there. The artifact was indexed, so every existing check passed.

Every check ships with a **negative test** — a fixture that violates it and
asserts the gate fires. A gate never observed to fail may be silently broken
(see `governance/policies/quality-gates.md`
§ "Writing a Gate That Can Be Proven to Fail").

Covers:
- S1 an entry matching no category → ERROR
- S2 a workflow's business output directory → ERROR with the right destination
- S3 a directory outside the two directory categories → ERROR
- every legitimate category passes (including the lowercase / prefix variants)
- a leading workflow name alone is NOT the signal (`analysis-*` is a category)
- the real repository has zero findings

Run:
    python -m unittest cli.tests.test_reports_scope
"""

import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "tools"))
sys.path.insert(0, str(REPO_ROOT))

from checks.base import Checker  # noqa: E402
from checks.reports_scope import check_reports_scope  # noqa: E402

REGISTRY = """version: 1
workflows:
  prepare: config/workflows/prepare.yaml
  bugfix: config/workflows/bugfix.yaml
  analysis: config/workflows/analysis.yaml
  spec: config/workflows/spec.yaml
"""


class ReportsScopeFixture(unittest.TestCase):
    """A throwaway repo root with an empty reports/ and a small registry."""

    def setUp(self):
        self._td = tempfile.TemporaryDirectory()
        self.root = Path(self._td.name)
        (self.root / "reports").mkdir()
        cfg = self.root / "config"
        cfg.mkdir()
        (cfg / "workflow-registry.yaml").write_text(
            REGISTRY, encoding="utf-8"
        )

    def tearDown(self):
        self._td.cleanup()

    def run_gate(self):
        c = Checker()
        check_reports_scope(c, root=self.root)
        return c

    def add_file(self, name):
        (self.root / "reports" / name).write_text("x", encoding="utf-8")

    def add_dir(self, name):
        (self.root / "reports" / name).mkdir()


class TestS1UncategorisedEntry(ReportsScopeFixture):
    def test_unmatched_file_errors(self):
        self.add_file("some-random-notes.md")
        c = self.run_gate()
        self.assertTrue(
            any("some-random-notes.md" in e for e in c.errors), c.errors
        )

    def test_business_prepare_directory_errors(self):
        """The 2026-09-28 incident, reproduced."""
        self.add_dir("prepare-beecount-2608")
        c = self.run_gate()
        self.assertEqual(len(c.errors), 1, c.errors)
        self.assertIn("outputs/prepare/", c.errors[0])
        self.assertIn("beecount", c.errors[0])

    def test_index_files_exempt(self):
        self.add_file("README.md")
        self.add_file("PROPOSALS.md")
        c = self.run_gate()
        self.assertEqual(c.errors, [], c.errors)


class TestS2WorkflowOutputHeuristic(ReportsScopeFixture):
    def test_workflow_name_alone_is_not_a_signal(self):
        """`analysis-*` is both a category and a workflow name."""
        self.add_dir("analysis-2026-08-01-structure-governance")
        c = self.run_gate()
        self.assertEqual(c.errors, [], c.errors)

    def test_workflow_plus_project_suffix_errors(self):
        self.add_dir("bugfix-invoice-npe")
        c = self.run_gate()
        self.assertTrue(
            any("outputs/bugfix/" in e for e in c.errors), c.errors
        )

    def test_unregistered_lead_token_is_not_a_workflow_output(self):
        self.add_dir("zzz-not-a-workflow-x")
        c = self.run_gate()
        # still an error, but as S3 (directory outside the two categories),
        # not as a workflow-output claim
        self.assertTrue(
            all("outputs/zzz-not-a-workflow-x/" not in e for e in c.errors),
            c.errors,
        )


class TestS3DirectoryCategories(ReportsScopeFixture):
    def test_analysis_directory_passes(self):
        self.add_dir("analysis-2026-08-03-structure-workflows")
        c = self.run_gate()
        self.assertEqual(c.errors, [], c.errors)

    def test_skill_source_directory_passes(self):
        self.add_dir("skill-source-2026-08-17-wayfinder")
        c = self.run_gate()
        self.assertEqual(c.errors, [], c.errors)

    def test_other_directory_errors(self):
        """A directory that is neither a category nor a workflow's output.

        Uses `prepare-single` deliberately: a leading workflow name whose
        remainder carries no second hyphen, so S2's project-suffix heuristic
        does not match either. This is the only shape where S3 is the sole
        reporter — with `random-collection`, S1 also fires and S3 would be
        redundant.
        """
        self.add_dir("prepare-single")
        c = self.run_gate()
        self.assertEqual(len(c.errors), 1, c.errors)
        self.assertIn("prepare-single", c.errors[0])
        self.assertIn("analysis-<date>-<topic>/", c.errors[0])


class TestLegitimateCategories(ReportsScopeFixture):
    """Every category in proposal-policy §6.1 must be accepted."""

    def test_all_categories_pass(self):
        for name in (
            # proposals
            "P76-PHASE-CONTRACT.md",
            "SPOTLESS-FORMAT-GATE-PROPOSAL.md",
            # maintenance
            "MAINTENANCE-2026-09-28.md",
            "MAINTENANCE-2026-08-24-workflows.md",
            "DAILY-2026-08-08.md",
            "EXTENSIONS-MAINTENANCE-2026-08-13.md",
            # assessments (incl. lowercase variants)
            "ARCHITECTURE-ASSESSMENT-2026-07.md",
            "architecture-review-2026-07.md",
            "ADR-0009-COMPLIANCE-DIAGNOSIS-2026-08-13.md",
            "GAP-ASSESSMENT-2026-08-08-context.md",
            "wayfinder-value-reevaluation-2026-09-17.md",
            "WORKFLOW-OPTIMIZATION-REPORT-2026-07.md",
            "R4-HANDOVER-2026-09-23.md",
            "CACHE-OPTIMIZATION-2026-08-13.md",
            # incidents / migrations
            "INCIDENT-2026-09-24-ignored-state-wipe.md",
            "MIGRATION-PLAN-v2.md",
            # decisions / standards
            "VALUE-BURDEN-DECISION-skill-sync-2026-09-23.md",
            "EXTENSION-STANDARDS.md",
        ):
            with self.subTest(entry=name):
                self.setUp()
                self.add_file(name)
                c = self.run_gate()
                self.assertEqual(c.errors, [], f"{name}: {c.errors}")
                self.tearDown()

    def test_real_repo_is_clean(self):
        """Real repository currently satisfies the ownership rules."""
        c = Checker()
        check_reports_scope(c, root=REPO_ROOT)
        self.assertEqual(
            c.errors, [], f"真实仓库不应有归属错误: {c.errors}"
        )


if __name__ == "__main__":
    unittest.main()
