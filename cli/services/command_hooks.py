"""Command lifecycle hooks.

Commands may register optional hooks invoked by the wizard's generic field
loop, so command-specific behavior does not live in wizard.py. Hooks receive
the wizard (for roots/i18n/state access) and the collected field values.
"""

from datetime import datetime
from pathlib import Path


class CommandHooks:
    """Base hook set. No-op by default."""

    def validate(self, wizard, values):
        """Return (ok, message). When ok is False the wizard prints
        message and re-asks only the field returned by fail_field()."""
        return True, None

    def fail_field(self, values):
        """Field to re-ask when validate fails (P57: targeted re-ask,
        no full re-collection loop). None = stay at the last field."""
        return None

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

        empty, reason = self._scope_empty(
            values,
            wizard.projects_root,
            wizard
        )

        if empty:

            if reason == "names":

                bad = self._unknown_names(
                    values,
                    wizard.projects_root,
                    wizard
                )

                return False, (
                    "\n⚠ 以下项目不存在或未映射（候选 = 已选容器 workspace.yaml "
                    "映射服务 / projects/ 目录 / 仓库绝对路径）：\n"
                    f"   {', '.join(bad)}\n"
                    "请从候选选择，或输入存在的仓库路径。"
                )

            return False, (
                "\n⚠ 无可搜索范围：未选 Workspace，"
                "且 projects/ 下没有可用项目。\n"
                "请选择 Workspace 或先运行 setup "
                "把代码仓库链接到 projects/。"
            )

        return True, None

    def fail_field(self, values):

        return "Projects"

    @staticmethod
    def _mapped_services(wizard):

        from cli.services import providers

        return set(
            providers.container_services(
                wizard,
                wizard.project
            )
        )

    @staticmethod
    def _unknown_names(values, projects_root, wizard):

        mapped = ScanHooks._mapped_services(wizard)

        bad = []

        for name in ScanHooks._split_names(values):

            if name in mapped:
                continue

            if (projects_root / name).is_dir():
                continue

            p = Path(name)

            if p.is_absolute() and p.is_dir():
                continue

            bad.append(name)

        return bad

    @staticmethod
    def _split_names(values):

        return [
            n.strip()
            for n in (values.get("Projects") or "").split(",")
            if n.strip()
        ]

    def prepare(self, wizard, values):

        scan_dir = self._result_dir(
            values,
            wizard.outputs_root
        )

        if scan_dir:
            values["Scan Directory"] = scan_dir

    @staticmethod
    def _scope_empty(values, projects_root, wizard):

        operation = values.get("Operation") or "search"

        if operation in ("diff", "manual"):
            return False, None

        if values.get("Workspace"):
            return False, None

        if values.get("Projects"):

            # P57：名称必须可解析（容器映射服务 / projects/ 目录 / 绝对路径），
            # 与 aic-scan.md Step 1 运行时语义对齐；假名不再假通过。
            if ScanHooks._unknown_names(
                values,
                projects_root,
                wizard
            ):
                return True, "names"

            return False, None

        if not projects_root.is_dir():
            return True, "empty"

        if any(
            p.is_dir()
            for p in projects_root.iterdir()
            if not p.name.startswith(".")
        ):
            return False, None

        return True, "empty"

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
                "有项目容器时从 workspace.yaml 映射选择（候选已列出）；"
                "无项目时请直接提供仓库路径/URL（逗号分隔）。\n"
                "可返回上一字段选择，或按 Esc 退出。"
            )

        return True, None

    def fail_field(self, values):

        return "Projects"


register("scan", ScanHooks())
register("change-impact", ChangeImpactHooks())
