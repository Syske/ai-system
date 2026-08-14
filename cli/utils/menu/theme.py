"""UI theme loader — colors come from config/ui.yaml (config-driven).

Adjusting colors requires editing config/ui.yaml only; no code change.
All menu modules (render/multi/select/text) read via get().
"""

from pathlib import Path

from cli.utils.yaml import load_yaml

_UI_PATH = (
    Path(__file__)
    .resolve()
    .parents[3]
    / "config"
    / "ui.yaml"
)

_THEME = None

# 默认值（ui.yaml 缺失时兜底，与历史硬编码一致）
_DEFAULTS = {
    "selected": "\x1b[7m",
    "name": "\x1b[1;36m",
    "desc": "\x1b[2;90m",
    "note": "\x1b[1;2m",
    "prompt": "bold fg:ansicyan",
    "toolbar_bg": "ansicyan",
    "toolbar_fg": "ansiblack",
    "divider": "\x1b[1;36m",
    "marker": "\x1b[7m",
    "reset": "\x1b[0m",
}


def _load():

    global _THEME

    if _THEME is not None:
        return _THEME

    theme = dict(_DEFAULTS)

    try:

        data = load_yaml(_UI_PATH)

        if isinstance(data, dict):

            configured = data.get("theme") or {}

            if isinstance(configured, dict):

                theme.update({
                    k: v
                    for k, v in configured.items()
                    if isinstance(v, str)
                })

    except Exception:

        pass

    _THEME = theme

    return _THEME


def get(key: str, default: str = "") -> str:

    return _load().get(key, default)


def reset():

    global _THEME

    _THEME = None
