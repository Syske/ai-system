"""Raw key reading and normalization (cross-platform).

Split from cli/utils/menu.py (P1 modularization, C4).
"""

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

    data = os.read(fd, n)

    if not data:
        return ""

    # raw 模式下输入过滤中文等多字节 UTF-8 字符时，首字节是 lead byte，
    # 单独解码会 UnicodeDecodeError（2026-09-11 实测 aic 崩溃）。
    # 按 UTF-8 编码规则补齐续字节后再解码；异常字节回退 latin-1（不崩溃）。
    lead = data[0]

    need = 1

    if lead >= 0xF0:
        need = 4
    elif lead >= 0xE0:
        need = 3
    elif lead >= 0xC0:
        need = 2

    while len(data) < need and _data_ready(fd):

        more = os.read(fd, 1)

        if not more:
            break

        data += more

    try:

        return data.decode("utf-8")

    except UnicodeDecodeError:

        return data.decode("latin-1")


def _unix_read_key():

    fd = sys.stdin.fileno()

    attrs = termios.tcgetattr(fd)

    # POSIX tcgetattr 顺序：0=iflag 1=oflag 2=cflag 3=lflag 4=ispeed 5=ospeed 6=cc。
    # 原实现错位取 attrs[3]/attrs[4] 并把掩码写进了 new[3]/new[4]（input flags 从未清、
    # ECHO/ISIG 未关、ispeed 槽被改写）——见 2026-09-21 外部盲检 V8。
    iflag, oflag, cflag, lflag, cc = (
        attrs[0],
        attrs[1],
        attrs[2],
        attrs[3],
        attrs[6]
    )

    new = list(attrs)

    new[0] = iflag & ~(
        termios.BRKINT
        | termios.ICRNL
        | termios.INPCK
        | termios.ISTRIP
        | termios.IXON
    )

    new[1] = oflag & ~termios.OPOST

    new[2] = cflag | termios.CS8

    new[3] = lflag & ~(
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


def _normalize(key):

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
