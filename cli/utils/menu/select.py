"""Single-select menu: choose with type-to-filter and fallback.

Split from cli/utils/menu.py (P1 modularization, C4).
"""

from cli.utils.menu.base import BACK, Section, _t
from cli.utils.menu.keys import _normalize, _read_key
from cli.utils.menu.render import _frame, _paint


def _visible_indices(options, selectable, filter_buf):
    """Base capability — type-to-filter.

    Return option indices (from `selectable`) whose text contains the filter
    (case-insensitive substring). Any menu built on choose/choose_many gets
    incremental filtering for free.
    """

    if not filter_buf:
        return list(selectable)

    lowered = filter_buf.lower()

    return [
        i
        for i in selectable
        if lowered in str(options[i]).lower()
    ]


def _handle_filter_key(key, filter_buf):
    """Base capability — filter editing keys.

    Backspace clears one char (or signals back when empty); Esc clears the
    filter (or signals quit when empty). Returns (action, new_filter_buf)
    where action is one of 'none', 'clear', 'back', 'quit'.
    """

    if key in ("back", "\x08", "\x7f"):

        if filter_buf:
            return "clear", filter_buf[:-1]

        return "back", filter_buf

    if key in ("\x1b", "\x03"):

        if filter_buf:
            return "clear", ""

        return "quit", filter_buf

    return "none", filter_buf


def _handle_no_match(title, note, filter_buf, header):
    """Base capability — render the no-match frame and process filter keys.

    Returns (action, new_filter_buf); action 'back' means the caller should
    return BACK.
    """

    body = [
        f"{title}:",
        "",
    ]

    if note:

        body.append(
            f"\x1b[1;2m{note}\x1b[0m"
        )

        body.append("")

    body.append(
        f"  {_t('menu.hint_no_match', '(无匹配 — 退格清空过滤)')}"
    )
    body.append("")
    body.append(
        f"{_t('menu.filter_prefix', 'filter')}: {filter_buf}"
    )

    _frame(header, body)

    return _handle_filter_key(
        _normalize(
            _read_key()
        ),
        filter_buf
    )


def choose(
    title,
    options,
    default=0,
    allow_skip=False,
    header=None,
    note=None
):
    """Single-select menu.

    Base capabilities (available to every menu built on this):
    - Type-to-filter: typing narrows options (case-insensitive substring);
      Backspace/Esc clear the filter, Enter selects.
    - Sections (Section items) are non-selectable headers.
    - `note` renders a dim hint line under the title.

    Returns the selected raw index, `None` when skipped, or BACK.
    """

    if not options:
        return None

    if not _is_tty():

        return _fallback(
            title,
            options,
            default,
            allow_skip,
            note
        )

    return _interactive(
        title,
        options,
        default,
        allow_skip,
        header or [],
        note
    )


def _is_tty():

    from cli.utils.menu.base import is_tty

    return is_tty()


def _interactive(title, options, default, allow_skip, header, note=None):

    idx = default

    selectable = [
        i
        for i, opt in enumerate(options)
        if not isinstance(opt, Section)
    ]

    if not selectable:
        return None

    if idx not in selectable:
        idx = selectable[0]

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
                f"\x1b[1;2m{note}\x1b[0m"
            )

            body.append("")

        for i, opt in enumerate(options):

            if isinstance(opt, Section):

                body.append(
                    f"\x1b[1;2m{opt.text}\x1b[0m"
                )

            elif i not in visible:

                continue

            elif i == idx:

                body.append(_paint(opt, True))

            else:

                body.append(_paint(opt, False))

        body.append("")

        if filter_buf:

            body.append(
                f"{_t('menu.filter_prefix', 'filter')}: {filter_buf}  "
                f"({len(visible)}/{len(selectable)})"
            )

            body.append(
                _t('menu.hint_filter', '输入过滤，退格清除，Enter 选中，Esc 清空')
            )

        else:

            body.append(
                _t(
                    'menu.hint_select',
                    '↑/↓ 选择，输入过滤，Enter 选中，'
                    '退格返回，Esc 退出'
                )
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

        elif key in ("\r", "\n"):
            return idx

        elif len(key) == 1 and key.isprintable():

            if not filter_buf and key.isdigit():

                n = int(key)

                if 1 <= n <= len(visible):
                    idx = visible[n - 1]

            else:

                filter_buf += key


def _fallback(title, options, default, allow_skip, note=None):

    selectable = [
        i
        for i, opt in enumerate(options)
        if not isinstance(opt, Section)
    ]

    if not selectable:
        return None

    if default not in selectable:
        default = selectable[0]

    print()
    print(f"{title}:")

    if note:
        print(f"  {note}")
        print()

    for i, opt in enumerate(options):

        if isinstance(opt, Section):

            print(f"\n  {opt.text}:")

        else:

            print(
                f"  {selectable.index(i) + 1}. {opt}"
            )

    hint = (
        _t('menu.fallback_hint_skip', '输入编号 [Enter=跳过, b=返回]')
        if allow_skip
        else (
            _t('menu.fallback_hint_default', '输入编号 [默认 {n}, b=返回]')
            .format(n=selectable.index(default) + 1)
        )
    )

    while True:

        raw = input(f"{hint}: ").strip()

        if raw.lower() == "b":
            return BACK

        if raw == "":

            if allow_skip:
                return None

            return default

        if (
            raw.isdigit()
            and 1 <= int(raw) <= len(selectable)
        ):

            return selectable[int(raw) - 1]

        print(_t('menu.invalid', '无效输入，请重试。'))
