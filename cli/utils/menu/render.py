"""Screen rendering helpers: frame and option painting.

Split from cli/utils/menu.py (P1 modularization, C4).
"""

import sys


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

    if " — " not in opt:

        if selected:
            return f"\x1b[7m> {opt}\x1b[0m"

        return f"  {opt}"

    name, _, desc = opt.partition(" — ")

    if selected:

        return (
            f"\x1b[7m> \x1b[1;36m{name}\x1b[0m"
            f"\x1b[7m \x1b[2;90m— {desc}\x1b[0m"
        )

    return (
        f"  \x1b[1;36m{name}\x1b[0m"
        f" \x1b[2;90m— {desc}\x1b[0m"
    )
