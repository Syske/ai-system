"""Local environment config (config/environments/local.yaml).

Resolves all base paths from the machine-specific environment file and
falls back to the default directory layout when the file is missing or
unparsable. The derivation mirrors runtime-bootstrap.md Phase 2 so the CLI
and the bootstrap runtime share one source of truth.
"""

from pathlib import Path

from cli.utils.yaml import load_yaml

DEFAULT_ENV = "local"


def env_path(
    root,
    name=DEFAULT_ENV
):

    return (
        root
        / "config"
        / "environments"
        / f"{name}.yaml"
    )


def has_environment(
    root,
    name=DEFAULT_ENV
):

    return env_path(
        root,
        name
    ).exists()


def load_environment(
    root,
    name=DEFAULT_ENV
):

    try:

        data = load_yaml(
            env_path(
                root,
                name
            )
        ) or {}

    except Exception:

        data = {}

    return data


def _path(value):

    if not value:
        return None

    return Path(value)


def paths(
    root,
    name=DEFAULT_ENV
):
    """Resolve all base paths for the given environment.

    workspace_root / repository_root / workspaces_root / ai_system_root /
    methodologies_root — each from local.yaml when present, otherwise
    derived from the default directory layout.
    """

    env = load_environment(
        root,
        name
    )

    workspace = (
        env.get("workspace") or {}
    )

    layers = (
        env.get("layers") or {}
    )

    workspace_root = (
        _path(workspace.get("root"))
        or root.parent
    )

    repository_root = (
        _path(workspace.get("repository_root"))
        or workspace_root / "projects"
    )

    ai_system = (
        layers.get("ai_system") or {}
    )

    methodologies = (
        layers.get("methodologies") or {}
    )

    return {
        "environment": name,
        "workspace_root": workspace_root,
        "repository_root": repository_root,
        "workspaces_root": workspace_root / "workspaces",
        "ai_system_root": (
            _path(ai_system.get("path"))
            or root
        ),
        "methodologies_root": (
            _path(methodologies.get("path"))
            or workspace_root / "methodologies"
        ),
    }


def workspaces_root(
    root,
    name=DEFAULT_ENV
):

    return paths(
        root,
        name
    )["workspaces_root"]


def projects_root(
    root,
    name=DEFAULT_ENV
):

    return paths(
        root,
        name
    )["repository_root"]
