"""Base menu primitives: i18n, Section, tty detection, icons, screen.

Split from cli/utils/menu.py (P1 modularization, C4). Public symbols are
re-exported from cli/utils/menu/__init__.py.
"""

import os
import sys
from pathlib import Path

from cli.utils.yaml import load_yaml

BACK = object()


_I18N = None


def _load_i18n():

    global _I18N

    if _I18N is not None:
        return _I18N

    # R2 修复：locale 与 MenuConfig 同源（config/menu.yaml → locale），
    # 原实现硬编码 zh.yaml —— 切换 locale 后菜单文案仍为中文（静默不一致）。
    root = Path(__file__).resolve().parents[3]

    locale = "zh"

    try:

        _menu_cfg = load_yaml(root / "config" / "menu.yaml") or {}

        locale = str(_menu_cfg.get("locale") or "zh").strip() or "zh"

    except Exception:

        locale = "zh"

    for candidate in (locale, "zh"):

        try:

            _I18N = load_yaml(root / "config" / "i18n" / f"{candidate}.yaml")

            if _I18N:
                return _I18N

        except Exception:

            _I18N = None

    _I18N = {}

    return _I18N


def _t(key, default=None):

    node = _load_i18n()

    for part in str(key).split("."):

        if not isinstance(node, dict):
            return default

        node = node.get(part)

        if node is None:
            return default

    return node if node is not None else default


class Section:

    def __init__(
        self,
        text
    ):

        self.text = text


def is_tty():

    return (
        hasattr(sys.stdout, "isatty")
        and sys.stdout.isatty()
        and os.environ.get("NO_TTY") != "1"
    )


def icons_enabled():

    if not is_tty():
        return False

    if os.environ.get("NO_ICONS") == "1":
        return False

    return True


def e(icon):

    if icons_enabled():
        return icon

    return ""
