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


def _paint_note(text):
    """Render a menu note: base note style (bold-dim), with `**...**`
    segments promoted to the name style (bold cyan — "高亮加粗").
    """

    note_s = _theme("note")
    name_s = _theme("name")
    reset_s = _theme("reset")

    if "**" not in text:
        return f"{note_s}{text}{reset_s}"

    chunks = text.split("**")

    out = [note_s]

    for i, chunk in enumerate(chunks):

        if not chunk:
            continue

        if i % 2 == 1:

            # reset 先清除 dim，再用 name 主题（bold cyan）高亮关键术语
            out.append(f"{reset_s}{name_s}{chunk}{reset_s}{note_s}")

        else:

            out.append(chunk)

    out.append(reset_s)

    return "".join(out)


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
