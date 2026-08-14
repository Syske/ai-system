#!/usr/bin/env python3
"""Intake (project-less intent menu) unit tests.

Covers the AI-guided entry (ADR-0009 / intent menu):
- builtin + AI-created intent loading
- usage-frequency ranking
- multi-command intents (chained flow)
- keyword intent matching
- new-intent creation (slug + command inference + persistence)
- usage recording whitelist
"""

import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from cli.services.state_store import StateStore  # noqa: E402
from cli.services.wizard.intake import WizardIntake  # noqa: E402


class FakeWizard(WizardIntake):

    def __init__(self):
        self.root = REPO_ROOT
        self.store = StateStore(
            Path(tempfile.mkdtemp()) / ".aic-state.yaml"
        )
        self.state = self.store.data


class TestIntents(unittest.TestCase):

    def test_builtin_intents_loaded(self):
        w = FakeWizard()
        intents = w.intents_config()
        self.assertGreaterEqual(len(intents), 8)
        names = {it["name"] for it in intents}
        self.assertIn("weekly-maintenance", names)
        self.assertIn("issue-investigation", names)

    def test_all_intents_includes_ai_created(self):
        w = FakeWizard()
        w.state["ai_intents"] = [{"name": "custom", "label": "自定义", "commands": ["scan"]}]
        names = {it["name"] for it in w._all_intents()}
        self.assertIn("custom", names)

    def test_ranking_by_usage(self):
        w = FakeWizard()
        w.state["projectless_usage"] = {"maintain": 8, "scan": 3}
        intents = w._all_intents()
        ranked = sorted(
            intents,
            key=lambda it: (-w._intent_usage(it), it.get("label", "")),
        )
        self.assertEqual(ranked[0]["name"], "weekly-maintenance")

    def test_multi_command_intent(self):
        w = FakeWizard()
        issue = [it for it in w._all_intents()
                 if it["name"] == "issue-investigation"][0]
        self.assertIn("scan", issue["commands"])
        self.assertIn("bugfix", issue["commands"])

    def test_keyword_matching(self):
        w = FakeWizard()
        self.assertEqual(
            w._match_intent_label("线上订单超时了")["name"],
            "issue-investigation",
        )
        self.assertEqual(
            w._match_intent_label("跑下巡检")["name"],
            "weekly-maintenance",
        )
        self.assertIsNone(w._match_intent_label("今天天气不错"))

    def test_create_ai_intent_persists(self):
        w = FakeWizard()
        name, cmds = w._create_ai_intent("排查MQ消费延迟")
        self.assertEqual(cmds, ["scan"])
        self.assertEqual(
            w.state["ai_intents"][0]["name"],
            name,
        )
        # 去重：同名意图复用
        name2, _ = w._create_ai_intent("排查MQ消费延迟")
        self.assertEqual(name, name2)
        self.assertEqual(len(w.state["ai_intents"]), 1)

    def test_infer_command(self):
        w = FakeWizard()
        self.assertEqual(w._infer_command("跑下巡检"), "maintain")
        self.assertEqual(w._infer_command("扫描代码"), "scan")
        self.assertEqual(w._infer_command("初始化扩展"), "extensions-init")
        self.assertIsNone(w._infer_command("随便聊聊"))

    def test_record_usage_whitelist(self):
        w = FakeWizard()
        w.record_usage("maintain")
        w.record_usage("maintain")
        w.record_usage("scan")
        self.assertEqual(w.state["projectless_usage"]["maintain"], 2)
        self.assertEqual(w.state["projectless_usage"]["scan"], 1)
        # 意图可达命令（含多命令意图展开）
        reachable = w._projectless_commands()
        self.assertIn("bugfix", reachable)
        self.assertIn("change-impact", reachable)
        # 非意图命令不记录
        w.record_usage("trace")
        self.assertNotIn("trace", w.state["projectless_usage"])

    def test_slug(self):
        w = FakeWizard()
        self.assertEqual(w._slug("排查MQ消费延迟"), "排查mq消费延迟")
        self.assertEqual(w._slug(""), "intent")


if __name__ == "__main__":
    unittest.main()
