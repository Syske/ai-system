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
                workflow,
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
        workflow_name: str,
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

        declared = self._workflow_fields(
            workflow_md
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
                    self._inputs(context, declared)
            }
        )

    def _build_command(
        self,
        name: str,
        command_path,
        context: dict
    ) -> str:

        declared = self._command_fields(name)

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
                    self._inputs(context, declared)
            }
        )

    def _workflow_fields(self, workflow_md):
        """Field names declared by a workflow's ## Inputs section.

        Inline annotations like `(default: master)` are stripped so the
        contract matches wizard/CLI keys (e.g. `Base Branch` matches
        `Base Branch (default: master)`).
        """

        import re

        from cli.services.workflow_reader import parse_inputs

        required, optional = parse_inputs(workflow_md)

        def norm(name):
            return re.sub(
                r"\s*\(default:[^)]*\)\s*$",
                "",
                name
            ).strip()

        return {
            norm(f)
            for f in (required + optional)
        }

    def _command_fields(self, name):
        """Field names declared in menu.yaml command_fields (or default)."""

        menu = load_yaml(
            self.root
            / "config"
            / "menu.yaml"
        ) or {}

        fields = (
            menu
            .get("command_fields", {})
            .get(name)
        )

        if fields is None:
            fields = menu.get(
                "default_command_fields",
                []
            )

        return {
            str(f[0])
            for f in fields
        }

    @staticmethod
    def _inputs(
        context: dict,
        declared=None
    ):

        ignore = {
            "workflow",
            "copy",
            "save",
            "output",
            "environment",
            "agent",
            "provider",
            "mode",
            "operation",
            "keep_results",
            "compare",
            "projects",
            "base",
            "code",
            "task",
            "change",
            "workspace",
            "project",
            "request",
            "issue",
            "version",
            "scope"
        }

        labels = PromptBuilder._labels()

        lines = []

        for k, v in context.items():

            if k in ignore:
                continue

            if v is None or v is False or v == "":
                continue

            if declared is not None and k not in declared:
                # 字段契约过滤：只输出当前目标声明的字段
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