"""Contract-consistency gate (pre-commit subset): workflow ↔ runtime contract.

Thin entrypoint used by `.githooks/pre-commit` when staged files touch
`workflows/*.md` or `templates/runtime/*.md`. Runs only the contract-consistency
checks (registry / outputs / frontmatter outputs.base) — the drift the full
`check.py` catches too late. Exit 0 = consistent, 1 = drift (block the commit).

Full gate remains `tools/check.py`; this is the fast pre-commit subset (no
unittest / repo-lint / path-audit).
"""

import sys
from pathlib import Path

_TOOLS_DIR = Path(__file__).resolve().parent
_REPO_ROOT = _TOOLS_DIR.parent

sys.path.insert(0, str(_REPO_ROOT))
sys.path.insert(0, str(_TOOLS_DIR))

from checks import Checker, discover, check_frontmatter_consistency, check_registry


def main():
    c = Checker()
    workflows, _commands = discover()
    check_registry(c)
    check_frontmatter_consistency(c)

    for e in c.errors:
        print(f"[FAIL] {e}")
    for w in c.warnings:
        print(f"[WARN] {w}")

    return 1 if c.errors else 0


if __name__ == "__main__":
    sys.exit(main())
