#!/usr/bin/env python3
"""Tests for `tools/jdt-profile-eval.py`（P65 Option B 评估器）。

仅测纯函数（profile 覆盖、统计解析、超长行扫描）——java 干跑本身属环境依赖，
不在此处断言；实跑结果记于 reports/P65-C2-PROFILE-SEMANTICS.md。

Run:
    python -m unittest cli.tests.test_jdt_profile_eval
"""

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
TOOLS = REPO_ROOT / "tools"

spec = importlib.util.spec_from_file_location(
    "jdt_profile_eval", TOOLS / "jdt-profile-eval.py")
jpe = importlib.util.module_from_spec(spec)
sys.modules["jdt_profile_eval"] = jpe
spec.loader.exec_module(jpe)

REAL_PROFILE = (TOOLS / "jdt-format-gate" / "eclipse-format.xml").read_text(encoding="utf-8")


class TestBuildProfile(unittest.TestCase):

    def test_override_existing_key(self):
        text, missing = jpe.build_profile(
            REAL_PROFILE, {jpe.MI: "17"})
        self.assertEqual(missing, [])
        self.assertIn(f'<setting id="{jpe.MI}" value="17"/>', text)
        self.assertNotIn(f'<setting id="{jpe.MI}" value="0"/>', text)

    def test_unknown_key_reported_not_silently_ignored(self):
        text, missing = jpe.build_profile(
            REAL_PROFILE, {"org.eclipse.jdt.core.formatter.not_a_real_key": "1"})
        self.assertEqual(missing, ["org.eclipse.jdt.core.formatter.not_a_real_key"])
        self.assertEqual(text, REAL_PROFILE)

    def test_other_settings_untouched(self):
        text, _ = jpe.build_profile(REAL_PROFILE, {jpe.MI: "17"})
        self.assertIn('value="120"', text)                     # lineSplit 保持
        self.assertIn('value="false"', text)                   # join_wrapped_lines 保持


class TestParseStats(unittest.TestCase):

    def test_parses_stats_line(self):
        out = "DIFF A.java\nJdtFormatCheck: files=12 differ=3 diffLines=45 first=/x"
        self.assertEqual(jpe.parse_stats(out), (12, 3, 45))

    def test_missing_stats_returns_none(self):
        self.assertEqual(jpe.parse_stats("boom"), (None, None, None))


class TestScanLongLines(unittest.TestCase):

    def test_counts_and_worst(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "A.java").write_text("short\n" + "x" * 130 + "\n", encoding="utf-8")
            (root / "sub").mkdir()
            (root / "sub" / "B.java").write_text("y" * 121 + "\n", encoding="utf-8")
            worst, over = jpe.scan_long_lines(root)
            self.assertEqual(worst, 130)
            self.assertEqual(over, 2)

    def test_limit_is_configurable(self):
        with tempfile.TemporaryDirectory() as td:
            (Path(td) / "A.java").write_text("z" * 100 + "\n", encoding="utf-8")
            self.assertEqual(jpe.scan_long_lines(td, limit=90)[1], 1)
            self.assertEqual(jpe.scan_long_lines(td, limit=200)[1], 0)


class TestCandidateDefinitions(unittest.TestCase):

    def test_every_candidate_key_exists_in_real_profile(self):
        for name, overrides in jpe.CANDIDATES.items():
            _, missing = jpe.build_profile(REAL_PROFILE, overrides)
            self.assertEqual(missing, [], f"{name} 引用了 profile 中不存在的键")

    def test_baseline_has_no_overrides(self):
        self.assertEqual(jpe.CANDIDATES["C0-baseline"], {})