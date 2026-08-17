#!/usr/bin/env python3
"""C1 test base — CLI services tests (no LLM / no network / no TTY).

First batch of the CLI test foundation (CLI-STANDARDIZATION C1). Covers the
pure-logic services that the command layer depends on, so later refactors
(C2 field drift, C3 docs, C4 code organization) can be done with a regression
net.

Run:
    python -m unittest discover -s cli/tests
"""

import sys
import unittest
from pathlib import Path

# Make cli/ importable from anywhere (tests may run from repo root or cli/)
REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from cli.services.menu_config import MenuConfig  # noqa: E402
from cli.services.prompt_builder import PromptBuilder  # noqa: E402

ROOT = REPO_ROOT


class TestMenuConfig(unittest.TestCase):
    """MenuConfig: YAML loading, i18n, command_fields resolution."""

    def setUp(self):
        self.mc = MenuConfig(ROOT)

    def test_load_menu(self):
        sections = self.mc.get("sections", [])
        self.assertTrue(isinstance(sections, list))
        self.assertGreater(len(sections), 0)

    def test_locale_resolved(self):
        # menu.yaml must define a locale (i18n selector)
        locale = self.mc.get("locale", "")
        self.assertTrue(isinstance(locale, str))
        self.assertNotEqual(locale, "")

    def test_command_fields_exists(self):
        fields = self.mc.command_fields("propose")
        # propose is registered; fields may be empty or populated, but the
        # lookup must not raise and must return a list
        self.assertTrue(isinstance(fields, list))

    def test_command_fields_missing_name(self):
        fields = self.mc.command_fields("no-such-command-xyz")
        # unknown commands fall back to default_command_fields (may be empty)
        self.assertTrue(isinstance(fields, list))

    def test_i18n_resolves(self):
        # t() must return a string (default or translated) without raising
        label = self.mc.t("menu.title", default="MENU")
        self.assertTrue(isinstance(label, str))

    def test_missing_i18n_returns_default(self):
        label = self.mc.t("no.such.path", default="FALLBACK")
        self.assertEqual(label, "FALLBACK")

    def test_menu_option(self):
        opt = self.mc.menu_option("commands_changes", "propose")
        # returns a section entry dict or empty string; must not raise
        self.assertTrue(opt is None or opt == "" or isinstance(opt, dict))


class TestPromptBuilder(unittest.TestCase):
    """PromptBuilder: workflow/command prompt construction."""

    def setUp(self):
        self.pb = PromptBuilder()

    def test_build_workflow_prompt(self):
        prompt = self.pb.build(workflow="develop", context={})
        self.assertTrue(isinstance(prompt, str))
        self.assertGreater(len(prompt), 0)

    def test_build_command_prompt(self):
        prompt = self.pb.build(workflow="scan", context={})
        self.assertTrue(isinstance(prompt, str))
        self.assertGreater(len(prompt), 0)

    def test_build_unknown_raises(self):
        with self.assertRaises((RuntimeError, KeyError, ValueError)):
            self.pb.build(workflow="no-such-thing-xyz", context={})

    def test_workflow_prompt_skeletonized(self):
        # runtime 骨架化：Phase 标题保留 + 源文件引用，体积缩减
        prompt = self.pb.build(workflow="release", context={})
        self.assertIn("# Phase 1", prompt)
        self.assertIn("Full runtime template", prompt)
        # 骨架化后显著小于全量 runtime（release 原 ~16K 字符）
        self.assertLess(len(prompt), 8000)

    def test_workflow_prompt_prefix_stable(self):
        # 同一工作流不同输入 → 前缀稳定（缓存优化：静态前置/动态后置）
        p1 = self.pb.build(workflow="develop", context={"Project ID": "a"})
        p2 = self.pb.build(workflow="develop", context={"Project ID": "b"})
        # 动态输入在末尾（# Task 段之后）
        i1 = p1.find("# Task")
        self.assertGreater(i1, 0)
        # 前缀（# Task 之前）完全一致
        self.assertEqual(p1[:i1], p2[:i1])

    def test_command_prompt_not_skeletonized(self):
        # 命令 prompt 保留完整命令文档（不骨架化）
        prompt = self.pb.build(workflow="maintain", context={"Mode": "weekly"})
        self.assertIn("**Steps**", prompt)


if __name__ == "__main__":
    unittest.main()


class TestMenuConfigRegression(unittest.TestCase):
    """C2 regression: relative-path root and command_fields registration."""

    def test_relative_root_loads_menu(self):
        # Regression: string relative root used to silently load empty menu
        mc = MenuConfig(".")
        self.assertGreater(len(mc.menu.get("sections", [])), 0)
        self.assertIn("command_fields", mc.menu)

    def test_c2_fields_registered(self):
        # C2: propose/apply/archive/explore must have command_fields
        mc = MenuConfig(ROOT)
        for cmd in ("propose", "apply", "archive", "explore"):
            fields = mc.command_fields(cmd)
            self.assertGreater(len(fields), 0, f"{cmd} missing command_fields")

    def test_fields_shape(self):
        mc = MenuConfig(ROOT)
        for cmd in ("propose", "apply", "archive", "explore"):
            for field, required in mc.command_fields(cmd):
                self.assertIsInstance(field, str)
                self.assertIsInstance(required, bool)


class TestSkillModeRouting(unittest.TestCase):
    """Unified /aic-skill: mode routing and mode_choices."""

    def test_providers_skill_modes(self):
        # skill command offers launch/optimize modes
        from cli.services import providers
        from cli.services.menu_config import MenuConfig

        mc = MenuConfig(ROOT)

        class FakeWizard:
            target_name = "skill"

        modes = providers.mode_choices(FakeWizard(), {})
        self.assertIn("launch", modes)
        self.assertNotIn("optimize", modes)  # optimize 已归档解绑

    def test_providers_maintain_modes_unchanged(self):
        from cli.services import providers

        class FakeWizard:
            target_name = "maintain"

        modes = providers.mode_choices(FakeWizard(), {})
        self.assertEqual(modes, ["weekly", "monthly", "quarterly", "on-demand"])

    def test_run_skill_unknown_mode_falls_back(self):
        from unittest.mock import patch
        from cli.services import skill_launcher

        with patch("cli.services.skill_launcher.run", return_value=("p", "a")):
            result = skill_launcher.run_skill(None, None, "bogus")
            self.assertEqual(result, ("p", "a"))

    def test_run_skill_optimize_falls_back(self):
        """optimize mode is decoupled after archiving skill-optimizer;
        it now falls back to run (like any unknown mode)."""
        from unittest.mock import patch
        from cli.services import skill_launcher

        with patch("cli.services.skill_launcher.run", return_value=("p", "a")):
            result = skill_launcher.run_skill(None, None, "optimize")
            self.assertEqual(result, ("p", "a"))
