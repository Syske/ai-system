r"""Initialize the AI system environment.

Usage:
    python tools/setup.py                       # interactive, with defaults
    python tools/setup.py --non-interactive     # use defaults, no prompts
    python tools/setup.py --workspace /path     # explicit workspace root
    python tools/setup.py --environment test    # environment name (default: local)

Non-destructive: creates missing directories and repository links only.
Never deletes or overwrites existing config, directories, or links.

Steps:
1. Generate config/environments/{environment}.yaml from template structure (if missing)
2. Scaffold workspace base directories (workspaces/ projects/ repositories/ methodologies/)
3. Auto-detect code repositories at the workspace root and link them into projects/
4. Run tools/path-audit.py to verify all referenced paths resolve
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent

SYSTEM_DIRS = {
    "ai-system",
    "workspaces",
    "projects",
    "repositories",
    "methodologies",
    "archived",
    "logs",
    "metrics",
    "reports",
    "skills",
    "governance",
    "templates",
    "loaders",
    "maintainers",
    "rfc",
    "cli",
    "config",
    "workflows",
    "tools",
    "aic.egg-info",
}

REPO_MARKERS = (
    ".git",
    "pom.xml",
    "package.json",
    "go.mod",
    "Cargo.toml",
    "build.gradle",
    "settings.gradle",
)

BASE_DIRS = (
    "workspaces",
    "projects",
    "repositories",
    "methodologies",
)


def _parse_args():

    interactive = True
    workspace = None
    environment = "local"

    args = list(sys.argv[1:])

    if "--non-interactive" in args:
        interactive = False
        args.remove("--non-interactive")

    if "--workspace" in args:
        index = args.index("--workspace")
        workspace = Path(args[index + 1])

    if "--environment" in args:
        index = args.index("--environment")
        environment = args[index + 1]

    return interactive, workspace, environment


def _ask(label, default=None):

    if default:
        raw = input(f"{label} (default: {default}): ").strip()
        return raw or default

    raw = input(f"{label}: ").strip()
    return raw


def _ensure_dir(path):

    if path.is_dir():
        return False

    path.mkdir(parents=True, exist_ok=True)

    return True


def generate_env(
    workspace_root,
    environment,
    interactive,
    env_dir=None
):

    env_dir = env_dir or ROOT / "config" / "environments"

    env_file = env_dir / f"{environment}.yaml"

    if env_file.exists():
        print(f"config exists, skipping: {env_file}")
        return False

    env_dir.mkdir(parents=True, exist_ok=True)

    repository_root = workspace_root / "projects"

    java_home = ""
    maven_home = ""
    maven_settings = ""

    if interactive:

        java_home = _ask("Java home (build.java_home)", "")
        maven_home = _ask("Maven home (build.maven_home)", "")
        maven_settings = _ask(
            "Maven settings path (build.maven_settings)",
            ""
        )

    data = {
        "workspace": {
            "root": str(workspace_root),
            "repository_root": str(repository_root),
        },
        "build": {
            "java_home": java_home,
            "maven_home": maven_home,
            "maven_settings": maven_settings,
        },
        "layers": {
            "ai_system": {
                "path": str(ROOT),
                "description": "AI Operating System core",
            },
            "projects": {
                "path": str(repository_root),
                "description": "all code repository",
            },
            "methodologies": {
                "path": str(workspace_root / "methodologies"),
                "description": "governance standards, openspec, specs, contracts",
            },
        },
    }

    import yaml

    env_file.write_text(
        yaml.safe_dump(
            data,
            allow_unicode=True,
            sort_keys=False
        ),
        encoding="utf-8"
    )

    print(f"generated: {env_file}")

    return True


def scaffold(workspace_root):

    created = 0

    for name in BASE_DIRS:

        if _ensure_dir(workspace_root / name):
            print(f"created: {workspace_root / name}")
            created += 1

    return created


def detect_repos(workspace_root):

    repos = []

    if not workspace_root.is_dir():
        return repos

    for entry in sorted(workspace_root.iterdir()):

        if not entry.is_dir():
            continue

        if entry.name.startswith("."):
            continue

        if entry.name in SYSTEM_DIRS:
            continue

        repos.append(entry)

    return repos


def _looks_like_repo(path):

    if any((path / m).exists() for m in REPO_MARKERS):
        return True

    return False


def link_repos(
    workspace_root,
    interactive
):

    projects = workspace_root / "projects"

    projects.mkdir(parents=True, exist_ok=True)

    repos = detect_repos(workspace_root)

    if not repos:

        print(
            "no candidate repositories detected under workspace root"
        )

        return 0

    confirmed = []

    for repo in repos:

        if _looks_like_repo(repo):
            confirmed.append(repo)

        elif interactive:

            raw = input(
                f"Link {repo.name} (no repo marker found)? [y/N]: "
            ).strip()

            if raw.lower() in ("y", "yes"):
                confirmed.append(repo)

    if not confirmed:

        print("no repositories to link")

        return 0

    linked = 0

    for repo in confirmed:

        target = projects / repo.name

        if target.is_symlink() or target.exists():

            print(f"link exists, skipping: {target}")

            continue

        _create_link(target, repo)

        print(f"linked: {target} -> {repo}")

        linked += 1

    return linked


def _create_link(target, source):

    if os.name == "nt":

        subprocess.run(
            ["cmd", "/c", "mklink", "/J", str(target), str(source)],
            check=True
        )

    else:

        target.symlink_to(
            source,
            target_is_directory=True
        )


def run_audit():

    audit = ROOT / "tools" / "path-audit.py"

    if not audit.exists():
        return

    print()

    subprocess.run(
        [sys.executable, str(audit)],
        cwd=str(ROOT)
    )


def main():

    interactive, workspace, environment = _parse_args()

    workspace_root = workspace or ROOT.parent

    workspace_root = workspace_root.resolve()

    print(f"workspace root: {workspace_root}")
    print(f"environment:    {environment}")

    generate_env(
        workspace_root,
        environment,
        interactive
    )

    scaffold(workspace_root)

    link_repos(
        workspace_root,
        interactive
    )

    print()
    print("Next:")
    print("  pip install -e .        # register the `aic` CLI")
    print("  aic                     # interactive wizard")

    run_audit()


if __name__ == "__main__":
    main()
