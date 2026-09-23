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
import io
import shutil
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stderr
from pathlib import Path

import yaml

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


class TestGenerateContractScalarQuoting(unittest.TestCase):
    """R4 G1：`format_entry_yaml` 的值必须能安全回读（含 `: ` / ` #` / 前导空格 / 隐式转型）。"""

    @classmethod
    def setUpClass(cls):
        cls.gc = _load("generate_contract_r4_g1",
                       "skills/contract-maintainer/scripts/generate_contract.py")

    def test_危险标量回读一致(self):
        for raw in ["a: b", "x #y", "  leading", "trailing  ", "true", "123",
                    "null", "[1,2]", "*star", "- dash", "多行\n第二行", "2026-09-23"]:
            token = self.gc._yaml_scalar(raw)
            loaded = yaml.safe_load("k: " + token)["k"]
            self.assertEqual(loaded, raw, f"{raw!r} -> {token!r}")

    def test_普通标量不加引号(self):
        self.assertEqual(self.gc._yaml_scalar("order-service"), "order-service")

    def test_整份产物可解析(self):
        entry = {"id": "a-b-Do: thing", "调用方": "svcA", "接口/主题": "Do: thing",
                 "切库规则": "#not-a-comment"}
        doc = "interactions:\n" + self.gc.format_entry_yaml(entry)
        data = yaml.safe_load(doc)
        self.assertEqual(data["interactions"][0]["接口/主题"], "Do: thing")
        self.assertEqual(data["interactions"][0]["切库规则"], "#not-a-comment")


class TestGenerateContractDedupWarns(unittest.TestCase):
    """R4 G2：去重静默保留首个 → 必须出声。"""

    @classmethod
    def setUpClass(cls):
        cls.gc = _load("generate_contract_r4_g2",
                       "skills/contract-maintainer/scripts/generate_contract.py")

    def test_重复条目告警且计数正确(self):
        buf = io.StringIO()
        with redirect_stderr(buf):
            kept = self.gc.deduplicate([
                {"id": "a-b-x", "_source": "S1"},
                {"id": "a-b-x", "_source": "S2"},
                {"id": "a-b-x", "_source": "S3"},
                {"id": "c-d-y", "_source": "S4"},
            ])
        self.assertEqual([e["id"] for e in kept], ["a-b-x", "c-d-y"])
        warnings = [l for l in buf.getvalue().splitlines() if "重复条目" in l]
        self.assertEqual(len(warnings), 2)
        self.assertIn("S3", buf.getvalue())

    def test_无重复无告警(self):
        buf = io.StringIO()
        with redirect_stderr(buf):
            kept = self.gc.deduplicate([{"id": "a"}, {"id": "b"}])
        self.assertEqual(len(kept), 2)
        self.assertEqual(buf.getvalue(), "")


class TestGenerateContractServiceMatching(unittest.TestCase):
    """R4 G3：服务匹配口径统一为「去空白后精确」（子串匹配不再是隐式口径）。"""

    @classmethod
    def setUpClass(cls):
        cls.gc = _load("generate_contract_r4_g3",
                       "skills/contract-maintainer/scripts/generate_contract.py")

    def test_精确匹配命中(self):
        specs = [{"调用方": "order", "被调用方": "target-svc",
                  "接口/主题": "CreateOrder", "_fields": ["enterpriseId"]}]
        scen = [{"场景引用": "S1", "服务": "order", "切库规则": "enterpriseId"}]
        self.assertEqual(self.gc.cross_validate(specs, scen), [])
        self.assertEqual(self.gc.validate_fields(specs, scen), [])

    def test_子串不再是匹配口径(self):
        """服务名 `target` 是 `target-svc` 的子串，但不是匹配 —— 两处口径一致。"""
        specs = [{"调用方": "target-svc", "被调用方": "x",
                  "接口/主题": "M", "_fields": ["enterpriseId"]}]
        scen = [{"场景引用": "S9", "服务": "target", "切库规则": "enterpriseId"}]
        self.assertEqual(self.gc.validate_fields(specs, scen), [])
        self.assertFalse(self.gc._service_matches("target", "target-svc"))
        warnings = self.gc.cross_validate(specs, scen)
        # 子串曾是「真」而精确为「假」：统一后两侧一致判为未匹配（各出一条告警）
        self.assertEqual(len(warnings), 2, warnings)

    def test_空白容错与空服务名(self):
        self.assertTrue(self.gc._service_matches(" order-service ", "order-service"))
        self.assertFalse(self.gc._service_matches("", ""))

    def test_触发条件仍按子串(self):
        specs = [{"调用方": "a", "被调用方": "b", "接口/主题": "CreateOrder"}]
        scen = [{"场景引用": "S2", "服务": "nope", "触发条件": "CreateOrder"}]
        # 场景侧命中（trigger 子串），Spec 侧仍报「无对应场景」
        self.assertEqual(len(self.gc.cross_validate(specs, scen)), 1)


class TestK8sHelperEffectiveStatus(unittest.TestCase):
    """R4 S3：仅看 `.status.phase` 会掩盖 CrashLoopBackOff / OOMKilled。"""

    @classmethod
    def setUpClass(cls):
        cls.kh = _load("k8s_helper_r4", "skills/k8s-logs/scripts/k8s_helper.py")

    def test_crashloopbackoff_被取出(self):
        st = {"phase": "Running", "containerStatuses": [
            {"state": {"waiting": {"reason": "CrashLoopBackOff"}},
             "lastState": {"terminated": {"reason": "Error"}}}]}
        self.assertEqual(self.kh.effective_status(st), "Running(CrashLoopBackOff)")

    def test_imagepullbackoff_与_initcontainer(self):
        self.assertEqual(self.kh.effective_status(
            {"phase": "Pending", "containerStatuses": [
                {"state": {"waiting": {"reason": "ImagePullBackOff"}}}]}),
            "Pending(ImagePullBackOff)")
        self.assertEqual(self.kh.effective_status(
            {"phase": "Pending", "initContainerStatuses": [
                {"state": {"waiting": {"reason": "CreateContainerConfigError"}}}]}),
            "Pending(CreateContainerConfigError)")

    def test_laststate_故障原因上提(self):
        self.assertEqual(self.kh.effective_status(
            {"phase": "Running", "containerStatuses": [
                {"state": {"running": {}},
                 "lastState": {"terminated": {"reason": "OOMKilled"}}}]}),
            "Running(OOMKilled)")

    def test_正常态不被改写(self):
        # Completed 不得盖掉 Succeeded，否则 -s/-f 状态过滤失效
        self.assertEqual(self.kh.effective_status(
            {"phase": "Succeeded", "containerStatuses": [
                {"state": {"terminated": {"reason": "Completed"}}}]}), "Succeeded")
        self.assertEqual(self.kh.effective_status({"phase": "Running"}), "Running")

    def test_空与缺字段容错(self):
        for bad in ({}, None, {"phase": "Running", "containerStatuses": None}):
            self.assertIn(self.kh.effective_status(bad), ("Unknown", "Running"))

    def test_状态过滤仍按相位(self):
        # 故障 Pod 不得因注解而被 'Running' 过滤漏掉
        pods = [("api-1", "Running(CrashLoopBackOff)"), ("api-2", "Running"),
                ("job-1", "Succeeded")]
        self.assertEqual([n for n, _ in self.kh.filter_pods_by_status(pods, "r")],
                         ["api-1", "api-2"])
        self.assertEqual(self.kh.base_status("Running(CrashLoopBackOff)"), "Running")

    def test_取数据走_json_且坏输出可降级(self):
        import json as _json
        calls = {}

        def fake(args, capture_output=False):
            calls["args"] = args
            return _json.dumps({"items": [
                {"metadata": {"name": "api-1"},
                 "status": {"phase": "Running", "containerStatuses": [
                     {"state": {"waiting": {"reason": "CrashLoopBackOff"}}}]}},
                {"metadata": {"name": "api-2"}, "status": {"phase": "Running"}},
                {"metadata": {}, "status": {"phase": "Running"}},
            ]}), "", 0

        orig = self.kh.run_kubectl
        self.kh.run_kubectl = fake
        try:
            pods, ok, _ = self.kh.get_all_pods("t2")
        finally:
            self.kh.run_kubectl = orig
        self.assertIn("json", calls["args"])
        self.assertTrue(ok)
        self.assertEqual(pods, [("api-1", "Running(CrashLoopBackOff)"), ("api-2", "Running")])

        self.kh.run_kubectl = lambda args, capture_output=False: ("not json", "", 0)
        try:
            pods2, ok2, err2 = self.kh.get_all_pods("t2")
        finally:
            self.kh.run_kubectl = orig
        self.assertFalse(ok2)          # 走手动降级，不静默给错结果
        self.assertEqual(pods2, [])
        self.assertIn("无法解析", err2)


class TestIndexProjectVenvProbe(unittest.TestCase):
    """R4 S1：`index-project/SKILL.md` 不得写死 Windows venv 布局（`Scripts/python`）。"""

    SKILL = REPO_ROOT / "skills" / "index-project" / "SKILL.md"

    def _probe_block(self):
        import re
        text = self.SKILL.read_text(encoding="utf-8")
        blocks = re.findall(r"```bash\n(.*?)```", text, re.S)
        hits = [b for b in blocks if "VENV=" in b]
        self.assertTrue(hits, "SKILL.md 应含探测式 venv 代码块")
        return hits[0]

    def test_探测两种布局且失败可见(self):
        text = self.SKILL.read_text(encoding="utf-8")
        self.assertIn("bin/python", text)
        self.assertIn("Scripts/python.exe", text)
        self.assertNotIn('"$HOME/.claude-code-index-venv/Scripts/python"', text)
        probe = self._probe_block()
        self.assertIn("exit 1", probe)      # 找不到解释器时必须显式失败

    @unittest.skipUnless(shutil.which("bash"), "无 bash，跳过 venv 探测行为测试")
    def test_三种布局实际可解析(self):
        probe = self._probe_block().replace(
            "$HOME/.claude/tools", "$HOME/tools")
        with tempfile.TemporaryDirectory() as td:
            home = Path(td) / "home"
            tools = home / "tools" / "code-indexer"
            tools.mkdir(parents=True)
            (tools / "reindex_cli.py").write_text(
                "import sys; print('OK', sys.argv[1:])\n", encoding="utf-8")
            script = Path(td) / "probe.sh"
            script.write_text(probe, encoding="utf-8")
            venv = home / ".claude-code-index-venv"

            for rel in ("bin/python", "Scripts/python", "Scripts/python.exe"):
                sub = venv / rel
                sub.parent.mkdir(parents=True, exist_ok=True)
                sub.write_text('#!/bin/sh\nexec python3 "$@"\n', encoding="utf-8")
                sub.chmod(0o755)
                proc = subprocess.run(["bash", str(script)], env={
                    "HOME": str(home), "PATH": "/usr/bin:/bin"},
                    capture_output=True, text=True, timeout=60)
                self.assertEqual(proc.returncode, 0, f"{rel}: {proc.stderr}")
                self.assertIn("OK", proc.stdout, rel)

            # 全无解释器 → 必须非 0 退出且信息明确
            for p in venv.rglob("python*"):
                p.unlink()
            proc = subprocess.run(["bash", str(script)], env={
                "HOME": str(home), "PATH": "/usr/bin:/bin"},
                capture_output=True, text=True, timeout=60)
            self.assertEqual(proc.returncode, 1)
            self.assertIn("interpreter not found", proc.stderr)


class TestIdeaMcpSseFailFast(unittest.TestCase):
    """R4 S4：SSE 断线被吞 → 后续 POST 空等 180s；`urlopen` 异常静默 pass。"""

    @classmethod
    def setUpClass(cls):
        cls.mod = _load("idea_mcp_r4", "skills/idea-build/idea-mcp.py")

    class _FakeSSE:
        SID = "abcdef01-2345-6789-abcd-ef0123456789"
        boom = None

        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

        def __iter__(self):
            yield f"event: endpoint\ndata: /message?sessionId={self.SID}\n".encode()
            if self.boom:
                raise self.boom
            yield b'data: {"jsonrpc":"2.0","id":99,"result":{"ok":true}}\n'

    class _FakePost:
        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

    def _patch(self, sse_boom=None, post_error=None):
        import urllib.request
        fake_sse, fake_post = self._FakeSSE, self._FakePost
        fake_sse.boom = sse_boom

        def fake(req, timeout=None):
            url = getattr(req, "full_url", str(req))
            if url.endswith("/sse"):
                return fake_sse()
            if post_error:
                raise post_error
            return fake_post()

        orig = urllib.request.urlopen
        urllib.request.urlopen = fake
        return orig

    def test_断线快速失败而非空等(self):
        import io
        import time
        import urllib.request
        from contextlib import redirect_stderr
        orig = self._patch()
        try:
            buf = io.StringIO()
            t0 = time.time()
            with redirect_stderr(buf):
                post = self.mod.mcp_session(port=1, project_path="/tmp/p")
                with self.assertRaises(RuntimeError) as ctx:
                    post({"jsonrpc": "2.0", "id": 1, "method": "tools/list"},
                         wait_ms=180000)
            elapsed = time.time() - t0
        finally:
            urllib.request.urlopen = orig
        self.assertIn("SSE", str(ctx.exception))
        self.assertLess(elapsed, 10, "原实现会空等满 180s")

    def test_断线前已达响应仍可取回(self):
        import urllib.request
        orig = self._patch()
        try:
            post = self.mod.mcp_session(port=1, project_path="/tmp/p")
            got = post({"jsonrpc": "2.0", "id": 99, "method": "x"}, wait_ms=3000)
        finally:
            urllib.request.urlopen = orig
        self.assertEqual(got.get("result"), {"ok": True})

    def test_sse_异常必须告警(self):
        import io
        import urllib.request
        from contextlib import redirect_stderr
        orig = self._patch(sse_boom=ConnectionResetError("connection reset by peer"))
        try:
            buf = io.StringIO()
            with redirect_stderr(buf):
                post = self.mod.mcp_session(port=1, project_path="/tmp/p")
                with self.assertRaises(RuntimeError) as ctx:
                    post({"jsonrpc": "2.0", "id": 5, "method": "tools/call"},
                         wait_ms=3000)
        finally:
            urllib.request.urlopen = orig
        self.assertIn("SSE 通道中断", buf.getvalue())
        self.assertIn("ConnectionResetError", str(ctx.exception))

    def test_post_非202_不再静默(self):
        import io
        import urllib.error
        import urllib.request
        from contextlib import redirect_stderr
        err = urllib.error.HTTPError("http://x", 500, "Server Error", {}, None)
        orig = self._patch(post_error=err)
        try:
            buf = io.StringIO()
            with redirect_stderr(buf):
                post = self.mod.mcp_session(port=1, project_path="/tmp/p")
                with self.assertRaises(RuntimeError) as ctx:
                    post({"jsonrpc": "2.0", "id": 7, "method": "build"}, wait_ms=3000)
        finally:
            urllib.request.urlopen = orig
        self.assertIn("HTTP 500", buf.getvalue())
        self.assertIn("POST 侧异常", str(ctx.exception))


class TestAuditStrengthUnified(unittest.TestCase):

    def test_命令超长与工作流同判(self):
        text = (REPO_ROOT / "tools" / "workflow-command-audit.py").read_text(encoding="utf-8")
        self.assertIn('results["errors"].append(f"{p.name}: {n} lines (thin-command gate, RFC-0003)")', text)
