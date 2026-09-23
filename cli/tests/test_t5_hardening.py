#!/usr/bin/env python3
"""T5 加固回归测试（2026-09-21 外部盲检第二批已核实缺陷）。

覆盖：
- bugfix_modes 契约校验：**不再执行** provider 代码；返回注解缺失 → WARN（失效必须响亮）；
  字段不匹配 → ERROR；字段匹配 → 静默通过
- prompt_builder `_skeletonize_runtime`：同一行文本重复时不再取错后续行
- pull.js：unzip 改为 execFileSync 数组传参（无 shell 解释）
- deepseek_share_to_md.save_file：远端文件名 `../` 不能写出目标目录

Run:
    python -m unittest cli/tests/test_t5_hardening.py
"""

import importlib.util
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
TOOLS = REPO_ROOT / "tools"
SKILL_SCRIPTS = REPO_ROOT / "skills" / "deepseek-share-to-md" / "scripts"

sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(TOOLS))
sys.path.insert(0, str(SKILL_SCRIPTS))

from checks import Checker                    # noqa: E402
from checks import bugfix_modes as bm         # noqa: E402


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class TestContractCheckIsStatic(unittest.TestCase):
    """T5-① ②：门禁不得执行 provider，且不得 fail-open。"""

    def setUp(self):
        self._td = tempfile.TemporaryDirectory()
        self.root = Path(self._td.name)

    def tearDown(self):
        self._td.cleanup()

    def _provider(self, body: str) -> Path:
        p = self.root / "branch_parser.py"
        p.write_text(body, encoding="utf-8")
        return p

    def test_provider_code_is_not_executed(self):
        # 模块级副作用可检测：探针调用若仍存在，会把标记写到文件
        marker = self.root / "SIDE_EFFECT"
        script = self._provider(f'''
from dataclasses import dataclass


@dataclass
class ParsedBranch:
    date: str
    type: str
    desc: str
    service: str


def parse(branch_name: str) -> ParsedBranch | None:
    open(r"{marker}", "w").write("called")      # 被调用即留下痕迹
    return None
''')
        c = Checker()
        bm._check_parser_contract(c, "t5", "t5-parser", script)
        self.assertFalse(marker.exists(), "门禁不应执行 provider 的 parse()")

    def test_matching_fields_pass(self):
        script = self._provider('''
from dataclasses import dataclass


@dataclass
class ParsedBranch:
    date: str
    type: str
    desc: str
    service: str


def parse(branch_name: str) -> ParsedBranch | None:
    return None
''')
        c = Checker()
        bm._check_parser_contract(c, "t5", "t5-parser", script)
        self.assertEqual(c.errors, [])
        self.assertEqual(c.warnings, [])

    def test_mismatched_fields_fail(self):
        script = self._provider('''
from dataclasses import dataclass


@dataclass
class ParsedBranch:
    date: str
    type: str
    desc: str


def parse(branch_name: str) -> ParsedBranch | None:
    return None
''')
        c = Checker()
        bm._check_parser_contract(c, "t5", "t5-parser", script)
        self.assertTrue(any("return fields" in e for e in c.errors), c.errors)

    def test_missing_annotation_is_loud_not_silent(self):
        # 原实现：探针恒返回 None → 直接 return（静默通过）。现在必须 WARN。
        script = self._provider('''
def parse(branch_name):
    return None
''')
        c = Checker()
        bm._check_parser_contract(c, "t5", "t5-parser", script)
        self.assertTrue(
            any("return annotation" in w for w in c.warnings),
            f"注解缺失必须响亮，实际 warnings={c.warnings} errors={c.errors}",
        )


class TestPromptBuilderSkeletonDuplicateLines(unittest.TestCase):
    """T5-③：同一行文本重复时不得取错后续行。"""

    def setUp(self):
        self.pb = _load("prompt_builder", REPO_ROOT / "cli" / "services" / "prompt_builder.py")

    def _instance(self):
        obj = self.pb.PromptBuilder.__new__(self.pb.PromptBuilder)
        obj.root = REPO_ROOT          # _skeletonize_runtime 需要 self.root 拼全量模板路径
        return obj

    def test_repeated_line_uses_current_position(self):
        # 两个 Phase 段落含完全相同的引导行；第二个 Phase 的列表项必须取自其后
        runtime = (
            "# Runtime: Demo\n\n"
            "## Phase 1 — First\n\n"
            "Collect:\n"
            "- first-item\n\n"
            "## Phase 2 — Second\n\n"
            "Collect:\n"
            "- second-item\n"
        )
        out = self.pb.PromptBuilder.__dict__["_skeletonize_runtime"](
            self._instance(), runtime, "runtime-demo.md"
        )
        self.assertIn("first-item", out)
        self.assertIn("second-item", out)
        # 关键：第二个 Collect 必须配到 second-item，而不是回退到 first-item
        second_block = out.split("Phase 2")[-1]
        self.assertIn("second-item", second_block)


class TestPullJsNoShellInterpolation(unittest.TestCase):

    @unittest.skipIf(shutil.which("node") is None, "node not available")
    def test_execfile_sync_does_not_expand_shell(self):
        # 行为验证：数组传参下 `$(...)`/引号不会被 shell 解释
        script = (
            "const {execFileSync} = require('child_process');"
            "execFileSync('/bin/echo', ['$(touch /tmp/t5_pwned)', '\"quoted\"'],"
            " {stdio: 'ignore'});"
        )
        Path("/tmp/t5_pwned").unlink(missing_ok=True)
        subprocess.run(["node", "-e", script], check=True)
        self.assertFalse(Path("/tmp/t5_pwned").exists(), "不得发生 shell 展开")

    def test_source_uses_execfile_not_template_exec(self):
        # skill-sync 已于 2026-09-23 经 Value-Burden 裁决归档；此处断言的是**归档快照**
        # （`archived/skills/skill-sync/scripts/pull.js`）仍保留 T5 的 execFileSync 修复，
        # 作为历史证据保留（恢复正常需重跑此断言）。
        src = (REPO_ROOT / "archived" / "skills" / "skill-sync" / "scripts" / "pull.js"
               ).read_text(encoding="utf-8")
        self.assertIn("execFileSync(", src)
        self.assertNotIn("execSync(`", src)


class TestSaveFileTraversal(unittest.TestCase):
    """T5-⑤：远端文件名不得穿越出目标目录。"""

    def setUp(self):
        self.mod = _load("deepseek_share_to_md", SKILL_SCRIPTS / "deepseek_share_to_md.py")
        self._td = tempfile.TemporaryDirectory()
        self.root = Path(self._td.name)
        self.dest = self.root / "attachments"
        self.dest.mkdir()

    def tearDown(self):
        self._td.cleanup()

    def test_parent_traversal_is_contained(self):
        rel = self.mod.save_file(b"x", str(self.dest), "../../escaped.txt")
        self.assertFalse((self.root / "escaped.txt").exists(), "不得写出目标目录")
        self.assertFalse((self.root.parent / "escaped.txt").exists())
        if rel:
            self.assertTrue((self.root / rel).resolve().is_relative_to(self.root))

    def test_absolute_path_is_contained(self):
        self.mod.save_file(b"x", str(self.dest), "/tmp/t5_abs_escape.txt")
        self.assertFalse(Path("/tmp/t5_abs_escape.txt").exists())

    def test_normal_name_written(self):
        rel = self.mod.save_file(b"hello", str(self.dest), "report.md")
        self.assertEqual((self.dest / "report.md").read_bytes(), b"hello")
        self.assertEqual(rel, "attachments/report.md")

    def test_windows_separator_traversal_contained(self):
        self.mod.save_file(b"x", str(self.dest), "..\\..\\escaped_win.txt")
        self.assertFalse((self.root / "escaped_win.txt").exists())