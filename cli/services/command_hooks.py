"""Command lifecycle hooks.

Commands may register optional hooks invoked by the wizard's generic field
loop, so command-specific behavior does not live in wizard.py. Hooks receive
the wizard (for roots/i18n/state access) and the collected field values.
"""

from datetime import datetime


class CommandHooks:
    """Base hook set. No-op by default."""

    def validate(self, wizard, values):
        """Return (ok, message). When ok is False the wizard prints
        message and re-asks the fields."""
        return True, None

    def prepare(self, wizard, values):
        """Mutate values (e.g. inject derived fields) before prompt build."""
        return None


_COMMAND_HOOKS = {}


def register(name, hooks):
    _COMMAND_HOOKS[name] = hooks


def get_hooks(name):
    return _COMMAND_HOOKS.get(name)


class ScanHooks(CommandHooks):
    """Scan command: scope validation + result directory provisioning."""

    def validate(self, wizard, values):

        if self._scope_empty(
            values,
            wizard.projects_root
        ):

            return False, (
                "\n⚠ 无可搜索范围：未选 Workspace，"
                "且 projects/ 下没有可用项目。\n"
                "请选择 Workspace 或先运行 setup "
                "把代码仓库链接到 projects/。"
            )

        return True, None

    def prepare(self, wizard, values):

        scan_dir = self._result_dir(
            values,
            wizard.workspaces
        )

        if scan_dir:
            values["Scan Directory"] = scan_dir

    @staticmethod
    def _scope_empty(values, projects_root):

        operation = values.get("Operation") or "search"

        if operation in ("diff", "manual"):
            return False

        if values.get("Workspace"):
            return False

        if values.get("Projects"):
            return False

        if not projects_root.is_dir():
            return True

        if any(
            p.is_dir()
            for p in projects_root.iterdir()
            if not p.name.startswith(".")
        ):
            return False

        return True

    @staticmethod
    def _result_dir(values, workspaces_root):

        if values.get("Keep Results") != "yes":
            return None

        workspace = values.get("Workspace") or "system"

        scan_dir = (
            workspaces_root
            / workspace
            / "scans"
            / f"scan-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        )

        scan_dir.mkdir(parents=True, exist_ok=True)

        return str(scan_dir)


register("scan", ScanHooks())
