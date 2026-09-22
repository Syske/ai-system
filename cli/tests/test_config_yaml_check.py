#!/usr/bin/env python3
"""Tests for `tools/checks/config_yaml.py` — config YAML must fail loud.

Background (2026-09-21): a hand edit inside a YAML block scalar (`- **…` — the
leading dash made `*` an alias) broke `config/maintenance.yaml`, and `check.py`
still reported PASS with exit 0. Declarative config is an input to nearly every
runtime, so a silent parse failure makes the runtime fall back to defaults and
the mistake surfaces much later — the P60 fail-loud principle applies.

Run:
    python -m unittest cli.tests.test_config_yaml_check
"""

import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "tools"))

from checks import Checker                       # noqa: E402
from checks import config_yaml as cy             # noqa: E402


class TestStrictLoad(unittest.TestCase):

    def _write(self, text):
        td = tempfile.TemporaryDirectory()
        path = Path(td.name) / "probe.yaml"
        path.write_text(text, encoding="utf-8")
        self.addCleanup(td.cleanup)
        return path

    def test_valid_document(self):
        data, error = cy.strict_load(self._write("a: 1\nb: [x, y]\n"))
        self.assertIsNone(error)
        self.assertEqual(data, {"a": 1, "b": ["x", "y"]})

    def test_broken_document_reports_line_and_column(self):
        data, error = cy.strict_load(self._write("a: 1\n  broken: [unclosed\n"))
        self.assertIsNone(data)
        self.assertIn("YAML parse error", error)
        self.assertIn("line", error)
        self.assertIn("column", error)

    def test_unreadable_reports_error(self):
        data, error = cy.strict_load(Path(tempfile.gettempdir()) / "no-such-file.yaml")
        self.assertIsNone(data)
        self.assertIn("unreadable", error)


class TestCheckerCases(unittest.TestCase):

    def _run(self, files: dict):
        td = tempfile.TemporaryDirectory()
        root = Path(td.name)
        for rel, text in files.items():
            path = root / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8")
        self.addCleanup(td.cleanup)

        original = cy.CONFIG_ROOT
        cy.CONFIG_ROOT = root
        try:
            c = Checker()
            cy.check_config_yaml(c)
        finally:
            cy.CONFIG_ROOT = original
        return c

    def test_block_scalar_breakage_is_reported(self):
        """The exact real-world failure: a list bullet inside a block scalar."""
        c = self._run({"maintenance.yaml": "notes: |\n  intro line\n- **bold**：x\n"})
        self.assertEqual(len(c.errors), 1, c.errors)
        self.assertIn("maintenance.yaml", c.errors[0])
        self.assertIn("YAML parse error", c.errors[0])

    def test_top_level_must_be_mapping(self):
        c = self._run({"menu.yaml": "- just\n- a list\n"})
        self.assertEqual(len(c.errors), 1, c.errors)
        self.assertIn("top level must be a mapping", c.errors[0])

    def test_empty_document_warns(self):
        c = self._run({"empty.yaml": "\n"})
        self.assertEqual(c.errors, [])
        self.assertEqual(len(c.warnings), 1, c.warnings)
        self.assertIn("empty YAML document", c.warnings[0])

    def test_nested_directories_are_scanned(self):
        c = self._run({"environments/local.yaml": "env: local\n",
                       "workflows/broken.yaml": "key: [oops\n"})
        self.assertEqual(len(c.errors), 1, c.errors)
        self.assertIn("workflows/broken.yaml", c.errors[0])

    def test_no_yaml_warns(self):
        c = self._run({"readme.txt": "not yaml\n"})
        self.assertEqual(c.errors, [])
        self.assertIn("no YAML files", c.warnings[0])

    def test_path_outside_repo_root_does_not_crash(self):
        """Gate robustness: an unusual-but-legit root must report, never raise."""
        c = self._run({"menu.yaml": "locale: zh\n"})
        self.assertEqual(c.errors, [])

    def test_healthy_config_passes(self):
        c = self._run({"menu.yaml": "locale: zh\nitems: [a, b]\n"})
        self.assertEqual(c.errors, [])
        self.assertEqual(c.warnings, [])


class TestRepositoryAndWiring(unittest.TestCase):

    def test_repository_config_is_healthy(self):
        c = Checker()
        cy.check_config_yaml(c)
        self.assertEqual(c.errors, [], c.errors)

    def test_check_is_wired_into_run_all(self):
        """Wiring guard: the gate must actually invoke this check."""
        source = (REPO_ROOT / "tools" / "checks" / "__init__.py").read_text(encoding="utf-8")
        self.assertIn("from .config_yaml import check_config_yaml", source)
        self.assertIn("check_config_yaml(c)", source)