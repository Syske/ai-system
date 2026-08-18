"""Wizard mixin: output selection, launch selection, state persistence.

Split from wizard.py (P0).
"""

from cli.utils.menu import BACK, e as _e, choose


class WizardOutput:

    @staticmethod
    def _dirs(
        path,
        exclude=None
    ):

        exclude = exclude or set()

        if not path.is_dir():
            return []

        return sorted(
            p.name
            for p in path.iterdir()
            if p.is_dir()
            and not p.name.startswith(".")
            and p.name not in exclude
        )

    def _select_output(
        self,
        header
    ):

        save_label = (
            "save to .ai-system/generated/"
        )

        try:

            save_label = (
                f"save to {self.outputs_root / 'generated'}/"
            )

        except AttributeError:
            pass

        options = [
            f"{_e(self._menu_option('output', 'copy'))}"
            "copy to clipboard",
            f"{_e(self._menu_option('output', 'print'))}"
            "print",
            f"{_e(self._menu_option('output', 'save'))}"
            f"{save_label}"
        ]

        idx = choose(
            "Output — where to send the generated prompt",
            options,
            header=header
        )

        if idx is BACK:
            return BACK

        return ("copy", "print", "save")[idx]

    def _select_launch(
        self,
        header
    ):

        providers = self.config.enabled_providers()

        options = [
            f"{_e(self._menu_option('launch', 'finish'))}"
            "finish (no launch)"
        ]

        for name in providers:

            options.append(
                f"{_e(self._menu_option('launch', name))}"
                f"open {name} in ai-workspace"
            )

        default = self.config.default_provider()

        try:

            default_idx = providers.index(
                default
            ) + 1

        except ValueError:

            default_idx = 0

        idx = choose(
            "Launch — open an agent at the workspace root",
            options,
            default=default_idx,
            header=header
        )

        if idx is BACK:
            return BACK

        return (None, *providers)[idx]

    def _project_exists(
        self,
        project
    ):        
        """Validate that a selected project is real before persisting state.

        A project is considered valid when its workspace context directory
        exists. When the business repository root (projects/ junction) is
        available, the corresponding repository must exist as well — this
        prevents stale references where the workspace dir remains after the
        business repo is removed (MAINTENANCE-2026-08-08 F1 / P16).
        """

        if not project:
            return False

        workspace_dir = (
            self.workspaces
            / project
        )

        if not workspace_dir.is_dir():
            return False

        projects_root = getattr(
            self,
            "projects_root",
            None
        )

        if projects_root is None:
            return True

        if not projects_root.is_dir():
            # repository root 不可用（如无 junction）——
            # 回退为仅校验 workspace 目录
            return True

        return (
            projects_root
            / project
        ).is_dir()

    def _save_state(
        self,
        project,
        target,
        values
    ):

        # 记录用户可选的任意项目状态——即 workspace 目录存在的项目。
        # 此处不套用 _project_exists（业务仓库）守卫：仅工作区项目
        # （如 pywechat-live-2608）也是合法、可选的上下文，其
        # last_action/last_workflow 必须持久化，wizard 推荐才能生效。
        # 业务仓库存在性检查针对仓库级操作，不针对状态记忆。
        if not project:
            # 无项目场景：记住一级菜单选择（recency）并记录命令使用统计。
            # last_target 使无项目入口也能标星默认上次目标（与有项目
            # 的 projects[p].last_* 对称）；command 走 record_usage 计数。
            name, kind = target
            self.state["last_target"] = {
                "name": name,
                "kind": kind
            }
            if kind == "command":
                self.record_usage(name)  # 内部已 save
            else:
                self.store.save()  # workflow 需显式保存
            return

        workspace_dir = self.workspaces / project

        if not workspace_dir.is_dir():
            return

        name, kind = target

        self.state["last_project"] = project

        pstate = (
            self.state
            .setdefault("projects", {})
            .setdefault(project, {})
        )

        if kind == "workflow":
            pstate["last_workflow"] = name

        else:
            pstate["last_command"] = name

        pstate["last_action"] = {
            "name": name,
            "kind": kind
        }

        if "Task ID" in values:
            pstate["last_task"] = values["Task ID"]

        if "Change ID" in values:
            pstate["last_change"] = values["Change ID"]

        self.store.save()
