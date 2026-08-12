#!/usr/bin/env python3
"""C1 test base — wizard state persistence guard tests (P16).

Covers the project existence validation added to _save_state /
_select_project (MAINTENANCE-2026-08-08 F1 / P16): state must not be
written for a project whose workspace dir or business repository is missing.

Run:
    python -m unittest discover -s cli/tests
"""

import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from cli.services.state_store import StateStore  # noqa: E402
from cli.services.wizard.output import WizardOutput  # noqa: E402


class FakeWizard(WizardOutput):
    """Minimal mixin host: only the fields _save_state / _project_exists need."""

    def __init__(self, workspaces, projects_root=None):
        self.workspaces = Path(workspaces)
        self.projects_root = (
            Path(projects_root)
            if projects_root is not None
            else None
        )
        self.store = StateStore(
            Path(workspaces)
            / ".aic-state.yaml"
        )
        self.state = self.store.data


class TestProjectExists(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.base = Path(self.tmp.name)
        self.workspaces = self.base / "workspaces"
        self.projects = self.base / "projects"

    def tearDown(self):
        self.tmp.cleanup()

    def test_empty_project_rejected(self):
        w = FakeWizard(self.workspaces)
        self.assertFalse(w._project_exists(""))

    def test_missing_workspace_rejected(self):
        w = FakeWizard(self.workspaces)
        self.assertFalse(w._project_exists("ghost"))

    def test_workspace_only_valid_when_no_repo_root(self):
        (self.workspaces / "demo").mkdir(parents=True)
        w = FakeWizard(self.workspaces)  # projects_root = None
        self.assertTrue(w._project_exists("demo"))

    def test_repo_root_unavailable_falls_back_to_workspace(self):
        (self.workspaces / "demo").mkdir(parents=True)
        # projects_root points at a non-existent dir (e.g. no junction)
        w = FakeWizard(
            self.workspaces,
            projects_root=self.base / "no-such-junction"
        )
        self.assertTrue(w._project_exists("demo"))

    def test_workspace_without_repo_rejected(self):
        # F1 scenario: workspace dir exists, business repo removed
        (self.workspaces / "pywechat-live-2608").mkdir(parents=True)
        self.projects.mkdir(parents=True)
        w = FakeWizard(self.workspaces, projects_root=self.projects)
        self.assertFalse(w._project_exists("pywechat-live-2608"))

    def test_workspace_with_repo_valid(self):
        (self.workspaces / "demo").mkdir(parents=True)
        (self.projects / "demo").mkdir(parents=True)
        w = FakeWizard(self.workspaces, projects_root=self.projects)
        self.assertTrue(w._project_exists("demo"))


class TestSaveStateGuard(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.base = Path(self.tmp.name)
        self.workspaces = self.base / "workspaces"
        self.projects = self.base / "projects"
        (self.workspaces / "demo").mkdir(parents=True)
        (self.projects / "demo").mkdir(parents=True)
        (self.workspaces / "stale").mkdir(parents=True)  # repo missing

    def tearDown(self):
        self.tmp.cleanup()

    def test_save_written_for_workspace_only_project(self):
        # "stale" has workspace dir but no repo — still a valid selectable
        # project; its state MUST persist (fix 2026-08-08: state memory
        # matches the project list, repo presence is not required).
        w = FakeWizard(self.workspaces, projects_root=self.projects)
        w._save_state(
            "stale",
            ("trace", "command"),
            {}
        )
        self.assertEqual(w.state["last_project"], "stale")
        self.assertEqual(
            w.state["projects"]["stale"]["last_command"],
            "trace"
        )

    def test_save_skipped_when_workspace_missing(self):
        # project with NO workspace dir at all -> cannot be picked -> skip
        w = FakeWizard(self.workspaces, projects_root=self.projects)
        w._save_state(
            "ghost",
            ("trace", "command"),
            {}
        )
        self.assertEqual(w.state, {})

    def test_save_written_for_valid_project(self):
        w = FakeWizard(self.workspaces, projects_root=self.projects)
        w._save_state(
            "demo",
            ("trace", "command"),
            {}
        )
        self.assertEqual(w.state["last_project"], "demo")
        self.assertEqual(
            w.state["projects"]["demo"]["last_command"],
            "trace"
        )

    def test_save_skipped_for_empty_project(self):
        w = FakeWizard(self.workspaces, projects_root=self.projects)
        w._save_state(
            None,
            ("trace", "command"),
            {}
        )
        self.assertEqual(w.state, {})


if __name__ == "__main__":
    unittest.main()


class TestSelectProjectListsAll(unittest.TestCase):
    """Regression: _select_project must list ALL workspace projects, even
    those without a business repo in projects/ (fix 2026-08-08). P16's
    _project_exists guards _save_state only, not the project list."""

    def _make_wizard(self, tmp):
        from pathlib import Path
        from cli.services.wizard import Wizard

        root = Path(tmp)
        (root / "config" / "environments").mkdir(parents=True)
        (root / "config" / "i18n").mkdir(parents=True)
        (root / "config" / "environments" / "local.yaml").write_text(
            "workspace:\n  root: {}\n".format(root.as_posix()),
            encoding="utf-8",
        )
        (root / "config" / "i18n" / "zh.yaml").write_text("{}", encoding="utf-8")
        (root / "workspaces" / "alpha").mkdir(parents=True)
        (root / "workspaces" / "beta").mkdir(parents=True)
        # business repo root exists but has NO alpha/beta dirs (real F1)
        (root / "projects").mkdir()
        return Wizard(root)

    def test_lists_workspace_projects_without_repo(self):
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            w = self._make_wizard(tmp)
            projects = w._dirs(w.workspaces, exclude={"archived"})
            self.assertEqual(projects, ["alpha", "beta"])
            # state persists for workspace-only projects (fix 2026-08-08)
            w._save_state("alpha", ("develop", "workflow"), {})
            self.assertIn("alpha", w.state.get("projects", {}))
