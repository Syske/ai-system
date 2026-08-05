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
            "on-demand"
        ],
        help="Execution modifier. re-entry = L3 change re-entry (prepare/spec); weekly/monthly/quarterly/on-demand = maintenance modes (maintain)"
    )

    parser.add_argument(
        "--operation",
        choices=[
            "search",
            "diff",
            "chain",
            "impact",
            "manual"
        ],
        help="Scan operation type: search/diff/chain/impact/manual"
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

    if args.workflow == "skill-launch":

        try:

            from cli.services import skill_launcher

            wizard = Wizard(
                builder.root,
                args.environment
            )

            result = skill_launcher.run(
                wizard,
                args.agent
            )

        except (EOFError, KeyboardInterrupt):

            print()
            print("Cancelled.")

            return

        if result is None:
            return

        prompt, agent = result

        copy(prompt)

        print()
        print("✓ Skill prompt copied.")

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

        try:

            name, context, output, launch = (
                Wizard(
                    builder.root,
                    args.environment
                ).run()
            )

        except (EOFError, KeyboardInterrupt):

            print()
            print("Cancelled.")

            return

        if name == "skill-launch":

            from cli.services import skill_launcher

            wizard = Wizard(
                builder.root,
                args.environment
            )

            result = skill_launcher.run(
                wizard,
                args.agent
            )

            if result is None:
                return

            prompt, agent = result

            launch = wizard.config.provider_command(agent)

        else:

            prompt = builder.build(
                name,
                context
            )

        if output == "copy":

            copy(prompt)

            print(
                "✓ Prompt copied."
            )

        elif output == "save":

            path = (
                Path(".ai-system")
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

        path = (
            Path(".ai-system")
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