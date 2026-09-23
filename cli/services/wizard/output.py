"""Wizard mixin: output selection, launch selection, state persistence.

Split from wizard.py (P0).
"""

import time
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
            "保存到 .ai-system/generated/"
        )

        try:

            save_label = (
                f"保存到 {self.outputs_root / 'generated'}/"
            )

        except AttributeError:
            pass

        options = [
            f"{_e(self._menu_option('output', 'copy'))}"
            "复制到剪贴板",
            f"{_e(self._menu_option('output', 'print'))}"
            "打印",
            f"{_e(self._menu_option('output', 'save'))}"
            f"{save_label}"
        ]

        idx = choose(
            "输出 — 生成的提示词发送到哪里",
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

        from cli.services.agent_detect import (
            merge_picker_entries,
            sort_by_usage,
        )

        entries = [
            ent
            for ent in merge_picker_entries(
                self.config
            )
            if ent["installed"]
        ]

        entries = sort_by_usage(
            entries,
            self.agent_usage(),
        )

        options = [
            f"{_e(self._menu_option('launch', 'finish'))}"
            "结束（不启动）"
        ]

        names = [None]

        for ent in entries:

            options.append(
                f"{_e(ent['icon'])}"
                f"在 ai-workspace 打开 {ent['label']}"
            )

            names.append(ent["name"])

        default = self.config.default_provider()

        try:

            default_idx = names.index(
                default
            )

        except ValueError:

            default_idx = 0

        idx = choose(
            "启动 — 在工作区根目录打开代理",
            options,
            default=default_idx,
            header=header
        )

        if idx is BACK:
            return BACK

        chosen = names[idx]

        if chosen:

            self.record_agent_usage(chosen)

        return chosen

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
            "kind": kind,
            # R2 修复：记录时间戳 —— 原实现依赖 dict 插入顺序推断"最近活跃"，
            # 一旦状态被外部编辑/重排即失准（`wizard/__init__.py` 的默认高亮）。
            "at": time.time(),
        }

        if "Task ID" in values:
            pstate["last_task"] = values["Task ID"]

        if "Change ID" in values:
            pstate["last_change"] = values["Change ID"]

        self.store.save()
