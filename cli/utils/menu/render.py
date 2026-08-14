"""Screen rendering helpers: frame and option painting.

Split from cli/utils/menu.py (P1 modularization, C4).
"""

import sys

from cli.utils.menu.theme import get as _theme


def _frame(header, body):

    out = ["\x1b[2J\x1b[H"]

    for line in header:
        out.append(f"{line}\n")

    if header:
        out.append("\n")

    for line in body:
        out.append(f"{line}\n")

    sys.stdout.write("".join(out))
    sys.stdout.flush()


def _paint(opt, selected):

    selected_s = _theme("selected")
    name_s = _theme("name")
    desc_s = _theme("desc")
    reset_s = _theme("reset")

    if " — " not in opt:

        if selected:
            return f"{selected_s}> {opt}{reset_s}"

        return f"  {opt}"

    name, _, desc = opt.partition(" — ")

    if selected:

        return (
            f"{selected_s}> {name_s}{name}{reset_s}"
            f"{selected_s} {desc_s}— {desc}{reset_s}"
        )

    return (
        f"  {name_s}{name}{reset_s}"
        f" {desc_s}— {desc}{reset_s}"
    )
