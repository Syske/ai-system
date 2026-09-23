#!/usr/bin/env python3
"""R4 批次回归测试 —— 工具一致性/健壮性。

覆盖：
- `checks/misc.py`：元组返回元数检查只看**函数自身** return（原 `ast.walk` 含嵌套函数 → 误报）
- `checks/misc.py`：外部门禁工具超时/不可执行 → **报错而非崩溃**
- `proposal-audit.py`：`PROPOSALS.md`（索引文件）不得被当作提案
- `maintain-report.py`：关闭状态大小写不敏感（与 proposal-audit 同口径）

Run:
    python -m unittest cli.tests.test_r4_tool_consistency
"""

import ast
import importlib.util
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "tools"))

from checks import misc                                # noqa: E402
from checks import Checker                             # noqa: E402


def _load(name, rel):
    spec = importlib.util.spec_from_file_location(name, REPO_ROOT / rel)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


class TestOwnReturns(unittest.TestCase):
    """元组元数检查不得把嵌套函数的 return 计入外层。"""

    def test_嵌套函数return被排除(self):
        src = (
            "def outer():\n"
            "    def inner():\n"
            "        return 1, 2\n"
            "    return 1\n"
        )
        tree = ast.parse(src)
        fn = tree.body[0]
        returns = list(misc._own_returns(fn))
        self.assertEqual(len(returns), 1, "只应统计 outer 自身的 return")

    def test_同一函数多个return仍可见(self):
        src = "def f(x):\n    if x:\n        return 1, 2\n    return 3, 4\n"
        returns = list(misc._own_returns(ast.parse(src).body[0]))
        self.assertEqual(len(returns), 2)


class TestGateToolTimeoutGuard(unittest.TestCase):
    """外部门禁工具超时 → c.error（原抛 TimeoutExpired 使 check.py 崩溃）。"""

    def _run(self, script):
        c = Checker()
        with tempfile.TemporaryDirectory() as td:
            tool = Path(td) / "slow.py"
            tool.write_text(script, encoding="utf-8")
            pair = misc._run_gate_tool(
                [sys.executable, str(tool)], c, "慢工具", timeout=1)
        return c, pair

    def test_超时被捕获并报错(self):
        c, (out, rc) = self._run("import time\ntime.sleep(5)\n")
        self.assertIsNone(out)
        self.assertIsNone(rc)
        self.assertTrue(any("超时" in e for e in c.errors), c.errors)

    def test_正常工具返回输出与返回码(self):
        c, (out, rc) = self._run("print('OK')\n")
        self.assertIn("OK", out)
        self.assertEqual(rc, 0)


class TestProposalIndexExcluded(unittest.TestCase):
    def test_索引文件不被当作提案(self):
        mod = _load("proposal_audit_r4", "tools/proposal-audit.py")
        result = mod.audit()
        names = {p["file"] for p in result["proposals"]}
        self.assertNotIn("PROPOSALS.md", names)

    def test_真实提案仍在列(self):
        mod = _load("proposal_audit_r4b", "tools/proposal-audit.py")
        names = {p["file"] for p in mod.audit()["proposals"]}
        self.assertIn("P60-GATE-SELF-VERIFICATION.md", names)


class TestMaintainReportClosedCase(unittest.TestCase):
    def test_关闭状态大小写不敏感(self):
        text = (REPO_ROOT / "tools" / "maintain-report.py").read_text(encoding="utf-8")
        self.assertIn('str(p.get("status") or "").lower()', text)
        self.assertIn('"implemented"', text)


if __name__ == "__main__":
    unittest.main()


class TestHiddenRegistryConsistency(unittest.TestCase):
    """#1：`hidden_workflows` / `hidden_commands` 悬空条目必须报错。"""

    def _run_with_menu(self, menu_text):
        import tempfile
        from checks import base as cbase
        from checks import menu as cmenu

        original = cbase.ROOT
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "config").mkdir(parents=True)
            (root / "config" / "menu.yaml").write_text(menu_text, encoding="utf-8")
            (root / "workflows").mkdir()
            (root / "workflows" / "develop.md").write_text("---\nname: develop\n---\n", encoding="utf-8")
            (root / "cli" / "commands").mkdir(parents=True)
            (root / "cli" / "commands" / "aic-scan.md").write_text("---\nname: scan\n---\n", encoding="utf-8")
            cbase.ROOT = root
            try:
                c = Checker()
                cmenu.check_hidden_registry(c)
            finally:
                cbase.ROOT = original
        return c

    def test_悬空条目报错(self):
        c = self._run_with_menu(
            "hidden_workflows:\n  - develop\n  - not-a-workflow\n"
            "hidden_commands:\n  - scan\n  - not-a-command   # 注释应被剥离\n"
        )
        self.assertEqual(len(c.errors), 2, c.errors)
        self.assertTrue(any("not-a-workflow" in e for e in c.errors))
        self.assertTrue(any("not-a-command" in e for e in c.errors))

    def test_正常条目无错(self):
        c = self._run_with_menu(
            "hidden_workflows:\n  - develop\nhidden_commands:\n  - scan\n")
        self.assertEqual(c.errors, [])

    def test_真实配置无误(self):
        from checks import menu as cmenu
        c = Checker()
        cmenu.check_hidden_registry(c)
        self.assertEqual(c.errors, [], c.errors)


class TestBugfixPhasesFromConfig(unittest.TestCase):

    def test_阶段集来自配置并集(self):
        from checks import base as cbase
        from checks import bugfix_modes

        config = cbase.load_yaml(cbase.ROOT / "config" / "workflows" / "bugfix-modes.yaml") or {}
        phases = bugfix_modes.known_phases()
        self.assertTrue(phases)

        found = set()

        def collect(node):
            if isinstance(node, dict):
                for k, v in node.items():
                    if k == "phases" and isinstance(v, list):
                        found.update(str(x) for x in v)
                    else:
                        collect(v)
            elif isinstance(node, list):
                for item in node:
                    collect(item)

        collect(config)
        self.assertTrue(found <= phases, f"配置阶段 {found - phases} 未进入并集")


class TestRepoMetricsSchemaGuard(unittest.TestCase):

    def test_缺字段明确报错(self):
        mod = _load("repo_metrics_r4", "tools/repo-metrics.py")
        with self.assertRaises(SystemExit) as ctx:
            mod._metric({"skills": {}}, "skills", "count")
        self.assertIn("缺少指标", str(ctx.exception))

    def test_有字段正常返回(self):
        mod = _load("repo_metrics_r4b", "tools/repo-metrics.py")
        self.assertEqual(mod._metric({"skills": {"count": 39}}, "skills", "count"), 39)


class TestAuditStrengthUnified(unittest.TestCase):

    def test_命令超长与工作流同判(self):
        text = (REPO_ROOT / "tools" / "workflow-command-audit.py").read_text(encoding="utf-8")
        self.assertIn('results["errors"].append(f"{p.name}: {n} lines (thin-command gate, RFC-0003)")', text)
