#!/usr/bin/env python3
"""Menu package regression tests (P1 modularization / C4).

Verifies the modularized cli/utils/menu/ package exposes the same public
API and behavior as the former single-file menu.py: imports, Section,
non-TTY fallbacks for choose / choose_many / ask_text.

Run:
    python -m unittest discover -s cli/tests
"""

import os
import subprocess
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))


class TestMenuPublicAPI(unittest.TestCase):
    """The package must re-export the original public symbols."""

    def test_public_symbols(self):
        from cli.utils import menu

        for name in (
            "BACK",
            "Section",
            "ask_path",
            "ask_text",
            "choose",
            "choose_many",
            "e",
            "icons_enabled",
            "is_tty",
            "screen_enter",
            "screen_exit",
        ):
            self.assertTrue(hasattr(menu, name), f"menu missing {name}")

    def test_section_text_attr(self):
        from cli.utils.menu import Section

        s = Section("group")
        self.assertEqual(s.text, "group")

    def test_back_is_sentinel(self):
        from cli.utils.menu import BACK

        self.assertIsNotNone(BACK)


class TestMenuFallbacks(unittest.TestCase):
    """Non-TTY fallback behavior must match the original."""

    def _run_no_tty(self, script, stdin):
        env = dict(os.environ)
        env["NO_TTY"] = "1"
        env["NO_ICONS"] = "1"
        return subprocess.run(
            [sys.executable, "-c", script],
            input=stdin,
            capture_output=True,
            text=True,
            env=env,
            cwd=str(REPO_ROOT),
        )

    def test_choose_fallback(self):
        code = (
            "import sys; sys.path.insert(0, '.')\n"
            "from cli.utils.menu import choose\n"
            "r = choose('pick', ['A','B','C'])\n"
            "print('RESULT', r)\n"
        )
        p = self._run_no_tty(code, "2\n")
        self.assertIn("RESULT 1", p.stdout)

    def test_choose_many_fallback(self):
        code = (
            "import sys; sys.path.insert(0, '.')\n"
            "from cli.utils.menu import choose_many\n"
            "r = choose_many('pick', ['X','Y','Z'])\n"
            "print('RESULT', r)\n"
        )
        p = self._run_no_tty(code, "1,3\n")
        self.assertIn("RESULT [0, 2]", p.stdout)

    def test_choose_many_max_visible_truncates_display(self):
        # max_visible：初始仅显示前 N 个，但仍可输入任意编号选中
        code = (
            "import sys; sys.path.insert(0, '.')\n"
            "from cli.utils.menu import choose_many\n"
            "opts = ['r%d' % i for i in range(15)]\n"
            "r = choose_many('pick', opts, max_visible=5)\n"
            "print('RESULT', r)\n"
        )
        # 选中第 12 个（编号 12 > max_visible 5）——仍可选
        p = self._run_no_tty(code, "12\n")
        self.assertIn("RESULT [11]", p.stdout)
        # 渲染截断提示存在
        self.assertIn("共 15 个", p.stdout)

    def test_ask_text_fallback(self):
        code = (
            "import sys; sys.path.insert(0, '.')\n"
            "from cli.utils.menu import ask_text\n"
            "r = ask_text('say: ')\n"
            "print('RESULT', r)\n"
        )
        p = self._run_no_tty(code, "hello\n")
        self.assertIn("RESULT hello", p.stdout)

    def test_choose_back_key(self):
        code = (
            "import sys; sys.path.insert(0, '.')\n"
            "from cli.utils.menu import choose, BACK\n"
            "r = choose('pick', ['A','B'])\n"
            "print('RESULT', r is BACK)\n"
        )
        p = self._run_no_tty(code, "b\n")
        self.assertIn("RESULT True", p.stdout)


if __name__ == "__main__":
    unittest.main()


class TestRawKeyUtf8(unittest.TestCase):
    """Regression: raw-mode key reading must survive multi-byte UTF-8 input
    (2026-09-11: typing a CJK filter char crashed _read_raw with
    UnicodeDecodeError on the lead byte)."""

    def _call_read_raw(self, bytes_seq):
        """Feed bytes one at a time via a fake os.read, skip _data_ready
        (continuation bytes always available)."""

        from unittest import mock

        import cli.utils.menu.keys as keys

        pending = list(bytes_seq)

        def fake_read(fd, n):
            if pending:
                return pending.pop(0)
            return b""

        with mock.patch.object(keys.os, "read", side_effect=fake_read), \
                mock.patch.object(keys, "_data_ready", return_value=True):
            return keys._read_raw(0, 1)

    def test_cjk_char_decodes(self):
        # '测' = e6 b5 8b
        self.assertEqual(
            self._call_read_raw([b"\xe6", b"\xb5", b"\x8b"]),
            "测",
        )

    def test_ascii_single_byte(self):
        self.assertEqual(self._call_read_raw([b"a"]), "a")

    def test_esc_byte_unchanged(self):
        self.assertEqual(self._call_read_raw([b"\x1b"]), "\x1b")

    def test_lone_lead_byte_falls_back_without_crash(self):
        # 孤立 lead byte（无续字节）不得抛 UnicodeDecodeError
        from unittest import mock

        import cli.utils.menu.keys as keys

        with mock.patch.object(keys.os, "read", return_value=b"\xe3"), \
                mock.patch.object(keys, "_data_ready", return_value=False):
            value = keys._read_raw(0, 1)
            self.assertTrue(isinstance(value, str))


if __name__ == "__main__":
    unittest.main()
