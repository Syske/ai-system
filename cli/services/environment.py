"""Local environment config (config/environments/local.yaml).

Resolves all base paths from the machine-specific environment file and
falls back to the default directory layout when the file is missing or
unparsable. The derivation mirrors runtime-bootstrap.md Phase 2 so the CLI
and the bootstrap runtime share one source of truth.
"""

import os
from pathlib import Path

from cli.utils.yaml import load_yaml

DEFAULT_ENV = "local"


def home_config_path():
    """机器层环境配置：~/.config/ai-system/env.yaml。

    跨平台原生（Windows 下即 C:\\Users\\<user>\\.config\\...），
    首启由 setup.py 按系统检测生成，特殊情况（如 WSL 路径）用户自行编辑。
    可用环境变量 AI_HOME_CONFIG 覆盖（测试/多配置场景）。
    """

    override = os.environ.get("AI_HOME_CONFIG")

    if override:
        return Path(override)

    return (
        Path.home()
        / ".config"
        / "ai-system"
        / "env.yaml"
    )


def load_home_environment():

    try:

        data = load_yaml(
            home_config_path()
        ) or {}

    except Exception:

        data = {}

    return data


def _deep_merge(base, override):
    """递归合并，override 优先；仅 dict 键递归，其余直接覆盖。"""

    out = dict(base)

    for k, v in override.items():

        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = _deep_merge(out[k], v)
        else:
            out[k] = v

    return out


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


def _is_installed_root(root):
    """home 机器层只对「本机已安装的 ai-system 根」生效。

    测试/备用克隆会以任意 root 调用 paths()——此时跳过 home 合并保持隔离；
    生产路径（paths()/resolve_environment 的 root 即安装根）正常合并。
    """

    try:

        return (
            Path(root).resolve()
            == ai_system_root().resolve()
        )

    except Exception:

        return False


def load_merged_environment(
    root,
    name=DEFAULT_ENV
):
    """合并后的环境配置：home 机器层优先，workspace 层兜底。

    home（~/.config/ai-system/env.yaml，按平台生成/用户可改）覆盖
    workspace config/environments/{name}.yaml 的对应键；两者均缺失时
    由调用方回退到默认推导（见 paths()）。仅安装根应用 home 层。
    """

    env = load_environment(root, name)

    if _is_installed_root(root):

        env = _deep_merge(
            env,
            load_home_environment()
        )

    return env


def _normalize_path(value):
    """Windows 风格绝对路径（D:\\...）归一化为 WSL 路径（/mnt/d/...）。

    防止 PosixPath 把反斜杠路径当作相对路径而伪造目录
    （如 /home/.../D:\\workspace\\...）。与 providers._linux_path 同构。
    """

    s = str(value)

    if len(s) < 3 or s[1] != ":" or s[2] not in ("\\", "/"):
        return s

    s = s.replace("\\", "/")

    drive = s[0].lower()

    return f"/mnt/{drive}{s[2:]}"


def _path(value):

    if not value:
        return None

    return Path(_normalize_path(value))


def paths(
    root,
    name=DEFAULT_ENV
):
    """Resolve all base paths for the given environment.

    workspace_root / repository_root / workspaces_root / ai_system_root /
    methodologies_root / outputs_root — each from local.yaml when present,
    otherwise derived from the default directory layout.
    """

    env = load_merged_environment(
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

    skills = (
        layers.get("skills") or {}
    )

    outputs_root = (
        workspace.get("outputs_root")
        or workspace_root / "outputs"
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
        "skills_root": (
            _path(skills.get("path"))
            or workspace_root / "extensions"
        ),
        "outputs_root": _path(outputs_root),
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


def skills_root(
    root,
    name=DEFAULT_ENV
):

    return paths(
        root,
        name
    )["skills_root"]


# --------------------------------------------------------------------------
# ai-system 根定位 + skill 环境上下文
# (2026-08-18) — skill 被独立调用时（agent 直接执行 SKILL.md，不经 aic 向导）
# 也必须能定位 ai-system 根并读取环境配置，而非硬编码路径或依赖 CWD。
# --------------------------------------------------------------------------


def ai_system_root(start=None):
    """Locate the ai-system root (directory holding config/environments/).

    Resolution priority:
      1. $AI_SYSTEM_ROOT — the machine/environment anchor, most reliable for
         standalone skill invocation (injected by the agent or shell).
      2. `start` (a file or dir inside the ai-system tree) walked upward to
         the first ancestor containing config/environments/local.yaml.
      3. Fallback to the default layout: the ai-system dir is the parent of
         the caller's package when running in-tree.

    Returns a Path, or None when unresolvable.
    """

    import os

    env_anchor = os.environ.get("AI_SYSTEM_ROOT")

    if env_anchor:

        p = Path(_normalize_path(env_anchor)).resolve()

        if p.is_dir() and (p / "config" / "environments").is_dir():
            return p

    if start is not None:

        cur = Path(start)

        if not cur.is_dir():
            cur = cur.parent

        for ancestor in [cur, *cur.parents]:

            if (
                (ancestor / "config" / "environments").is_dir()
                and (ancestor / "governance").is_dir()
            ):
                return ancestor

    # 最终兜底：包内位置（树内运行）
    return Path(__file__).resolve().parents[2]


def resolve_environment(start=None, environment=None):
    """Resolve a skill's runtime environment context.

    Returns a dict:

        {
          "root": ai-system root (Path or None),
          "environment": env name or None,
          "paths": paths() result or None,
          "config": raw environment config dict or None,
          "build": build config (java_home/maven_home/backend/...) or None,
        }

    Standalone skills should read paths/config from here — never hardcode
    machine-specific absolute paths (see outputs-convention / skill-author).
    """

    root = ai_system_root(start)

    if root is None:
        return {
            "root": None,
            "environment": None,
            "paths": None,
            "config": None,
            "build": None,
        }

    name = environment or DEFAULT_ENV

    config = load_merged_environment(root, name) or {}

    try:
        p = paths(root, name)
    except Exception:
        p = None

    return {
        "root": root,
        "environment": name,
        "paths": p,
        "config": config,
        "build": config.get("build"),
    }
