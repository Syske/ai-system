import re
from pathlib import Path

from cli.services import providers
from cli.services.command_hooks import get_hooks
from cli.utils.file import read_text
from cli.utils.menu import (
    BACK,
    Section,
    ask_text,
    choose,
    choose_many,
    icons_enabled,
    is_tty,
    screen_enter,
    screen_exit
)
from cli.utils.yaml import load_yaml, save_yaml


def _e(icon):

    if is_tty() and icons_enabled():
        return icon

    return ""


class Wizard:

    def __init__(
        self,
        root: Path
    ):

        self.root = root

        self.workspaces = (
            root.parent
            / "workspaces"
        )

        self.projects_root = (
            root.parent
            / "projects"
        )

        self.state_file = (
            self.workspaces
            / ".aic-state.yaml"
        )

        self.state = self._load_state()

        self.menu = self._load_menu()

        self.i18n = self._load_i18n()

        self.history = {}

        self.project = None

        self.target_name = None

    def _load_i18n(self):

        locale = self.menu.get("locale", "zh")

        try:

            return load_yaml(
                self.root
                / "config"
                / "i18n"
                / f"{locale}.yaml"
            ) or {}

        except Exception:

            return {}

    def _t(self, path, default=None):

        node = self.i18n

        parts = path.split(".")

        def _get(data, keys):

            if not keys:
                return data

            if not isinstance(data, dict):
                return None

            return _get(
                data.get(keys[0]),
                keys[1:]
            )

        result = _get(node, parts)

        if result is None:
            return default

        return result

    def _load_menu(self):

        try:

            return load_yaml(
                self.root
                / "config"
                / "menu.yaml"
            ) or {}

        except Exception:

            return {}

    def _menu(self, key, default=None):

        return self.menu.get(key, default or {})

    def _command_fields(self, name):

        fields = self._menu(
            "command_fields"
        ).get(name)

        if fields:
            return [
                (f[0], bool(f[1]))
                for f in fields
            ]

        default = self._menu(
            "default_command_fields"
        )

        if default:
            return [
                (f[0], bool(f[1]))
                for f in default
            ]

        return []

    def _field_icon(self, field):

        return (
            self._menu("field_icons")
            .get(field, "")
        )

    def _field_note(self, field):

        return self._t(
            f"field_notes.{field}"
        )

    def _field_choices(self, field):

        return (
            self._menu("field_choices")
            .get(field, [])
        )

    def _option_descriptions(self, field):

        return self._t(
            f"option_descriptions.{field}"
        )

    def _command_next(self, name):

        return (
            self._menu("command_next")
            .get(name)
        )

    def _auto_fields(self):

        return set(
            self._menu("auto_fields")
        )

    def _multi_select_fields(self):

        return set(
            self._menu("multi_select_fields")
        )

    def _menu_option(self, menu, key):

        return (
            self._menu("menu_options")
            .get(menu, {})
            .get(key, "")
        )

    def _load_state(self):

        try:

            return load_yaml(
                self.state_file
            ) or {}

        except Exception:

            return {}

    def run(self):

        screen_enter()

        try:

            return self._steps()

        finally:

            screen_exit()

    def _steps(self):

        project = None
        target = None
        fields = []
        values = {}
        output = None

        step = 0

        while True:

            if step == 0:

                result = self._select_project(
                    self._header(
                        None,
                        None,
                        [],
                        {}
                    )
                )

                if result is BACK:
                    continue

                project = result

                self.project = result

                step = 1

                continue

            if step == 1:

                result = self._select_target(
                    self._header(
                        project,
                        None,
                        [],
                        {}
                    ),
                    project
                )

                if result is BACK:
                    step = 0
                    continue

                target = result

                fields = self._fields_for(
                    target
                )

                values = {}

                if project:

                    for field, _ in fields:

                        if field in self._auto_fields():
                            values[field] = project

                    fields = [
                        (f, r)
                        for f, r in fields
                        if f not in self._auto_fields()
                    ]

                step = 2

                continue

            index = step - 2

            if index < len(fields):

                field, required = fields[index]

                values.pop(field, None)

                result = self._ask_field(
                    self._header(
                        project,
                        target,
                        fields,
                        values
                    ),
                    values,
                    field,
                    required,
                    index + 1,
                    len(fields)
                )

                if result is BACK:
                    step -= 1
                    continue

                if result is not None:
                    values[field] = result

                step += 1

                continue

            if index == len(fields):

                hooks = get_hooks(target[0])

                if hooks is not None:

                    ok, message = hooks.validate(
                        self,
                        values
                    )

                    if not ok:

                        print(message)

                        step = 2

                        continue

                    hooks.prepare(
                        self,
                        values
                    )

                result = self._select_output(
                    self._header(
                        project,
                        target,
                        fields,
                        values
                    )
                )

                if result is BACK:
                    step -= 1
                    continue

                output = result

                step += 1

                continue

            header = self._header(
                project,
                target,
                fields,
                values
            )

            header.append(
                f"{_e('✅ ')}output: {output}"
            )

            result = self._select_launch(
                header
            )

            if result is BACK:
                step -= 1
                continue

            self._save_state(
                project,
                target,
                values
            )

            return target[0], values, output, result

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

        projects = self._dirs(
            self.workspaces,
            exclude={"archived"}
        )

        options = [
            f"{_e(self._menu_option('project', 'item'))}{p}"
            for p in projects
        ]

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

    def _workflow_purpose(
        self,
        name
    ):

        try:

            text = read_text(
                self.root
                / "workflows"
                / f"{name}.md"
            )

        except OSError:

            return ""

        section = None

        for line in text.splitlines():

            stripped = line.strip()

            if stripped.startswith("## "):
                section = stripped[3:]
                continue

            if section == "Purpose" and stripped:
                return stripped

        return ""

    def _command_description(
        self,
        name
    ):

        path = (
            self.root
            / "cli"
            / "commands"
            / f"aic-{name}.md"
        )

        if not path.exists():

            path = (
                self.root
                / "cli"
                / "commands"
                / f"{name}.md"
            )

        try:

            text = read_text(path)

        except OSError:

            return ""

        for line in text.splitlines():

            stripped = line.strip()

            if stripped.startswith("description:"):

                return stripped.split(
                    ":",
                    1
                )[1].strip()

        return ""

    @staticmethod
    def _short(
        text,
        limit=58
    ):

        if len(text) <= limit:
            return text

        return text[: limit - 1] + "…"

    def _fields_for(
        self,
        target
    ):

        name, kind = target

        self.target_name = name

        if kind == "command":

            return self._command_fields(name)

        required, optional = self._parse_inputs(
            read_text(
                self.root
                / "workflows"
                / f"{name}.md"
            )
        )

        fields = []

        for f in required:
            fields.append((f, True))

        for f in optional:
            fields.append((f, False))

        return fields

    @staticmethod
    def _parse_inputs(
        text
    ):

        required = []
        optional = []

        section = None
        bucket = None

        for line in text.splitlines():

            stripped = line.strip()

            if stripped.startswith("## "):
                section = stripped[3:]
                bucket = None
                continue

            if section != "Inputs":
                continue

            if stripped == "Required:":
                bucket = required
                continue

            if stripped == "Optional:":
                bucket = optional
                continue

            if (
                stripped.startswith("- ")
                and bucket is not None
            ):

                item = stripped[2:].strip()

                if item and item != "None":
                    bucket.append(item)

        return required, optional

    def _ask_field(
        self,
        header,
        values,
        field,
        required,
        position,
        total
    ):

        choices = self._choices_for(
            values,
            field
        )

        suffix = (
            "required"
            if required
            else "optional"
        )

        title = f"{field} ({suffix}) [{position}/{total}]"

        note = self._field_note(field)

        icon = _e(
            self._field_icon(field)
        )

        if choices:

            labels = self._option_descriptions(field)

            options = []

            for c in choices:

                display = c

                if labels and c in labels:
                    display = f"{c} — {labels[c]}"

                options.append(f"{icon}{display}")

            if field in self._multi_select_fields():

                picked = choose_many(
                    title,
                    options,
                    header=header,
                    note=note
                )

                if picked is BACK:
                    return BACK

                if picked is None:
                    return None

                value = ", ".join(
                    choices[i] for i in picked
                )

                self.history[field] = value

                return value

            options.append(
                f"{_e(self._menu_option('field_actions', 'manual'))}"
                f"{self._t('field_actions.manual', 'type manually')}"
            )

            manual_index = len(choices)

            skip_index = None

            if not required:

                options.append(
                    f"{_e(self._menu_option('field_actions', 'skip'))}"
                    f"{self._t('field_actions.skip', 'skip')}"
                )

                skip_index = manual_index + 1

            default = 0

            previous = self._previous_value(
                field
            )

            if previous in choices:
                default = choices.index(previous)

            idx = choose(
                title,
                options,
                default,
                allow_skip=not required,
                header=header,
                note=note
            )

            if idx is BACK:
                return BACK

            if idx is None:
                return None

            if (
                skip_index is not None
                and idx == skip_index
            ):
                return None

            if idx == manual_index:

                value = ask_text(
                    f"{icon}{field}: ",
                    header,
                    note=note
                )

                if value is BACK:
                    return BACK

                if not value:
                    return None

            else:

                value = choices[idx]

            self.history[field] = value

            return value

        prompt = (
            f"{icon}{field} ({suffix}): "
            if required
            else f"{icon}{field} ({suffix}, Enter to skip): "
        )

        value = ask_text(
            prompt,
            header,
            note=note
        )

        if value is BACK:
            return BACK

        if not value:
            return None

        self.history[field] = value

        return value

    def _previous_value(
        self,
        field
    ):

        previous = self.history.get(field)

        if previous:
            return previous

        if not self.project:
            return None

        pstate = (
            self.state
            .get("projects", {})
            .get(self.project, {})
        )

        if field == "Task ID":
            return pstate.get("last_task")

        if field == "Change ID":
            return pstate.get("last_change")

        return None

    def _choices_for(
        self,
        values,
        field
    ):

        if field in self._auto_fields():
            return providers.workspace_dirs(self)

        if field == "Mode":

            if self.target_name == "maintain":
                return [
                    "weekly",
                    "monthly",
                    "quarterly",
                    "on-demand"
                ]

            return ["re-entry"]

        if field in (
            "Base Branch",
            "Zip",
            "Operation",
            "Keep Results",
            "Knowledge Operation",
            "Analysis Target",
            "Analysis Scope"
        ):

            return self._field_choices(field)

        if field == "Workspace":
            return providers.workspace_dirs(self)

        if field == "Projects":
            return providers.projects_dirs(self)

        if field == "Branch":
            return providers.git_branches(self, values)

        project = (
            values.get("Project ID")
            or values.get("Workspace ID")
            or self.project
        )

        if field == "Change ID" and project:
            return providers.change_dirs(
                self,
                values,
                project
            )

        if field == "Task ID" and project:
            return providers.task_ids(
                self,
                values,
                project
            )

        return []

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

        options = [
            f"{_e(self._menu_option('launch', 'finish'))}"
            "finish (no launch)",
            f"{_e(self._menu_option('launch', 'opencode'))}"
            "open opencode in ai-workspace",
            f"{_e(self._menu_option('launch', 'pi'))}"
            "open pi in ai-workspace"
        ]

        idx = choose(
            "Launch — open an agent at the workspace root",
            options,
            header=header
        )

        if idx is BACK:
            return BACK

        return (None, "opencode", "pi")[idx]

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

        try:

            save_yaml(
                self.state_file,
                self.state
            )

        except OSError:

            pass
