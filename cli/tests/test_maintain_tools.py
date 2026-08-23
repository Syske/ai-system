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
        # 打桩判定逻辑（不依赖 git 历史深度——CI 为 shallow checkout，
        # rev-list --max-parents=0 会返回浅边界=HEAD 自身，无法取真实根提交）
        self.delta.save_state("old-head", "2026-08-22")
        self.delta.current_head = lambda: "new-head"
        self.delta.changed_areas = lambda old, new: (["cli", "tools"], ["cli/a.py"])
        v = self.delta.check_verdict()
        self.assertEqual(v["verdict"], "CHANGED")
        self.assertEqual(v["areas"], ["cli", "tools"])
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


class TestPromptMetrics(unittest.TestCase):

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.pm = _load("prompt-metrics")
        self._orig_metrics = self.pm.METRICS
        self.pm.METRICS = Path(self._tmp.name)

    def tearDown(self):
        self.pm.METRICS = self._orig_metrics
        self._tmp.cleanup()

    def test_measure_returns_summary(self):
        import yaml

        registry = yaml.safe_load(
            (REPO_ROOT / "config" / "workflow-registry.yaml")
            .read_text(encoding="utf-8")
        )["workflows"]
        data = self.pm.measure(registry, [])
        s = data["summary"]
        self.assertGreater(s["prompts"], 0)
        self.assertGreater(s["total_chars"], 0)
        # 前缀稳定：同工作流不同输入静态前缀一致
        self.assertEqual(
            s["prefix_stable_count"],
            len(registry),
        )

    def test_main_records_json(self):
        sys.argv = ["prompt-metrics.py", "--date", "2099-01-01"]
        rc = self.pm.main()
        self.assertEqual(rc, 0)
        target = self.pm.METRICS / "prompt-2099-01-01.json"
        self.assertTrue(target.exists())
        data = json.loads(target.read_text(encoding="utf-8"))
        self.assertIn("summary", data)
        self.assertIn("rows", data)


if __name__ == "__main__":
    unittest.main()
