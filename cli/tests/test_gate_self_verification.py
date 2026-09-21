#!/usr/bin/env python3
"""P60 门禁自校验 —— 关键声明式规则的正反例自测。

来源：2026-09-21 外部盲检（11 项缺陷中 5 项属「门禁自身静默失效」）。
本文件把「声明式规则」变成可测对象：每条规则都要**正例命中 + 负例不命中**，
防止「规则写错但静默失效」（本次 V3/V5 即此类）。

覆盖：
- repo-lint 工作流关键词豁免正则（V3）
- agent-debug-diagnosis 危险命令守卫正则（V5）
- path-audit 显式相对引用正则（P60 §5.3，含省略号路径误报回归）
- tests_collected 校验器本身（P60 §5.1：故意弄坏必须报）

Run:
    python -m unittest cli/tests/test_gate_self_verification.py
"""

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
TOOLS = REPO_ROOT / "tools"
SKILL_SCRIPTS = REPO_ROOT / "skills" / "agent-debug-diagnosis" / "scripts"

sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(TOOLS))
sys.path.insert(0, str(SKILL_SCRIPTS))

from checks import Checker                    # noqa: E402
from checks import tests_collected as tc      # noqa: E402

import agentdebug_common                      # noqa: E402


def _load(name):
    spec = importlib.util.spec_from_file_location(
        name.replace("-", "_"), TOOLS / f"{name}.py"
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class TestRepoLintExemptionRule(unittest.TestCase):
    """repo-lint 工作流关键词豁免（V3：`)\\b` 写成字面反斜杠 → 豁免永不匹配）。"""

    @classmethod
    def setUpClass(cls):
        cls.mod = _load("repo-lint")
        cls.re = cls.mod.WORKFLOW_KEYWORD_RE

    def test_positive_cases_match(self):
        for body in ("Purpose: 说明", "Workflow 入口", "Runtime", "Exit Criteria now",
                     "Stopping Conditions", "Guardrails"):
            self.assertTrue(self.re.match(body), f"应命中: {body!r}")

    def test_negative_cases_do_not_match(self):
        for body in ("# Purpose", "not-a-keyword", "Runtimeish", "purpose: x", ""):
            self.assertFalse(self.re.match(body), f"不应命中: {body!r}")


class TestDangerousCommandGuard(unittest.TestCase):
    """危险命令守卫（V5：外层 `\\b` 使 `rm -rf /` 分支不可达）。"""

    POSITIVE = (
        "rm -rf /",
        "rm -rf /tmp",
        "rm -rf / ",
        "git push --force",
        "drop table users",
        "mkfs /dev/sda",
        "shutdown -h now",
        "reboot",
    )
    NEGATIVE = ("ls -la", "xmkfs", "echo hello", "git push origin main")

    def test_positive_cases_detected(self):
        for cmd in self.POSITIVE:
            self.assertTrue(
                agentdebug_common.DANGEROUS_COMMAND_RE.search(cmd),
                f"应检出: {cmd!r}",
            )

    def test_negative_cases_not_detected(self):
        for cmd in self.NEGATIVE:
            self.assertFalse(
                agentdebug_common.DANGEROUS_COMMAND_RE.search(cmd),
                f"不应检出: {cmd!r}",
            )


class TestPathAuditDotRelativeRule(unittest.TestCase):
    """path-audit 显式相对引用正则（P60 §5.3）。"""

    @classmethod
    def setUpClass(cls):
        cls.mod = _load("path-audit")

    def test_matches_explicit_relative_ref(self):
        found = self.mod.DOT_REL_RE.findall(
            "Read [CLI-ONESHOT.md](./references/CLI-ONESHOT.md) first."
        )
        self.assertEqual(found, ["./references/CLI-ONESHOT.md"])

    def test_ignores_ellipsis_path_tail(self):
        # 回归：`.../AuditTypeEnum.java` 的尾部曾误匹配为 `./AuditTypeEnum.java`
        found = self.mod.DOT_REL_RE.findall("Modified: api/.../AuditTypeEnum.java")
        self.assertEqual(found, [])

    def test_placeholder_forms_are_matched_so_they_count_as_placeholders(self):
        # 正则**故意**匹配 `{x}`/`*` 形态：由 main() 将其计为 placeholders 而非 broken
        for text in ("./references/{x}.md", "./a/*.md"):
            self.assertEqual(self.mod.DOT_REL_RE.findall(text), [text])

    def test_angle_bracket_form_does_not_match(self):
        self.assertEqual(self.mod.DOT_REL_RE.findall("./references/<name>.md"), [])


class TestTestsCollectedChecker(unittest.TestCase):
    """tests_collected 校验器本身（故意弄坏 → 必须报）。"""

    def setUp(self):
        self._td = tempfile.TemporaryDirectory()
        self.root = Path(self._td.name)
        (self.root / "cli" / "tests").mkdir(parents=True)
        self._old_root = tc.ROOT
        tc.ROOT = self.root
        self._purge()

    def _purge(self):
        # unittest 按名字导入会命中 sys.modules 缓存（会让临时根失效）→ 先清掉
        for name in [n for n in sys.modules if n == "cli" or n.startswith("cli.tests")]:
            del sys.modules[name]

    def tearDown(self):
        tc.ROOT = self._old_root
        self._purge()
        self._td.cleanup()

    def _errors(self):
        c = Checker()
        tc.check_tests_collected(c)
        return c.errors

    def test_nested_test_method_is_reported(self):
        (self.root / "cli" / "tests" / "test_probe_nested.py").write_text(
            "import unittest\n\n\n"
            "class T(unittest.TestCase):\n"
            "    def test_ok(self):\n"
            "        pass\n\n\n"
            'if __name__ == "__main__":\n'
            "    unittest.main()\n\n"
            "    def test_hidden(self):\n"
            "        pass\n",
            encoding="utf-8",
        )
        errors = self._errors()
        self.assertTrue(
            any("never collected" in e and "test_hidden" in e for e in errors), errors
        )

    def test_declared_vs_collected_mismatch_is_reported(self):
        (self.root / "cli" / "__init__.py").write_text("", encoding="utf-8")
        (self.root / "cli" / "tests" / "__init__.py").write_text("", encoding="utf-8")
        (self.root / "cli" / "tests" / "test_probe_mismatch.py").write_text(
            "import unittest\n\n\n"
            "def test_module_level():\n"          # 声明但 unittest 不收集
            "    pass\n\n\n"
            "class T(unittest.TestCase):\n"
            "    def test_ok(self):\n"
            "        pass\n",
            encoding="utf-8",
        )
        errors = self._errors()
        self.assertTrue(
            any("declared 2" in e and "collects 1" in e for e in errors), errors
        )

    def test_consistent_file_has_no_error(self):
        (self.root / "cli" / "__init__.py").write_text("", encoding="utf-8")
        (self.root / "cli" / "tests" / "__init__.py").write_text("", encoding="utf-8")
        (self.root / "cli" / "tests" / "test_probe_clean.py").write_text(
            "import unittest\n\n\n"
            "class T(unittest.TestCase):\n"
            "    def test_a(self):\n"
            "        pass\n"
            "    def test_b(self):\n"
            "        pass\n",
            encoding="utf-8",
        )
        self.assertEqual(self._errors(), [])