#!/usr/bin/env python3
"""T6a 加固回归测试（2026-09-21 外部盲检第二批·代码层 11 条）。

覆盖：
- C1 agent_detect：含空格路径必须引号包裹（shell=True 分词）
- C2 prompt_builder：environment 必须贯穿到 paths()
- C3 clipboard：后端不可用时降级返回 False，不抛异常
- C4 checks/workflow.check_frontmatter_consistency(only=…) 与 check-contract --files 映射
- C5 checkstyle：配置挂 SuppressionFilter，且 suppressions.xml 必须是合法 XML
   （实测发现的更深缺陷：注释内 `--` 使该文件无法被任何 XML 解析器读取）
- C6 repo-lint：单行 docstring 之后的注释仍被检查；三引号字符串内文不误报
- C9 spec_updater：生成脚本路径按仓根解析且存在
- C10 generate_contract：YAML 解析失败被记录（不再静默）
- C11 generate_contract：描述型「切库规则」不再恒定 ERROR
- 附：外部盲检 BLOCKER —— deepseek_share_to_md.is_binary 中文误判（两评委均命中）

Run:
    python -m unittest cli/tests/test_t6a_hardening.py
"""

import importlib.util
import sys
import tempfile
import unittest
import unittest.mock
import xml.dom.minidom
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
TOOLS = REPO_ROOT / "tools"

sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(TOOLS))

from cli.services import agent_detect            # noqa: E402
from cli.utils import clipboard                  # noqa: E402
from checks import Checker                       # noqa: E402
from checks import workflow as wf_mod            # noqa: E402


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class TestLaunchCommandQuoting(unittest.TestCase):
    """C1：未引号路径在 shell=True 下会被分词。"""

    class Cfg:

        def __init__(self, command=None):
            self._command = command

        def provider_command(self, name):
            return self._command or name

    def _resolve(self, path):
        with unittest.mock.patch.object(
            agent_detect, "detect_agent",
            return_value={"installed": True, "path": path},
        ):
            return agent_detect.resolve_launch_command(self.Cfg(command=None), "aider")

    def test_path_with_space_is_quoted(self):
        out = self._resolve("/mnt/c/Program Files/node/pi")
        self.assertTrue(out.startswith('"') and out.endswith('"'), out)

    def test_plain_path_unchanged(self):
        self.assertEqual(self._resolve("/home/u/.qoder/qoder"), "/home/u/.qoder/qoder")


class TestPromptBuilderEnvironment(unittest.TestCase):
    """C2：--environment 必须传到 paths()。"""

    def test_environment_threaded_to_paths(self):
        from cli.services import environment as env_mod
        from cli.services.prompt_builder import PromptBuilder

        seen = {}

        def fake_paths(root, name=None):
            seen["name"] = name
            return {}

        with unittest.mock.patch.object(env_mod, "paths", fake_paths):
            b = PromptBuilder(environment="prod")
            b._resolve_root_placeholders("{workspace_root}")

        self.assertEqual(seen.get("name"), "prod")


class TestClipboardDegrades(unittest.TestCase):
    """C3：剪贴板不可用不得抛异常（否则提示词生成后崩溃）。"""

    def test_backend_raising_returns_false(self):
        class Boom:
            @staticmethod
            def copy(text):
                raise RuntimeError("no clipboard backend")

        with unittest.mock.patch.dict(sys.modules, {"pyperclip": Boom}):
            self.assertFalse(clipboard.copy("hello"))

    def test_missing_module_returns_false(self):
        with unittest.mock.patch.dict(sys.modules, {"pyperclip": None}):
            self.assertFalse(clipboard.copy("hello"))

    def test_success_returns_true(self):
        class Ok:
            copied = []

            @classmethod
            def copy(cls, text):
                cls.copied.append(text)

        with unittest.mock.patch.dict(sys.modules, {"pyperclip": Ok}):
            self.assertTrue(clipboard.copy("hello"))
        self.assertEqual(Ok.copied, ["hello"])


class TestContractSubsetCheck(unittest.TestCase):
    """C4：按 staged 收窄校验范围。"""

    def test_affected_mapping(self):
        cc = _load("check_contract", TOOLS / "check-contract.py")
        names = cc._affected(
            "workflows/alpha.md,templates/runtime/runtime-beta.md,"
            "config/workflows/gamma.yaml,docs/readme.md"
        )
        self.assertEqual(names, {"alpha", "beta", "gamma"})

    def test_no_files_means_all(self):
        cc = _load("check_contract", TOOLS / "check-contract.py")
        self.assertIsNone(cc._affected(""))

    def test_only_restricts_frontmatter_check(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "workflows").mkdir()
            broken = "---\nname: a\nworkflow:\n  inputs:\n    required: [X]\n  outputs:\n    base: \"reports/\"\n---\n# W\n\n## Inputs\n\nRequired:\n\n- None\n"
            (root / "workflows" / "a.md").write_text(broken, encoding="utf-8")
            (root / "workflows" / "b.md").write_text(
                broken.replace("name: a", "name: b"), encoding="utf-8")

            old_root = wf_mod.ROOT
            wf_mod.ROOT = root
            try:
                c = Checker()
                wf_mod.check_frontmatter_consistency(c, only={"a"})
                self.assertTrue(all("a.md" in e for e in c.errors), c.errors)
                self.assertTrue(c.errors)
            finally:
                wf_mod.ROOT = old_root


class TestCheckstyleSuppressionWiring(unittest.TestCase):
    """C5：抑制清单必须真正可加载（配置挂载 + XML 合法）。"""

    def test_config_declares_suppression_filter(self):
        cfg = (REPO_ROOT / "tools" / "checkstyle" / "checkstyle.xml").read_text(
            encoding="utf-8")
        self.assertIn("SuppressionFilter", cfg)
        self.assertIn('name="optional"', cfg)

    def test_suppressions_file_is_well_formed_xml(self):
        # 回归：注释内的 `--` 会让该文件无法被任何 XML 解析器读取
        xml.dom.minidom.parse(str(REPO_ROOT / "tools" / "checkstyle" / "suppressions.xml"))

    def test_no_illegal_double_hyphen_inside_comments(self):
        import re
        text = (REPO_ROOT / "tools" / "checkstyle" / "suppressions.xml").read_text(
            encoding="utf-8")
        for m in re.finditer(r"<!--(.*?)-->", text, re.S):
            self.assertNotIn("--", m.group(1), "XML 注释内不得出现 '--'")


class TestRepoLintTripleQuoteStateMachine(unittest.TestCase):
    """C6：单行 docstring 之后的注释仍被检查；字符串内文不误报。"""

    def _run(self, body: str):
        import subprocess
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "cli").mkdir()
            (root / "cli" / "probe.py").write_text(body, encoding="utf-8")
            r = subprocess.run(
                [sys.executable, str(TOOLS / "repo-lint.py"), "--repo-root", str(root),
                 "--verbose"],
                capture_output=True, text=True,
            )
            return r.stdout + r.stderr

    def test_comment_after_single_line_docstring_is_checked(self):
        out = self._run('def f():\n    """short docstring."""\n'
                        '    # english comment after docstring\n    return 1\n')
        self.assertIn("English comment", out)

    def test_multiline_docstring_inner_hash_lines_not_reported(self):
        out = self._run('def g():\n    """\n'
                        '    # not a comment: inside string\n    """\n    return 1\n')
        self.assertNotIn("English comment", out)


class TestSkillScriptFixes(unittest.TestCase):

    def test_c9_generate_script_resolves(self):
        su = _load("spec_updater", REPO_ROOT / "skills" / "spec-updater" / "scripts"
                   / "spec_updater.py")
        self.assertTrue(su.GENERATE_SCRIPT.is_file(), su.GENERATE_SCRIPT)

    def test_c10_yaml_error_is_recorded(self):
        gc = _load("generate_contract",
                   REPO_ROOT / "skills" / "contract-maintainer" / "scripts"
                   / "generate_contract.py")
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "m.md").write_text(
                "```yaml\nrpc: [ {a: 1,,} ]\n```\n", encoding="utf-8")
            gc.PARSE_PROBLEMS.clear()
            gc.parse_spec_yaml_blocks(str(root))
            self.assertTrue(gc.PARSE_PROBLEMS, "YAML 解析失败必须被记录")

    def test_c11_description_value_skips_field_check(self):
        gc = _load("generate_contract",
                   REPO_ROOT / "skills" / "contract-maintainer" / "scripts"
                   / "generate_contract.py")
        specs = [{"调用方": "svc", "被调用方": "tgt", "接口/主题": "x",
                  "_fields": ["enterpriseId"]}]
        scenarios = [{"场景引用": "S1", "服务": "svc",
                      "切库规则": "订单参数/来源描述"}]
        self.assertEqual(gc.validate_fields(specs, scenarios), [])

    def test_c11_real_field_name_still_checked(self):
        gc = _load("generate_contract",
                   REPO_ROOT / "skills" / "contract-maintainer" / "scripts"
                   / "generate_contract.py")
        specs = [{"调用方": "svc", "被调用方": "tgt", "接口/主题": "x",
                  "_fields": ["enterpriseId"]}]
        scenarios = [{"场景引用": "S1", "服务": "svc", "切库规则": "notAField"}]
        errs = gc.validate_fields(specs, scenarios)
        self.assertTrue(any("notAField" in e for e in errs), errs)

class TestIsBinaryBlockerFix(unittest.TestCase):
    """外部盲检 BLOCKER（两评委均命中）：中文 UTF-8 不得被判为二进制。

    原口径「解码字符数/字节数 < 0.9」在中文上约 0.33 → 中文文本误判为二进制，
    导致含中文附件的分享导出把文本附件按二进制处理。
    """

    @classmethod
    def setUpClass(cls):
        cls.mod = _load(
            "deepseek_share_to_md",
            REPO_ROOT / "skills" / "deepseek-share-to-md" / "scripts"
            / "deepseek_share_to_md.py",
        )

    def test_chinese_text_is_not_binary(self):
        for payload in ("这是中文内容。", "中文" * 500, "中文 ABC 🚀 混排"):
            self.assertFalse(self.mod.is_binary(payload.encode("utf-8")), payload[:12])

    def test_truncated_multibyte_tail_tolerated(self):
        self.assertFalse(self.mod.is_binary(("中" * 2000).encode("utf-8")[:4096]))

    def test_english_text_is_not_binary(self):
        self.assertFalse(self.mod.is_binary(b"plain english text"))

    def test_binary_payloads_detected(self):
        for payload in (b"\x89PNG\r\n\x1a\n" + bytes(range(256)),
                        bytes(range(256)) * 8):
            self.assertTrue(self.mod.is_binary(payload))

    def test_nul_marks_binary(self):
        self.assertTrue(self.mod.is_binary(b"abc\x00def"))

    def test_empty_is_not_binary(self):
        self.assertFalse(self.mod.is_binary(b""))
