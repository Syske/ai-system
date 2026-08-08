"""Menu package — modularized interactive menu primitives.

Split from the former single-file cli/utils/menu.py (P1 modularization,
C4). Public API is unchanged; existing `from cli.utils.menu import ...`
imports keep working.

Modules:
- base.py   — BACK, Section, i18n (_t), tty/icons detection, icons (e)
- keys.py   — raw key reading + normalization, VT enable
- render.py — frame + option painting
- text.py   — ask_text / ask_path (prompt_toolkit with fallback)
- select.py — choose (single-select, type-to-filter, fallback)
- multi.py  — choose_many (multi-select, type-to-filter, fallback)
"""

from cli.utils.menu.base import (
    BACK,
    Section,
    _t,
    e,
    icons_enabled,
    is_tty,
)
from cli.utils.menu.keys import _enable_vt
from cli.utils.menu.multi import choose_many
from cli.utils.menu.select import choose
from cli.utils.menu.text import ask_path, ask_text
from cli.utils.menu.render import _frame  # noqa: F401  (internal, re-exported)


import sys


def screen_enter():
    """Enter the alternate screen (full-screen mode) when on a TTY."""

    if not is_tty():
        return

    _enable_vt()

    sys.stdout.write(
        "\x1b[?1049h\x1b[?25l\x1b[2J\x1b[H"
    )

    sys.stdout.flush()


def screen_exit():
    """Leave the alternate screen and restore the cursor."""

    if not is_tty():
        return

    sys.stdout.write(
        "\x1b[?25h\x1b[?1049l"
    )

    sys.stdout.flush()


__all__ = [
    "BACK",
    "Section",
    "ask_path",
    "ask_text",
    "choose",
    "choose_many",
    "e",
    "icons_enabled",
    "is_tty",
    "screen_enter",
    "screen_exit",
]
