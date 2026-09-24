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

class TestMaintenanceFindingsFormat(unittest.TestCase):
    """Root fix (2026-09-24): `last_findings` items are folded block scalars (`- >-`).

    Before this, items were multi-line PLAIN scalars and the file was broken three
    times (leading dash -> `*` alias; ASCII `: `; space-hash). Documenting the three
    terminators was symptom treatment: measured, the plain form has one LOUD failure
    (ScannerError, needs two colons) and two SILENT ones (a dict instead of a string;
    comment truncation) — silence is what survives review. A folded block scalar
    makes content lines literal, so the whole class of early terminators disappears.
    """

    PROSE = [
        "- 短横开头（原禁忌 1：会另起列表项）",
        "关键词A: B 值（原禁忌 2：半角冒号+空格 → 被当成嵌套映射）",
        "正文 # 行内井号（原禁忌 3：空格井号 → 注释截断）",
        "# 行首井号",
        "* 星号（未加引号时曾被解析为别名）",
        "% 百分号 · [中括号] · {花括号} · 引号 \"x\" 'y' · & 与号 · ! 叹号",
    ]

    def _load(self, text):
        td = tempfile.TemporaryDirectory()
        path = Path(td.name) / "maintenance.yaml"
        path.write_text(text, encoding="utf-8")
        self.addCleanup(td.cleanup)
        return cy.strict_load(path)

    def test_prose_that_used_to_break_the_file_is_now_literal(self):
        """块标量下：全部危险形态原样保留，结构不变。"""
        text = "last_findings:\n- >-\n" + "".join(f"  {line}\n" for line in self.PROSE)
        data, error = self._load(text)
        self.assertIsNone(error)
        self.assertEqual(len(data["last_findings"]), 1, data)
        item = data["last_findings"][0]
        for line in self.PROSE:
            self.assertIn(line, item)          # 零截断、零逃逸变形

    def test_plain_scalar_form_silently_mutates_or_fails(self):
        """对照（根因证据）：同样的散文用 plain scalar 承载 —— 半角冒号静默变 dict。"""
        data, error = self._load("last_findings:\n- 关键词A: B 值\n")
        self.assertIsNone(error, error)        # 连报错都没有
        self.assertIsInstance(data["last_findings"][0], dict)   # 散文被吃掉成映射

    def test_space_hash_plain_form_silently_truncates(self):
        """对照（根因证据）：空格井号在 plain scalar 下静默截断成注释。"""
        data, error = self._load("last_findings:\n- 正文 # 行内井号\n")
        self.assertIsNone(error, error)
        self.assertEqual(data["last_findings"][0], "正文")

    def test_repository_findings_use_folded_block_scalars(self):
        """迁移守卫：仓内每一项都必须以 `- >-` 引入（防退化回 plain scalar）。"""
        path = REPO_ROOT / "config" / "maintenance.yaml"
        text = path.read_text(encoding="utf-8")
        body = text.split("last_findings:", 1)[1]
        markers = {line.strip() for line in body.splitlines() if line.startswith("-")}
        self.assertEqual(markers, {"- >-"},
                         f"非折叠块标量的项: {sorted(markers)}")

        data, error = cy.strict_load(path)
        self.assertIsNone(error)
        findings = data["last_findings"]
        self.assertTrue(findings, "last_findings 为空")
        for item in findings:
            self.assertIsInstance(item, str)
            self.assertTrue(item.strip())

    def test_check_is_wired_into_run_all(self):
        """Wiring guard: the gate must actually invoke this check."""
        source = (REPO_ROOT / "tools" / "checks" / "__init__.py").read_text(encoding="utf-8")
        self.assertIn("from .config_yaml import check_config_yaml", source)
        self.assertIn("check_config_yaml(c)", source)