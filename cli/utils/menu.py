import ctypes
import os
import sys
from pathlib import Path

try:

    import msvcrt

except ImportError:

    msvcrt = None

try:

    import select
    import termios

except ImportError:

    termios = None

try:

    from prompt_toolkit import PromptSession
    from prompt_toolkit.history import InMemoryHistory
    from prompt_toolkit.key_binding import KeyBindings
    from prompt_toolkit.keys import Keys

except ImportError:

    PromptSession = None
    InMemoryHistory = None
    KeyBindings = None
    Keys = None


BACK = object()


_I18N = None


def _load_i18n():

    global _I18N

    if _I18N is not None:
        return _I18N

    try:

        import yaml

        root = Path(__file__).resolve().parents[2]

        menu = yaml.safe_load(
            (root / "config" / "menu.yaml")
            .read_text(encoding="utf-8")
        ) or {}

        locale = menu.get("locale", "zh")

        _I18N = yaml.safe_load(
            (root / "config" / "i18n" / f"{locale}.yaml")
            .read_text(encoding="utf-8")
        ) or {}

    except Exception:

        _I18N = {}

    return _I18N


def _t(key, default=None):

    node = _load_i18n()

    for part in key.split("."):

        if not isinstance(node, dict):
            break

        node = node.get(part)

        if node is None:
            break

    if node is None:
        return default

    return node


class Section:

    def __init__(
        self,
        text
    ):

        self.text = text


def is_tty():

    return (
        sys.stdin.isatty()
        and sys.stdout.isatty()
    )


def icons_enabled():

    override = os.environ.get(
        "AIC_ICONS",
        ""
    ).lower()

    if override == "emoji":
        return True

    if override in ("off", "ascii", "none"):
        return False

    term = os.environ.get(
        "TERM",
        ""
    ).lower()

    minimal = {
        "dumb",
        "unknown",
        "linux",
        "cons25",
        "vt100",
        "vt102",
        "vt220",
        "ansi"
    }

    return bool(
        os.environ.get("WT_SESSION")
        or os.environ.get("TERM_PROGRAM") == "vscode"
        or (
            term
            and term not in minimal
        )
    )


def e(icon):
    """Return an emoji icon when the terminal supports it, else empty.

    Public helper for menus and launchers; respects AIC_ICONS=off/emoji.
    """

    if is_tty() and icons_enabled():
        return icon

    return ""


def screen_enter():

    if not is_tty():
        return

    _enable_vt()

    sys.stdout.write(
        "\x1b[?1049h\x1b[?25l\x1b[2J\x1b[H"
    )

    sys.stdout.flush()


def screen_exit():

    if not is_tty():
        return

    sys.stdout.write(
        "\x1b[?25h\x1b[?1049l"
    )

    sys.stdout.flush()


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

    if not is_tty():

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


def choose_many(
    title,
    options,
    header=None,
    note=None
):
    """Multi-select menu (checkbox).

    Same base capabilities as choose (type-to-filter, note, sections);
    Space toggles the highlighted item, Enter confirms.

    Returns a list of selected raw indices, `None` when skipped, or BACK.
    """

    if not options:
        return None

    if not is_tty():

        return _fallback_many(
            title,
            options,
            note
        )

    return _interactive_many(
        title,
        options,
        header or [],
        note
    )


_TEXT_SESSIONS = {}


def _text_bindings():

    kb = KeyBindings()

    @kb.add(Keys.Escape)
    def _quit(event):
        event.app.exit(
            exception=KeyboardInterrupt,
            style="class:aborting"
        )

    @kb.add(Keys.Backspace)
    def _back(event):

        buf = event.current_buffer

        if not buf.text:
            event.app.exit(BACK)
            return

        buf.delete_before_cursor()

    @kb.add(Keys.Enter)
    @kb.add(Keys.ControlM)
    @kb.add(Keys.ControlJ)
    def _submit(event):
        event.current_buffer.validate_and_handle()

    @kb.add(Keys.Escape, Keys.Enter)
    def _newline(event):
        event.current_buffer.insert_text("\n")

    return kb


def ask_text(
    prompt,
    header=None,
    note=None
):

    if (
        not is_tty()
        or PromptSession is None
    ):

        raw = input(prompt)

        if raw.strip() == "<":
            return BACK

        return raw.strip()

    body = [
        _t('menu.hint_text', 'Enter 提交，Alt+Enter 换行，空行退格返回，Esc/Ctrl+C 退出'),
        ""
    ]

    if note:

        body.insert(
            0,
            f"\x1b[1;2m{note}\x1b[0m"
        )

        body.insert(1, "")

    _frame(
        header or [],
        body
    )

    session = _TEXT_SESSIONS.get(prompt)

    if session is None:

        session = PromptSession(
            history=InMemoryHistory()
        )

        _TEXT_SESSIONS[prompt] = session

    try:

        raw = session.prompt(
            prompt,
            multiline=True,
            key_bindings=_text_bindings()
        )

    finally:

        sys.stdout.write("\x1b[?25l")
        sys.stdout.flush()

    if raw is BACK:
        return BACK

    return raw.strip()


def ask_path(
    prompt,
    header=None,
    note=None,
    only_directories=False
):
    """Path input with tab completion (prompt_toolkit PathCompleter).

    Completes existing directories (and files when only_directories is
    False) as you type. Falls back to a plain input() line when not a TTY
    or when prompt_toolkit is unavailable.
    """

    if (
        not is_tty()
        or PromptSession is None
    ):

        raw = input(prompt)

        if raw.strip() == "<":
            return BACK

        return raw.strip()

    try:

        from prompt_toolkit.completion import PathCompleter

    except ImportError:

        PathCompleter = None

    body = [
        _t('menu.hint_path', '输入路径，Tab 补齐，Enter 提交，退格返回，Esc/Ctrl+C 退出'),
        ""
    ]

    if note:

        body.insert(
            0,
            f"\x1b[1;2m{note}\x1b[0m"
        )

        body.insert(1, "")

    _frame(
        header or [],
        body
    )

    session = _TEXT_SESSIONS.get(prompt)

    if session is None:

        session = PromptSession(
            history=InMemoryHistory(),
            completer=(
                PathCompleter(
                    only_directories=only_directories,
                    expanduser=True
                )
                if PathCompleter is not None
                else None
            ),
            complete_while_typing=True
        )

        _TEXT_SESSIONS[prompt] = session

    try:

        raw = session.prompt(
            prompt,
            key_bindings=_text_bindings()
        )

    finally:

        sys.stdout.write("\x1b[?25l")
        sys.stdout.flush()

    if raw is BACK:
        return BACK

    return raw.strip()


def _read_key():

    if msvcrt is not None:

        ch = msvcrt.getwch()

        if ch in ("\x00", "\xe0"):
            ch += msvcrt.getwch()

        return ch

    if termios is not None:

        return _unix_read_key()

    return sys.stdin.read(1)


def _data_ready(fd):

    return bool(
        select.select(
            [fd],
            [],
            [],
            0.1
        )[0]
    )


def _read_raw(fd, n):

    return os.read(fd, n).decode()


def _unix_read_key():

    fd = sys.stdin.fileno()

    attrs = termios.tcgetattr(fd)

    iflag, oflag, cflag, lflag, cc = (
        attrs[3],
        attrs[1],
        attrs[2],
        attrs[4],
        attrs[6]
    )

    new = list(attrs)

    new[3] = iflag & ~(
        termios.BRKINT
        | termios.ICRNL
        | termios.INPCK
        | termios.ISTRIP
        | termios.IXON
    )

    new[1] = oflag & ~termios.OPOST

    new[2] = cflag | termios.CS8

    new[4] = lflag & ~(
        termios.ECHO
        | termios.ICANON
        | termios.IEXTEN
        | termios.ISIG
    )

    new[6] = list(cc)

    new[6][termios.VMIN] = 1

    new[6][termios.VTIME] = 0

    try:

        termios.tcsetattr(
            fd,
            termios.TCSADRAIN,
            new
        )

        ch = _read_raw(fd, 1)

        if ch != "\x1b":
            return ch

        if not _data_ready(fd):
            return "\x1b"

        seq = _read_raw(fd, 1)

        if seq not in ("[", "O"):
            return "\x1b" + seq

        rest = _read_raw(fd, 1)

        if rest.isdigit() and _data_ready(fd):
            rest += _read_raw(fd, 1)

        return "\x1b" + seq + rest

    finally:

        termios.tcsetattr(
            fd,
            termios.TCSADRAIN,
            attrs
        )


def _normalize(
    key
):

    if key in ("\x00H", "\xe0H", "\x1b[A"):
        return "up"

    if key in ("\x00P", "\xe0P", "\x1b[B"):
        return "down"

    if key in ("\x00K", "\xe0K", "\x1b[D"):
        return "back"

    if key in ("\x00M", "\xe0M", "\x1b[C"):
        return "right"

    if key in ("\x00G", "\xe0G", "\x1b[H", "\x1b[1~"):
        return "home"

    if key in ("\x00O", "\xe0O", "\x1b[F", "\x1b[4~"):
        return "end"

    return key


def _enable_vt():

    try:

        kernel32 = ctypes.windll.kernel32

        handle = kernel32.GetStdHandle(-11)

        mode = ctypes.c_uint32()

        if kernel32.GetConsoleMode(
            handle,
            ctypes.byref(mode)
        ):

            kernel32.SetConsoleMode(
                handle,
                mode.value | 0x0004
            )

    except Exception:

        os.system("")


def _frame(
    header,
    body
):

    out = ["\x1b[2J\x1b[H"]

    for line in header:
        out.append(f"{line}\n")

    if header:
        out.append("\n")

    for line in body:
        out.append(f"{line}\n")

    sys.stdout.write("".join(out))
    sys.stdout.flush()


def _paint(
    opt,
    selected
):

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


def _visible_indices(
    options,
    selectable,
    filter_buf
):
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


def _handle_filter_key(
    key,
    filter_buf
):
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


def _handle_no_match(
    title,
    note,
    filter_buf,
    header
):
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


def _interactive(
    title,
    options,
    default,
    allow_skip,
    header,
    note=None
):

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


def _fallback(
    title,
    options,
    default,
    allow_skip,
    note=None
):

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


def _paint_many(
    opt,
    selected,
    marked
):

    marker = "[x]" if marked else "[ ]"

    if " — " not in opt:

        if selected:
            return f"\x1b[7m> {marker} {opt}\x1b[0m"

        return f"  {marker} {opt}"

    name, _, desc = opt.partition(" — ")

    if selected:

        return (
            f"\x1b[7m> {marker} \x1b[1;36m{name}\x1b[0m"
            f"\x1b[7m \x1b[2;90m— {desc}\x1b[0m"
        )

    return (
        f"  {marker} \x1b[1;36m{name}\x1b[0m"
        f" \x1b[2;90m— {desc}\x1b[0m"
    )


def _interactive_many(
    title,
    options,
    header,
    note=None
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
    note=None
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
