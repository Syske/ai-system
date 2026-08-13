"""Wizard mixin: header, project/target selection, workflow recommendation.

Split from wizard.py (P0).
"""

import re

from cli.services import workflow_reader
from cli.utils.file import read_text
from cli.utils.menu import BACK, Section, e as _e, choose, is_tty
from cli.utils.yaml import load_yaml


class WizardSelection:

    def _header(
        self,
        project,
        target,
        fields,
        values
    ):

        lines = [
                f"{_e('🚀 ')}AI Prompt Generator"
        ]

        lines.append(
            f"{_e('🌍 ')}environment: {self.environment_name}"
        )

        if self.environment_missing:

            lines.append(
                f"{_e('⚠️ ')}config/environments/{self.environment_name}.yaml "
                "missing — bootstrap will run tools/setup.py to provision it"
            )

        if self.project is not None or project:

            shown = project or self.project

            if shown:

                lines.append(
                    f"{_e(self._menu_option('project', 'item'))}"
                    f"project: {shown}"
                )

        if target:

            name, kind = target

            lines.append(
                f"{_e('✅ ')}{kind}: {name}"
            )

            for field, _ in fields:

                if field in values:

                    lines.append(
                        f"{_e('✅ ')}{field}: {values[field]}"
                    )

        return lines

    def _select_project(
        self,
        header
    ):

        # 列出全部工作区项目——包括 projects/ 下无业务仓库的项目
        # （它们是合法工作区上下文，如 pywechat-live-2608）。
        # P16 的 _project_exists 守卫作用于 _save_state（防止陈旧
        # last_project），不作用于此处列表。
        projects = self._dirs(
            self.workspaces,
            exclude={"archived"}
        )

        from cli.services.providers import project_repos

        options = []

        for p in projects:

            repos = project_repos(self, p)

            available = repos.get("available") or []

            if available:

                services = ", ".join(
                    r.get("service", "?")
                    for r in available[:3]
                )

                suffix = f" — {services}"

            else:

                suffix = " (no repo mapped)"

            options.append(
                f"{_e(self._menu_option('project', 'item'))}{p}{suffix}"
            )

        options.append(
            f"{_e(self._menu_option('project', 'system'))}"
            "system (no project)"
        )

        default = 0

        last = self.state.get("last_project")

        if last in projects:
            default = projects.index(last)

        options[default] = (
            f"{_e(self._menu_option('project', 'default_mark'))}"
            f"{options[default]}"
        )

        idx = choose(
            "Project — select the working project",
            options,
            default,
            header=header
        )

        if idx is BACK:
            return BACK

        if idx == len(projects):
            return None

        return projects[idx]

    def _select_target(
        self,
        header,
        project
    ):

        registry = load_yaml(
            self.root
            / "config"
            / "workflow-registry.yaml"
        )

        workflows = list(
            registry["workflows"].keys()
        )

        commands = sorted(
            p.stem.replace("aic-", "")
            for p in (
                self.root
                / "cli"
                / "commands"
            ).glob("*.md")
        )

        targets = []
        labels = []

        def add(
            name,
            kind,
            icon,
            number=None
        ):

            targets.append((name, kind))

            if kind == "workflow":

                desc = self._workflow_purpose(name)

            else:

                desc = self._command_description(name)

            if number is not None and is_tty():

                label = f"{_e(icon)}{number}. {name}"

            else:

                label = f"{_e(icon)}{name}"

            if kind == "command":
                label += " (command)"

            if desc:
                label += f" — {self._short(desc)}"

            labels.append(label)

        def section(text):

            targets.append(None)

            labels.append(Section(text))

        configured = {
            "workflow": set(),
            "command": set()
        }

        for sec in self._menu("sections"):

            present = []

            for item in sec.get("items") or []:

                name = item.get("name")
                kind = item.get("kind", "workflow")

                if (
                    kind == "workflow"
                    and name in workflows
                ) or (
                    kind == "command"
                    and name in commands
                ):

                    present.append(item)

                    configured[kind].add(name)

            if not present:
                continue

            section(
                self._t(
                    f"sections.{sec['title']}",
                    sec["title"]
                )
            )

            for item in present:

                add(
                    item["name"],
                    item["kind"],
                    item.get("icon", ""),
                    item.get("number")
                )

        remaining = [
            w
            for w in workflows
            if w not in configured["workflow"]
            and w not in self.hidden_workflows()
        ]

        if remaining:

            section(
                self._t(
                    "sections.flow_other",
                    "其他流程"
                )
            )

            for name in remaining:
                add(name, "workflow", "🚀 ")

        remaining_commands = [
            c
            for c in commands
            if c not in configured["command"]
        ]

        if remaining_commands:

            section(
                self._t(
                    "sections.commands_other",
                    "其他命令"
                )
            )

            for c in remaining_commands:
                add(c, "command", "⚡ ")

        default = 0

        recommended = self._recommend_workflow(
            project,
            workflows
        )

        if recommended in workflows:

            try:

                default = targets.index(
                    (recommended, "workflow")
                )

            except ValueError:

                default = 0

            labels[default] = (
                f"{_e('⭐ ')}{labels[default]}"
            )

        idx = choose(
            "Select a workflow or command",
            labels,
            default,
            header=header
        )

        if idx is BACK:
            return BACK

        return targets[idx]

    def _recommend_workflow(
        self,
        project,
        workflows
    ):

        if not project:
            return None

        pstate = (
            self.state
            .get("projects", {})
            .get(project, {})
        )

        last_action = pstate.get("last_action")

        if last_action:

            if last_action.get("kind") == "command":

                recommended = self._command_next(
                    last_action.get("name")
                )

                if recommended in workflows:
                    return recommended

            else:

                recommended = self._parse_next(
                    last_action.get("name"),
                    workflows
                )

                if recommended:
                    return recommended

                return "prepare"

        last = pstate.get("last_workflow")

        if last:

            recommended = self._parse_next(
                last,
                workflows
            )

            if recommended:
                return recommended

            return "prepare"

        changes = self._dirs(
            self.workspaces
            / project
            / "openspec"
            / "changes",
            exclude={"archive"}
        )

        if changes:
            return "develop"

        return "prepare"

    def _parse_next(
        self,
        name,
        workflows
    ):

        try:

            text = read_text(
                self.root
                / "workflows"
                / f"{name}.md"
            )

        except OSError:

            return None

        section = None

        for line in text.splitlines():

            stripped = line.strip()

            if stripped.startswith("## "):
                section = stripped[3:]
                continue

            if section != "Next":
                continue

            if not stripped.startswith("- "):
                continue

            lowered = stripped.lower()

            tokens = re.findall(
                r"[a-z][a-z0-9-]*",
                lowered
            )

            if not tokens:
                continue

            first = tokens[0]

            if (
                first in workflows
                and first != name
            ):
                return first

        return None
