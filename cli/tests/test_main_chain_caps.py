"""Tests for the main-chain external capability loader."""

import tempfile
import unittest
from pathlib import Path

from cli.services import main_chain_caps


class TestMainChainCaps(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        (self.root / "config").mkdir(parents=True)
        (self.root / "config" / "main-chain-capabilities.yaml").write_text(
            "capabilities:\n"
            "  prepare:\n"
            "    - {skill: confluence-markdown-publisher, path: extensions/confluence-markdown-publisher, desc: wiki}\n"
            "    - {skill: off-skill, enabled: false}\n"
            "  develop: []\n",
            encoding="utf-8",
        )

    def tearDown(self):
        self.tmp.cleanup()

    def test_prepare_returns_enabled_capability(self):
        caps = main_chain_caps.external_capabilities(self.root, "prepare")
        names = [c["skill"] for c in caps]
        self.assertIn("confluence-markdown-publisher", names)
        # enabled:false 被过滤
        self.assertNotIn("off-skill", names)

    def test_empty_stage(self):
        self.assertEqual(
            main_chain_caps.external_capabilities(self.root, "develop"),
            [],
        )

    def test_missing_stage_and_missing_file(self):
        self.assertEqual(
            main_chain_caps.external_capabilities(self.root, "release"),
            [],
        )
        empty = self.root / "nested"
        empty.mkdir()
        self.assertEqual(
            main_chain_caps.external_capabilities(empty, "prepare"),
            [],
        )


if __name__ == "__main__":
    unittest.main()
