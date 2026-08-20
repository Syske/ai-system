#!/usr/bin/env python3
"""Core service tests: skill_launcher / skill_scan / agent_picker pure logic.

P0 test coverage for the interactive skill flow (no LLM / no network / no
TTY). Covers the pure functions that the skill launcher/optimizer depend on.

Run:
    python -m unittest discover -s cli/tests
"""

import os
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

# Force non-TTY so icon helpers degrade to plain text in labels
os.environ.setdefault("NO_TTY", "1")
os.environ.setdefault("NO_ICONS", "1")

from cli.services import skill_launcher as sl  # noqa: E402
from cli.services import skill_scan  # noqa: E402


class TestSourceMark(unittest.TestCase):
    def test_known_sources(self):
        self.assertIn("ext", sl._source_mark("extensions"))
        self.assertIn("g", sl._source_mark("global"))
        self.assertIn("proj", sl._source_mark("local"))
        self.assertIn("core", sl._source_mark("core"))

    def test_unknown_source_passthrough(self):
        self.assertEqual(sl._source_mark("custom"), "custom")


class TestSkillLabel(unittest.TestCase):
    def test_label_with_description(self):
        label = sl._skill_label(
            {"name": "bugfix", "source": "local", "description": "Fix bugs"}
        )
        self.assertIn("bugfix", label)
        self.assertIn("Fix bugs", label)

    def test_label_empty_description(self):
        label = sl._skill_label(
            {"name": "x", "source": "global", "description": ""}
        )
        self.assertIn("x", label)
        self.assertNotIn("—", label)


class TestSkillBlock(unittest.TestCase):
    def test_block_references_path(self):
        block = sl._skill_block(
            {"name": "bugfix", "path": "skills/bugfix", "source": "local"}
        )
        self.assertIn("bugfix", block)
        self.assertIn("skills/bugfix", block)


class TestGroupSkills(unittest.TestCase):
    def test_groups_by_config(self):
        skills = [
            {"name": "a", "source": "extensions", "description": ""},
            {"name": "b", "source": "global", "description": ""},
            {"name": "c", "source": "local", "description": ""},
        ]

        class FakeConfig:
            def skill_groups(self):
                return [
                    {"type": "source", "value": "extensions", "title": "ext"},
                    {"type": "source", "value": "local", "title": "loc"},
                ]

            def skill_group_title(self, key):
                return key

        options, by_index = sl._group_skills(FakeConfig(), skills)

        # selectable labels only for a and c (b not in any group -> "other")
        self.assertTrue(by_index)

        # every skill appears exactly once in by_index
        names = {by_index[i]["name"] for i in by_index}
        self.assertEqual(names, {"a", "b", "c"})

    def test_groups_by_config_includes_core_source(self):
        skills = [
            {"name": "ds", "source": "core", "description": "DeepSeek md"},
        ]

        class FakeConfig:
            def skill_groups(self):
                return [
                    {"type": "source", "value": "core", "title": "core"},
                ]

            def skill_group_title(self, key):
                return key

        options, by_index = sl._group_skills(FakeConfig(), skills)

        self.assertTrue(by_index)
        names = {by_index[i]["name"] for i in by_index}
        self.assertEqual(names, {"ds"})


class TestRenderPrompt(unittest.TestCase):
    def test_render_substitutes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            tmpl_dir = root / "templates" / "prompts"
            tmpl_dir.mkdir(parents=True)
            (tmpl_dir / "skill-launch.md").write_text(
                "Skills:\n{{skill_list}}\nTask: {{task}}\nAgent: {{agent}}\n",
                encoding="utf-8",
            )

            class FakeWizard:
                pass

            FakeWizard.root = root

            out = sl._render_prompt(
                FakeWizard(),
                [{"name": "bugfix", "path": "skills/bugfix", "source": "local"}],
                "fix the thing",
                "opencode",
            )
            self.assertIn("bugfix", out)
            self.assertIn("fix the thing", out)
            self.assertIn("opencode", out)


class TestSkillScan(unittest.TestCase):
    def test_skills_in_empty_dir(self):
        with tempfile.TemporaryDirectory() as tmp:
            items = list(skill_scan._skills_in(Path(tmp)))
            self.assertEqual(items, [])

    def test_skills_in_finds_skill_with_skil_md(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            skill_dir = root / "my-skill"
            skill_dir.mkdir()
            (skill_dir / "SKILL.md").write_text(
                "---\nname: my-skill\ndescription: test skill\n---\n",
                encoding="utf-8",
            )
            items = list(skill_scan._skills_in(root))
            names = {i[0] for i in items}
            self.assertIn("my-skill", names)
            self.assertIn("test skill", items[0][1]["description"])

    def test_skills_in_skips_dir_without_skil_md(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "no-skill").mkdir()
            items = list(skill_scan._skills_in(root))
            self.assertEqual(items, [])


if __name__ == "__main__":
    unittest.main()


class TestProjectRepos(unittest.TestCase):
    """workspace.yaml repository mapping read (ADR-0008)."""

    def test_reads_repository_mapping(self):
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            ws = root / "workspaces" / "demo"
            ws.mkdir(parents=True)
            (ws / "workspace.yaml").write_text(
                "repository:\n"
                "  available:\n"
                "    - service: svc-a\n"
                "      path: /repos/svc-a\n"
                "  unavailable:\n"
                "    - svc-b\n",
                encoding="utf-8",
            )

            from cli.services.providers import project_repos

            class FakeWizard:
                workspaces = root / "workspaces"
                projects_root = root

            repos = project_repos(FakeWizard(), "demo")
            self.assertEqual(repos["available"][0]["service"], "svc-a")
            self.assertEqual(repos["unavailable"], ["svc-b"])

    def test_missing_yaml_returns_empty(self):
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "workspaces" / "nope").mkdir(parents=True)

            from cli.services.providers import project_repos

            class FakeWizard:
                workspaces = root / "workspaces"
                projects_root = root

            self.assertEqual(project_repos(FakeWizard(), "nope"), {})

    def test_repo_path_dual_platform(self):
        """_repo_path branches: win32 relative joins under projects_root;
        Linux branch must NOT require projects_root (via _linux_path).

        Regression guard for P24: FakeWizard must expose projects_root on
        non-Linux; the Linux branch must resolve without it.
        """
        import tempfile
        from unittest import mock

        from cli.services.providers import _linux_path, _repo_path

        # _linux_path unit: Windows drive path normalizes to a WSL mount
        self.assertEqual(_linux_path(r"D:\workspace\svc-a"), "/mnt/d/workspace/svc-a")

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)

            class FakeWizard:
                workspaces = root / "workspaces"
                projects_root = root

            wiz = FakeWizard()

            # Linux branch must not need projects_root (P24 guard)
            class NoRootWizard:
                workspaces = root / "workspaces"

            with mock.patch("cli.services.providers.sys.platform", "linux"):
                lnx = _repo_path(NoRootWizard(), "repos/svc-a")
                self.assertEqual(lnx, Path("repos/svc-a"))

            # win32: relative path joins under projects_root (P24 regression)
            with mock.patch("cli.services.providers.sys.platform", "win32"):
                rel = _repo_path(wiz, "repos/svc-a")
                self.assertEqual(rel, root / "repos" / "svc-a")

            # absolute path passes through on any platform
            with mock.patch("cli.services.providers.sys.platform", "win32"):
                abs_p = _repo_path(wiz, str(root / "svc-a"))
                self.assertEqual(abs_p, root / "svc-a")

            # empty path -> None
            self.assertIsNone(_repo_path(wiz, ""))
