#!/usr/bin/env python3
"""maintain-delta / maintain-report 工具测试（Q1：增量巡检 + 报告骨架）。

覆盖：
- maintain-delta: FIRST_RUN / NO_CHANGES / CHANGED 三态判定 + --record
- maintain-report: 渲染含四节骨架、非破坏（已存在不覆盖）

Run:
    python -m unittest cli/tests/test_maintain_tools.py
"""

import importlib.util
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

TOOLS = REPO_ROOT / "tools"


def _load(name):
    spec = importlib.util.spec_from_file_location(
        name.replace("-", "_"),
        TOOLS / f"{name}.py",
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class TestMaintainDelta(unittest.TestCase):

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.delta = _load("maintain-delta")
        # 状态文件隔离到临时目录
        self._orig_state = self.delta.STATE
        self.delta.STATE = Path(self._tmp.name) / "state.json"

    def tearDown(self):
        self.delta.STATE = self._orig_state
        self._tmp.cleanup()

    def test_first_run(self):
        v = self.delta.check_verdict()
        self.assertEqual(v["verdict"], "FIRST_RUN")

    def test_no_changes_after_record(self):
        head = self.delta.current_head()
        self.delta.save_state(head, "2026-08-23")
        v = self.delta.check_verdict()
        self.assertEqual(v["verdict"], "NO_CHANGES")

    def test_changed_detects_areas(self):
        # 伪造旧 HEAD（根提交）→ diff 全量 → CHANGED + 区域非空
        import subprocess

        root_commit = subprocess.run(
            ["git", "rev-list", "--max-parents=0", "HEAD"],
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
        ).stdout.strip()
        self.assertTrue(root_commit)
        self.delta.save_state(root_commit, "2026-08-22")
        v = self.delta.check_verdict()
        self.assertEqual(v["verdict"], "CHANGED")
        self.assertTrue(v["areas"])
        self.assertTrue(v["suggested_tools"])

    def test_state_roundtrip(self):
        self.delta.save_state("abc123", "2026-08-23")
        state = json.loads(
            self.delta.STATE.read_text(encoding="utf-8")
        )
        self.assertEqual(state["head"], "abc123")
        self.assertEqual(state["date"], "2026-08-23")


class TestMaintainReport(unittest.TestCase):

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.report = _load("maintain-report")

    def tearDown(self):
        self._tmp.cleanup()

    def test_render_has_four_sections(self):
        content = self.report.render("2099-01-01")
        for header in (
            "工具校验结果",
            "指标对比",
            "quick-check 趋势",
            "提案状态",
            "巡检发现",
        ):
            self.assertIn(header, content)

    def test_non_destructive(self):
        # 目标已存在 → 不覆盖
        self.report.REPORTS = Path(self._tmp.name) / "reports"
        self.report.REPORTS.mkdir(parents=True)
        target = self.report.REPORTS / "MAINTENANCE-2099-01-01.md"
        target.write_text("existing", encoding="utf-8")

        sys.argv = ["maintain-report.py", "--date", "2099-01-01"]
        rc = self.report.main()
        self.assertEqual(rc, 0)
        self.assertEqual(
            target.read_text(encoding="utf-8"),
            "existing",
        )

    def test_generates_when_missing(self):
        self.report.REPORTS = Path(self._tmp.name) / "reports"
        self.report.REPORTS.mkdir(parents=True)
        sys.argv = ["maintain-report.py", "--date", "2099-01-02"]
        rc = self.report.main()
        self.assertEqual(rc, 0)
        target = self.report.REPORTS / "MAINTENANCE-2099-01-02.md"
        self.assertTrue(target.exists())
        self.assertIn("工具校验结果", target.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
