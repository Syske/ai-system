from pathlib import Path


def read_text(path: Path) -> str:
    if not path.exists():
        raise FileNotFoundError(path)

    return path.read_text(
        encoding="utf-8"
    )


def write_text(
    path: Path,
    content: str
):

    path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    path.write_text(
        content,
        encoding="utf-8"
    )

def unique_dir(path):
    """返回**不冲突**的目录路径（`path` 已存在时追加 `-2`/`-3`…）。

    R2 修复：产物目录此前用 `mkdir(exist_ok=True)`，同日同描述（如重跑同一 chain /
    skill 报告）会**静默覆写**上一个运行的 manifest/report，而文档承诺「追加 -N」。
    本函数把「追加 -N」变为实现事实（单一来源，chain / skill / scan 共用）。
    """

    path = Path(path)

    if not path.exists():
        return path

    for index in range(2, 1000):

        candidate = path.with_name(f"{path.name}-{index}")

        if not candidate.exists():
            return candidate

    return path


