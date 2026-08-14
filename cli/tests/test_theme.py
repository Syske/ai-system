#!/usr/bin/env python3
"""UI theme loader tests (config/ui.yaml-driven colors).

Covers:
- theme loads from config/ui.yaml
- defaults applied when ui.yaml missing/incomplete
- render.py uses theme (no hardcoded ANSI in paint)
"""

import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))


class TestTheme(unittest.TestCase):

    def test_theme_loads_from_config(self):
        from cli.utils.menu import theme
        theme.reset()
        # 值存在且为 ANSI 序列 / 样式名
        self.assertEqual(theme.get("selected"), "\x1b[7m")
        self.assertEqual(theme.get("prompt"), "bold fg:ansicyan")
        self.assertIn("\x1b[", theme.get("reset"))

    def test_unknown_key_returns_default(self):
        from cli.utils.menu import theme
        theme.reset()
        self.assertEqual(theme.get("nonexistent", "fallback"), "fallback")

    def test_defaults_match_historical(self):
        from cli.utils.menu import theme
        theme.reset()
        self.assertEqual(theme.get("name"), "\x1b[1;36m")
        self.assertEqual(theme.get("desc"), "\x1b[2;90m")
        self.assertEqual(theme.get("selected"), "\x1b[7m")

    def test_paint_uses_theme(self):
        from cli.utils.menu.render import _paint
        # 渲染含主题色（非裸文本）
        out = _paint("demo — desc", selected=True)
        self.assertIn("\x1b[7m", out)     # selected
        self.assertIn("\x1b[1;36m", out)  # name
        self.assertIn("\x1b[2;90m", out)  # desc


if __name__ == "__main__":
    unittest.main()
