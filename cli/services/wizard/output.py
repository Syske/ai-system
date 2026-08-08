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

        options = [
            f"{_e(self._menu_option('output', 'copy'))}"
            "copy to clipboard",
            f"{_e(self._menu_option('output', 'print'))}"
            "print",
            f"{_e(self._menu_option('output', 'save'))}"
            "save to .ai-system/generated/"
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

    def _save_state(
        self,
        project,
        target,
        values
    ):

        if not project:
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
