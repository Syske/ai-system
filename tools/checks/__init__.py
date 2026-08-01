"""Integrity check submodules aggregated into a single runnable gate."""

from .base import Checker, ROOT
from .misc import (
    check_build,
    check_commands,
    check_compile,
    check_imports,
    check_repo_lint,
)
from .menu import check_menu, check_wizard_dry_run
from .memory import check_memory
from .workflow import (
    check_next_sections,
    check_registry,
    discover,
)


def run_all():

    c = Checker()

    workflows, commands = discover()

    check_compile(c)
    check_imports(c)
    check_menu(c, workflows, commands)
    check_registry(c)
    check_next_sections(c, workflows)
    check_commands(c)
    check_build(c, workflows, commands)
    check_wizard_dry_run(c, workflows, commands)
    check_repo_lint(c)
    check_memory(c)

    print(
        f"discovered: {len(workflows)} workflows, "
        f"{len(commands)} commands"
    )

    for w in c.warnings:
        print(f"  [WARN] {w}")

    for e in c.errors:
        print(f"  [FAIL] {e}")

    print()

    if c.errors:
        print(
            f"FAIL: {len(c.errors)} error(s), "
            f"{len(c.warnings)} warning(s)"
        )
        return 1

    print(f"PASS: {len(c.warnings)} warning(s)")
    return 0
