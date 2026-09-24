#!/usr/bin/env python3
"""P72 受保护路径检测 —— 正反例回归测试。

覆盖（提案 §6 的反证要求）：
- 干净树（真实仓库）→ 本检查 0 findings
- 受保护路径缺失（missing: error）→ ERROR
- 机器本地项缺失（missing: warn）→ WARN
- 受保护目录内的文件在 git 中显示删除 → ERROR（改名同理）
- 历史位置（仓库内 logs/）出现 → WARN（回归信号）
- 非 git 工作树 → WARN（检测能力受限）
- 清单缺失 → WARN（跳过而非崩溃）

Run:
    python -m unittest cli.tests.test_protected_paths
"""

import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "tools"))

from checks import Checker                                    # noqa: E402
from checks.protected_paths import check_protected_paths       # noqa: E402

SPEC_TEMPLATE = """version: 1
classes:
  - id: machine-runtime-state
    why: machine-local
    missing: warn
    paths:
      - <workspace>/metrics
  - id: ai-system-body
    why: system body
    missing: error
    paths:
      - <repo>/skills
regression:
  - <repo>/logs
"""


class TestProtectedPaths(unittest.TestCase):
    def setUp(self):
        # 工作区层 = 临时目录；仓库层 = 其下的 repo/
        self.tmp = tempfile.TemporaryDirectory()
        self.workspace = Path(self.tmp.name)
        self.repo = self.workspace / "repo"
        (self.repo / "config").mkdir(parents=True)
        (self.repo / "skills").mkdir()
        self._write_spec(SPEC_TEMPLATE)

    def tearDown(self):
        self.tmp.cleanup()

    def _write_spec(self, text):
        (self.repo / "config" / "protected-paths.yaml").write_text(text, encoding="utf-8")

    def _git(self, *args):
        return subprocess.run(["git", "-C", str(self.repo), *args],
                              capture_output=True, text=True)

    def _check(self):
        c = Checker()
        check_protected_paths(c, root=self.repo)
        return c

    def test_clean_tree_has_no_findings_from_this_check(self):
        (self.workspace / "metrics").mkdir()      # 机器本地运行时态就位
        self._git("init", "-q")
        c = self._check()
        self.assertEqual(c.errors, [])
        self.assertEqual(c.warnings, [], f"干净树不应有 warning：{c.warnings}")

    def test_missing_repo_path_is_error(self):
        shutil.rmtree(self.repo / "skills")
        c = self._check()
        self.assertTrue(any("protected path missing" in e and "<repo>/skills" in e for e in c.errors),
                        c.errors)

    def test_missing_machine_local_path_is_warn(self):
        c = self._check()
        self.assertTrue(any("protected path missing" in w and "<workspace>/metrics" in w
                            for w in c.warnings), c.warnings)
        self.assertFalse(any("protected path missing" in e for e in c.errors), c.errors)

    def test_git_deleted_file_inside_protected_dir_is_error(self):
        (self.repo / "skills" / "keep.md").write_text("x\n", encoding="utf-8")
        self._git("init", "-q")
        self._git("config", "user.email", "t@example.com")
        self._git("config", "user.name", "t")
        self._git("add", "-A")
        self._git("commit", "-q", "-m", "init")
        (self.repo / "skills" / "keep.md").unlink()          # 目录仍在，文件被删
        c = self._check()
        self.assertTrue(any("deleted/renamed in git" in e and "skills" in e for e in c.errors),
                        c.errors)

    def test_legacy_location_present_is_warn(self):
        (self.repo / "logs").mkdir()
        c = self._check()
        self.assertTrue(any("runtime state found inside the repo" in w for w in c.warnings),
                        c.warnings)

    def test_non_git_tree_warns(self):
        c = self._check()                                     # 未 git init
        self.assertTrue(any("not a git work tree" in w for w in c.warnings), c.warnings)

    def test_missing_spec_warns_instead_of_crashing(self):
        (self.repo / "config" / "protected-paths.yaml").unlink()
        c = self._check()
        self.assertTrue(any("protected-paths" in w and "skipped" in w for w in c.warnings),
                        c.warnings)
        self.assertEqual(c.errors, [])

    def test_real_repo_is_clean(self):
        """真实仓库当前应无本检查的 findings（受保护路径齐备、无历史位置残留）。"""
        c = Checker()
        check_protected_paths(c, root=REPO_ROOT)
        self.assertEqual(c.errors, [], f"真实仓库不应有 P72 错误：{c.errors}")
        self.assertEqual([w for w in c.warnings
                          if "runtime state found" in w or "protected path missing" in w], [])


if __name__ == "__main__":
    unittest.main()