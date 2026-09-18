"""Dynamic field candidate providers.

Static choices live in config/menu.yaml (field_choices). Dynamic choices —
filesystem directories and git branches — are computed here so wizard.py
stays a thin dispatcher. Each provider receives the wizard (for workspace /
project roots) and the collected field values.
"""

import subprocess
import sys
from pathlib import Path


def _linux_path(path):
    """Convert a Windows absolute path (e.g. D:\\workspace\\x) to WSL (/mnt/d/workspace/x).

    No-op on Windows or for non-Windows-style paths. Used so workspace.yaml
    repo paths written on Windows resolve correctly under WSL.
    """

    s = str(path)

    if len(s) < 3 or s[1] != ":":
        return s

    s = s.replace("\\", "/")

    drive = s[0].lower()

    return f"/mnt/{drive}{s[2:]}"


def _repo_path(wizard, path):
    """Resolve a repo path from workspace.yaml to a real filesystem path."""

    if not path:
        return None

    p = Path(str(path))

    if Path(str(p)).is_absolute():
        return p

    if sys.platform == "linux":
        return Path(_linux_path(path))

    return wizard.projects_root / path


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
            "launch"
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


def task_card_summaries(wizard, values, project):
    """每张任务卡 → 一行概述（标题 + 服务），供 Task ID 选项描述。

    从卡片首行 `# T-{id}: {标题}` 与 `**服务**` 字段解析；无标题时回退卡名。
    """

    cards = (
        wizard.workspaces
        / project
        / "openspec"
        / "changes"
    ).glob("*/tasks/cards/*.md")

    out = {}

    for card in cards:

        text = card.read_text(encoding="utf-8", errors="replace")

        title = ""

        for line in text.splitlines():

            line = line.strip()

            if line.startswith("# T-"):

                _, _, title = line.partition(":")
                title = title.strip()
                break

        svc = ""

        for line in text.splitlines():

            stripped = line.strip()

            if stripped.startswith("**服务**") and ":" in stripped:
                svc = stripped.split(":", 1)[1].strip()
                break

            if stripped.startswith("**服务**：") :
                svc = stripped.split("：", 1)[1].strip()
                break

        summary = title or card.stem

        if svc:
            summary = f"{summary}（{svc}）"

        out[card.stem] = summary

    return out


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
        return _repo_path(wizard, mapped)

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

    for bucket in ("available", "unavailable"):

        for entry in repos.get(bucket) or []:

            if isinstance(entry, dict) and entry.get("path"):

                entry["path"] = _repo_path(wizard, entry["path"])

    return repos
