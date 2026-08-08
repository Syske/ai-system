"""Dynamic field candidate providers.

Static choices live in config/menu.yaml (field_choices). Dynamic choices —
filesystem directories and git branches — are computed here so wizard.py
stays a thin dispatcher. Each provider receives the wizard (for workspace /
project roots) and the collected field values.
"""

import subprocess


def mode_choices(wizard, values):

    if wizard.target_name == "maintain":
        return [
            "weekly",
            "monthly",
            "quarterly",
            "on-demand"
        ]

    if wizard.target_name == "skill":
        return [
            "launch",
            "optimize"
        ]

    return ["re-entry"]


def workspace_dirs(wizard):

    return wizard._dirs(
        wizard.workspaces,
        exclude={"archived"}
    )


def projects_dirs(wizard):

    return wizard._dirs(
        wizard.projects_root,
        exclude={"archived"}
    )


def change_dirs(wizard, values, project):

    return wizard._dirs(
        wizard.workspaces
        / project
        / "openspec"
        / "changes",
        exclude={"archive"}
    )


def task_ids(wizard, values, project):

    cards = (
        wizard.workspaces
        / project
        / "openspec"
        / "changes"
    ).glob("*/tasks/cards/*.md")

    return sorted(
        {c.stem for c in cards}
    )


def git_branches(wizard, values):

    projects = values.get("Projects")

    if not projects:
        return []

    branches = set()

    for name in projects.split(","):

        name = name.strip()

        if not name:
            continue

        repo = wizard.projects_root / name

        if not repo.is_dir():
            continue

        try:

            result = subprocess.run(
                [
                    "git",
                    "-C",
                    str(repo),
                    "-c",
                    "safe.directory=*",
                    "branch",
                    "--format=%(refname:short)"
                ],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode != 0:
                continue

            for line in result.stdout.splitlines():

                line = line.strip()

                if line:
                    branches.add(line)

        except Exception:

            continue

    return sorted(branches)
