#!/usr/bin/env python3
r"""check.py — System integrity + runnability gate (thin entrypoint).

Run after any ai-system modification:

    python tools/check.py

Validates:
1. Python sources compile and all CLI modules import
2. config/menu.yaml structure and referential integrity
3. config/workflow-registry.yaml chain (config -> workflow -> runtime)
4. Command files (aic-* prefix, kebab-case, no opsx- remnants)
5. Prompt build smoke: every registered workflow and command builds a prompt
6. Wizard dry-run: the config-driven target menu builds without a TTY
7. tools/repo-lint.py passes (BLOCKER/ERROR == 0)
8. governance/memory structure, entry format, language, and index
9. tools/path-audit.py reports no broken path references
10. Every tools/*.py is registered in tools/README.md

The check logic lives in `tools/checks/` submodules; this file keeps the
documented command entrypoint stable.

Exit code 0 = pass, 1 = failures (system may be unrunnable).
"""

import sys
from pathlib import Path

_TOOLS_DIR = Path(__file__).resolve().parent
_REPO_ROOT = _TOOLS_DIR.parent

# 使 tools/ 与仓库根均可导入（不依赖 CWD）。
# 从其他目录运行 check.py 时 `import cli`（仓库根包）会失败；
# CI workflow 从仓库根运行，但这里只插入了 tools/，故需显式加入根。
sys.path.insert(0, str(_REPO_ROOT))
sys.path.insert(0, str(_TOOLS_DIR))

from checks import run_all


def main():
    return run_all()


if __name__ == "__main__":
    sys.exit(main())
