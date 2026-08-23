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
2. Scaffold workspace base directories (workspaces/ projects/ repositories/ methodologies/ extensions/)
3. Ensure ai-system runtime dirs exist (metrics/ logs/)
4. Auto-detect code repositories at the workspace root and link them into projects/
5. Record a metrics baseline snapshot (metrics/baseline-{date}.json, if missing)
6. Run tools/path-audit.py to verify all referenced paths resolve
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent

sys.path.insert(0, str(ROOT))

try:

    from cli.utils.menu import BACK, ask_path

    _PATH_INPUT = True

except Exception:

    _PATH_INPUT = False

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
    "extensions",
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


def _ask_path(label, default="", only_directories=True):

    if _PATH_INPUT:

        value = ask_path(
            f"{label} (default: {default}): "
            if default
            else f"{label}: ",
            only_directories=only_directories
        )

        if value is BACK:
            return default

        return value or default

    return _ask(label, default)


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

        java_home = _ask_path(
            "Java home (build.java_home)",
            "",
            only_directories=True
        )
        maven_home = _ask_path(
            "Maven home (build.maven_home)",
            "",
            only_directories=True
        )
        maven_settings = _ask_path(
            "Maven settings path (build.maven_settings)",
            "",
            only_directories=False
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
            "skills": {
                "path": str(workspace_root / "extensions"),
                "description": "company/platform skill extensions (not auto-scanned by agents)",
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


def detect_platform():
    """平台检测：windows / wsl / linux（供首启生成机器层配置）。"""

    import platform

    if sys.platform == "win32":
        return "windows"

    if sys.platform.startswith("linux"):

        release = platform.release().lower()

        if "microsoft" in release or "wsl" in release:
            return "wsl"

        return "linux"

    return sys.platform


def _probe_build_paths(platform_name):
    """按平台探测常见 JDK/Maven 位置（找不到返回空串，用户自行填写）。"""

    java_home = ""
    maven_home = ""

    candidates = {
        "windows": [
            ("JAVA_HOME", "JAVA_HOME"),
            ("D:/tools/java", "D:/tools/java"),
            ("C:/Program Files/Java", "C:/Program Files/Java"),
        ],
        "wsl": [
            ("/usr/lib/jvm", "/usr/lib/jvm"),
            ("/opt/java", "/opt/java"),
            ("/mnt/d/tools/java", "/mnt/d/tools/java"),
        ],
        "linux": [
            ("/usr/lib/jvm", "/usr/lib/jvm"),
            ("/opt/java", "/opt/java"),
        ],
    }[platform_name]

    env_candidates = [c for c in candidates if c[0] == "JAVA_HOME"]

    for env_name, _ in env_candidates:

        val = os.environ.get(env_name)

        if val:
            java_home = val
            break

    if not java_home:

        for env_name, base in candidates:

            if env_name == "JAVA_HOME":
                continue

            if os.path.isdir(base):

                entries = sorted(os.listdir(base))

                jdk = next(
                    (e for e in entries if e.lower().startswith("jdk") or "java" in e.lower()),
                    None
                )

                if jdk:
                    java_home = os.path.join(base, jdk)
                    break

    for env_name, base in candidates:

        if env_name == "JAVA_HOME":
            continue

        maven = os.path.join(base, "..", "apache-maven-3.6.3")

        maven = os.path.normpath(maven)

        if os.path.isdir(maven):
            maven_home = maven
            break

    return java_home, maven_home


def generate_home_env(
    workspace_root,
    interactive
):
    """首启生成机器层配置 ~/.config/ai-system/env.yaml（非破坏，存在即跳过）。

    默认全部走 ~/.config：跨平台原生（Path.home()/.config 各平台一致）；
    按系统检测生成；特殊情况（如 WSL 下 /mnt/d/...）用户自行编辑本文件。
    """

    from cli.services.environment import home_config_path

    target = home_config_path()

    if target.exists():
        print(f"home config exists, skipping: {target}")
        return False

    platform_name = detect_platform()

    java_home, maven_home = _probe_build_paths(platform_name)

    if interactive and not java_home:

        java_home = _ask_path(
            "Java home (build.java_home, 留空跳过)",
            "",
            only_directories=True
        )

    if interactive and not maven_home:

        maven_home = _ask_path(
            "Maven home (build.maven_home, 留空跳过)",
            "",
            only_directories=True
        )

    data = {
        "workspace": {
            "root": str(workspace_root),
        },
        "build": {
            "java_home": java_home,
            "maven_home": maven_home,
            "maven_settings": "",
            "backend": "maven",
        },
    }

    import yaml

    target.parent.mkdir(parents=True, exist_ok=True)

    target.write_text(
        "# 机器层环境配置（首启按系统检测生成，可自行编辑）。\n"
        "# 平台: " + platform_name + "\n"
        "# 跨平台原生：默认全部走 ~/.config；WSL/Linux 用 /mnt/d/... 或 /usr/...，"
        "Windows 用 D:\\...，各平台各有一份，互不覆盖。\n"
        "# 特殊情况（如 WSL 工作区在 /mnt/d/...）：直接修改本文件对应路径即可。\n"
        + yaml.safe_dump(
            data,
            allow_unicode=True,
            sort_keys=False
        ),
        encoding="utf-8"
    )

    print(f"generated: {target} (平台: {platform_name})")
    print("  -> 如需调整（如 WSL 路径 /mnt/d/...），直接编辑该文件")

    return True


def scaffold(workspace_root):

    created = 0

    for name in BASE_DIRS:

        if _ensure_dir(workspace_root / name):
            print(f"created: {workspace_root / name}")
            created += 1

    return created


def ensure_runtime_dirs():

    """Create ai-system runtime dirs (metrics/, logs/) that the contract
    declares and generated artifacts depend on.

    Non-destructive: existing dirs are skipped.
    """

    created = 0

    for name in ("metrics", "logs"):

        if _ensure_dir(ROOT / name):
            print(f"created: {ROOT / name}")
            created += 1

    return created


def record_baseline():

    """Record the first metrics snapshot as the health baseline.

    Snapshot path follows governance/policies/skill-policy.md section 6
    (metrics/baseline-{date}.json). Skipped when a baseline already exists
    so re-runs stay non-destructive.
    """

    import datetime

    metrics_dir = ROOT / "metrics"

    if not metrics_dir.is_dir():
        return False

    existing = sorted(metrics_dir.glob("baseline-*.json"))

    if existing:
        return False

    metrics = ROOT / "tools" / "repo-metrics.py"

    if not metrics.exists():
        return False

    stamp = datetime.date.today().isoformat()

    snapshot = metrics_dir / f"baseline-{stamp}.json"

    print()
    print("recording metrics baseline snapshot")

    subprocess.run(
        [sys.executable, str(metrics), "--repo-root", str(ROOT), "--snapshot", str(snapshot)],
        cwd=str(ROOT)
    )

    return True


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

    generate_home_env(
        workspace_root,
        interactive
    )

    scaffold(workspace_root)

    ensure_runtime_dirs()

    link_repos(
        workspace_root,
        interactive
    )

    record_baseline()

    print()
    print("Next:")
    print("  pip install -e .        # register the `aic` CLI")
    print("  aic                     # interactive wizard")

    run_audit()


if __name__ == "__main__":
    main()
