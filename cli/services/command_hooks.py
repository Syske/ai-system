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
            wizard.outputs_root
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
    def _result_dir(values, outputs_root):

        if values.get("Keep Results") != "yes":
            return None

        # Projectess/system workspace dirs are no longer a scan target —
        # every saved scan lands under the configured outputs root, per the
        # outputs convention (outputs-convention.md). A timestamp dir keeps
        # naming deterministic (no agent-derived descriptor needed).
        scan_dir = (
            outputs_root
            / "scan"
            / f"scan-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        )

        scan_dir.mkdir(parents=True, exist_ok=True)

        return str(scan_dir)


class ChangeImpactHooks(CommandHooks):
    """Change-impact workflow: requires at least one reviewable repo.

    Projects is Required: from the workspace.yaml mapping (project context)
    or directly supplied by the user as repo path/URL (one-time task,
    no project container needed). This hook enforces a non-empty Projects
    at the CLI so a run without any repo cannot start.
    """

    def validate(self, wizard, values):

        projects = values.get("Projects")

        if not projects:

            return False, (
                "\n⚠ change-impact 需要至少一个代码仓库（Projects）。\n"
                "有项目容器时从 workspace.yaml 映射选择；无项目时请直接提供"
                "仓库路径/URL（逗号分隔）。"
            )

        return True, None


register("scan", ScanHooks())
register("change-impact", ChangeImpactHooks())
