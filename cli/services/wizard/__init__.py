"""Wizard — orchestration class composed from mixin modules.

Modularization of the former single-file cli/services/wizard.py (P0,
1235 lines). Public API unchanged: `from cli.services.wizard import Wizard`
keeps working; Wizard exposes .run(), .root, .environment_name, .config,
.store, .state.

Modules:
- base.py      — config access helpers (_t/_menu/_command_fields/_field_*)
- steps.py     — _steps main state machine
- selection.py — project/target selection + workflow recommendation
- fields.py    — field resolution, defaults, ask loop
- output.py    — output dir / launch / state persistence
- analysis.py  — workflow purpose / command description helpers
"""

from pathlib import Path

from cli.services import environment as env
from cli.services.menu_config import MenuConfig
from cli.services.state_store import StateStore
from cli.utils.menu import screen_enter, screen_exit

from .analysis import WizardAnalysis
from .base import WizardConfigAccess
from .fields import WizardFields
from .intake import WizardIntake
from .output import WizardOutput
from .selection import WizardSelection
from .steps import WizardSteps


class Wizard(
    WizardConfigAccess,
    WizardSteps,
    WizardSelection,
    WizardIntake,
    WizardFields,
    WizardOutput,
    WizardAnalysis,
):

    def __init__(
        self,
        root: Path,
        environment: str = None
    ):

        self.root = root

        self.environment_name = (
            environment
            or env.DEFAULT_ENV
        )

        self.environment_explicit = (
            environment is not None
        )

        self.environment_missing = (
            self.environment_explicit
            and not env.has_environment(
                root,
                self.environment_name
            )
        )

        env_paths = env.paths(
            root,
            self.environment_name
        )

        self.workspaces = env_paths[
            "workspaces_root"
        ]

        self.projects_root = env_paths[
            "repository_root"
        ]

        self.outputs_root = env_paths[
            "outputs_root"
        ]

        self.config = MenuConfig(root)

        self.store = StateStore(
            self.workspaces
            / ".aic-state.yaml"
        )

        self.state = self.store.data

        # 状态自愈：历史遗留的显式 `last_project: null`（08-06 清空产物，
        # 被每次读-改-存往返保留）会压制项目默认高亮。当值为空但项目
        # 历史存在时，回填最近写入的活跃项目。
        if (
            not self.state.get("last_project")
            and self.state.get("projects")
        ):

            projects = self.state["projects"]

            last_active = list(projects)[-1]

            self.state["last_project"] = last_active

            self.store.save()

        self.history = {}

        self._field_defaults = {}

        self.project = None

        self.target_name = None

    def run(self):

        screen_enter()

        try:

            return self._steps()

        finally:

            screen_exit()


__all__ = ["Wizard"]
