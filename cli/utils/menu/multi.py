"""Multi-select menu: choose_many with type-to-filter and fallback.

Split from cli/utils/menu.py (P1 modularization, C4).
"""

from cli.utils.menu.base import BACK, Section, _t
from cli.utils.menu.keys import _normalize, _read_key
from cli.utils.menu.render import _frame
from cli.utils.menu.select import _handle_filter_key, _handle_no_match, _visible_indices
from cli.utils.menu.theme import get as _theme


def _paint_many(opt, selected, marked):

    marker = "[x]" if marked else "[ ]"

    selected_s = _theme("selected")
    marker_s = _theme("marker")
    name_s = _theme("name")
    desc_s = _theme("desc")
    reset_s = _theme("reset")

    if " — " not in opt:

        if selected:
            return f"{selected_s}> {marker} {opt}{reset_s}"

        return f"  {marker} {opt}"

    name, _, desc = opt.partition(" — ")

    if selected:

        return (
            f"{selected_s}> {marker_s}{marker} {name_s}{name}{reset_s}"
            f"{selected_s} {desc_s}— {desc}{reset_s}"
        )

    return (
        f"  {marker_s}{marker} {name_s}{name}{reset_s}"
        f" {desc_s}— {desc}{reset_s}"
    )


def choose_many(
    title,
    options,
    header=None,
    note=None,
    enter_selects_current=False
):
    """Multi-select menu (checkbox).

    Same base capabilities as choose (type-to-filter, note, sections);
    Space toggles the highlighted item, Enter confirms.

    When `enter_selects_current` is True and nothing is marked, pressing
    Enter selects the currently highlighted item (instead of returning
    None / skip). This lets a launcher treat Enter as "pick this one".

    Returns a list of selected raw indices, `None` when skipped, or BACK.
    """

    if not options:
        return None

    from cli.utils.menu.base import is_tty

    if not is_tty():

        return _fallback_many(
            title,
            options,
            note,
            enter_selects_current
        )

    return _interactive_many(
        title,
        options,
        header or [],
        note,
        enter_selects_current
    )


def _interactive_many(
    title,
    options,
    header,
    note=None,
    enter_selects_current=False
):

    selectable = [
        i
        for i, opt in enumerate(options)
        if not isinstance(opt, Section)
    ]

    selected = set()

    idx = 0

    filter_buf = ""

    while True:

        visible = _visible_indices(
            options,
            selectable,
            filter_buf
        )

        if not visible:

            action, filter_buf = _handle_no_match(
                title,
                note,
                filter_buf,
                header
            )

            if action == "back":
                return BACK

            continue

        if idx not in visible:
            idx = visible[0]

        body = [f"{title}:", ""]

        if note:

            body.append(
                f"{_theme('note')}{note}{_theme('reset')}"
            )

            body.append("")

        for i, opt in enumerate(options):

            if isinstance(opt, Section):

                body.append(
                    f"{_theme('note')}{opt.text}{_theme('reset')}"
                )

            elif i not in visible:

                continue

            else:

                body.append(
                    _paint_many(
                        opt,
                        i == idx,
                        i in selected
                    )
                )

        body.append("")

        if filter_buf:

            body.append(
                f"{_t('menu.filter_prefix', 'filter')}: {filter_buf}  "
                f"({len(visible)}/{len(selectable)})"
            )

        body.append(
            f"空格选中/取消，Enter 确认（已选 {len(selected)}），"
            "退格清除，Esc 清空"
        )

        _frame(header, body)

        key = _normalize(
            _read_key()
        )

        if key == "up":

            pos = visible.index(idx)

            idx = visible[
                (pos - 1) % len(visible)
            ]

        elif key == "down":

            pos = visible.index(idx)

            idx = visible[
                (pos + 1) % len(visible)
            ]

        elif key in ("back", "\x08", "\x7f", "\x1b", "\x03"):

            action, filter_buf = _handle_filter_key(
                key,
                filter_buf
            )

            if action == "back":
                return BACK

            if action == "quit":
                raise KeyboardInterrupt

        elif key == "home":
            idx = visible[0]

        elif key == "end":
            idx = visible[-1]

        elif key == " ":

            if idx in selected:
                selected.discard(idx)

            else:
                selected.add(idx)

        elif key in ("\r", "\n"):

            if selected:
                return sorted(selected)

            if enter_selects_current and idx in selectable:
                return [idx]

            return None

        elif (
            len(key) == 1
            and key.isprintable()
            and key != " "
        ):

            filter_buf += key


def _fallback_many(
    title,
    options,
    note=None,
    enter_selects_current=False
):

    print()
    print(f"{title}:")

    if note:
        print(f"  {note}")
        print()

    selectable = [
        i
        for i, opt in enumerate(options)
        if not isinstance(opt, Section)
    ]

    for i, opt in enumerate(options):

        if isinstance(opt, Section):

            print(f"\n  {opt.text}:")

        else:

            num = selectable.index(i) + 1

            print(f"  {num}. {opt}")

    print(_t('menu.fallback_many', '输入编号（逗号分隔多个），空=跳过全部，b=返回'))

    while True:

        raw = input(_t('menu.fallback_many_prompt', '选择 (如 1,3): ')).strip()

        if raw.lower() == "b":
            return BACK

        if raw == "":

            if enter_selects_current and selectable:
                return [selectable[0]]

            return None

        picks = []

        ok = True

        for part in raw.split(","):

            part = part.strip()

            if (
                not part.isdigit()
                or not 1 <= int(part) <= len(selectable)
            ):

                ok = False

                break

            picks.append(selectable[int(part) - 1])

        if ok and picks:
            return picks

        print(_t('menu.invalid', '无效输入，请重试。'))
