"""Tests for cli.services.agent_detect (auto-detect + merge with providers.yaml).

Covers: detect_agent signal order, scan cache, excluded_names semantics,
merge_picker_entries ordering / badges / opt-outs. Detection is mocked via
shutil.which patch — no real PATH dependence.
"""

import os
import sys
import unittest
from unittest import mock
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from cli.services import agent_detect


class FakeConfig:

    def __init__(self, providers, default="opencode"):
        self.provider_config = {"providers": providers, "default": {"provider": default}}

    def enabled_providers(self):
        return [
            name
            for name, cfg in (self.provider_config.get("providers", {}) or {}).items()
            if isinstance(cfg, dict) and cfg.get("enabled", True)
        ]

    def provider_meta(self):
        out = {}
        for name, cfg in (self.provider_config.get("providers", {}) or {}).items():
            if isinstance(cfg, dict):
                out[name] = {
                    "label": cfg.get("label") or name,
                    "icon": cfg.get("icon") or "",
                    "description": cfg.get("description") or "",
                }
        return out


def _reset_cache():
    agent_detect.scan_agents._cache = None


class DetectAgentTest(unittest.TestCase):

    def setUp(self):
        _reset_cache()

    @mock.patch("cli.services.agent_detect.shutil.which", return_value="/usr/bin/opencode")
    def test_detect_via_path(self, which):
        r = agent_detect.detect_agent("opencode")
        self.assertTrue(r["installed"])
        self.assertEqual(r["path"], "/usr/bin/opencode")
        self.assertEqual(r["via"], "path")

    @mock.patch("cli.services.agent_detect.shutil.which", return_value=None)
    @mock.patch("cli.services.agent_detect.Path.is_file", return_value=True)
    @mock.patch("cli.services.agent_detect.os.access", return_value=True)
    @mock.patch("cli.services.agent_detect.Path.exists", return_value=True)
    def test_detect_via_known_path(self, _w, _a, _p, _e):
        r = agent_detect.detect_agent("qoder")
        self.assertTrue(r["installed"])
        self.assertEqual(r["via"], "known-path")

    @mock.patch("cli.services.agent_detect.shutil.which", return_value=None)
    def test_detect_via_npm_bin(self, which):

        import tempfile

        with tempfile.TemporaryDirectory() as td:

            exe = Path(td) / "gemini"
            exe.write_text("#!/bin/sh\n")
            exe.chmod(0o755)

            with mock.patch(
                "cli.services.agent_detect._npm_global_bins",
                return_value=[Path(td)],
            ), mock.patch(
                "cli.services.agent_detect._windows_path_dirs",
                return_value=[],
            ):
                r = agent_detect.detect_agent("gemini")

        self.assertTrue(r["installed"])
        self.assertEqual(r["via"], "npm")

    @mock.patch("cli.services.agent_detect.shutil.which", return_value=None)
    def test_detect_via_windows_npm_cmd(self, which):

        import tempfile

        with tempfile.TemporaryDirectory() as td:

            (Path(td) / "opencode.cmd").write_text("@echo off\n")

            with mock.patch(
                "cli.services.agent_detect._npm_global_bins",
                return_value=[Path(td)],
            ), mock.patch(
                "cli.services.agent_detect._windows_path_dirs",
                return_value=[],
            ):
                r = agent_detect.detect_agent("opencode")

        self.assertTrue(r["installed"])
        self.assertEqual(r["via"], "npm-win")
        self.assertTrue(r["path"].endswith(".cmd"))

    @mock.patch("cli.services.agent_detect.shutil.which", return_value=None)
    def test_detect_via_windows_path_dir(self, which):

        import tempfile

        with tempfile.TemporaryDirectory() as td:

            (Path(td) / "codex.exe").write_bytes(b"MZ")

            with mock.patch(
                "cli.services.agent_detect._npm_global_bins",
                return_value=[],
            ), mock.patch(
                "cli.services.agent_detect._windows_path_dirs",
                return_value=[Path(td)],
            ):
                r = agent_detect.detect_agent("codex")

        self.assertTrue(r["installed"])
        self.assertEqual(r["via"], "win-path")

    @mock.patch("cli.services.agent_detect.shutil.which", return_value=None)
    @mock.patch("cli.services.agent_detect._npm_global_bins", return_value=[])
    @mock.patch("cli.services.agent_detect._windows_path_dirs", return_value=[])
    def test_detect_missing(self, which, _np, _wp):
        r = agent_detect.detect_agent("aider")
        self.assertFalse(r["installed"])
        self.assertIsNone(r["via"])

    @mock.patch("cli.services.agent_detect.shutil.which")
    @mock.patch("cli.services.agent_detect._npm_global_bins", return_value=[])
    @mock.patch("cli.services.agent_detect._windows_path_dirs", return_value=[])
    def test_scan_cache_single_detection(self, _wp, _np, which):
        def fake_which(name):
            return "/usr/bin/" + name if name == "opencode" else None

        which.side_effect = fake_which
        first = agent_detect.scan_agents()
        calls_after_first = which.call_count  # 7 known agents
        second = agent_detect.scan_agents()
        self.assertEqual(first, second)  # cache returns same content
        self.assertEqual(which.call_count, calls_after_first)  # cache hit, no re-detect
        self.assertTrue(first["opencode"]["installed"])


class MergePickerEntriesTest(unittest.TestCase):

    def setUp(self):
        _reset_cache()

    def test_configured_enabled_entries_first(self):
        cfg = FakeConfig({
            "opencode": {"enabled": True, "label": "opencode"},
            "codex": {"enabled": False},
        })
        detected = {
            "opencode": {"installed": True, "path": "/a", "via": "path"},
            "qoder": {"installed": True, "path": "/q", "via": "known-path"},
            "codex": {"installed": True, "path": "/c", "via": "path"},
        }
        entries = agent_detect.merge_picker_entries(cfg, detected)
        names = [e["name"] for e in entries]
        self.assertEqual(names, ["opencode", "qoder"])  # codex: enabled:false excluded
        self.assertTrue(entries[0]["configured"])
        self.assertTrue(entries[0]["installed"])
        self.assertFalse(entries[1]["configured"])

    def test_detected_not_configured_added(self):
        cfg = FakeConfig({"opencode": {"enabled": True}})
        detected = {"qoder": {"installed": True, "path": "/q", "via": "known-path"}}
        entries = agent_detect.merge_picker_entries(cfg, detected)
        self.assertEqual([e["name"] for e in entries], ["opencode", "qoder"])

    def test_not_installed_detected_not_added(self):
        cfg = FakeConfig({"opencode": {"enabled": True}})
        detected = {"aider": {"installed": False, "path": None, "via": None}}
        entries = agent_detect.merge_picker_entries(cfg, detected)
        self.assertEqual([e["name"] for e in entries], ["opencode"])

    def test_detect_false_excludes_auto_detect_but_keeps_enabled(self):
        cfg = FakeConfig({"qoder": {"enabled": True, "detect": False}})
        detected = {"qoder": {"installed": True, "path": "/q", "via": "known-path"}}
        entries = agent_detect.merge_picker_entries(cfg, detected)
        # qoder 为 enabled → 配置列表保留它；excluded 只作用于「未配置自动检测」段
        # （此处 qoder 是已配置项，故不受 detect:false 影响）。
        self.assertEqual([e["name"] for e in entries], ["qoder"])
        self.assertTrue(entries[0]["configured"])

    def test_detect_false_not_configured_excluded_from_auto(self):
        cfg = FakeConfig({"qoder": {"enabled": False, "detect": False}})
        detected = {"qoder": {"installed": True, "path": "/q", "via": "known-path"}}
        entries = agent_detect.merge_picker_entries(cfg, detected)
        self.assertEqual(entries, [])

    def test_missing_configured_badge_data(self):
        cfg = FakeConfig({"claude": {"enabled": True}})
        detected = {"claude": {"installed": False, "path": None, "via": None}}
        entries = agent_detect.merge_picker_entries(cfg, detected)
        self.assertEqual(entries[0]["name"], "claude")
        self.assertFalse(entries[0]["installed"])  # ⚠ badge data


class ExcludedNamesTest(unittest.TestCase):

    def test_enabled_false_and_detect_false(self):
        cfg = FakeConfig({
            "codex": {"enabled": False},
            "aider": {"enabled": True, "detect": False},
            "gemini": {"enabled": True},
        })
        self.assertEqual(
            agent_detect.excluded_names(cfg),
            {"codex", "aider"},
        )


class ResolveLaunchCommandTest(unittest.TestCase):

    def setUp(self):
        _reset_cache()

    class Cfg:

        def __init__(self, command=None):
            self._command = command

        def provider_command(self, name):
            return self._command or name

    def test_config_override_wins(self):
        cfg = self.Cfg(command="npx pi")
        with mock.patch(
            "cli.services.agent_detect.detect_agent",
            return_value={"installed": True, "path": "/x/pi"},
        ):
            self.assertEqual(
                agent_detect.resolve_launch_command(cfg, "pi"),
                "npx pi",
            )

    def test_detected_path_used(self):
        cfg = self.Cfg()
        with mock.patch(
            "cli.services.agent_detect.detect_agent",
            return_value={"installed": True, "path": "/home/u/.qoder/entry/qoder"},
        ):
            self.assertEqual(
                agent_detect.resolve_launch_command(cfg, "qoder"),
                "/home/u/.qoder/entry/qoder",
            )

    def test_wsl_cmd_shim_wrapped(self):
        cfg = self.Cfg()
        with mock.patch(
            "cli.services.agent_detect.detect_agent",
            return_value={
                "installed": True,
                "path": "/mnt/c/Users/t/AppData/Roaming/npm/opencode.cmd",
            },
        ):
            self.assertEqual(
                agent_detect.resolve_launch_command(cfg, "opencode"),
                'cmd.exe /c "C:\\Users\\t\\AppData\\Roaming\\npm\\opencode.cmd"',
            )

    def test_fallback_to_name(self):
        cfg = self.Cfg()
        with mock.patch(
            "cli.services.agent_detect.detect_agent",
            return_value={"installed": False, "path": None},
        ):
            self.assertEqual(
                agent_detect.resolve_launch_command(cfg, "aider"),
                "aider",
            )


class NpmGlobalBinsWin32Test(unittest.TestCase):

    def tearDown(self):
        agent_detect._npm_global_bins._cache = None

    @mock.patch("cli.services.agent_detect.sys.platform", "win32")
    def test_win32_no_bin_subdir_and_appdata(self):

        import tempfile

        with tempfile.TemporaryDirectory() as td_prefix, tempfile.TemporaryDirectory() as td_app:

            # win32：npm prefix -g 本身就是 shim 目录（不拼 /bin），且扫描 APPDATA\npm
            npm_dir = Path(td_app) / "npm"
            npm_dir.mkdir()

            with mock.patch(
                "cli.services.agent_detect.subprocess.run",
                return_value=mock.Mock(
                    returncode=0,
                    stdout=str(td_prefix) + "\n",
                ),
            ), mock.patch.dict(
                os.environ,
                {"APPDATA": td_app},
            ):
                dirs = agent_detect._npm_global_bins()

            self.assertEqual(
                [str(d) for d in dirs],
                [td_prefix, str(npm_dir)],
            )
            # 未把 td_prefix/bin 加进去（win32 无 bin 子目录）
            self.assertNotIn(str(Path(td_prefix) / "bin"), [str(d) for d in dirs])


class SortByUsageTest(unittest.TestCase):

    def _e(self, name):
        return {"name": name, "label": name, "icon": "", "description": "",
                "installed": True, "path": None, "via": None, "configured": True}

    def test_descending_stable(self):
        entries = [self._e("opencode"), self._e("pi"), self._e("qoder")]
        usage = {"pi": 5, "opencode": 1}
        out = agent_detect.sort_by_usage(entries, usage)
        self.assertEqual([e["name"] for e in out], ["pi", "opencode", "qoder"])

    def test_ties_keep_order(self):
        entries = [self._e("opencode"), self._e("pi")]
        out = agent_detect.sort_by_usage(entries, None)
        self.assertEqual([e["name"] for e in out], ["opencode", "pi"])


if __name__ == "__main__":
    unittest.main()
