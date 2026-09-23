#!/usr/bin/env python3
"""workflow-command-audit 回归测试 —— 薄命令门禁必须**报错而非崩溃**。

背景（2026-09-23，P70 实施中发现）：`results` 初始化缺少 `errors` 键，而
`audit_command` 对 >100 行的命令写 `results["errors"]` → 一旦真有命令超限，
工具抛 `KeyError` 崩溃，`check.py` 只能报「unrecognized output (tool may be broken)」，
即**门禁失效**（该缺陷在无超标命令时长期潜伏）。修复后：报 ERROR + 退出码 1。

Run:
    python -m unittest cli.tests.test_workflow_command_audit
"""

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
AUDIT = REPO_ROOT / "tools" / "workflow-command-audit.py"


def _load(name, rel):
    spec = importlib.util.spec_from_file_location(name, REPO_ROOT / rel)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


class TestThinCommandGate(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        (self.root / "cli" / "commands").mkdir(parents=True)
        (self.root / "config").mkdir()
        # 命令需在 menu.yaml 注册，否则会多出 menu blocker（与本次被测缺陷无关）
        (self.root / "config" / "menu.yaml").write_text(
            "sections:\n  - items:\n      - name: big\n        kind: command\nclass big\n",
            encoding="utf-8",
        )

    def tearDown(self):
        self.tmp.cleanup()

    def _write_command(self, lines):
        body = "\n".join(f"line {i}" for i in range(lines))
        (self.root / "cli" / "commands" / "aic-big.md").write_text(body + "\n", encoding="utf-8")

    def _run(self):
        return subprocess.run(
            [sys.executable, str(AUDIT), "--repo-root", str(self.root), "--json"],
            capture_output=True, text=True,
        )

    def test_oversize_command_reports_error_not_crash(self):
        self._write_command(105)
        proc = self._run()
        self.assertNotIn("Traceback", proc.stderr, "工具崩溃（应报错而非抛异常）")
        self.assertEqual(proc.returncode, 1)
        payload = json.loads(proc.stdout)
        self.assertTrue(
            any("thin-command" in e for e in payload["errors"]),
            f"未报薄命令错误：{payload}",
        )

    def test_boundary_100_lines_is_clean(self):
        self._write_command(100)
        proc = self._run()
        self.assertNotIn("Traceback", proc.stderr)
        payload = json.loads(proc.stdout)
        self.assertEqual([e for e in payload["errors"] if "thin-command" in e], [])

    def test_human_output_lists_errors_and_summary_counts(self):
        self._write_command(105)
        proc = subprocess.run(
            [sys.executable, str(AUDIT), "--repo-root", str(self.root)],
            capture_output=True, text=True,
        )
        self.assertIn("[ERROR]", proc.stdout)
        self.assertIn("errors", proc.stdout.split("Summary:")[-1])


if __name__ == "__main__":
    unittest.main()