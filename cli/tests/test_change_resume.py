"""change_resume 重入检测测试：已有产物加载 + §8 未决澄清解析。"""

import tempfile
import unittest
from pathlib import Path

from cli.services.change_resume import (
    change_artifact_path,
    read_change_artifact,
)

_FIXTURE = (
    Path(__file__).parent
    / "fixtures"
    / "proposal-demo.md"
).read_text(encoding="utf-8")


class ChangeResumeTest(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.workspaces = Path(self.tmp.name)
        self.project = "demo-project"
        self.change_id = "demo-change"
        artifact = (
            self.workspaces
            / self.project
            / "openspec"
            / "changes"
            / self.change_id
            / "proposal.md"
        )
        artifact.parent.mkdir(parents=True)
        artifact.write_text(_FIXTURE, encoding="utf-8")
        self.artifact = artifact

    def tearDown(self):
        self.tmp.cleanup()

    def test_change_artifact_path(self):
        path = change_artifact_path(
            self.workspaces, self.project, self.change_id
        )
        self.assertEqual(path, self.artifact)
        self.assertTrue(path.exists())

    def test_missing_artifact_returns_none(self):
        result = read_change_artifact(
            self.workspaces, "no-such-project", "no-such-change"
        )
        self.assertIsNone(result)

    def test_reads_header_and_prefill(self):
        result = read_change_artifact(
            self.workspaces, self.project, self.change_id
        )
        self.assertIsNotNone(result)
        self.assertEqual(
            result["change_request"],
            "init + supplement (existing prod sync interface)",
        )
        self.assertEqual(result["readiness"], "Ready for Specification")

    def test_open_questions_exclude_resolved(self):
        result = read_change_artifact(
            self.workspaces, self.project, self.change_id
        )
        # §8 中：1 已解决（删除线）；2/3/4/5 未决
        self.assertEqual(len(result["open_questions"]), 4)
        self.assertTrue(
            all("R1" not in q for q in result["open_questions"])
        )
        self.assertTrue(
            any(q.startswith("R8") for q in result["open_questions"])
        )

    def test_no_section_8_returns_empty(self):
        tmp = tempfile.TemporaryDirectory()
        workspaces = Path(tmp.name)
        artifact = (
            workspaces
            / "p"
            / "openspec"
            / "changes"
            / "c"
            / "proposal.md"
        )
        artifact.parent.mkdir(parents=True)
        artifact.write_text(
            "# Preparation Report — c\\n\\n> Readiness: **Blocked**\\n",
            encoding="utf-8",
        )
        result = read_change_artifact(workspaces, "p", "c")
        self.assertEqual(result["readiness"], "Blocked")
        self.assertEqual(result["open_questions"], [])
        self.assertEqual(result["change_request"], "")
        tmp.cleanup()


if __name__ == "__main__":
    unittest.main()
