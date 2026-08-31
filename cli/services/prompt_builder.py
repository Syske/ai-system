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

        prompt = self._render(
            template,
            {
                "workflow_name":
                    config["name"],
                "workflow_definition":
                    self._dedupe_runtime_section(
                        self._strip_frontmatter(workflow_md)
                    ),
                "runtime_definition":
                    self._skeletonize_runtime(
                        config["runtime"],
                        runtime_md
                    ),
                "external_capabilities":
                    self._capabilities_section(workflow_name),
                "inputs":
                    self._inputs(context, declared),
                "ai_system_root":
                    str(self.root),
                "workspace_root":
                    str(self.root.parent),
            }
        )

        return self._resolve_root_placeholders(prompt)

    def _capabilities_section(
        self,
        workflow_name: str
    ) -> str:
        """Build the optional-external-capabilities note for a main-chain stage.

        Injected at the `{{external_capabilities}}` anchor (before `# Task`),
        so the agent sees it before execution starts. Returns an empty string
        when the stage has no enabled entry or none of its paths resolve — a
        missing extensions/ repo must NOT leak a dangling relative path into
        the generated prompt (machine/environment-level fact, not a capability).
        """

        from cli.services import main_chain_caps

        caps = main_chain_caps.external_capabilities(
            self.root,
            workflow_name
        )

        if not caps:

            return ""

        resolved = []

        for c in caps:

            path = self._resolve_ref(c.get("path") or "")

            if not path:
                continue

            desc = c.get("desc") or ""

            resolved.append(
                f"- {c.get('skill', '')} ({path}) — {desc}"
            )

        if not resolved:

            return ""

        lines = [
            "## Optional External Capabilities",
            "You may use these registered external skills on demand for "
            "this stage:",
            "",
            *resolved,
        ]

        return "\n".join(lines)

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

        return self._resolve_root_placeholders(
            self._render(
                template,
                {
                    "command_name":
                        name,
                    "command_definition":
                        self._strip_frontmatter(
                            read_text(command_path)
                        ),
                    "inputs":
                        self._inputs(context, declared),
                    "ai_system_root":
                        str(self.root),
                    "workspace_root":
                        str(self.root.parent),
                }
            )
        )

    def _resolve_root_placeholders(self, prompt: str) -> str:
        """渲染期解析根路径占位符（P30，白名单）。

        仅替换 environment.paths() 返回的键（{workspace_root}/{repository_root}/
        {workspaces_root}/{outputs_root}/{environment} 等）的单括号占位符；
        运行期键（{desc}/{date}/{service_id}/{project_id} 等）不在白名单，保持符号。
        模板文件零改动（P25 单一来源）；paths() 解析失败或键缺失时保留原文。
        """

        try:

            from cli.services.environment import paths

            resolved = {
                k: str(v)
                for k, v in paths(self.root).items()
                if v
            }

        except Exception:

            return prompt

        result = prompt

        for key, value in resolved.items():

            result = result.replace(
                "{" + key + "}",
                value
            )

        return result

    def _resolve_ref(self, p: str):
        """Resolve a capability reference to an absolute path, existence-first.

        Convention: `skills/...` resolves against the ai-system root,
        `extensions/...` against the workspace root. Returns the resolved
        absolute path when the target exists; `None` when it does NOT — a
        missing target (e.g. an extensions/ repo absent on this machine) must
        never be injected as a dangling relative path into the prompt.
        """

        if not p:
            return None

        cand = Path(p)

        if cand.is_absolute():
            return str(cand)

        for base in (self.root, self.root.parent):

            probe = base / p

            if probe.exists():
                return str(probe)

        return None

    @staticmethod
    def _strip_frontmatter(md: str) -> str:
        """Strip the YAML frontmatter block (P25 asset syntax).

        The frontmatter is the machine contract (name/description/workflow);
        its inputs/next/outputs are repeated by the eight Markdown sections
        below it, so embedding it whole is redundant noise for the agent.
        Returns the body unchanged when no frontmatter is present.
        """

        import re

        m = re.match(r"^---\n.*?\n---\n?", md, re.S)

        if not m:
            return md

        return md[m.end():].lstrip("\n")

    @staticmethod
    def _dedupe_runtime_section(md: str) -> str:
        """Point the workflow body's `## Runtime` section at the skeleton.

        The workflow body carries `## Runtime` with a relative path
        (`templates/runtime/runtime-<wf>.md`); the embedded runtime skeleton
        (below) already lists the same file with an absolute path. Replacing
        the section body with a pointer avoids the duplicated reference while
        keeping the eight-section structure intact (render-layer only — the
        source workflow file is untouched, P25 / single source).
        """

        import re

        m = re.search(
            r"(?ms)^## Runtime\n.*?\n(?=## )",
            md,
        )

        if not m:
            return md

        return (
            md[:m.start()]
            + "## Runtime\n\n- See the Runtime Skeleton below (full "
            "template path listed there).\n\n"
            + md[m.end():]
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

    def _skeletonize_runtime(
        self,
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

        R3 强制全量开关（Q2）：设置环境变量 AIC_FULL_RUNTIME=1 时内嵌全量
        runtime（用于 agent 无文件读取能力 / 需要完整指令的场景）。
        """

        import os

        if os.environ.get("AIC_FULL_RUNTIME") == "1":
            return runtime_md

        import re
        lines = runtime_md.splitlines()
        skeleton = []
        current_phase = None
        last_phase = None
        intro_seen = False

        # Behavior constraints tagged `<!-- @keep -->` survive skeletoning:
        # they are interaction rules (clarify one-question-at-a-time,
        # mid-task checkpoints) that must reach the prompt even though the
        # phase body itself is only referenced on demand.
        keep_marker = "<!-- @keep -->"

        # Phase headings may be level-1 (`# Phase N — …`, dev-setup) or
        # level-2 (`## Phase N — …`, prepare); match both, preserving the
        # original heading text verbatim.
        for line in lines:

            s = line.strip()

            if keep_marker in line:

                kept = line.split(keep_marker)[0].rstrip()

                if kept:

                    if last_phase:
                        skeleton.append(f"  {kept}")
                    else:
                        skeleton.append(f"- {kept}")

                continue

            m = re.match(r"^#{1,2} Phase (\d+[^—]*—?.+)$", s)

            if m:

                if current_phase:

                    skeleton.append("")

                current_phase = s
                last_phase = s
                intro_seen = False

                skeleton.append(s)

                continue

            if current_phase and s and not s.startswith(("#", "-", "|", "`")):

                # 引言行（Collect:/Generate:/Identify: 等，后跟列表项）单独取
                # 会丢失宾语；尝试合并首个列表项，否则取原文。
                snippet = f"  {s[:120]}"

                for nxt in lines[lines.index(line) + 1:]:

                    ns = nxt.strip()

                    if ns.startswith("-") and ns[1:].strip():
                        snippet += f"\n    {ns[:120]}"
                        break

                    if ns and not ns.startswith(("-", "#", "|", "`", ":")):
                        break

                skeleton.append(snippet)

                current_phase = None  # 只取每阶段第一句要求

        skeleton.append(
            f""
        )
        skeleton.append(
            f"Full runtime template: {self.root / runtime_path} "
            "(read the phase's section when executing it)"
        )

        body = "\n".join(skeleton)

        return (
            "## Runtime Skeleton\n\n"
            "Phases of the full runtime template (read the referenced file "
            "when executing a phase):\n\n"
            + body
        )

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