from pathlib import Path

from cli.utils.file import read_text
from cli.utils.menu import (
    BACK,
    Section,
    ask_text,
    choose,
    icons_enabled,
    is_tty,
    screen_enter,
    screen_exit
)
from cli.utils.yaml import load_yaml, save_yaml


FIELD_NOTES = {
    "Project ID": "from workspaces/",
    "Workspace ID": "from workspaces/",
    "Change ID": "from openspec/changes/",
    "Task ID": "from openspec/changes/*/tasks/cards/",
    "Mode": "re-entry = L3 change (prepare/spec); weekly/monthly/quarterly/on-demand = maintain"
}

FIELD_ICONS = {
    "Project ID": "🏠 ",
    "Workspace ID": "🖥️ ",
    "Change ID": "🔀 ",
    "Task ID": "🎯 "
}

AUTO_FIELDS = (
    "Project ID",
    "Workspace ID"
)

DEFAULT_COMMAND_FIELDS = [
    ("Project ID", False),
    ("Change ID", False),
    ("Change Request", False)
]

COMMAND_FIELDS = {
    "trace": [
        ("Project ID", False),
        ("Code Reference", False),
        ("Change ID", False),
        ("Base Branch", False)
    ],
    "maintain": [
        ("Mode", False),
        ("Scope", False)
    ],
    "pack": [
        ("Output Directory", False),
        ("Zip", False)
    ],
    "setup": [
        ("Workspace Root", False)
    ]
}

COMMAND_NEXT = {
    "trace": "verify",
    "propose": "spec"
}

MAIN_FLOW = [
    "prepare",
    "spec",
    "dev-setup",
    "develop",
    "review",
    "verify",
    "release"
]

BRANCH_FLOW = [
    "bugfix"
]

SUPPORT_FLOW = [
    "bootstrap",
    "analysis",
    "knowledge"
]


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

        self.state_file = (
            self.workspaces
            / ".aic-state.yaml"
        )

        self.state = self._load_state()

        self.history = {}

        self.project = None

        self.target_name = None

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

                        if field in AUTO_FIELDS:
                            values[field] = project

                    fields = [
                        (f, r)
                        for f, r in fields
                        if f not in AUTO_FIELDS
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
                    f"{_e('🏠 ')}project: {shown}"
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
            f"{_e('🏠 ')}{p}"
            for p in projects
        ]

        options.append(
            f"{_e('💻 ')}system (no project)"
        )

        default = 0

        last = self.state.get("last_project")

        if last in projects:
            default = projects.index(last)

        options[default] = (
            f"{_e('⭐ ')}{options[default]}"
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
            p.stem.replace("opsx-", "")
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
            number=None
        ):

            targets.append((name, kind))

            if kind == "workflow":

                icon = _e("🚀 ")

                desc = self._workflow_purpose(name)

            else:

                icon = _e("⚡ ")

                desc = self._command_description(name)

            if number is not None and is_tty():

                label = f"{icon}{number}. {name}"

            else:

                label = f"{icon}{name}"

            if kind == "command":
                label += " (command)"

            if desc:
                label += f" — {self._short(desc)}"

            labels.append(label)

        def section(text):

            targets.append(None)

            labels.append(Section(text))

        section("Main Flow")

        for number, name in enumerate(MAIN_FLOW, 1):

            if name in workflows:
                add(name, "workflow", number)

        section("Branch")

        for name in BRANCH_FLOW:

            if name in workflows:
                add(name, "workflow")

        section("Support")

        for name in SUPPORT_FLOW:

            if name in workflows:
                add(name, "workflow")

        remaining = [
            w
            for w in workflows
            if (
                w not in MAIN_FLOW
                and w not in BRANCH_FLOW
                and w not in SUPPORT_FLOW
            )
        ]

        if remaining:

            section("Other")

            for name in remaining:
                add(name, "workflow")

        section("Commands")

        for c in commands:
            add(c, "command")

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

                recommended = COMMAND_NEXT.get(
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

            for w in workflows:

                if w != name and w in lowered:
                    return w

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
            / f"opsx-{name}.md"
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

            return list(
                COMMAND_FIELDS.get(
                    name,
                    DEFAULT_COMMAND_FIELDS
                )
            )

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

        note = FIELD_NOTES.get(field)

        if note and choices:
            title += f" — {note}"

        if choices:

            icon = _e(
                FIELD_ICONS.get(field, "")
            )

            options = [
                f"{icon}{c}"
                for c in choices
            ]

            options.append(
                f"{_e('⌨️ ')}type manually"
            )

            manual_index = len(choices)

            skip_index = None

            if not required:

                options.append(
                    f"{_e('⏭️ ')}skip"
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
                header=header
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
                    f"{field}: ",
                    header
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
            f"{field} ({suffix}): "
            if required
            else f"{field} ({suffix}, Enter to skip): "
        )

        value = ask_text(
            prompt,
            header
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

        if field in AUTO_FIELDS:
            return self._dirs(
                self.workspaces,
                exclude={"archived"}
            )

        if field == "Mode":

            if self.target_name == "maintain":
                return [
                    "weekly",
                    "monthly",
                    "quarterly",
                    "on-demand"
                ]

            return ["re-entry"]

        if field == "Base Branch":
            return ["master", "main"]

        if field == "Zip":
            return ["yes", "no"]

        project = (
            values.get("Project ID")
            or values.get("Workspace ID")
            or self.project
        )

        if field == "Change ID" and project:

            return self._dirs(
                self.workspaces
                / project
                / "openspec"
                / "changes",
                exclude={"archive"}
            )

        if field == "Task ID" and project:

            cards = (
                self.workspaces
                / project
                / "openspec"
                / "changes"
            ).glob("*/tasks/cards/*.md")

            return sorted(
                {c.stem for c in cards}
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
            f"{_e('📥 ')}copy to clipboard",
            f"{_e('🖨️ ')}print",
            f"{_e('📦 ')}save to .ai-system/generated/"
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
            f"{_e('🏁 ')}finish (no launch)",
            f"{_e('🤖 ')}open opencode in ai-workspace",
            f"{_e('🌀 ')}open pi in ai-workspace"
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
