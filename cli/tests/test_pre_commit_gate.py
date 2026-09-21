"""Tests for the pre-commit gate Python body (tools/pre-commit-gate.py).

The thin bash shim (`.githooks/pre-commit`) just probes python3/python and
execs this module — the testable surface is here: zone matching, git root
resolution, and the gate runner's exit semantics.
"""

import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "tools"))

from pre_commit_gate import (  # noqa: E402
    MEMORY_RE,
    ZONE_RE,
    git_repo_root,
    memory_language_check,
    run_checks,
    staged_memory_files,
    staged_zone_files,
)


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


class TestMemoryGate(unittest.TestCase):
    """memory 英文纪律门禁（2026-09-21 补；防中文 memory 绕过提交）。"""

    def test_memory_re_matches_memory_only(self):
        cases = [
            ("governance/memory/java/coding-memory.md", True),
            ("governance/memory/java/integration.md", True),
            ("governance/memory/coding-memory.md", True),
            ("governance/OPERATIONS.md", False),
            ("cli/main.py", False),
            ("governance/memoryfuel/x.md", False),
        ]
        for path, expected in cases:
            self.assertEqual(bool(MEMORY_RE.match(path)), expected, path)

    def test_staged_memory_files_returns_list(self):
        files = staged_memory_files(REPO_ROOT)
        self.assertIsInstance(files, list)
        self.assertTrue(all(MEMORY_RE.match(f) for f in files))

    def test_clean_memory_not_blocked(self):
        self.assertEqual(
            memory_language_check(["governance/memory/java/integration.md"]),
            [],
        )

    def test_cjk_memory_blocks(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            target = REPO_ROOT / "governance" / "memory" / "_probe_cjk.md"
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text("# probe\n\n- 中文测试\n", encoding="utf-8")
            try:
                lines = memory_language_check(["governance/memory/_probe_cjk.md"])
                self.assertTrue(lines)
                self.assertIn("memory English-discipline", lines[0])
                self.assertTrue(any("_probe_cjk.md" in l for l in lines))

                # 仅 memory 文件（无 zone 文件）也阻塞，且不跑 zone 门禁
                blocked, out = run_checks(
                    REPO_ROOT,
                    [],
                    ["governance/memory/_probe_cjk.md"],
                )
                self.assertTrue(blocked)
                self.assertTrue(any("memory English-discipline" in l for l in out))
            finally:
                target.unlink(missing_ok=True)

    def test_language_violations_root_index_exempt(self):
        """根索引豁免；主题级 coding-memory.md 不再被按名放过（2026-09-21 修复）。"""
        from checks.memory import language_violations

        self.assertEqual(
            language_violations(["governance/memory/coding-memory.md"]),
            [],
        )
        target = REPO_ROOT / "governance" / "memory" / "java" / "_probe_topic.md"
        target.write_text("# probe\n\n- 中文测试\n", encoding="utf-8")
        try:
            got = language_violations([
                "governance/memory/java/_probe_topic.md",
            ])
            self.assertEqual(len(got), 1)
            self.assertTrue(got[0][1] > 0)
        finally:
            target.unlink(missing_ok=True)


if __name__ == "__main__":
    unittest.main()
