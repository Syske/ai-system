#!/usr/bin/env python3
"""机器层环境配置（~/.config/ai-system/env.yaml）测试。

覆盖：
- home_config_path 支持 AI_HOME_CONFIG 覆盖（测试/多配置场景）
- _deep_merge：home 优先、嵌套 dict 递归合并
- load_merged_environment：home build 覆盖 workspace local.yaml，其余保留
- tools/setup.py::generate_home_env：首启生成（非破坏：已存在则跳过）、平台检测落盘

Run:
    python -m unittest cli/tests/test_home_env.py
"""

import os
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from cli.services import environment  # noqa: E402
from cli.services.environment import (  # noqa: E402
    _deep_merge,
    home_config_path,
    load_home_environment,
    load_merged_environment,
)


class TestHomeConfigPath(unittest.TestCase):

    def test_default_is_dot_config(self):
        # 默认 ~/.config/ai-system/env.yaml（跨平台原生）
        os.environ.pop("AI_HOME_CONFIG", None)
        p = home_config_path()
        self.assertEqual(
            p,
            Path.home() / ".config" / "ai-system" / "env.yaml",
        )

    def test_env_override(self):
        os.environ["AI_HOME_CONFIG"] = "/tmp/ai-test-env.yaml"
        try:
            self.assertEqual(
                home_config_path(),
                Path("/tmp/ai-test-env.yaml"),
            )
        finally:
            os.environ.pop("AI_HOME_CONFIG", None)


class TestDeepMerge(unittest.TestCase):

    def test_home_wins_scalar(self):
        merged = _deep_merge(
            {"build": {"java_home": "ws-java", "backend": "maven"}},
            {"build": {"java_home": "home-java"}},
        )
        self.assertEqual(merged["build"]["java_home"], "home-java")
        self.assertEqual(merged["build"]["backend"], "maven")

    def test_nested_merge_recursive(self):
        merged = _deep_merge(
            {"a": {"b": {"c": 1, "d": 2}}},
            {"a": {"b": {"c": 9}}},
        )
        self.assertEqual(merged, {"a": {"b": {"c": 9, "d": 2}}})

    def test_new_keys_added(self):
        merged = _deep_merge({"x": 1}, {"y": {"z": 2}})
        self.assertEqual(merged, {"x": 1, "y": {"z": 2}})


class TestLoadMerged(unittest.TestCase):

    def setUp(self):
        # 临时 ai-system 根：config/environments/local.yaml（workspace 层）
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name) / "ai-system"
        env_dir = self.root / "config" / "environments"
        env_dir.mkdir(parents=True)
        (env_dir / "local.yaml").write_text(
            "workspace:\n"
            "  root: /ws/derived\n"
            "build:\n"
            "  java_home: ws-java\n"
            "  backend: maven\n"
            "bugfix:\n"
            "  mode: hotfix\n",
            encoding="utf-8",
        )

        # 机器层 home 配置（临时文件）
        self.home_file = Path(self._tmp.name) / "home" / "env.yaml"
        self.home_file.parent.mkdir(parents=True)
        self.home_file.write_text(
            "workspace:\n"
            "  root: /ws/home-anchor\n"
            "build:\n"
            "  java_home: /mnt/d/tools/java/jdk8\n",
            encoding="utf-8",
        )
        self._old = os.environ.get("AI_HOME_CONFIG")
        os.environ["AI_HOME_CONFIG"] = str(self.home_file)

    def tearDown(self):
        if self._old is None:
            os.environ.pop("AI_HOME_CONFIG", None)
        else:
            os.environ["AI_HOME_CONFIG"] = self._old
        self._tmp.cleanup()

    def test_merged_home_wins(self):
        merged = load_merged_environment(self.root)
        # home 覆盖 build.java_home 与 workspace.root
        self.assertEqual(
            merged["build"]["java_home"],
            "/mnt/d/tools/java/jdk8",
        )
        self.assertEqual(merged["workspace"]["root"], "/ws/home-anchor")
        # workspace 层保留未覆盖键
        self.assertEqual(merged["build"]["backend"], "maven")
        self.assertEqual(merged["bugfix"]["mode"], "hotfix")

    def test_load_home_environment(self):
        home = load_home_environment()
        self.assertEqual(
            home["build"]["java_home"],
            "/mnt/d/tools/java/jdk8",
        )

    def test_paths_use_home_anchor(self):
        ps = environment.paths(self.root)
        # home 的 workspace.root 生效 → workspace_root 随之
        self.assertEqual(str(ps["workspace_root"]), "/ws/home-anchor")


class TestGenerateHomeEnv(unittest.TestCase):

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.home_file = Path(self._tmp.name) / "env.yaml"
        self._old = os.environ.get("AI_HOME_CONFIG")
        os.environ["AI_HOME_CONFIG"] = str(self.home_file)

    def tearDown(self):
        if self._old is None:
            os.environ.pop("AI_HOME_CONFIG", None)
        else:
            os.environ["AI_HOME_CONFIG"] = self._old
        self._tmp.cleanup()

    def test_generate_and_skip(self):
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "setup_mod",
            REPO_ROOT / "tools" / "setup.py",
        )
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)

        ws = Path(self._tmp.name) / "ws"
        ws.mkdir()

        created = mod.generate_home_env(ws, interactive=False)
        self.assertTrue(created)
        self.assertTrue(self.home_file.exists())
        text = self.home_file.read_text(encoding="utf-8")
        self.assertIn("workspace", text)
        self.assertIn("build", text)
        self.assertIn("java_home", text)

        # 非破坏：再次调用跳过
        created2 = mod.generate_home_env(ws, interactive=False)
        self.assertFalse(created2)


if __name__ == "__main__":
    unittest.main()
