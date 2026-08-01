#!/usr/bin/env python3
r"""check.py — System integrity + runnability check.

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

Exit code 0 = pass, 1 = failures (system may be unrunnable).
"""

import py_compile
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent


class Checker:

    def __init__(self):
        self.errors = []
        self.warnings = []

    def error(self, msg):
        self.errors.append(msg)

    def warn(self, msg):
        self.warnings.append(msg)


def load_yaml(path):
    import yaml

    try:
        with open(path, encoding="utf-8") as fh:
            return yaml.safe_load(fh) or {}
    except Exception as exc:
        return {"__error__": str(exc)}


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


def discover():
    registry = load_yaml(ROOT / "config" / "workflow-registry.yaml")
    workflows = set(
        registry.get("workflows", {}).keys()
        if isinstance(registry.get("workflows"), dict)
        else []
    )
    commands = sorted(
        p.stem.replace("aic-", "")
        for p in (ROOT / "cli" / "commands").glob("*.md")
    )
    return workflows, commands


def check_menu(c, workflows, commands):
    menu = load_yaml(ROOT / "config" / "menu.yaml")

    if "__error__" in menu:
        c.error(f"config/menu.yaml invalid: {menu['__error__']}")
        return

    locale = menu.get("locale", "zh")

    i18n = load_yaml(ROOT / "config" / "i18n" / f"{locale}.yaml")

    if "__error__" in i18n:
        c.error(
            f"config/i18n/{locale}.yaml missing or invalid"
        )
        return

    i18n_sections = i18n.get("sections", {})

    seen = set()

    for sec in menu.get("sections", []):

        title_key = sec.get("title", "")

        if not title_key:
            c.error("config/menu.yaml: section missing title")

        elif title_key not in i18n_sections:
            c.error(
                f"config/menu.yaml section key "
                f"'{title_key}' not defined in "
                f"config/i18n/{locale}.yaml"
            )

        for item in sec.get("items") or []:

            name = item.get("name")
            kind = item.get("kind")

            if not name or kind not in ("workflow", "command"):
                c.error(
                    f"config/menu.yaml [{title_key}]: "
                    f"item missing name/kind: {item}"
                )
                continue

            key = (name, kind)

            if key in seen:
                c.error(
                    f"config/menu.yaml [{title_key}]: "
                    f"duplicate {kind} {name}"
                )

            seen.add(key)

            if kind == "workflow" and name not in workflows:
                c.error(
                    f"config/menu.yaml [{title_key}]: "
                    f"workflow '{name}' not in workflow-registry.yaml"
                )

            if kind == "command" and name not in commands:
                c.error(
                    f"config/menu.yaml [{title_key}]: "
                    f"command '{name}' has no cli/commands/aic-{name}.md"
                )

            if not item.get("icon", ""):
                c.warn(
                    f"config/menu.yaml [{title_key}]: "
                    f"{name} has no icon"
                )

    for key in ("command_fields", "command_next"):

        for name in menu.get(key, {}):

            if name not in commands:
                c.error(
                    f"config/menu.yaml {key}: "
                    f"'{name}' has no command file"
                )


# External targets allowed as the leading token of a Next bullet (not
# workflows in the registry).
NEXT_EXTERNAL = {"deployment", "none"}


def check_next_sections(c, workflows):
    """Validate the machine-readable `## Next` convention.

    Each bullet must start with the downstream workflow name (kebab-case),
    'None', or a known external target. This keeps _parse_next deterministic
    and prevents prose from being misread as a workflow name.
    """

    for md in sorted((ROOT / "workflows").glob("*.md")):

        if md.name == "README.md":
            continue

        name = md.stem

        text = md.read_text(encoding="utf-8")

        section = None

        for line in text.splitlines():

            stripped = line.strip()

            if stripped.startswith("## "):
                section = stripped[3:]
                continue

            if section != "Next":
                continue

            if not stripped.startswith("- "):
                continue

            tokens = re.findall(
                r"[a-z][a-z0-9-]*",
                stripped.lower()
            )

            if not tokens:
                continue

            first = tokens[0]

            if first in NEXT_EXTERNAL:
                continue

            if first in workflows:

                if first == name:
                    c.warn(
                        f"workflows/{name}.md Next: "
                        "self-reference (re-run loop)"
                    )

                continue

            c.error(
                f"workflows/{name}.md Next: "
                f"'{first}' is not a registered workflow "
                "(put the workflow name first in the bullet)"
            )


def check_registry(c):
    registry = load_yaml(
        ROOT / "config" / "workflow-registry.yaml"
    )

    if "__error__" in registry:
        c.error("config/workflow-registry.yaml invalid")
        return

    workflows = registry.get("workflows")

    if not isinstance(workflows, dict):
        c.error(
            "config/workflow-registry.yaml: "
            "workflows must be a mapping"
        )
        return

    for name, rel in workflows.items():

        wf_yaml = ROOT / rel

        if not wf_yaml.exists():
            c.error(f"workflow {name}: missing {rel}")
            continue

        wf = load_yaml(wf_yaml)

        if "__error__" in wf:
            c.error(f"workflow {name}: {rel} invalid")
            continue

        for key in ("workflow", "runtime"):

            target = ROOT / wf.get(key, "")

            if not target.exists():
                c.error(
                    f"workflow {name}: {key} "
                    f"'{wf.get(key)}' missing"
                )

        check_workflow_runtime_section(c, name, wf)
        check_outputs_consistency(c, name, wf)

    registered = set(workflows.keys())

    for md in (ROOT / "workflows").glob("*.md"):

        if md.name == "README.md":
            continue

        if md.stem not in registered:
            c.warn(
                f"workflows/{md.stem}.md not registered "
                "in workflow-registry.yaml"
            )


def check_workflow_runtime_section(c, name, wf):

    wf_md = ROOT / wf.get("workflow", "")

    if not wf_md.exists():
        return

    text = wf_md.read_text(encoding="utf-8")

    m = re.search(r"## Runtime\s*\n+\s*-\s+(.+)", text)

    if not m:
        c.error(
            f"workflow {name}: {wf_md.name} "
            "missing '## Runtime' section"
        )
        return

    declared = m.group(1).strip()

    normalized = declared.replace("ai-system/", "").lstrip("./")

    expected = wf.get("runtime", "")

    if normalized != expected:
        c.error(
            f"workflow {name}: '## Runtime' section "
            f"'{declared}' does not match config runtime "
            f"'{expected}'"
        )


def check_outputs_consistency(c, name, wf):

    wf_md = ROOT / wf.get("workflow", "")
    rt_md = ROOT / wf.get("runtime", "")

    if not wf_md.exists() or not rt_md.exists():
        return

    wf_text = wf_md.read_text(encoding="utf-8")
    rt_text = rt_md.read_text(encoding="utf-8")

    wf_items = _extract_outputs(wf_text, "## Outputs")
    rt_items = _extract_outputs(rt_text, "# Outputs")

    if not rt_items:
        return

    missing = [
        item
        for item in wf_items
        if item not in rt_items
    ]

    for item in missing:
        c.error(
            f"workflow {name}: output '{item}' declared in "
            f"{wf_md.name} but not in {rt_md.name}"
        )


def _extract_outputs(text, marker):

    i = text.find(marker)

    if i < 0:
        return []

    i += len(marker)

    end = len(text)

    for m in ("\n## ", "\n# "):
        k = text.find(m, i)
        if 0 < k < end:
            end = k

    items = []

    for line in text[i:end].splitlines():

        s = line.strip()

        if not s.startswith("- "):
            continue

        item = s[2:].strip()

        item = re.sub(r"\s+#.*$", "", item).strip()

        item = re.sub(r"\s+", " ", item).strip()

        item = re.sub(r"\s*\([^)]*\)\s*$", "", item).strip()

        if item:
            items.append(item)

    return items


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


def check_wizard_dry_run(c, workflows, commands):
    try:
        import cli.utils.menu as menu
        from cli.services import wizard as wz
        from cli.services.wizard import Wizard

        def fake_choose(
            title,
            options,
            default=0,
            allow_skip=False,
            header=None,
            note=None
        ):
            for i, opt in enumerate(options):
                if not isinstance(opt, menu.Section):
                    return i
            return 0

        wz.choose = fake_choose
        wz.choose_many = lambda *a, **k: None

        w = Wizard(ROOT)
        w._recommend_workflow = lambda project, ws: None

        target = w._select_target([], None)

        if target is None:
            c.error("wizard menu dry-run returned no target")

        for name in commands:
            try:
                w._fields_for((name, "command"))
            except Exception as exc:
                c.error(
                    f"command '{name}' fields fail: {exc!r}"
                )

    except Exception as exc:
        c.error(f"wizard dry-run failed: {exc!r}")


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
        r"BLOCKERS:\s*(\d+)\s*\|\s*ERRORS:\s*(\d+)",
        out
    )

    blockers = int(m.group(1)) if m else 1
    errors = int(m.group(2)) if m else 1

    if blockers or errors:
        c.error(
            f"repo-lint: {blockers} blocker(s), "
            f"{errors} error(s)"
        )


def main():

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


if __name__ == "__main__":
    sys.exit(main())
