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

    try:

        _I18N = load_yaml(
            Path(__file__).resolve().parents[3]
            / "config"
            / "i18n"
            / "zh.yaml"
        )

    except Exception:

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
