"""Compile, import, command, prompt-build, and repo-lint checks."""

import json
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


def check_tuple_return_arity(c):
    """静态检查：同一函数的所有 tuple-return 元数必须一致。

    防止多返回值签名变更时只改部分 return 导致 UnpackingError
    （曾发生：wizard skill 目录 return 4 元组、意图链路径 5 元组，
    启动即 'ValueError: not enough values to unpack'）。
    """

    import ast

    def tuple_arity(node):
        if not isinstance(node, ast.Tuple):
            return None
        return len(node.elts)

    for p in py_files():

        try:

            tree = ast.parse(
                p.read_text(encoding="utf-8")
            )

        except SyntaxError:
            # check_compile 已单独报
            continue

        for fn in ast.walk(tree):

            if not isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue

            arities = []

            for n in ast.walk(fn):

                if not isinstance(n, ast.Return) or not n.value:
                    continue

                arity = tuple_arity(n.value)

                if arity is not None:
                    arities.append(arity)

            if len(set(arities)) > 1:

                c.error(
                    f"{p.relative_to(ROOT)}::{fn.name}: inconsistent tuple "
                    f"return arity {sorted(set(arities))} "
                    f"(expected a single arity)"
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


def check_proposal_audit(c):
    """Proposal-policy gate via tools/proposal-audit.py.

    Errors break the build (invalid Status, missing Implementation Record).
    Leftover proposals / open items are reported as warnings for the
    maintenance report.
    """

    script = ROOT / "tools" / "proposal-audit.py"

    if not script.exists():
        c.warn("tools/proposal-audit.py not found, skipped")
        return

    try:

        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "proposal_audit_check",
            script
        )

        mod = importlib.util.module_from_spec(spec)

        spec.loader.exec_module(mod)

    except Exception as exc:

        c.error(f"cannot load proposal-audit: {exc!r}")

        return

    try:

        result = mod.audit()

    except Exception as exc:

        c.error(f"proposal-audit failed: {exc!r}")

        return

    for e in result.get("errors", []):
        c.error(f"proposal: {e}")

    for w in result.get("warnings", []):
        c.warn(f"proposal: {w}")

    leftover = [
        p["file"]
        for p in result.get("proposals", [])
        if p["status"].lower() not in mod.CLOSED_STATUSES
    ]

    open_items = result.get("open_items", [])

    if leftover:
        c.warn(
            f"proposal: open proposals — {', '.join(leftover)}"
        )

    if open_items:
        c.warn(
            f"proposal: {len(open_items)} open action item(s) in reports/"
        )


def check_workflow_command_audit(c):
    """Dangling command refs and structural health of workflows/commands."""

    audit = ROOT / "tools" / "workflow-command-audit.py"

    if not audit.exists():
        c.warn("tools/workflow-command-audit.py not found, skipped")
        return

    result = subprocess.run(
        [sys.executable, str(audit), "--repo-root", str(ROOT), "--json"],
        capture_output=True,
        text=True,
        timeout=120
    )

    try:
        data = json.loads(result.stdout)
    except Exception:
        c.error("workflow-command-audit: unrecognized output (tool may be broken)")
        return

    for b in data.get("blockers", []):
        c.error(f"wfc-audit: {b}")

    for w in data.get("warnings", []):
        c.warn(f"wfc-audit: {w}")


def check_cli_tests(c):
    """CLI service unit tests (C1 test base) must pass."""

    tests_dir = ROOT / "cli" / "tests"
    if not tests_dir.exists():
        c.warn("cli/tests not found, skipped")
        return

    result = subprocess.run(
        [sys.executable, "-m", "unittest", "discover", "-s", str(tests_dir)],
        capture_output=True,
        text=True,
        timeout=180,
        cwd=str(ROOT),
    )

    out = result.stdout + result.stderr
    if result.returncode != 0:
        c.error("cli tests failed:\n" + out[-2000:])


def check_outputs_convention(c):
    """输出产物路径规范门禁（outputs-convention §6）。

    Business-facing workflow/command docs that reference `outputs/` MUST use
    the `{yyMMdd}` date format (e.g. 260818). The legacy `{YYYY-MM-DD}` /
    timestamp-prefixed (`scan-20260817...`) forms are banned for new outputs
    (drifted from code, which uniformly uses yyMMdd since 2026-08-18).
    """

    import re

    LEGACY = [
        (r"outputs/\{[Yy]{4}[^}]*\}", "{{YYYY-MM-DD}} old format"),
        (r"outputs/[A-Za-z-]+/\{[Yy]{2,4}-[^}]*\}", "legacy date placeholder"),
        (r"outputs/\{[Yy]{4}-", "{{YYYY-...}} old format"),
        (r"outputs/[A-Za-z-]+/\{[Yy]{2}\}", "{{YY}} placeholder missing descriptor"),
    ]

    # 扫描 business-facing 文档（workflows + 命令 + 脚手架模板）
    targets = []

    for base in ("workflows", "cli/commands"):
        d = ROOT / base
        if d.exists():
            targets.extend(sorted(d.glob("*.md")))

    targets.extend([
        ROOT / "tools" / "workflow-scaffold.py",
        ROOT / "tools" / "command-scaffold.py",
    ])

    for p in targets:

        try:

            text = p.read_text(encoding="utf-8", errors="replace")

        except OSError:
            continue

        for pattern, label in LEGACY:

            if re.search(pattern, text):

                c.error(
                    f"{p.relative_to(ROOT)}: legacy outputs date format ({label}); "
                    f"use {{yyMMdd}} per outputs-convention (§6)"
                )
