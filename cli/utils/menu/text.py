"""Text and path input prompts (prompt_toolkit, with plain fallback).

Split from cli/utils/menu.py (P1 modularization, C4).
"""

import sys

try:

    from prompt_toolkit import PromptSession
    from prompt_toolkit.history import InMemoryHistory
    from prompt_toolkit.key_binding import KeyBindings
    from prompt_toolkit.keys import Keys
    from prompt_toolkit.formatted_text import HTML
    from prompt_toolkit.styles import Style as PTStyle

except ImportError:

    PromptSession = None
    InMemoryHistory = None
    KeyBindings = None
    Keys = None
    HTML = None
    PTStyle = None

from cli.utils.menu.base import BACK, _t, is_tty
from cli.utils.menu.render import _frame
from cli.utils.menu.theme import get as _theme

_TEXT_SESSIONS = {}

# 输入区域醒目标识（prompt_toolkit 高级特性，零新依赖）：
# - 输入行青色加粗提示符
# - 底部反白操作提示条（bottom_toolbar）
# - 顶部边框分隔线（由调用方/渲染在 frame 中绘制）
_INPUT_STYLE = PTStyle.from_dict(
    {
        "prompt": "bold fg:ansicyan",
        "bottom-toolbar": "reverse bold",
    }
) if PTStyle is not None else None

_INPUT_TOOLBAR_TEXT = (
    "⏎ Enter 提交 · Alt+Enter 换行 · 退格返回 · Esc/Ctrl+C 退出"
)


def _input_toolbar():
    """反白底部提示条（输入区域醒目标识）。"""
    if HTML is None:
        return None
    return HTML(
        f"<style bg='ansicyan' fg='ansiblack'>{_INPUT_TOOLBAR_TEXT}</style>"
    )


def _input_divider():
    """输入区顶部边框分隔线（与上方内容视觉隔离）。"""
    return _theme("divider") + "─" * 40 + _theme("reset")


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
        _input_divider(),
        "",
        _t('menu.hint_text', 'Enter 提交，Alt+Enter 换行，空行退格返回，Esc/Ctrl+C 退出'),
        "",
    ]

    if note:

        body.insert(
            0,
            f"{_theme('note')}{note}{_theme('reset')}"
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
            key_bindings=_text_bindings(),
            style=_INPUT_STYLE,
            bottom_toolbar=_input_toolbar(),
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
            f"{_theme('note')}{note}{_theme('reset')}"
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
            key_bindings=_text_bindings(),
            style=_INPUT_STYLE,
            bottom_toolbar=_input_toolbar(),
        )

    finally:

        sys.stdout.write("\x1b[?25l")
        sys.stdout.flush()

    if raw is BACK:
        return BACK

    return raw.strip()
