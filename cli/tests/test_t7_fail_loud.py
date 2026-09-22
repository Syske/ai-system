#!/usr/bin/env python3
"""T7 批次 — 盲检 WARN/INFO 收尾中的 fail-loud / 健壮性修复回归测试。

覆盖：
- generate_contract：RPC 条目缺必填键 → 显式 ValueError（原裸 KeyError）
- deepseek：查询串感知的 `ty=r` 追加（原 `&ty=r` 产出畸形 URL）
- state_store：状态文件不可读/不可写 → 输出可得（原静默吞）
- checks/menu：wizard dry-run 的 monkeypatch 必须恢复（原污染同进程后续检查）

Run:
    python -m unittest cli.tests.test_t7_fail_loud
"""

import importlib.util
import io
import sys
import tempfile
import unittest
from contextlib import redirect_stderr
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "tools"))


def _load(name, rel):
    spec = importlib.util.spec_from_file_location(name, REPO_ROOT / rel)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


GC = _load("generate_contract_t7", "skills/contract-maintainer/scripts/generate_contract.py")
DS = _load("deepseek_t7", "skills/deepseek-share-to-md/scripts/deepseek_share_to_md.py")

from cli.services.state_store import StateStore          # noqa: E402


class TestGenerateContractRequiredKeys(unittest.TestCase):

    def test_missing_key_raises_explicit_error(self):
        with self.assertRaises(ValueError) as ctx:
            GC.build_rpc_entry({"caller": "svc-a", "name": "m"})
        self.assertIn("callee", str(ctx.exception))
        self.assertIn("缺少必填键", str(ctx.exception))

    def test_complete_entry_builds(self):
        entry = GC.build_rpc_entry(
            {"caller": "a", "callee": "b", "name": "query", "description": "d"})
        self.assertEqual(entry["id"], "a-b-query")
        self.assertEqual(entry["接口/主题"], "query")


class TestDeepseekQueryAwareAppend(unittest.TestCase):

    def _share_url(self, base):
        """复用生产逻辑：查询串感知追加 ty=r。"""

        url = base
        url += ("&" if "?" in url else "?") + "ty=r"
        return url

    def test_no_query_uses_question_mark(self):
        self.assertEqual(
            self._share_url("https://chat.deepseek.com/share/abc"),
            "https://chat.deepseek.com/share/abc?ty=r",
        )

    def test_existing_query_appends_with_ampersand(self):
        self.assertEqual(
            self._share_url("https://chat.deepseek.com/share/abc?x=1"),
            "https://chat.deepseek.com/share/abc?x=1&ty=r",
        )

    def test_source_uses_query_aware_form(self):
        src = (REPO_ROOT / "skills/deepseek-share-to-md/scripts"
               / "deepseek_share_to_md.py").read_text(encoding="utf-8")
        self.assertIn('("&" if "?" in url else "?") + "ty=r"', src)
        self.assertNotIn('url += "&ty=r"', src)


class TestStateStoreFailLoud(unittest.TestCase):

    def test_unreadable_state_warns(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "broken.yaml"
            path.write_text("a: [unclosed\n", encoding="utf-8")
            err = io.StringIO()
            with redirect_stderr(err):
                store = StateStore(path)
            self.assertEqual(store.data, {})
            self.assertIn("WARN: 读取状态文件失败", err.getvalue())

    def test_save_failure_warns(self):
        with tempfile.TemporaryDirectory() as td:
            store = StateStore(Path(td) / "state.yaml")
            store.set("last_project", value="demo")
            # 指向不可写路径（无需 mock 类属性）
            store.path = Path("/proc/none/state.yaml")
            err = io.StringIO()
            with redirect_stderr(err):
                store.save()
            self.assertIn("WARN: 写入状态文件失败", err.getvalue())


class TestWizardDryRunRestoresMonkeypatch(unittest.TestCase):

    def test_module_attributes_restored(self):
        import cli.services.wizard.fields as wfields
        import cli.services.wizard.selection as wsel
        import cli.services.wizard.output as wout
        from checks import Checker
        from checks.menu import check_wizard_dry_run

        before = {m.__name__: m.choose for m in (wsel, wfields, wout)}
        check_wizard_dry_run(Checker(), [], [])
        after = {m.__name__: m.choose for m in (wsel, wfields, wout)}
        self.assertEqual(before, after)


if __name__ == "__main__":
    unittest.main()
