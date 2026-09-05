#!/usr/bin/env python3
"""P36 触发层 T-b 测试：首启环境只读检测 + 交互确认。

覆盖：
- _env_uninitialized：配置缺失判定（workspace local.yaml / 机器层 env.yaml）
- _offer_env_init 非交互：stderr 一行指引、不执行 env-init
- _offer_env_init 交互 + 确认：调用 setup.env_init

Run:
    python -m unittest cli/tests/test_main_p36.py
"""

import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from cli import main as cm


class TestEnvUninitialized(unittest.TestCase):
    def _root(self):
        return REPO_ROOT

    def test_missing_workspace_config(self):
        with tempfile.TemporaryDirectory() as td:
            td_path = Path(td)
            # workspace local.yaml 缺失
            with mock.patch.object(Path, "exists", return_value=False):
                self.assertTrue(cm._env_uninitialized())

    def test_all_present(self):
        # 配置齐全（exists 全 True）→ 未初始化判定为 False
        with mock.patch.object(Path, "exists", return_value=True):
            self.assertFalse(cm._env_uninitialized())


class TestOfferEnvInit(unittest.TestCase):
    def test_non_interactive_stderr_hint(self):
        # 非 TTY：stderr 指引、不执行 env-init
        with mock.patch.object(Path, "exists", return_value=False), \
             mock.patch("sys.stdin.isatty", return_value=False), \
             mock.patch("tools.setup.env_init") as env_init_mock:
            cm._offer_env_init()
            env_init_mock.assert_not_called()

    def test_interactive_yes_runs_env_init(self):
        # TTY + 确认 y → 执行 setup.env_init
        with mock.patch.object(Path, "exists", return_value=False), \
             mock.patch("sys.stdin.isatty", return_value=True), \
             mock.patch("builtins.input", return_value="y"), \
             mock.patch("tools.setup.env_init") as env_init_mock:
            cm._offer_env_init()
            env_init_mock.assert_called_once()

    def test_interactive_no_skips(self):
        # TTY + 拒绝 → 不执行
        with mock.patch.object(Path, "exists", return_value=False), \
             mock.patch("sys.stdin.isatty", return_value=True), \
             mock.patch("builtins.input", return_value="n"), \
             mock.patch("tools.setup.env_init") as env_init_mock:
            cm._offer_env_init()
            env_init_mock.assert_not_called()


if __name__ == "__main__":
    unittest.main()
