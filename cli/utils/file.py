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