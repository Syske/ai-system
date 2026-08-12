"""Dynamic field candidate providers.

Static choices live in config/menu.yaml (field_choices). Dynamic choices —
filesystem directories and git branches — are computed here so wizard.py
stays a thin dispatcher. Each provider receives the wizard (for workspace /
project roots) and the collected field values.
"""

import subprocess
from pathlib import Path


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


def project_meta(wizard, project):
    """Read workspaces/<project>/contexts/project.yaml mapping.

    Returns a dict ({} when absent): {project_id, repo_path, repo_mapped,
    openspec, notes}. The mapping links a workspace project to its business
    repo in projects/ WITHOUT moving code (architecture decision 2026-08-08:
    logical mapping, physical separation).
    """

    from cli.utils.yaml import load_yaml

    if not project:
        return {}

    meta_path = (
        wizard.workspaces
        / project
        / "contexts"
        / "project.yaml"
    )

    try:

        data = load_yaml(meta_path) or {}

    except Exception:

        return {}

    if not isinstance(data, dict):
        return {}

    data.setdefault("project_id", project)

    data.setdefault("repo_path", "")

    data.setdefault("repo_mapped", bool(data.get("repo_path")))

    return data


def repo_path_for(wizard, project):
    """Resolve the business repo path for a project (mapped or projects/<id>)."""

    meta = project_meta(wizard, project)

    mapped = meta.get("repo_path")

    if mapped:
        return wizard.projects_root / mapped if not Path(mapped).is_absolute() else Path(mapped)

    if (wizard.projects_root / project).is_dir():
        return wizard.projects_root / project

    return None


def project_repos(wizard, project):
    """Read workspaces/<project>/workspace.yaml repository mapping.

    Returns {"available": [...], "unavailable": [...]} from the existing
    workspace.yaml (architecture decision 2026-08-08: logical mapping,
    physical separation — business repos stay in projects/, the workspace
    file maps service -> repo path/branch/remote). Empty dict when absent.
    """

    if not project:
        return {}

    yaml_path = (
        wizard.workspaces
        / project
        / "workspace.yaml"
    )

    from cli.utils.yaml import load_yaml

    try:

        data = load_yaml(yaml_path) or {}

    except Exception:

        return {}

    repos = data.get("repository") or {}

    if not isinstance(repos, dict):
        return {}

    return repos
