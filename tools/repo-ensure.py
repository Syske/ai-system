#!/usr/bin/env python3
"""repo-ensure.py — ensure service repositories exist under projects/ (P58).

Source of truth: {workspace_root}/repositories/{service_id}.yaml
(service metadata: repositories.<id>.git.url / default_branch / technology).

Modes:
  ensure <service_id>   — clone into {repository_root}/{service_id} when missing;
                          verify the repo when present (no fetch by default).
  check <service_id>    — print status: cloned / missing / no-metadata / invalid.
  list                  — print service ids with metadata (repositories/*.yaml).
  validate              — validate all repositories/*.yaml (id unique, git.url).

Exit code: 0 = ok; 1 = not cloned (missing/invalid); 2 = usage error.
"""

import argparse
import subprocess
import sys
from pathlib import Path


def _workspace_paths():
    """Resolve workspace/repository roots via the shared environment layer."""

    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

    from cli.services.environment import resolve_environment

    env = resolve_environment()

    paths = env.get("paths") or {}

    if not paths:
        # fallback: default layout (ai-system root parent = workspace root)
        root = Path(__file__).resolve().parents[1].parent
        return root, root / "projects"

    return Path(paths["workspace_root"]), Path(paths["repository_root"])


def _load_yaml(path):
    """Load yaml via the shared loader (cli.utils.yaml)."""

    from cli.utils.yaml import load_yaml

    try:
        return load_yaml(path) or {}
    except Exception:
        return {}


def load_metadata(workspace_root, service_id):
    """Return (git_url, default_branch) from repositories/<id>.yaml.

    Returns (None, None) when metadata is absent.
    """

    yaml_path = workspace_root / "repositories" / f"{service_id}.yaml"

    if not yaml_path.exists():
        return None, None

    data = _load_yaml(yaml_path)

    entry = (
        (data.get("repositories") or {})
        .get(service_id, {})
    )

    if isinstance(entry, str):
        entry = {}

    git = entry.get("git") or {}

    url = (
        git.get("url")
        or (data.get("git") or {}).get("url")
    )

    default_branch = (
        entry.get("default_branch")
        or (data.get("repositories") or {}).get(service_id, {})
        .get("default_branch")
    )

    return url, default_branch


def _run(cmd, cwd=None):
    return subprocess.run(
        cmd,
        cwd=cwd,
        capture_output=True,
        text=True,
        timeout=600,
    )


def ensure_service(workspace_root, projects_root, service_id, pull=False):
    """Ensure projects/<service_id> exists as a git clone. Returns (ok, msg)."""

    target = projects_root / service_id

    url, default_branch = load_metadata(workspace_root, service_id)

    if not url:
        return False, (
            f"no metadata for '{service_id}': "
            f"repositories/{service_id}.yaml missing or has no git.url"
        )

    if target.is_symlink():
        return False, (
            f"'{target}' is a symlink — P58 迁移后不应存在软链；"
            "请先解链（rm 软链后重试 ensure）。"
        )

    if target.is_dir():

        r = _run(["git", "-C", str(target), "rev-parse", "--is-inside-work-tree"])

        if r.returncode != 0:
            return False, f"'{target}' exists but is not a git repository"

        if pull:
            r2 = _run(["git", "-C", str(target), "fetch", "--all"])
            if r2.returncode != 0:
                return False, f"fetch failed: {r2.stderr.strip()[:300]}"

        return True, f"already cloned: {target}"

    # clone on demand
    cmd = ["git", "clone"]

    if default_branch:
        cmd += ["--branch", default_branch]

    cmd += [url, str(target)]

    r = _run(cmd)

    if r.returncode != 0:
        return False, f"clone failed: {r.stderr.strip()[:400]}"

    return True, f"cloned: {url} -> {target}"


def list_services(workspace_root):
    repos_dir = workspace_root / "repositories"

    if not repos_dir.is_dir():
        return []

    return sorted(p.stem for p in repos_dir.glob("*.yaml"))


def validate_metadata(workspace_root):
    """Validate every repositories/*.yaml: id unique + git.url present.

    Returns (errors: list[str]).
    """

    repos_dir = workspace_root / "repositories"

    errors = []

    if not repos_dir.is_dir():
        return ["repositories/ dir missing"]

    seen = {}

    for p in sorted(repos_dir.glob("*.yaml")):

        data = _load_yaml(p)

        data_id = data.get("id")

        if data_id in seen:
            errors.append(f"{p.name}: duplicate id '{data_id}' (also {seen[data_id]})")

        seen[data_id] = p.name

        entry = (data.get("repositories") or {}).get(data_id or "", {})

        url = None

        if isinstance(entry, dict):
            url = (entry.get("git") or {}).get("url")

        if not url:
            errors.append(f"{p.name}: no git.url for '{data_id}'")

    return errors


def main(argv=None):

    parser = argparse.ArgumentParser(description=__doc__)

    parser.add_argument(
        "mode",
        choices=["ensure", "check", "list", "validate"],
    )

    parser.add_argument("service_id", nargs="?")

    parser.add_argument(
        "--pull",
        action="store_true",
        help="ensure: git fetch when the clone already exists",
    )

    args = parser.parse_args(argv)

    workspace_root, projects_root = _workspace_paths()

    if args.mode == "list":

        for s in list_services(workspace_root):
            print(s)

        return 0

    if args.mode == "validate":

        errors = validate_metadata(workspace_root)

        if errors:

            print("repositories/ validation FAILED:")

            for e in errors:
                print(f"  - {e}")

            return 1

        print("repositories/ validation OK")

        return 0

    if not args.service_id:

        print(f"repo-ensure {args.mode} requires <service_id>", file=sys.stderr)

        return 2

    if args.mode == "check":

        url, branch = load_metadata(workspace_root, args.service_id)

        target = projects_root / args.service_id

        if not url:
            print(f"{args.service_id}: no-metadata")
            return 1

        if target.is_dir():
            print(f"{args.service_id}: cloned ({target})")
            return 0

        print(f"{args.service_id}: missing (would clone {url})")
        return 1

    # ensure
    ok, msg = ensure_service(
        workspace_root,
        projects_root,
        args.service_id,
        pull=args.pull,
    )

    print(msg)

    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
