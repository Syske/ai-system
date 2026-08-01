"""Compile, import, command, prompt-build, and repo-lint checks."""

import re
import subprocess
import sys

from .base import ROOT


def py_files():
    files = []

    for base in (ROOT / "cli", ROOT / "tools"):
        for p in base.rglob("*.py"):
            files.append(p)

    return sorted(set(files))


def check_compile(c):
    for p in py_files():
        try:
            source = p.read_text(encoding="utf-8")
            compile(source, str(p), "exec")
        except Exception as exc:
            c.error(
                f"compile failed: {p.relative_to(ROOT)}: {exc}"
            )


def check_imports(c):
    try:
        import cli.main  # noqa: F401
        import cli.services.wizard  # noqa: F401
        import cli.services.prompt_builder  # noqa: F401
        import cli.utils.menu  # noqa: F401
    except Exception as exc:
        c.error(f"import smoke failed: {exc!r}")


def check_commands(c):

    names = []

    for p in sorted((ROOT / "cli" / "commands").glob("*.md")):

        if not p.name.startswith("aic-"):
            c.error(
                f"command file not using aic- prefix: {p.name}"
            )

        stem = p.stem

        if stem.startswith("aic-"):
            stem = stem[len("aic-"):]

        if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", stem):
            c.error(f"command name not kebab-case: {p.name}")

        names.append(stem)

        text = p.read_text(encoding="utf-8")

        if "/opsx-" in text:
            c.error(
                f"{p.name} still references /opsx- "
                "(naming migration incomplete)"
            )

    if len(names) != len(set(names)):
        c.error("duplicate command display names")

    for p in (ROOT / "cli").rglob("*.py"):

        if "opsx" in p.read_text(encoding="utf-8"):
            c.error(
                f"{p.relative_to(ROOT)} still contains 'opsx'"
            )


def check_build(c, workflows, commands):
    try:
        from cli.services.prompt_builder import PromptBuilder
    except Exception as exc:
        c.error(f"cannot import PromptBuilder: {exc!r}")
        return

    builder = PromptBuilder()

    for name in sorted(workflows):

        try:
            builder.build(name, {})
        except Exception as exc:
            c.error(f"workflow '{name}' fails to build: {exc!r}")

    for name in commands:

        try:
            builder.build(name, {})
        except Exception as exc:
            c.error(f"command '{name}' fails to build: {exc!r}")


def check_repo_lint(c):
    audit = ROOT / "tools" / "repo-lint.py"

    if not audit.exists():
        c.warn("tools/repo-lint.py not found, skipped")
        return

    result = subprocess.run(
        [sys.executable, str(audit), "--repo-root", str(ROOT)],
        capture_output=True,
        text=True,
        timeout=120
    )

    out = result.stdout + result.stderr

    m = re.search(
        r"Skills:\s*(\d+).*BLOCKERS:\s*(\d+)\s*\|\s*ERRORS:\s*(\d+)",
        out
    )

    if not m:
        c.error(
            "repo-lint: unrecognized output (tool may be broken)"
        )
        return

    skills = int(m.group(1))
    blockers = int(m.group(2))
    errors = int(m.group(3))

    if skills == 0:
        c.error(
            "repo-lint: detected 0 skills (check root resolution)"
        )

    if blockers or errors:
        c.error(
            f"repo-lint: {blockers} blocker(s), "
            f"{errors} error(s)"
        )


def check_path_audit(c):
    audit = ROOT / "tools" / "path-audit.py"

    if not audit.exists():
        c.warn("tools/path-audit.py not found, skipped")
        return

    result = subprocess.run(
        [sys.executable, str(audit)],
        capture_output=True,
        text=True,
        timeout=120
    )

    out = result.stdout + result.stderr

    m = re.search(r"BROKEN \((\d+)\):", out)

    broken = int(m.group(1)) if m else 1

    if result.returncode != 0 or broken:
        c.error(
            f"path-audit: {broken} broken path reference(s)"
        )


def check_tools_readme(c):
    """Every tools/*.py must be registered in tools/README.md."""

    readme = ROOT / "tools" / "README.md"

    if not readme.exists():
        c.warn("tools/README.md not found, skipped")
        return

    text = readme.read_text(encoding="utf-8")

    listed = set(
        re.findall(r"`([a-z-]+\.py)`", text)
    )

    actual = {
        p.name
        for p in (ROOT / "tools").glob("*.py")
        if p.name not in ("__init__.py",)
    }

    for name in sorted(actual - listed):
        c.error(
            f"tools/{name} not registered in tools/README.md"
        )
