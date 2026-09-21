"""剪贴板工具（T6a C3：后端口缺失时必须降级，不得抛异常）。"""


def copy(text: str) -> bool:
    """复制到剪贴板；成功返回 True。

    2026-09-21 外部盲检 T6a：原实现模块级 `import pyperclip` + 无保护的
    `pyperclip.copy()` —— headless/WSL/CI 下会抛异常，使"提示词已生成"的
    交互流程直接崩溃。改为惰性导入 + 吞掉后端异常（调用方据返回值提示）。
    """

    try:
        import pyperclip
    except Exception:                       # noqa: BLE001
        return False

    try:
        pyperclip.copy(text)
        return True
    except Exception:                       # noqa: BLE001
        return False
