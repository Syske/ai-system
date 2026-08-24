"""Release Version 自动推导（release 工作流，P37 批次 1）。

三条衡量点（P37 §4.1）：可生成/可推断 → 不让用户填。Release Version 从
git tag（或上一版本）推导，无 tag 时确定性回退。

确定性规则，零 LLM（与 Change ID slug 派生同原则）。
"""

import re
from datetime import datetime
from pathlib import Path

_TAG_RE = re.compile(r"^v?(\d+)\.(\d+)\.(\d+)(?:[-+].*)?$")


def _git_tags(repo: Path):
    """列出仓库内版本型 tag（vX.Y.Z 或 X.Y.Z），最新在前。"""

    import subprocess

    try:

        out = subprocess.run(
            ["git", "-C", str(repo), "tag", "--sort=-creatordate"],
            capture_output=True,
            text=True,
            timeout=10,
        )

    except Exception:

        return []

    return [
        t.strip()
        for t in out.stdout.splitlines()
        if _TAG_RE.match(t.strip())
    ]


def _bump_rc(version: str) -> str:
    """末段自增（X.Y.Z → X.Y.Z+1）。"""

    m = _TAG_RE.match(version)

    if not m:
        return ""

    major, minor, patch = m.groups()

    return f"{major}.{minor}.{int(patch) + 1}"


def guess_release_version(repo: Path | None = None) -> str:
    """建议下一个发布版本。

    优先级：
      1. git describe --tags（最近 tag）→ patch 段自增
      2. 最新版本型 tag → patch 段自增
      3. 无 tag 回退：`0.1.0-{YYYYMMDD}`（确定性）

    `repo` 默认 ai-system 根（不依赖 CWD 的解析）。
    """

    if repo is None:

        repo = Path(__file__).resolve().parents[2]

    # 1. 最近 tag（git describe）
    try:

        import subprocess

        out = subprocess.run(
            ["git", "-C", str(repo), "describe", "--tags", "--abbrev=0"],
            capture_output=True,
            text=True,
            timeout=10,
        )

        nearest = out.stdout.strip()

        if nearest and _TAG_RE.match(nearest):

            bumped = _bump_rc(nearest)

            if bumped:
                return bumped

    except Exception:

        pass

    # 2. 最新版本型 tag
    tags = _git_tags(repo)

    if tags:

        bumped = _bump_rc(tags[0])

        if bumped:
            return bumped

    # 3. 无 tag 回退
    return f"0.1.0-{datetime.now().strftime('%Y%m%d')}"