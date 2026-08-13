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
            / f"aic-{workflow}.md"
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
                    self._skeletonize_runtime(
                        config["runtime"],
                        runtime_md
                    ),
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
            "output",
            "environment"
        }

        labels = PromptBuilder._labels()

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
    def _skeletonize_runtime(
        runtime_path: str,
        runtime_md: str
    ) -> str:
        """Reduce a full runtime template to a phase skeleton for the prompt.

        Cache/volume optimization (轨道 A 延伸): the full runtime template
        is large (release ~12K chars) and 98% static. Embedding it whole
        inflates the prompt prefix. Instead, embed:
          - every `# Phase N — Title` heading
          - the first requirement line under each phase (if any)
          - a reference to the full template file for on-demand reading

        The agent reads the referenced file when it reaches a phase.
        Determinism: phase names/order are preserved verbatim.
        """

        import re

        lines = runtime_md.splitlines()
        skeleton = []
        current_phase = None

        for line in lines:

            s = line.strip()

            m = re.match(r"^# Phase (\d+[^—]*—?.+)$", s)

            if m:

                if current_phase:
                    skeleton.append("")

                current_phase = s

                skeleton.append(s)

                continue

            if current_phase and s and not s.startswith(("#", "-", "|", "`")):

                skeleton.append(f"  {s[:120]}")

                current_phase = None  # 只取每阶段第一句要求

        skeleton.append(
            f""
        )
        skeleton.append(
            f"Full runtime template: ai-system/{runtime_path} "
            "(read the phase's section when executing it)"
        )

        return "\n".join(skeleton)

    @staticmethod
    def _labels():

        try:

            import yaml

            root = (
                Path(__file__)
                .resolve()
                .parents[2]
            )

            menu = yaml.safe_load(
                (root / "config" / "menu.yaml")
                .read_text(encoding="utf-8")
            ) or {}

            locale = menu.get("locale", "zh")

            i18n = yaml.safe_load(
                (root / "config" / "i18n" / f"{locale}.yaml")
                .read_text(encoding="utf-8")
            ) or {}

            return i18n.get("input_labels", {}) or {}

        except Exception:

            return {}

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