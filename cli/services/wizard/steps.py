"""Wizard mixin: main step state machine.

Split from wizard.py (P0). Steps: select project → select target →
collect fields → defaults/hooks → select output → launch confirm.
"""

from cli.services.command_hooks import get_hooks
from cli.utils.menu import BACK, e as _e


class WizardSteps:

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

                self._apply_field_defaults(
                    fields,
                    values
                )

                target_name = target[0]

                if target_name in ("skill", "skill-launch", "skill-optimize"):

                    self._save_state(
                        project,
                        target,
                        values
                    )

                    return target_name, values, "copy", None

                hooks = get_hooks(target_name)

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
