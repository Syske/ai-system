"""Tests for the chain (积木组合) service: registry, resolve, run context/manifest."""

import tempfile
import unittest
from pathlib import Path

from cli.services import chain


class TestChain(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        # minimal chains config
        (self.root / "config").mkdir(parents=True)
        (self.root / "config" / "chains.yaml").write_text(
            "version: 1\n"
            "chains:\n"
            "  - name: analyze-and-publish\n"
            "    label: 分析并发布到wiki\n"
            "    scenario: 分析代码并把结果发到 wiki\n"
            "    blocks:\n"
            "      - {type: command, name: scan}\n"
            "      - {type: skill, name: confluence-markdown-publisher}\n"
            "  - name: bugfix-release-doc\n"
            "    label: 改bugfix并出转测文档\n"
            "    scenario: 改 bug 并出转测文档 + MR\n"
            "    blocks:\n"
            "      - {type: workflow, name: bugfix}\n",
            encoding="utf-8",
        )

    def tearDown(self):
        self.tmp.cleanup()

    def test_load_chains(self):
        chains = chain.load_chains(self.root)
        self.assertEqual(len(chains), 2)
        self.assertEqual(chains[0]["name"], "analyze-and-publish")

    def test_load_chains_missing_config(self):
        empty = Path(self.tmp.name) / "nested"
        empty.mkdir()
        self.assertEqual(chain.load_chains(empty), [])

    def test_resolve_by_label(self):
        chains = chain.load_chains(self.root)
        got = chain.resolve_chain("麻烦把结果发布到 wiki（分析并发布到wiki）", chains)
        self.assertEqual(got["name"], "analyze-and-publish")

    def test_resolve_by_scenario_and_blockname(self):
        chains = chain.load_chains(self.root)
        self.assertEqual(
            chain.resolve_chain("分析代码并把结果发到 wiki", chains)["name"],
            "analyze-and-publish",
        )
        # block name 参与匹配
        self.assertEqual(
            chain.resolve_chain("想跑 scan 然后发布", chains)["name"],
            "analyze-and-publish",
        )

    def test_resolve_none(self):
        chains = chain.load_chains(self.root)
        self.assertIsNone(chain.resolve_chain("做一顿晚饭", chains))

    def test_block_names(self):
        chains = chain.load_chains(self.root)
        self.assertEqual(
            chain.block_names(chains[0]),
            ["scan", "confluence-markdown-publisher"],
        )

    def test_create_chain_run_and_record_artifact(self):
        chains = chain.load_chains(self.root)
        run_dir, manifest_path = chain.create_chain_run(
            self.root,
            chains[0],
            outputs_root=self.root / "outputs",
            desc="upload-test",
        )
        self.assertIn("upload-test", run_dir.name)
        self.assertTrue(manifest_path.exists())

        manifest = chain.read_manifest(manifest_path)
        self.assertEqual(manifest["chain"], "analyze-and-publish")
        self.assertEqual(len(manifest["blocks"]), 2)
        self.assertIsNone(manifest["blocks"][0]["artifact"])

        # record artifact for scan
        updated = chain.record_artifact(
            manifest_path,
            "scan",
            "outputs/scan/260820-x/scan-report.md",
        )
        self.assertIsNotNone(updated)
        self.assertEqual(
            updated["blocks"][0]["artifact"],
            "outputs/scan/260820-x/scan-report.md",
        )
        # persists to disk
        reloaded = chain.read_manifest(manifest_path)
        self.assertEqual(
            reloaded["blocks"][0]["artifact"],
            "outputs/scan/260820-x/scan-report.md",
        )

    def test_record_artifact_missing_block(self):
        chains = chain.load_chains(self.root)
        _, manifest_path = chain.create_chain_run(
            self.root,
            chains[0],
            outputs_root=self.root / "outputs",
        )
        self.assertIsNone(
            chain.record_artifact(manifest_path, "nope", "anything")
        )

    def test_project_requirement_explicit(self):
        chains = chain.load_chains(self.root)
        for c in chains:
            c["project"] = "required"
        self.assertEqual(
            chain.project_requirement(chains[0]), "required"
        )

    def test_project_requirement_inferred_from_workflow_block(self):
        # 无 project 字段，但含 workflow 块 → required
        c = {"blocks": [{"type": "workflow", "name": "bugfix"}]}
        self.assertEqual(chain.project_requirement(c), "required")

    def test_project_requirement_none_when_skill_only(self):
        c = {"blocks": [{"type": "skill", "name": "publish"}]}
        self.assertEqual(chain.project_requirement(c), "none")

    def test_project_requirement_none_overrides(self):
        c = {"project": "none", "blocks": [{"type": "workflow", "name": "bugfix"}]}
        self.assertEqual(chain.project_requirement(c), "none")


if __name__ == "__main__":
    unittest.main()
