"""Auto-detect installed agent CLIs for the launch / agent picker.

Detection is supplementary: config/providers.yaml stays the source of truth
for metadata (label / icon / description / command / enabled). Auto-detection
fills two gaps (方案 B, 2026-09-17):

  1. Configured providers show an install-status badge (installed / missing).
  2. Installed agents that are NOT configured (e.g. qoder) appear in the
     picker with a default label, unless excluded (enabled: false or
     detect: false in providers.yaml).

Signals (first hit wins):

  - PATH executable (shutil.which)
  - known non-PATH install locations (e.g. ~/.qoder/entry/qoder)
  - config-dir presence (weak signal, e.g. ~/.claude, ~/.config/opencode)
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path

# 已知 agent CLI 名单。此处元数据仅用于「未在 providers.yaml 配置」的自动检测条目；
# 已配置条目以 providers.yaml 元数据为准。known_paths = 不保证在 PATH 上的安装位置；
# config_dirs = 弱信号（配置目录存在 → 很可能已安装）。
KNOWN_AGENTS = {
    "opencode": {
        "label": "opencode",
        "icon": "🤖 ",
        "description": "OpenCode agent",
        "known_paths": [],
        "config_dirs": ["~/.config/opencode"],
    },
    "pi": {
        "label": "pi",
        "icon": "🌀 ",
        "description": "Pi agent",
        "known_paths": [],
        "config_dirs": [],
    },
    "claude": {
        "label": "claude",
        "icon": "⚡ ",
        "description": "Claude Code agent",
        "known_paths": [],
        "config_dirs": ["~/.claude"],
    },
    "codex": {
        "label": "codex",
        "icon": "💠 ",
        "description": "Codex agent",
        "known_paths": [],
        "config_dirs": [],
    },
    "qoder": {
        "label": "qoder",
        "icon": "🛠️ ",
        "description": "Qoder agent",
        "known_paths": ["~/.qoder/entry/qoder"],
        "config_dirs": ["~/.qoder"],
    },
    "aider": {
        "label": "aider",
        "icon": "🧑‍💻 ",
        "description": "Aider agent",
        "known_paths": [],
        "config_dirs": [],
    },
    "gemini": {
        "label": "gemini",
        "icon": "✨ ",
        "description": "Gemini CLI agent",
        "known_paths": [],
        "config_dirs": [],
    },
}


_WIN_EXTS = (".exe", ".cmd", ".bat", ".com")


def _expand(path):
    return Path(os.path.expanduser(path))


def _config_present(info):
    return any(
        _expand(p).exists()
        for p in (info or {}).get("config_dirs", [])
    )


def _npm_global_bins():
    """Locate npm global bin dir(s), cached per process.

    Returns a list of Paths: the current environment's `npm prefix -g` bin
    dir plus the Windows APPDATA npm dir when reachable (native win32 or
    WSL mount). One `npm prefix -g` subprocess, cached.
    """

    cache = getattr(_npm_global_bins, "_cache", None)

    if cache is not None:
        return cache

    dirs = []

    try:

        out = subprocess.run(
            ["npm", "prefix", "-g"],
            capture_output=True,
            text=True,
            timeout=10,
        )

        if out.returncode == 0 and out.stdout.strip():

            prefix = Path(out.stdout.strip())

            # win32：npm 全局 shim 就在 prefix 根（opencode.cmd），无 bin 子目录
            d = prefix if sys.platform == "win32" else prefix / "bin"

            if d.is_dir():
                dirs.append(d)

    except Exception:
        pass

    if sys.platform == "win32":

        appdata = os.environ.get("APPDATA")

        if appdata:
            p = Path(appdata) / "npm"
            if p.is_dir():
                dirs.append(p)

    elif sys.platform.startswith("linux"):

        # WSL：扫描 Windows 用户目录挂载下的 npm 全局 bin（/mnt/c 下存在
        # 不可读的系统用户目录，所有探测必须 OSError 安全）
        base = Path("/mnt/c/Users")

        try:

            if base.is_dir():

                for user_dir in base.iterdir():

                    cand = user_dir / "AppData" / "Roaming" / "npm"

                    try:

                        if cand.is_dir():
                            dirs.append(cand)

                    except OSError:
                        continue

        except OSError:
            pass

    _npm_global_bins._cache = dirs

    return dirs


def _windows_path_dirs():
    """Windows PATH dirs visible from WSL (entries under /mnt/<drive>/).

    Lets detection find Windows-installed agent executables
    (opencode.cmd / pi.exe ...) that Linux `shutil.which` cannot resolve
    (Linux which has no PATHEXT). File-system only, no subprocess.
    """

    if not sys.platform.startswith("linux"):
        return []

    dirs = []

    for entry in os.environ.get("PATH", "").split(os.pathsep):

        if not entry:
            continue

        p = Path(entry)

        try:

            if p.is_dir() and str(p).startswith("/mnt/"):
                dirs.append(p)

        except OSError:
            continue

    return dirs


def _check_dir(directory, name):
    """Check a directory for an executable named `name`.

    On non-Windows (incl. WSL) also tries Windows extensions (.exe/.cmd/...),
    so npm/Windows-installed agents are found. Returns the path or None.
    """

    candidates = [(name, True)]

    # 所有平台都尝试 Windows 扩展名变体：win32 下 npm shim 为
    # name.cmd/name.ps1，非 win32（WSL/类 Unix）下覆盖 interop 场景
    candidates += [(name + ext, False) for ext in _WIN_EXTS]

    for cand_name, need_exec in candidates:

        cand = Path(directory) / cand_name

        try:

            if not cand.is_file():
                continue

        except OSError:
            continue

        if need_exec:

            try:

                if not os.access(cand, os.X_OK):
                    continue

            except OSError:
                continue

        return str(cand)

    return None


def detect_agent(name):
    """Detect a single agent CLI.

    Returns {installed, path, via, config_present}.
    via: "path" | "known-path" | "npm" | "npm-win" | "win-path" | None.
    Signal order: PATH → known non-PATH locations → npm global bin
    (current + Windows APPDATA) → Windows PATH dirs (WSL interop).
    """

    info = KNOWN_AGENTS.get(name, {})

    which = shutil.which(name)

    if which:
        return {
            "installed": True,
            "path": which,
            "via": "path",
            "config_present": _config_present(info),
        }

    for p in info.get("known_paths", []):

        path = _expand(p)

        if path.is_file() and os.access(path, os.X_OK):
            return {
                "installed": True,
                "path": str(path),
                "via": "known-path",
                "config_present": _config_present(info),
            }

    for directory in _npm_global_bins():

        hit = _check_dir(directory, name)

        if hit:
            via = (
                "npm-win"
                if hit.lower().endswith(_WIN_EXTS)
                else "npm"
            )
            return {
                "installed": True,
                "path": hit,
                "via": via,
                "config_present": _config_present(info),
            }

    for directory in _windows_path_dirs():

        hit = _check_dir(directory, name)

        if hit:
            return {
                "installed": True,
                "path": hit,
                "via": "win-path",
                "config_present": _config_present(info),
            }

    return {
        "installed": False,
        "path": None,
        "via": None,
        "config_present": _config_present(info),
    }


def scan_agents(names=None):
    """Detect all known agent CLIs, cached per process.

    Detection spawns no subprocesses (shutil.which + file checks only), so
    the cache is a cheap guard against repeated picker renders in one session.
    """

    names = names or list(KNOWN_AGENTS)

    cache = getattr(scan_agents, "_cache", None)

    if cache is None:
        cache = scan_agents._cache = {
            n: detect_agent(n)
            for n in names
        }

    return dict(cache)


def excluded_names(config):
    """Names explicitly opted out of auto-detection.

    A configured provider with `enabled: false` (explicit opt-out) or
    `detect: false` is excluded from the auto-detected list; enabled: false
    also removes it from the configured list (unchanged semantics).
    """

    providers = (
        config.provider_config.get("providers", {})
        if isinstance(config.provider_config, dict)
        else {}
    )

    excluded = set()

    for name, cfg in (providers or {}).items():

        if not isinstance(cfg, dict):
            continue

        if cfg.get("enabled", True) is False:
            excluded.add(name)

        elif cfg.get("detect", True) is False:
            excluded.add(name)

    return excluded


def _wsl_to_win(path):
    """/mnt/c/Users/x/npm/opencode.cmd -> C:\\Users\\x\\npm\\opencode.cmd.

    cmd.exe（Windows 批处理）不认 WSL 挂载路径，启动 .cmd/.bat shim 前需转换。
    """

    p = str(path)

    if p.startswith("/mnt/") and len(p) > 6:

        parts = p.split("/")

        drive = parts[2].upper()

        return f"{drive}:\\" + "\\".join(parts[3:])

    return p


def resolve_launch_command(config, name):
    """Resolve the shell launch command for an agent (launch layer, 2026-09-17).

    Priority:
      1. providers.yaml `command` override (explicit user config)
      2. detected install path (agent_detect), with WSL interop wrapping
         for Windows .cmd/.bat shims (cmd.exe /c + path conversion)
      3. the agent name itself (assumed resolvable on PATH)

    Returns a command string suitable for subprocess shell=True.
    """

    explicit = config.provider_command(name)

    if explicit != name:
        return explicit

    result = detect_agent(name)

    if result.get("installed") and result.get("path"):

        path = result["path"]

        if (
            sys.platform.startswith("linux")
            and path.lower().endswith((".cmd", ".bat"))
        ):

            return f'cmd.exe /c "{_wsl_to_win(path)}"'

        if any(ch.isspace() for ch in path):
            # 空格路径必须引号包裹：_launch 以 shell=True 执行，未引号会被分词
            # 导致启动失败（2026-09-21 外部盲检 T6a C1）。
            return f'"{path}"'

        return path

    return name


def sort_by_usage(entries, usage=None):
    """Sort picker entries by usage count (descending), stable.

    Ties keep the merge order (configured first, then auto-detected).
    usage: {agent_name: count} from wizard state `agent_usage`.
    """

    usage = usage or {}

    return sorted(
        entries,
        key=lambda e: -usage.get(e["name"], 0),
    )


def merge_picker_entries(config, detected=None):
    """Merge configured enabled providers + auto-detected agents.

    Returns an ordered list of picker entries:
      {name, label, icon, description, installed, path, via, configured}

    Order: configured (providers.yaml order) first, then auto-detected
    not-configured agents (KNOWN_AGENTS order).
    """

    detected = detected if detected is not None else scan_agents()

    enabled = config.enabled_providers()
    meta = config.provider_meta()
    excluded = excluded_names(config)

    entries = []

    for name in enabled:

        m = meta.get(name, {})

        d = detected.get(name, {}) or {}

        entries.append({
            "name": name,
            "label": m.get("label") or name,
            "icon": m.get("icon") or "",
            "description": m.get("description") or "",
            "installed": bool(d.get("installed")),
            "path": d.get("path"),
            "via": d.get("via"),
            "configured": True,
        })

    for name in detected:

        if name in excluded or name in enabled:
            continue

        d = detected[name]

        if not d.get("installed"):
            continue

        info = KNOWN_AGENTS.get(name, {})

        entries.append({
            "name": name,
            "label": info.get("label") or name,
            "icon": info.get("icon") or "",
            "description": info.get("description") or "",
            "installed": True,
            "path": d.get("path"),
            "via": d.get("via"),
            "configured": False,
        })

    return entries
