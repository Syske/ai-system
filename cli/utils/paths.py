"""路径转换的单一来源（R2：#20 双实现合并）。

`_linux_path` 曾在 `cli/services/providers.py` 与 `cli/services/environment.py`
各有一份实现（口径漂移风险）。现统一在此定义。
"""


def linux_path(path):
    """把 Windows 绝对路径（如 `D:\\workspace\\x`）转为 WSL 形式（`/mnt/d/workspace/x`）。

    非 Windows 风格路径原样返回。
    """

    text = str(path)

    if len(text) < 3 or text[1] != ":":
        return text

    drive = text[0].lower()

    rest = text[2:].replace("\\", "/")

    if not rest.startswith("/"):
        rest = "/" + rest

    return f"/mnt/{drive}{rest}"
