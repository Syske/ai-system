"""Contract-consistency gate (pre-commit subset): workflow ↔ runtime contract.

Thin entrypoint used by `.githooks/pre-commit` when staged files touch
`workflows/*.md` or `templates/runtime/*.md`. Runs only the contract-consistency
checks (registry / outputs / frontmatter outputs.base) — the drift the full
`check.py` catches too late. Exit 0 = consistent, 1 = drift (block the commit).

Full gate remains `tools/check.py`; this is the fast pre-commit subset (no
unittest / repo-lint / path-audit).
"""

import argparse
import sys
from pathlib import Path

_TOOLS_DIR = Path(__file__).resolve().parent
_REPO_ROOT = _TOOLS_DIR.parent

sys.path.insert(0, str(_REPO_ROOT))
sys.path.insert(0, str(_TOOLS_DIR))

from checks import Checker, discover, check_frontmatter_consistency, check_registry


def _affected(files: str):
    """staged 文件 → 受影响 workflow 名集合（None=未指定，按全仓校验）。"""

    if not files.strip():
        return None

    names = set()

    for raw in files.split(","):
        p = raw.strip().replace("\\", "/")

        if not p:
            continue

        if p.startswith("workflows/") and p.endswith(".md"):
            names.add(Path(p).stem)
        elif p.startswith("templates/runtime/runtime-") and p.endswith(".md"):
            names.add(Path(p).stem[len("runtime-"):])
        elif p.startswith("config/workflows/") and p.endswith(".yaml"):
            names.add(Path(p).stem)

    return names


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--files", default="",
                    help="staged 文件（逗号分隔）；给定时只校验受影响的 workflow")
    args = ap.parse_args()

    c = Checker()
    workflows, _commands = discover()
    check_registry(c)

    only = _affected(args.files)

    if only is not None and not only:
        # staged 中没有 workflow/runtime/registry 相关文件 → 无可校验项
        return 0

    check_frontmatter_consistency(c, only=only)

    for e in c.errors:
        print(f"[FAIL] {e}")
    for w in c.warnings:
        print(f"[WARN] {w}")

    return 1 if c.errors else 0


if __name__ == "__main__":
    sys.exit(main())
