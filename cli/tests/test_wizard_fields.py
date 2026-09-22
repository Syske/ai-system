#!/usr/bin/env python3
"""P57 tests — candidate-driven field selection + hook fail-field (no loop).

Covers:
- providers.container_services: workspace.yaml mapped services
- _choices_for("Projects"): container services first, projects/ fallback
- _choices_for("Review Focus"): preset candidates wired (G3)
- branch_candidates: workspace.yaml dev_branch + local git branches
- ScanHooks.validate: unresolvable names rejected (no fake pass), mapped pass
- ChangeImpactHooks.validate / fail_field: Projects targeted re-ask
- Branch single-candidate auto-adopt in _ask_field

Run:
    python -m unittest cli.tests.test_wizard_fields
"""

import sys
import tempfile
import unittest
import unittest.mock
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from cli.services import providers  # noqa: E402
from cli.services.command_hooks import (  # noqa: E402
    ChangeImpactHooks,
    ScanHooks,
)
from cli.services.wizard import Wizard  # noqa: E402
from cli.services.wizard.fields import WizardFields  # noqa: E402


def _make_workspace(tmp, services=("svc-a", "svc-b"), with_projects=True):
    """Build workspaces/<pid>/workspace.yaml with mapped services."""

    root = Path(tmp)
    ws = root / "workspaces" / "demo"
    ws.mkdir(parents=True)
    lines = ["repository:\n", "  available:\n"]
    for i, svc in enumerate(services):
        lines.append(
            f"    - service: {svc}\n"
            f"      path: /repos/{svc}\n"
            f"      dev_branch: cc20260920_demo_{svc}\n"
            f"      branch: master\n"
        )
    lines.append("  unavailable: []\n")
    (ws / "workspace.yaml").write_text("".join(lines), encoding="utf-8")
    if with_projects:
        # projects/ dirs for the fallback path
        projs = root / "projects"
        for svc in ("svc-a", "svc-b", "other-c"):
            (projs / svc).mkdir(parents=True)
    return root


class FakeWizard(WizardFields):
    """Minimal wizard surface used by _choices_for / providers."""

    def __init__(self, root, project=None):
        self.workspaces = root / "workspaces"
        self.projects_root = root / "projects"
        self.project = project
        self._field_choices_map = {}

    def _auto_fields(self):
        return set()

    def _field_choices(self, field):
        return self._field_choices_map.get(field, [])

    @staticmethod
    def _dirs(root, exclude=None):
        exclude = exclude or set()
        return sorted(
            p.name
            for p in root.iterdir()
            if p.is_dir() and p.name not in exclude
        )


class TestContainerServices(unittest.TestCase):

    def test_returns_mapped_services(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = _make_workspace(tmp)
            w = FakeWizard(root, project="demo")
            self.assertEqual(
                providers.container_services(w, "demo"),
                ["svc-a", "svc-b"],
            )

    def test_empty_when_no_project(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = _make_workspace(tmp)
            w = FakeWizard(root)
            self.assertEqual(providers.container_services(w, None), [])

    def test_empty_when_no_mapping(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "workspaces" / "empty").mkdir(parents=True)
            w = FakeWizard(root, project="empty")
            self.assertEqual(
                providers.container_services(w, "empty"),
                [],
            )


class TestProjectsChoices(unittest.TestCase):

    def test_container_services_preferred(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = _make_workspace(tmp)
            w = FakeWizard(root, project="demo")
            choices = w._choices_for({}, "Projects")
            self.assertEqual(choices, ["svc-a", "svc-b"])

    def test_falls_back_to_projects_dirs(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = _make_workspace(tmp)
            w = FakeWizard(root, project=None)
            choices = w._choices_for({}, "Projects")
            self.assertEqual(choices, ["other-c", "svc-a", "svc-b"])


class TestReviewFocusWiring(unittest.TestCase):
    """G3: preset candidates must reach _choices_for."""

    def test_preset_candidates_returned(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = _make_workspace(tmp)
            w = FakeWizard(root, project="demo")
            w._field_choices_map["Review Focus"] = [
                "性能", "安全", "正确性", "并发",
            ]
            self.assertEqual(
                w._choices_for({}, "Review Focus"),
                ["性能", "安全", "正确性", "并发"],
            )


class TestBranchCandidates(unittest.TestCase):

    def test_dev_branch_from_mapping(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = _make_workspace(tmp)
            w = FakeWizard(root, project="demo")
            choices = providers.branch_candidates(w, {"Project ID": "demo"})
            self.assertIn("cc20260920_demo_svc-a", choices)
            self.assertIn("master", choices)


class TestScanHooks(unittest.TestCase):

    def test_empty_scope_fails(self):
        # projects/ 为空 → 无 Workspace 无 Projects = 无可搜索范围
        with tempfile.TemporaryDirectory() as tmp:
            root = _make_workspace(tmp, with_projects=False)
            w = FakeWizard(root, project="demo")
            ok, _ = ScanHooks().validate(w, {})
            self.assertFalse(ok)

    def test_fake_name_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = _make_workspace(tmp)
            w = FakeWizard(root, project="demo")
            ok, msg = ScanHooks().validate(
                w,
                {"Projects": "no-such-repo-xyz"},
            )
            self.assertFalse(ok)
            self.assertIn("no-such-repo-xyz", msg)

    def test_mapped_service_accepted(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = _make_workspace(tmp)
            w = FakeWizard(root, project="demo")
            ok, _ = ScanHooks().validate(
                w,
                {"Projects": "svc-a"},
            )
            self.assertTrue(ok)

    def test_fail_field_is_projects(self):
        self.assertEqual(ScanHooks().fail_field({}), "Projects")

    def test_clonable_metadata_service_accepted(self):
        """P58：有 repositories 元数据、但未 clone 的服务应通过（可按需 clone）。"""
        with tempfile.TemporaryDirectory() as tmp:
            root = _make_workspace(tmp)
            repos = root / "repositories"
            repos.mkdir(parents=True)
            (repos / "remote-svc.yaml").write_text(
                "id: remote-svc\n"
                "repositories:\n"
                "  remote-svc:\n"
                "    git:\n"
                "      url: git@example.com:remote-svc.git\n",
                encoding="utf-8",
            )
            w = FakeWizard(root, project=None)
            ok, msg = ScanHooks().validate(w, {"Projects": "remote-svc"})
            self.assertTrue(ok, msg)

    def test_all_candidates_pass_validation(self):
        """不变量：候选源与校验谓词必须一致——所有候选都通过校验（防“选一轮拒一轮”循环）。"""
        with tempfile.TemporaryDirectory() as tmp:
            root = _make_workspace(tmp)
            repos = root / "repositories"
            repos.mkdir(parents=True)
            for svc in ("remote-a", "remote-b"):
                (repos / f"{svc}.yaml").write_text(
                    f"id: {svc}\n"
                    f"repositories:\n"
                    f"  {svc}:\n"
                    f"    git:\n"
                    f"      url: git@example.com:{svc}.git\n",
                    encoding="utf-8",
                )
            w = FakeWizard(root, project=None)
            sh = ScanHooks()
            cand = providers.repo_candidates(w)
            self.assertTrue(cand)
            for name in cand:
                ok, msg = sh.validate(w, {"Projects": name})
                self.assertTrue(ok, f"候选 {name} 被拒（候选/校验不一致）: {msg}")


class TestChangeImpactHooks(unittest.TestCase):

    def test_empty_projects_fails_with_exit_guidance(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = _make_workspace(tmp)
            w = FakeWizard(root, project="demo")
            ok, msg = ChangeImpactHooks().validate(w, {})
            self.assertFalse(ok)
            self.assertIn("Esc", msg)

    def test_fail_field_is_projects(self):
        self.assertEqual(ChangeImpactHooks().fail_field({}), "Projects")


class TestRepositoryFlowLoops(unittest.TestCase):
    """回归：仓库/项目选择的循环类缺陷（实测发现）。"""

    def test_top_level_back_cancels(self):
        """顶层 BACK = 取消退出（KeyboardInterrupt），不再无限重渲染。"""
        from cli.services.wizard.steps import WizardSteps
        from cli.utils.menu import BACK

        class FakeSteps(WizardSteps):

            def _select_project(self, header):
                return BACK

            def _header(self, *a):
                return []

        with self.assertRaises(KeyboardInterrupt):
            FakeSteps()._steps()


class TestRepositorySource(unittest.TestCase):
    """P58: repositories/*.yaml 为服务元数据源，候选 = 元数据 ∪ 本地克隆。"""

    def _make_repos(self, root):
        repos = root / "repositories"
        repos.mkdir(parents=True)
        for svc in ("svc-a", "svc-b"):
            (repos / f"{svc}.yaml").write_text(
                f"id: {svc}\n"
                f"repositories:\n"
                f"  {svc}:\n"
                f"    git:\n"
                f"      url: git@example.com:{svc}.git\n"
                f"    default_branch: master\n",
                encoding="utf-8",
            )
        return repos

    def test_repositories_services_lists_metadata(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = _make_workspace(tmp)
            self._make_repos(root)
            w = FakeWizard(root, project=None)
            self.assertEqual(
                providers.repositories_services(w),
                ["svc-a", "svc-b"],
            )

    def test_repo_candidates_is_union(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = _make_workspace(tmp)
            self._make_repos(root)
            w = FakeWizard(root, project=None)
            # projects/ 有 svc-a svc-b other-c；repositories/ 有 svc-a svc-b
            # 并集 = svc-a svc-b other-c（projects_dirs 的 other-c 也保留）
            self.assertEqual(
                providers.repo_candidates(w),
                ["other-c", "svc-a", "svc-b"],
            )

    def test_projects_choices_uses_union_without_container(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = _make_workspace(tmp)
            self._make_repos(root)
            w = FakeWizard(root, project=None)
            choices = w._choices_for({}, "Projects")
            self.assertIn("svc-a", choices)
            self.assertIn("other-c", choices)


class TestRepoEnsure(unittest.TestCase):
    """P58 repo-ensure 三态 + 元数据校验（不真实 clone，仅模块逻辑）。"""

    @staticmethod
    def _load_module():
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "repo_ensure",
            REPO_ROOT / "tools" / "repo-ensure.py",
        )
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod

    def test_load_metadata(self):
        re = self._load_module()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "repositories").mkdir()
            (root / "repositories" / "svc-a.yaml").write_text(
                "id: svc-a\n"
                "repositories:\n"
                "  svc-a:\n"
                "    git:\n"
                "      url: git@example.com:svc-a.git\n"
                "    default_branch: master\n",
                encoding="utf-8",
            )
            url, branch = re.load_metadata(root, "svc-a")
            self.assertEqual(url, "git@example.com:svc-a.git")
            self.assertEqual(branch, "master")
            self.assertEqual(re.load_metadata(root, "no-such"), (None, None))

    def test_ensure_states(self):
        from unittest import mock

        re = self._load_module()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            repos_dir = root / "repositories"
            repos_dir.mkdir()
            (repos_dir / "svc-a.yaml").write_text(
                "id: svc-a\n"
                "repositories:\n"
                "  svc-a:\n"
                "    git:\n"
                "      url: git@example.com:svc-a.git\n",
                encoding="utf-8",
            )
            proj = root / "projects"
            proj.mkdir()

            # 元数据缺失 → 失败并提示
            ok, msg = re.ensure_service(root, proj, "no-such")
            self.assertFalse(ok)
            self.assertIn("no metadata", msg)

            # 已存在但非 git → 失败
            (proj / "junk").mkdir()
            ok, _ = re.ensure_service(root, proj, "junk")
            self.assertFalse(ok)

            # clone 失败 → 返回错误不崩溃（mock _run 避免真实 SSH 网络）
            fail = mock.Mock(returncode=128, stderr="host key verification failed")
            with mock.patch.object(re, "_run", return_value=fail):
                ok, msg = re.ensure_service(root, proj, "svc-a")
                self.assertFalse(ok)
                self.assertIn("clone failed", msg)

            # clone 成功 → 返回成功消息（目录创建由真实 git 完成，手工验证过）
            ok_run = mock.Mock(returncode=0, stderr="")
            with mock.patch.object(re, "_run", return_value=ok_run):
                ok, msg = re.ensure_service(root, proj, "svc-a")
                self.assertTrue(ok)
                self.assertIn("cloned", msg)

    def test_validate_metadata(self):
        re = self._load_module()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            repos_dir = root / "repositories"
            repos_dir.mkdir()
            (repos_dir / "good.yaml").write_text(
                "id: good\nrepositories:\n  good:\n    git:\n      url: x.git\n",
                encoding="utf-8",
            )
            (repos_dir / "bad.yaml").write_text("id: bad\n", encoding="utf-8")
            errors = re.validate_metadata(root)
            self.assertEqual(len(errors), 1)
            self.assertIn("bad.yaml", errors[0])


class TestBranchSingleCandidateAutoAdopt(unittest.TestCase):
    """code-review contract: single candidate adopted directly (no menu)."""

    def test_single_candidate_auto_adopted(self):
        from cli.services.wizard.fields import WizardFields

        class FakeFields(WizardFields):

            def __init__(self):
                self.history = {}
                self.environment_explicit = False

            def _choices_for(self, values, field):
                return ["master"]

            def _field_note(self, field):
                return None

            def _field_icon(self, field):
                return ""

            def _t(self, *a, **k):
                return ""

        wf = FakeFields()
        value = wf._ask_field(
            header=[],
            values={},
            field="Branch",
            required=False,
            position=3,
            total=5,
        )
        self.assertEqual(value, "master")
        self.assertEqual(wf.history, {"Branch": "master"})

    def test_multiple_candidates_not_auto(self):
        from unittest import mock
        from cli.services.wizard.fields import WizardFields

        class FakeFields(WizardFields):

            def __init__(self):
                self.history = {}
                self.config = None
                self.environment_explicit = False

            def _choices_for(self, values, field):
                return ["master", "dev"]

            def _field_note(self, field):
                return None

            def _field_icon(self, field):
                return ""

            def _t(self, *a, **k):
                return ""

            def _option_descriptions(self, field):
                return {}

            def _multi_select_fields(self):
                return set()

            def _previous_value(self, field):
                return None

            def _manual_default(self, field, values):
                return None

            def _menu_option(self, *a, **k):
                return ""

        wf = FakeFields()
        with mock.patch(
            "cli.services.wizard.fields.choose",
            return_value=0,
        ):
            value = wf._ask_field(
                header=[],
                values={},
                field="Branch",
                required=False,
                position=3,
                total=5,
            )
        # 走菜单路径（choose 被调用）→ 选中第一个候选
        self.assertEqual(value, "master")


if __name__ == "__main__":
    unittest.main()


# ── P66：code-review / change-impact 重复追问项目与分支 ─────────────────────


class TestBranchCategoryMatching(unittest.TestCase):
    """P66：单候选自动采纳改为**类别匹配**（原只认字面量 "Branch" → P57 契约失配）。"""

    def test_category_truth_table(self):
        from cli.services.wizard.fields import is_branch_target_field

        cases = {
            "Branch": True,
            "Source Branch": True,
            "Target Branch": True,
            "Branch Mapping": False,   # 显式覆盖项
            "Base Branch": False,      # 基线
            "Projects": False,
            "Review Focus": False,
        }
        for field, expected in cases.items():
            self.assertEqual(
                is_branch_target_field(field), expected, field
            )


class TestContainerDerived(unittest.TestCase):
    """P66：容器已确定 / 覆盖项 / 默认值字段 → 预填并跳过提问。"""

    def _wizard(self, tmp, services=("svc-a", "svc-b"), project="demo"):
        root = _make_workspace(tmp, services=services)

        class W(WizardFields):

            def __init__(self):
                self.workspaces = root / "workspaces"
                self.projects_root = root / "projects"
                self.project = project
                self._field_defaults = {"Base Branch": "master"}

        return W()

    def test_projects_and_branch_fields_derived(self):
        with tempfile.TemporaryDirectory() as tmp:
            w = self._wizard(tmp)
            fields = [
                ("Projects", True),
                ("Target Theme", False),
                ("Branch Mapping", False),
                ("Base Branch", False),
            ]
            silent, reasons = w._container_derived(fields, {}, "demo")

            self.assertEqual(silent["Projects"], "svc-a, svc-b")
            self.assertIsNone(silent["Branch Mapping"])   # 不设值，仅不再提问
            self.assertEqual(silent["Base Branch"], "master")
            self.assertNotIn("Target Theme", silent)      # 主题保留追问（可引导分支匹配）
            self.assertTrue(all(f in reasons for f in silent))

    def test_single_service_project(self):
        with tempfile.TemporaryDirectory() as tmp:
            w = self._wizard(tmp, services=("only-svc",))
            silent, _ = w._container_derived([("Projects", True)], {}, "demo")
            self.assertEqual(silent["Projects"], "only-svc")

    def test_no_mapping_falls_back_to_asking(self):
        with tempfile.TemporaryDirectory() as tmp:
            w = self._wizard(tmp, services=())
            silent, _ = w._container_derived(
                [("Projects", True), ("Base Branch", False)], {}, "demo"
            )
            self.assertNotIn("Projects", silent)
            self.assertEqual(silent["Base Branch"], "master")

    def test_no_project_derives_nothing(self):
        with tempfile.TemporaryDirectory() as tmp:
            w = self._wizard(tmp)
            silent, _ = w._container_derived(
                [("Projects", True), ("Branch Mapping", False)], {}, None
            )
            self.assertEqual(silent, {})


class TestP66NoDuplicatePrompts(unittest.TestCase):
    """端到端：已选项目后，code-review / change-impact 不再追问项目与分支。"""

    def _drive(self, target, services=("svc-a", "svc-b")):
        import cli.services.wizard.fields as wfields

        with tempfile.TemporaryDirectory() as tmp:
            root = _make_workspace(tmp, services=services)
            w = Wizard(REPO_ROOT)

            w.workspaces = root / "workspaces"
            w.projects_root = root / "projects"
            w.outputs_root = root / "outputs"
            w.project = "demo"

            w._recommend_workflow = lambda *a, **k: None
            w._save_state = lambda *a, **k: None
            w._select_project = lambda header: "demo"
            kind = "command" if target == "scan" else "workflow"
            w._select_target = lambda commands, project: (target, kind)
            w._select_output = lambda header: "<none>"
            w._select_launch = lambda header: None

            titles = []

            def spy_choose(title, options, default=0, allow_skip=False,
                           header=None, note=None):
                titles.append(title)
                return 0

            def spy_choose_many(title, options, header=None, note=None,
                                enter_selects_current=False, max_visible=None,
                                selected_theme="selected"):
                titles.append(title)
                return [0]

            def spy_ask_text(prompt, header=None, note=None, default=None):
                titles.append(prompt)
                return default if default is not None else "x"

            with unittest.mock.patch.object(wfields, "choose", spy_choose), \
                    unittest.mock.patch.object(wfields, "choose_many",
                                              spy_choose_many), \
                    unittest.mock.patch.object(wfields, "ask_text", spy_ask_text):
                result = w._steps()

            return titles, result

    def _prompted_field(self, titles, field):
        return any(t.startswith(field) for t in titles)

    def test_code_review_skips_project_and_branch(self):
        titles, result = self._drive("code-review")
        self.assertFalse(self._prompted_field(titles, "Projects"), titles)
        self.assertFalse(self._prompted_field(titles, "Base Branch"), titles)
        self.assertFalse(self._prompted_field(titles, "Branch Mapping"), titles)

        values = result[1]
        self.assertEqual(values.get("Projects"), "svc-a, svc-b")
        self.assertEqual(values.get("Base Branch"), "master")

    def test_change_impact_keeps_required_code_reference(self):
        titles, result = self._drive("change-impact")
        self.assertFalse(self._prompted_field(titles, "Projects"), titles)
        self.assertTrue(self._prompted_field(titles, "Code Reference"), titles)
        self.assertEqual(result[1].get("Projects"), "svc-a, svc-b")

    def test_single_service_container(self):
        titles, result = self._drive("code-review", services=("only-svc",))
        self.assertFalse(self._prompted_field(titles, "Projects"), titles)
        self.assertEqual(result[1].get("Projects"), "only-svc")

    def test_unmapped_container_still_asks(self):
        titles, result = self._drive("code-review", services=())
        self.assertTrue(self._prompted_field(titles, "Projects"), titles)

    def test_opt_in_scope_keeps_scan_service_selection(self):
        """P66 显式 opt-in：`scan`（P57 服务级选择是其交互目的）仍须追问 Projects。"""
        titles, _ = self._drive("scan")
        self.assertTrue(self._prompted_field(titles, "Projects"), titles)

    def test_non_opt_in_target_derives_nothing(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = _make_workspace(tmp)

            class W(WizardFields):

                def __init__(self):
                    self.workspaces = root / "workspaces"
                    self.projects_root = root / "projects"
                    self.project = "demo"
                    self._field_defaults = {"Base Branch": "master"}

            silent, _ = W()._container_derived(
                [("Projects", True)], {}, "demo", "scan"
            )
            self.assertEqual(silent, {})
