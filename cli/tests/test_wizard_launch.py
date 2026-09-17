"""Tests for the wizard launch menu (wizard/output.py::_select_launch).

Locks the 2026-09-17 方案 B behavior: the launch menu is built from merged
picker entries (configured enabled + auto-detected), not-installed agents are
hidden, icons come from provider/detection metadata, entries sort by usage
count, and a selection records agent usage. Regression guard for the launch
menu (previously only used enabled_providers()).
"""

import sys
import unittest
from unittest import mock
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from cli.services.wizard.output import WizardOutput


class FakeOut(WizardOutput):

    class _Cfg:

        @staticmethod
        def default_provider():
            return "opencode"

    def __init__(self):
        self.config = self._Cfg()
        self._usage = {}
        self.recorded = []

    def _menu_option(self, *args, **kwargs):
        return ""

    def agent_usage(self):
        return self._usage

    def record_agent_usage(self, name):
        self.recorded.append(name)


def _entry(name, installed=True, configured=True, label=None, icon=""):
    return {
        "name": name,
        "label": label or name,
        "icon": icon,
        "description": "",
        "installed": installed,
        "path": "/x" if installed else None,
        "via": "path" if installed else None,
        "configured": configured,
    }


class SelectLaunchTest(unittest.TestCase):

    @mock.patch("cli.services.wizard.output.choose")
    @mock.patch("cli.services.wizard.output._e", side_effect=lambda x: x)
    def test_detected_not_configured_appears(self, _e, choose):

        choose.side_effect = lambda t, o, default=0, **k: 0

        w = FakeOut()

        with mock.patch(
            "cli.services.agent_detect.merge_picker_entries",
            return_value=[
                _entry("opencode"),
                _entry("qoder", configured=False, label="qoder", icon="🛠️ "),
            ],
        ):
            w._select_launch("")

        options = choose.call_args[0][1]

        self.assertEqual(len(options), 3)  # 结束 + opencode + qoder
        self.assertIn("opencode", options[1])
        self.assertIn("qoder", options[2])
        self.assertIn("🛠️ ", options[2])  # icon from detection metadata
        # 无「（检测到）」标记：配置项与检测项展示统一（2026-09-17 用户反馈）
        self.assertNotIn("（检测到）", options[2])
        self.assertNotIn("✓", options[1])

    @mock.patch("cli.services.wizard.output.choose")
    def test_configured_missing_hidden(self, choose):

        choose.side_effect = lambda t, o, default=0, **k: 0

        w = FakeOut()

        with mock.patch(
            "cli.services.agent_detect.merge_picker_entries",
            return_value=[
                _entry("claude", installed=False),
            ],
        ):
            result = w._select_launch("")

        options = choose.call_args[0][1]

        self.assertEqual(len(options), 1)  # 仅 结束
        self.assertFalse(any("claude" in o for o in options))
        self.assertIsNone(result)

    @mock.patch("cli.services.wizard.output.choose")
    def test_sorted_by_usage(self, choose):

        choose.side_effect = lambda t, o, default=0, **k: 0

        w = FakeOut()
        w._usage = {"pi": 5, "opencode": 1}

        with mock.patch(
            "cli.services.agent_detect.merge_picker_entries",
            return_value=[
                _entry("opencode", icon="🤖 "),
                _entry("pi", icon="🌀 "),
            ],
        ):
            w._select_launch("")

        options = choose.call_args[0][1]

        # pi（使用 5 次）排在 opencode（1 次）前
        self.assertLess(options.index("🌀 pi" if "🌀 pi" in options else next(o for o in options if "pi" in o)),
                        options.index(next(o for o in options if "opencode" in o)))

    @mock.patch("cli.services.wizard.output.choose")
    def test_selection_records_usage(self, choose):

        # 选择第 2 项 = pi
        choose.side_effect = lambda t, o, default=0, **k: 2

        w = FakeOut()

        with mock.patch(
            "cli.services.agent_detect.merge_picker_entries",
            return_value=[
                _entry("opencode", icon="🤖 "),
                _entry("pi", icon="🌀 "),
            ],
        ):
            result = w._select_launch("")

        self.assertEqual(result, "pi")
        self.assertEqual(w.recorded, ["pi"])


if __name__ == "__main__":
    unittest.main()
