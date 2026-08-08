"""Wizard mixin: workflow purpose / command description helpers.

Split from wizard.py (P0).
"""

from cli.services import workflow_reader


class WizardAnalysis:

    def _workflow_purpose(
        self,
        name
    ):

        return workflow_reader.purpose(
            self.root,
            name
        )

    def _command_description(
        self,
        name
    ):

        return workflow_reader.command_description(
            self.root,
            name
        )

    @staticmethod
    def _short(
        text,
        limit=58
    ):

        return workflow_reader.short(
            text,
            limit
        )
