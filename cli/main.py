import argparse
import subprocess
from pathlib import Path

from cli.services.prompt_builder import PromptBuilder
from cli.services.wizard import Wizard
from cli.utils.clipboard import copy
from cli.utils.file import write_text


def _launch(
    tool,
    cwd
):

    print(
        f"Launching {tool} in {cwd} ..."
    )

    code = subprocess.call(
        tool,
        cwd=str(cwd),
        shell=True
    )

    if code != 0:

        print(
            f"{tool} exited with code {code}."
        )


_INTERACTIVE_COMMANDS = {
    "skill": "skill_launcher",
    "skill-launch": "skill_launcher",
    "chain": "chain_launcher",
    "chain-launch": "chain_launcher",
}


def _run_interactive(builder, args, name, mode=None):
    """Run an interactive command (skill / skill-launch).

    Returns (prompt, agent) or None (cancelled/quit).
    mode is the wizard-collected Mode field for /aic-skill.
    """

    import importlib

    module = importlib.import_module(
        f"cli.services.{_INTERACTIVE_COMMANDS[name]}"
    )

    wizard = Wizard(
        builder.root,
        args.environment
    )

    try:

        if name == "skill":

            return module.run_skill(
                wizard,
                args.agent,
                mode or args.mode
            )

        return module.run(
            wizard,
            args.agent
        )

    except (EOFError, KeyboardInterrupt):

        return None


def main():

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "workflow",
        nargs="?"
    )

    parser.add_argument(
        "--agent",
        help="Agent to launch for skill-launch (opencode / pi / claude; defaults to interactive pick)"
    )

    parser.add_argument(
        "--project"
    )

    parser.add_argument(
        "--environment",
        help="Environment name; resolves config/environments/{environment}.yaml (default: local). Pre-fills the wizard Environment field when given"
    )

    parser.add_argument(
        "--workspace"
    )

    parser.add_argument(
        "--task"
    )

    parser.add_argument(
        "--change",
        help="Change ID: change set directory name under workspaces/{project_id}/openspec/changes/"
    )

    parser.add_argument(
        "--issue"
    )

    parser.add_argument(
        "--version"
    )

    parser.add_argument(
        "--request",
        help="Change Request: requirement description or change point statement"
    )

    parser.add_argument(
        "--code",
        help="Code Reference: file path / class / method / API path to trace"
    )

    parser.add_argument(
        "--base",
        help="Base Branch for trace diff (default: master)"
    )

    parser.add_argument(
        "--mode",
        choices=[
            "re-entry",
            "weekly",
            "monthly",
            "quarterly",
            "on-demand",
            "launch",
        ],
        help="Execution modifier. re-entry = L3 change re-entry (prepare/spec); weekly/monthly/quarterly/on-demand = maintenance modes (maintain); launch = skill mode (/aic-skill)"
    )

    parser.add_argument(
        "--operation",
        choices=[
            "search",
            "diff",
            "chain",
            "manual"
        ],
        help="Scan operation type: search/diff/chain/manual"
    )

    parser.add_argument(
        "--projects",
        help="Scan Projects (comma separated); empty = all projects"
    )

    parser.add_argument(
        "--compare",
        help="Scan Compare With: second code block for diff"
    )

    parser.add_argument(
        "--keep-results",
        action="store_true",
        help="Scan: keep results to scans/ directory"
    )

    parser.add_argument(
        "--copy",
        action="store_true"
    )

    parser.add_argument(
        "--save",
        action="store_true"
    )

    parser.add_argument(
        "-o",
        "--output"
    )

    args = parser.parse_args()

    builder = PromptBuilder()

    if args.workflow in _INTERACTIVE_COMMANDS:

        result = _run_interactive(
            builder,
            args,
            args.workflow
        )

        if result is None:
            return

        prompt, agent = result

        copy(prompt)

        print()
        print("✓ Prompt copied.")

        wizard = Wizard(
            builder.root,
            args.environment
        )

        _launch(
            wizard.config.provider_command(agent),
            builder.root.parent
        )

        print(
            f"🚀 {agent} launched — paste with Ctrl+V."
        )

        return

    if not args.workflow:

        while True:

            try:

                name, context, output, launch, chain = (
                    Wizard(
                        builder.root,
                        args.environment
                    ).run()
                )

            except (EOFError, KeyboardInterrupt):

                print()
                print("Cancelled.")

                return

            if name in _INTERACTIVE_COMMANDS:

                mode = None

                if isinstance(context, dict):
                    mode = context.get("Mode")

                result = _run_interactive(
                    builder,
                    args,
                    name,
                    mode=mode
                )

                if result is None:

                    print()
                    print("Cancelled — back to the wizard.")

                    continue

                prompt, agent = result

                wizard = Wizard(
                    builder.root,
                    args.environment
                )

                launch = wizard.config.provider_command(agent)

            else:

                prompt = builder.build(
                    name,
                    context
                )

            break

        # 意图链：主命令 prompt 构建后，为链上后续命令构建 prompt
        # （透传已收集的 context，字段按各链命令契约自动过滤填充，如 project；
        #   剩余缺项由 AI 依各命令 ## Inputs 在对话中向用户收集）
        chain_prompts = []

        if chain:

            print()
            print(
                f"▶ 意图链后续命令: {', '.join(chain)}"
            )

            for cmd in chain:

                try:

                    chain_prompts.append(
                        builder.build(cmd, context)
                    )

                except Exception as exc:

                    print(
                        f"  ⚠ 链命令 {cmd} 构建失败: {exc}"
                    )

        if output == "copy":

            copy(prompt)

            print(
                "✓ Prompt copied."
            )

        elif output == "save":

            from cli.services import environment as env

            outputs_root = env.paths(
                builder.root,
                args.environment
            )["outputs_root"]

            path = (
                outputs_root
                / "generated"
                / f"{name}.md"
            )

            write_text(
                path,
                prompt
            )

            print(
                f"✓ Saved: {path}"
            )

        else:

            print(prompt)

        # 链 prompt：逐一输出（多命令意图的后续命令提示词）
        if chain_prompts:

            print()
            print("═" * 40)
            print("意图链后续命令提示词:")
            print("═" * 40)

            for i, cp in enumerate(chain_prompts):

                print()
                print(f"--- 链命令 {i + 1}/{len(chain_prompts)} ---")
                print()
                print(cp)

            if output == "copy":

                print(
                    "\n（链提示词已在上方输出；如需复制请分别复制）"
                )

        if launch:

            if output == "copy":

                print(
                    "Prompt is in the clipboard — paste it into the session."
                )

            _launch(
                launch,
                builder.root.parent
            )

        return

    prompt = builder.build(
        args.workflow,
        vars(args)
    )

    if args.copy:

        copy(prompt)

        print(
            "✓ Prompt copied."
        )

    if args.save:

        from cli.services import environment as env

        outputs_root = env.paths(
            builder.root,
            args.environment
        )["outputs_root"]

        path = (
            outputs_root
            / "generated"
            / f"{args.workflow}.md"
        )

        write_text(
            path,
            prompt
        )

        print(
            f"✓ Saved: {path}"
        )

    if args.output:

        write_text(
            Path(args.output),
            prompt
        )

        print(
            f"✓ Output: {args.output}"
        )

    if (
        not args.copy
        and not args.save
        and not args.output
    ):

        print(prompt)


if __name__ == "__main__":

    main()