#!/usr/bin/env python3
"""Tests for `tools/checks/jdt_ignore.py` — C2 豁免清单治理（P65 Option D）。

契约：每个路径条目紧邻上方需 `# reason: <理由>（<YYYY-MM-DD> 复核基线）`（单行）；
缺理由/缺日期/悬空理由 = ERROR；复核基线超 180 天 = WARN。

Run:
    python -m unittest cli.tests.test_jdt_ignore_check
"""

import datetime
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "tools"))

from checks import Checker                        # noqa: E402
from checks import jdt_ignore as ji               # noqa: E402


def today_minus(days):
    return (datetime.date.today() - datetime.timedelta(days=days)).isoformat()


class TestJdtIgnoreCheck(unittest.TestCase):

    def _run(self, text):
        original = ji.IGNORE_FILE
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "known-ignore.txt"
            path.write_text(text, encoding="utf-8")
            ji.IGNORE_FILE = path
            try:
                c = Checker()
                ji.check_jdt_ignore(c)
            finally:
                ji.IGNORE_FILE = original
        return c

    def test_entry_with_reason_and_date_passes(self):
        c = self._run(f"# reason: 振荡（{today_minus(1)} 复核基线）\nmain/java/A.java\n")
        self.assertEqual(c.errors, [])
        self.assertEqual(c.warnings, [])

    def test_missing_reason_is_error(self):
        c = self._run("# 只有说明注释\nmain/java/A.java\n")
        self.assertEqual(len(c.errors), 1)
        self.assertIn("缺少理由", c.errors[0])

    def test_missing_date_is_error(self):
        c = self._run("# reason: 振荡，人工确认\nmain/java/A.java\n")
        self.assertEqual(len(c.errors), 1)
        self.assertIn("复核基线日期", c.errors[0])

    def test_stale_review_is_warning(self):
        c = self._run(f"# reason: 振荡（{today_minus(400)} 复核基线）\nmain/java/A.java\n")
        self.assertEqual(c.errors, [])
        self.assertEqual(len(c.warnings), 1)
        self.assertIn("未复核", c.warnings[0])

    def test_dangling_reason_is_error(self):
        c = self._run(f"# reason: 振荡（{today_minus(1)} 复核基线）\n# 后面没有条目\n")
        self.assertEqual(len(c.errors), 1)
        self.assertIn("悬空理由", c.errors[0])

    def test_comments_only_file_is_clean(self):
        c = self._run("# 只有注释，没有豁免条目\n")
        self.assertEqual(c.errors, [])
        self.assertEqual(c.warnings, [])

    def test_repository_manifest_is_governed(self):
        """真实清单必须已带理由与日期（否则门禁常红）。"""
        c = Checker()
        ji.check_jdt_ignore(c)
        self.assertEqual(c.errors, [], c.errors)

    def test_parser_reports_entry_and_reason(self):
        text = f"# reason: A 振荡（{today_minus(1)} 复核基线）\nmain/java/A.java\n"
        entries, dangling = ji.parse_entries(text)
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0][0], "main/java/A.java")
        self.assertIn("振荡", entries[0][1])
        self.assertEqual(dangling, [])


if __name__ == "__main__":
    unittest.main()
