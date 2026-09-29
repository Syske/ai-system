#!/usr/bin/env python3
"""ADR gate tests (check.py item 8).

This gate had **no negative test at all** — it was the one check under
`tools/checks/` whose rules could never be observed to fire, which is exactly
the failure class `governance/policies/quality-gates.md`
§ "Writing a Gate That Can Be Proven to Fail" exists to prevent.

Enabling this test also required making `check_adr` accept an injectable
`root` (it previously hardcoded the module-level `_RFC_DIR`, so it could only
ever run against the real repository — a gate that cannot be pointed at a
broken fixture is a gate that cannot be proven to work).

Covers:
- a clean two-ADR repository passes
- bad file name → ERROR
- missing status → ERROR
- invalid status → ERROR
- missing date → ERROR
- missing required section → WARN
- numbering gap → WARN
- unregistered ADR → ERROR
- the real repository has zero findings

Run:
    python -m unittest cli.tests.test_checks_adr
"""

import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "tools"))
sys.path.insert(0, str(REPO_ROOT))

from checks.adr import check_adr  # noqa: E402
from checks.base import Checker  # noqa: E402

GOOD = """# ADR-{num}: {title}

Status: Accepted

Date: 2026-01-0{num}

## Context

x

## Decision

x

## Rationale

x

## Consequences

x
"""


class AdrFixture(unittest.TestCase):
    def setUp(self):
        self._td = tempfile.TemporaryDirectory()
        self.root = Path(self._td.name)
        self.rfc = self.root / "rfc"
        self.rfc.mkdir()
        self.write_readme(1, 2)
        self.write_adr(1, "One")
        self.write_adr(2, "Two")

    def tearDown(self):
        self._td.cleanup()

    def write_readme(self, *nums):
        """Mirror the real rfc/README.md row shape:
        `| ADR-0001 | Title | Status |` (no link, no `ADR` header cell)."""
        titles = {1: "One", 2: "Two", 3: "Three"}
        rows = "\n".join(
            f"| ADR-{n:04d} | {titles.get(n, 'X')} | Accepted |" for n in nums
        )
        (self.rfc / "README.md").write_text(
            f"| ADR | Title | Status |\n|---|---|---|\n{rows}\n",
            encoding="utf-8",
        )

    def write_adr(self, num, title, text=None):
        (self.rfc / f"ADR-{num:04d}-{title.lower()}.md").write_text(
            text or GOOD.format(num=num, title=title), encoding="utf-8"
        )

    def run_gate(self):
        c = Checker()
        check_adr(c, root=self.root)
        return c


class TestBaseline(AdrFixture):
    def test_clean_repo_passes(self):
        c = self.run_gate()
        self.assertEqual(c.errors, [], c.errors)
        self.assertEqual(c.warnings, [], c.warnings)


class TestErrors(AdrFixture):
    def test_bad_file_name_errors(self):
        (self.rfc / "ADR-1-bad.md").write_text(
            GOOD.format(num=1, title="Bad"), encoding="utf-8"
        )
        c = self.run_gate()
        self.assertTrue(
            any("file name must match" in e for e in c.errors), c.errors
        )

    def test_missing_status_errors(self):
        self.write_adr(
            1, "One", GOOD.format(num=1, title="One").replace("Status: Accepted\n", "")
        )
        c = self.run_gate()
        self.assertTrue(
            any("missing status" in e for e in c.errors), c.errors
        )

    def test_invalid_status_errors(self):
        self.write_adr(
            1, "One",
            GOOD.format(num=1, title="One").replace("Accepted", "Whatever"),
        )
        c = self.run_gate()
        self.assertTrue(
            any("invalid status" in e for e in c.errors), c.errors
        )

    def test_missing_date_errors(self):
        self.write_adr(
            1, "One",
            GOOD.format(num=1, title="One").replace("Date: 2026-01-01\n", ""),
        )
        c = self.run_gate()
        self.assertTrue(any("missing date" in e for e in c.errors), c.errors)

    def test_unregistered_adr_errors(self):
        # ADR-0003 exists on disk but not in the README table
        self.write_adr(3, "Three")
        c = self.run_gate()
        self.assertTrue(
            any("not registered" in e for e in c.errors), c.errors
        )


class TestWarnings(AdrFixture):
    def test_numbering_gap_warns(self):
        # A gap needs a *skipped* number: adding ADR-0003 keeps 1..3
        # continuous. ADR-0004 alone leaves 3 missing.
        self.write_adr(4, "Four")
        self.write_readme(1, 2, 4)
        c = self.run_gate()
        self.assertTrue(
            any("numbering gap" in w and "3" in w for w in c.warnings),
            c.warnings,
        )

    def test_missing_section_warns(self):
        self.write_adr(
            1, "One",
            GOOD.format(num=1, title="One").replace("## Rationale\n\nx\n\n", ""),
        )
        c = self.run_gate()
        self.assertTrue(
            any("missing '## " in w for w in c.warnings), c.warnings
        )


class TestRealRepo(unittest.TestCase):
    def test_real_repo_is_clean(self):
        c = Checker()
        check_adr(c, root=REPO_ROOT)
        self.assertEqual(c.errors, [], f"真实仓库 ADR 错误: {c.errors}")


if __name__ == "__main__":
    unittest.main()
