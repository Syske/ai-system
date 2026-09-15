"""Tests for the pre-commit gate Python body (tools/pre-commit-gate.py).

The thin bash shim (`.githooks/pre-commit`) just probes python3/python and
execs this module — the testable surface is here: zone matching, git root
resolution, and the gate runner's exit semantics.
"""

import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "tools"))

from pre_commit_gate import ZONE_RE, git_repo_root, run_checks, staged_zone_files


class TestZoneMatch(unittest.TestCase):

    def test_zone_re_matches_english_discipline_zone(self):
        cases = [
            ("templates/runtime/runtime-prepare.md", True),
            ("templates/runtime/runtime-develop.md", True),
            ("workflows/review.md", True),
            ("workflows/README.md", True),
            ("workflows/sub/dir.md", True),   # 子目录 .md 同属纪律区
            ("cli/services/chain.py", False),
            ("tools/check.py", False),
            ("config/chains.yaml", False),
            ("workflows/README.txt", False),   # 非 .md
        ]
        for path, expected in cases:
            self.assertEqual(bool(ZONE_RE.match(path)), expected, path)

    def test_git_repo_root(self):
        self.assertIsNotNone(git_repo_root())
        self.assertEqual(git_repo_root(), REPO_ROOT)

    def test_staged_zone_files_returns_list(self):
        files = staged_zone_files(REPO_ROOT)
        self.assertIsInstance(files, list)
        # 空 staged 时返回空列表（不抛错）
        self.assertTrue(all(ZONE_RE.match(f) for f in files))


class TestRunChecks(unittest.TestCase):

    def test_empty_files_never_blocks(self):
        blocked, lines = run_checks(REPO_ROOT, [])
        self.assertFalse(blocked)
        self.assertEqual(lines, [])

    def test_clean_repo_not_blocked(self):
        # 无 zone staged 文件时，gate 不应阻塞（main 短路路径）
        from pre_commit_gate import main

        # 当前仓 staged 非 zone 文件时 main 返回 0
        self.assertEqual(main([]), 0)


if __name__ == "__main__":
    unittest.main()
