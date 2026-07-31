import ctypes
import os
import sys

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
    header=None
):

    if not options:
        return None

    if not is_tty():

        return _fallback(
            title,
            options,
            default,
            allow_skip
        )

    return _interactive(
        title,
        options,
        default,
        allow_skip,
        header or []
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
    header=None
):

    if (
        not is_tty()
        or PromptSession is None
    ):

        raw = input(prompt)

        if raw.strip() == "<":
            return BACK

        return raw.strip()

    _frame(
        header or [],
        [
            "Enter submit, Alt+Enter newline, "
            "Backspace on empty = back, Esc/Ctrl+C quit",
            ""
        ]
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


def _interactive(
    title,
    options,
    default,
    allow_skip,
    header
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

    while True:

        body = [f"{title}:", ""]

        for i, opt in enumerate(options):

            if isinstance(opt, Section):

                body.append(
                    f"\x1b[1;2m{opt.text}\x1b[0m"
                )

            elif i == idx:

                body.append(f"\x1b[7m> {opt}\x1b[0m")

            else:

                body.append(f"  {opt}")

        body.append("")

        body.append(
            "Up/Down move, digits jump, Enter select, "
            "Left/Backspace back, Esc quit"
        )

        _frame(header, body)

        key = _normalize(
            _read_key()
        )

        if key == "up":

            pos = selectable.index(idx)

            idx = selectable[
                (pos - 1) % len(selectable)
            ]

        elif key == "down":

            pos = selectable.index(idx)

            idx = selectable[
                (pos + 1) % len(selectable)
            ]

        elif key in ("back",):
            return BACK

        elif key == "home":
            idx = selectable[0]

        elif key == "end":
            idx = selectable[-1]

        elif key in ("\r", "\n"):
            return idx

        elif key in ("\x08", "\x7f"):
            return BACK

        elif key in ("\x1b", "\x03"):
            raise KeyboardInterrupt

        elif key.isdigit():

            n = int(key)

            if 1 <= n <= len(selectable):
                idx = selectable[n - 1]


def _fallback(
    title,
    options,
    default,
    allow_skip
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

    for i, opt in enumerate(options):

        if isinstance(opt, Section):

            print(f"\n  {opt.text}:")

        else:

            print(
                f"  {selectable.index(i) + 1}. {opt}"
            )

    hint = (
        "Number [Enter=skip, b=back]"
        if allow_skip
        else (
            "Number "
            f"[{selectable.index(default) + 1}, b=back]"
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

        print("Invalid choice, try again.")
