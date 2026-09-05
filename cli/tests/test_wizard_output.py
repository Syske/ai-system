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
from cli.services.wizard.fields import WizardFields  # noqa: E402

# 无项目命令集合（用于测试 record_usage 白名单；与 intake 保持一致）
_PROJECTLESS = {"maintain", "scan", "extensions-init", "skill-source",
                "pack", "workflow", "command", "skill"}


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

    def record_usage(self, target):
        """Minimal stand-in for WizardIntake.record_usage (real Wizard has it)."""
        if target not in _PROJECTLESS:
            return
        usage = self.state.setdefault("projectless_usage", {})
        usage[target] = usage.get(target, 0) + 1
        self.store.save()


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
        # projects_root 指向不存在目录（如无 junction）
        w = FakeWizard(
            self.workspaces,
            projects_root=self.base / "no-such-junction"
        )
        self.assertTrue(w._project_exists("demo"))

    def test_workspace_without_repo_rejected(self):
        # F1 场景：workspace 目录存在，业务仓库已移除
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
        # “stale” 有 workspace 目录但无仓库——仍是合法可选项；
        # 其状态必须持久化（2026-08-08 修复：状态记忆与项目列表一致，
        # 仓库存在性非必需）。
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
        # 无 workspace 目录的项目 → 不可选 → 跳过
        w = FakeWizard(self.workspaces, projects_root=self.projects)
        w._save_state(
            "ghost",
            ("trace", "command"),
            {}
        )
        self.assertEqual(w.state, {})

    def test_save_command_without_project_records_last_target(self):
        # 无项目 command：记录 last_target（一级菜单 recency）+ 使用计数
        w = FakeWizard(self.workspaces, projects_root=self.projects)
        w._save_state(
            None,
            ("scan", "command"),
            {}
        )
        self.assertEqual(
            w.state["last_target"],
            {"name": "scan", "kind": "command"}
        )
        self.assertEqual(
            w.state["projectless_usage"]["scan"],
            1
        )

    def test_save_workflow_without_project_records_last_target(self):
        # 无项目 workflow：记录 last_target（一级菜单 recency）；
        # 不记 usage（计数仅针对命令集合）
        w = FakeWizard(self.workspaces, projects_root=self.projects)
        w._save_state(
            None,
            ("maintain", "workflow"),
            {}
        )
        self.assertEqual(
            w.state["last_target"],
            {"name": "maintain", "kind": "workflow"}
        )
        self.assertNotIn("projectless_usage", w.state)

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
        # 旧语义：空项目 → 无 last_target。新行为（2026-08-18）：
        # 无项目也记录一级菜单 recency（last_target），仅不记 usage 计数
        # （trace 不在无项目命令白名单）。
        w = FakeWizard(self.workspaces, projects_root=self.projects)
        w._save_state(
            None,
            ("trace", "command"),
            {}
        )
        self.assertEqual(
            w.state.get("last_target"),
            {"name": "trace", "kind": "command"}
        )
        self.assertNotIn("projectless_usage", w.state)

    def test_usage_recorded_for_projectless_command(self):
        w = FakeWizard(self.workspaces, projects_root=self.projects)
        # maintain 在无项目命令集合 → 无项目时记录使用统计
        w._save_state(
            None,
            ("maintain", "command"),
            {}
        )
        self.assertEqual(
            w.state["projectless_usage"].get("maintain"),
            1,
        )

class TestInvalidateDependents(unittest.TestCase):
    """H6: upstream field change clears stale downstream values."""

    def test_projects_change_clears_branch(self):
        w = WizardFields()
        values = {"Projects": "a,b", "Branch": "main"}
        w._invalidate_dependents(values, "Projects")
        self.assertNotIn("Branch", values)

    def test_project_change_clears_task_and_change(self):
        w = WizardFields()
        values = {"Project ID": "p1", "Task ID": "t1", "Change ID": "c1"}
        w._invalidate_dependents(values, "Project ID")
        self.assertNotIn("Task ID", values)
        self.assertNotIn("Change ID", values)

    def test_unrelated_field_untouched(self):
        w = WizardFields()
        values = {"Projects": "a", "Branch": "main"}
        w._invalidate_dependents(values, "Code Reference")
        self.assertIn("Branch", values)


class TestP37DeriveFields(unittest.TestCase):
    """P37 批次 1：可推导字段运行期自动填充（三条衡量点）。"""

    def test_change_id_slug_from_change_request(self):
        from cli.services import change_resume
        cid = change_resume.suggest_change_id("add support for multi-tenant login flow")
        self.assertRegex(cid, r"^\d{6}-multi-tenant-login-flow$")
        cid2 = change_resume.suggest_change_id("接入微信支付")
        self.assertRegex(cid2, r"^\d{6}-接入微信支付$")

    def test_release_version_fallback(self):
        from cli.services import git_version
        import datetime
        v = git_version.guess_release_version()
        today = datetime.date.today().strftime("%Y%m%d")
        self.assertEqual(v, f"0.1.0-{today}")

    def test_spec_reference_path_derived(self):
        from cli.services import change_resume
        p = change_resume.spec_reference_path("/ws", "proj", "202608-x")
        self.assertEqual(str(p), "/ws/proj/openspec/changes/202608-x")

    def test_derive_fields_task_single_card(self):
        import tempfile
        from pathlib import Path
        tmp = Path(tempfile.mkdtemp())
        card = tmp / "proj" / "openspec" / "changes" / "c1" / "tasks" / "cards"
        card.mkdir(parents=True)
        (card / "T-001.md").write_text("# T-001", encoding="utf-8")
        w = WizardFields()
        w.workspaces = tmp
        values = {"Project ID": "proj", "Change ID": "c1"}
        w._derive_fields([("Task ID", False)], values)
        self.assertEqual(values.get("Task ID"), "T-001")

    def test_derive_fields_release_version(self):
        w = WizardFields()
        values = {}
        w._derive_fields([("Release Version", False)], values)
        from cli.services import git_version
        self.assertEqual(values.get("Release Version"), git_version.guess_release_version())

    # ---- P37 批次 2：项目选择类 + 默认类推导 ----

    def test_derive_projects_from_selected(self):
        w = WizardFields()
        values = {"Project ID": "proj-x"}
        w._derive_fields([("Projects", False)], values)
        self.assertEqual(values.get("Projects"), "proj-x")

    def test_derive_project_id_from_workspace(self):
        w = WizardFields()
        values = {"Workspace ID": "ws-a"}
        w._derive_fields([("Project ID", False)], values)
        self.assertEqual(values.get("Project ID"), "ws-a")

    def test_derive_analysis_target_default(self):
        w = WizardFields()
        values = {}
        w._derive_fields([("Analysis Target", False)], values)
        self.assertEqual(values.get("Analysis Target"), "ai-system")

    def test_derive_knowledge_operation_default(self):
        w = WizardFields()
        values = {}
        w._derive_fields([("Knowledge Operation", False)], values)
        self.assertEqual(values.get("Knowledge Operation"), "collect")

    def test_derive_analysis_target_keeps_selected(self):
        # 已有项目上下文时 analysis target 不覆盖
        w = WizardFields()
        values = {"Project ID": "proj-y"}
        w._derive_fields([("Analysis Target", False)], values)
        self.assertIsNone(values.get("Analysis Target"))

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
        # 业务仓库根存在但无 alpha/beta 目录（真实 F1）
        (root / "projects").mkdir()
        return Wizard(root)

    def test_lists_workspace_projects_without_repo(self):
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            w = self._make_wizard(tmp)
            projects = w._dirs(w.workspaces, exclude={"archived"})
            self.assertEqual(projects, ["alpha", "beta"])
            # 仅工作区项目状态持久化（2026-08-08 修复）
            w._save_state("alpha", ("develop", "workflow"), {})
            self.assertIn("alpha", w.state.get("projects", {}))

    def test_last_project_heals_from_stale_null(self):
        # 自愈：遗留显式 `last_project: null`（08-06 清空产物）在加载时
        # 回填最近活跃项目，恢复项目列表默认高亮（2026-08-18）。
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            state_path = root / "workspaces" / ".aic-state.yaml"
            state_path.parent.mkdir(parents=True)
            state_path.write_text(
                "last_project: null\n"
                "projects:\n"
                "  alpha:\n"
                "    last_workflow: develop\n"
                "  beta:\n"
                "    last_workflow: verify\n",
                encoding="utf-8",
            )
            w = self._make_wizard(tmp)
            self.assertEqual(w.state["last_project"], "beta")
            # 自愈已持久化
            reloaded = StateStore(state_path).data
            self.assertEqual(reloaded["last_project"], "beta")
