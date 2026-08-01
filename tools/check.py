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

sys.path.insert(0, str(Path(__file__).resolve().parent))

from checks import run_all


def main():
    return run_all()


if __name__ == "__main__":
    sys.exit(main())
