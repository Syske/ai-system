"""Wizard mixin: field collection, defaults, and ask loop.

Split from wizard.py (P0).
"""

import re

from cli.services import providers, workflow_reader
from cli.utils.file import read_text
from cli.utils.menu import BACK, e as _e, ask_text, choose, choose_many


class WizardFields:

    def _fields_for(
        self,
        target
    ):

        name, kind = target

        self.target_name = name

        if kind == "command":

            self._field_defaults = {}

            if name in ("skill", "skill-launch"):
                return []

            return self._command_fields(name)

        text = read_text(
            self.root
            / "workflows"
            / f"{name}.md"
        )

        required, optional = self._parse_inputs(
            text
        )

        self._field_defaults = (
            workflow_reader.field_defaults(
                text
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

        return workflow_reader.parse_inputs(text)

    def _apply_field_defaults(
        self,
        fields,
        values
    ):
        """Fill skipped fields that carry an inline default like
        "Environment (default: local)" so the prompt never ships an
        empty # User Inputs for a field that has a documented default.

        Defaults are parsed once in workflow_reader.field_defaults at
        field-collection time, not re-derived here.
        """

        for field, _ in fields:

            if field in values:
                continue

            default = self._field_defaults.get(
                field
            )

            if default is not None:

                values[field] = default

    def _ask_field(
        self,
        header,
        values,
        field,
        required,
        position,
        total
    ):

        if (
            self.environment_explicit
            and field.startswith("Environment")
        ):

            return self.environment_name

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
                    note=note,
                    max_visible=(
                        10
                        if field == "Projects"
                        else None
                    )
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

        field = re.sub(
            r"\s*\(default:[^)]*\)\s*$",
            "",
            field
        )

        if field in self._auto_fields():
            return providers.workspace_dirs(self)

        if field == "Mode":

            return providers.mode_choices(
                self,
                values
            )

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
