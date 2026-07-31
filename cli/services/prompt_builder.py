from pathlib import Path

from cli.utils.file import read_text
from cli.utils.yaml import load_yaml


class PromptBuilder:

    def __init__(self):

        self.root = (
            Path(__file__)
            .resolve()
            .parents[2]
        )

        self.registry = (
            self.root
            / "config"
            / "workflow-registry.yaml"
        )

        self.template = (
            self.root
            / "templates"
            / "prompts"
            / "workflow.md"
        )

    def build(
        self,
        workflow: str,
        context: dict
    ) -> str:

        registry = load_yaml(
            self.registry
        )

        workflows = registry["workflows"]

        if workflow in workflows:

            return self._build_workflow(
                workflows[workflow],
                context
            )

        command_path = (
            self.root
            / "cli"
            / "commands"
            / f"opsx-{workflow}.md"
        )

        if not command_path.exists():

            command_path = (
                self.root
                / "cli"
                / "commands"
                / f"{workflow}.md"
            )

        if command_path.exists():

            return self._build_command(
                workflow,
                command_path,
                context
            )

        raise RuntimeError(
            f"Unknown workflow or command: {workflow}"
        )

    def _build_workflow(
        self,
        config_path,
        context: dict
    ) -> str:

        config = load_yaml(
            self.root
            / config_path
        )

        workflow_md = read_text(
            self.root
            / config["workflow"]
        )

        runtime_md = read_text(
            self.root
            / config["runtime"]
        )

        template = read_text(
            self.template
        )

        return self._render(
            template,
            {
                "workflow_name":
                    config["name"],
                "workflow_definition":
                    workflow_md,
                "runtime_definition":
                    runtime_md,
                "inputs":
                    self._inputs(context)
            }
        )

    def _build_command(
        self,
        name: str,
        command_path,
        context: dict
    ) -> str:

        template = read_text(
            self.root
            / "templates"
            / "prompts"
            / "command.md"
        )

        return self._render(
            template,
            {
                "command_name":
                    name,
                "command_definition":
                    read_text(command_path),
                "inputs":
                    self._inputs(context)
            }
        )

    @staticmethod
    def _inputs(
        context: dict
    ):

        ignore = {
            "workflow",
            "copy",
            "save",
            "output"
        }

        labels = {
            "workspace": "Workspace ID",
            "project": "Project ID",
            "task": "Task ID",
            "change": "Change ID",
            "issue": "Issue ID",
            "version": "Release Version",
            "request": "Change Request",
            "code": "Code Reference",
            "base": "Base Branch",
            "mode": "Mode"
        }

        lines = []

        for k, v in context.items():

            if k in ignore:
                continue

            if v is None:
                continue

            lines.append(
                f"{labels.get(k, k)}: {v}"
            )

        return "\n".join(lines)

    @staticmethod
    def _render(
        template,
        values
    ):

        result = template

        for k, v in values.items():

            result = result.replace(
                "{{" + k + "}}",
                str(v)
            )

        return result