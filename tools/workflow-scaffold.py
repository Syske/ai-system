r"""Scaffold a new workflow and register it in the registry.

Usage:
    python tools/workflow-scaffold.py <name>
    python tools/workflow-scaffold.py <name> --purpose "One-sentence purpose"
    python tools/workflow-scaffold.py <name> --next review
    python tools/workflow-scaffold.py --list          # list existing workflows + Purpose

Generates (non-destructive, never overwrites existing files):
    workflows/<name>.md             8-section entry contract
    config/workflows/<name>.yaml    minimal registry entry (version/name/workflow/runtime)
    templates/runtime/runtime-<name>.md  runtime skeleton (extends runtime-base.md)

Appends the registry entry to config/workflow-registry.yaml (idempotent:
refuses when the workflow name already exists). Prints the menu.yaml /
workflows/README.md registration checklist.

After scaffolding, the operator fills in the 8 sections (Preconditions,
Inputs, Context, Outputs, Exit Criteria) and then runs:
    python tools/check.py
    python tools/repo-lint.py --repo-root .
"""

import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent

NAME_RE = re.compile(r"^[a-z][a-z0-9]*(?:-[a-z0-9]+)*$")

WORKFLOW_TEMPLATE = """---
name: {name}
description: \"{purpose}\"
workflow:
  inputs:
    required: [TBD]
    optional: [TBD]
  next: [None]
---
# Workflow: {Title}

## Purpose

{purpose}

## Runtime

- templates/runtime/runtime-{name}.md

## Preconditions

- TBD

## Inputs

Required:

- TBD

Optional:

- TBD

## Context

Load only:

- TBD

Never load the entire repository tree into context.

## Outputs

- {lower}-report.md

  (按 outputs-convention：`outputs/{lower}/{yyMMdd}-{descriptor}/`，
  descriptor 为本次会话主题 kebab-case ≤30 字符；同日重跑追加 -N)

## Exit Criteria

Success:

- TBD

Stop:

- TBD

## Next

{next_line}
"""

RUNTIME_TEMPLATE = """# Runtime: {Title}

Extends:

- runtime-base.md

---

## Purpose

{purpose}

The Runtime produces {lower} outputs. No implementation is performed.

---

## Governance

This Runtime is bound by:

- AI Operating Rules: governance/AI_OPERATING_RULES.md
- Source of Truth: governance/SOURCE_OF_TRUTH.md
- Context Loading: governance/CONTEXT_LOADING.md
- Repository First: governance/REPOSITORY_FIRST.md
- Reflection Rules: governance/REFLECTION_RULES.md

Context is loaded according to governance/CONTEXT_LOADING.md.
Standards are loaded according to loaders/standards-loader.md.

---

## Responsibilities

The Runtime is responsible for:

- TBD

---

## Runtime Context

Provided by Runtime Base:

- Runtime Configuration
- Operating Rules

Resolved by {Title} Runtime:

- TBD

---

## Phase 1 — TBD

Collect:

- TBD

Generate:

- TBD

---

## Outputs

Generate:

- TBD

## Reflection

Before declaring completion, execute Reflection according to governance/REFLECTION_RULES.md.

Evaluate:
1. Simpler implementation possible?
2. Code duplication introduced?
3. Standards violated?
4. Over-engineering present?
5. Anything incomplete?

Record the Reflection Report in the Completion output.
Do NOT modify code during Reflection.

---

## Completion

Return:

- TBD
"""

REGISTRY_ENTRY = """  {name}: config/workflows/{name}.yaml"""


def _title(name):

    return " ".join(
        part.capitalize()
        for part in name.split("-")
    )


def _write(path, content):

    if path.exists():
        print(f"EXISTS (skipped): {path}")
        return False

    path.write_text(content, encoding="utf-8")

    print(f"created: {path}")

    return True


def _append_registry(name, config_path):

    if not config_path.exists():
        print(f"ERROR: {config_path} not found")
        return False

    text = config_path.read_text(encoding="utf-8")

    if re.search(rf"^\s+{re.escape(name)}:", text, re.MULTILINE):
        print(f"EXISTS in registry (skipped): {name}")
        return False

    text = text.rstrip() + "\n" + REGISTRY_ENTRY.format(name=name) + "\n"

    config_path.write_text(text, encoding="utf-8")

    print(f"registry: appended '{name}' to {config_path}")

    return True


def _list_workflows():

    """Print existing workflows with their Purpose for overlap assessment."""

    wf_dir = ROOT / "workflows"

    rows = []

    for path in sorted(wf_dir.glob("*.md")):

        if path.name == "README.md":
            continue

        text = path.read_text(encoding="utf-8")

        purpose = ""

        section = None

        for line in text.splitlines():

            stripped = line.strip()

            if stripped.startswith("## "):
                section = stripped[3:]
                continue

            if section == "Purpose" and stripped:
                purpose = stripped
                break

        rows.append((path.stem, purpose))

    if not rows:

        print("no workflows registered")

        return

    width = max(len(name) for name, _ in rows)

    for name, purpose in rows:

        print(f"{name.ljust(width)}  {purpose}")


def main():

    if len(sys.argv) < 2:

        print(__doc__)

        return 1

    if sys.argv[1] == "--list":

        _list_workflows()

        return 0

    name = sys.argv[1]

    if not NAME_RE.match(name):

        print(
            "ERROR: workflow name must be kebab-case "
            "(lowercase letters, digits, hyphens), got: "
            f"'{name}'"
        )

        return 1

    purpose = "TBD"
    next_target = None

    args = sys.argv[2:]

    i = 0

    while i < len(args):

        if args[i] == "--purpose":

            i += 1

            if i < len(args):
                purpose = args[i]

        elif args[i] == "--next":

            i += 1

            if i < len(args):
                next_target = args[i]

        i += 1

    title = _title(name)

    next_line = (
        f"- {next_target}"
        if next_target
        else "- None"
    )

    config_path = ROOT / "config" / "workflow-registry.yaml"

    wf = ROOT / "workflows" / f"{name}.md"
    cfg = ROOT / "config" / "workflows" / f"{name}.yaml"
    rt = ROOT / "templates" / "runtime" / f"runtime-{name}.md"

    workflow_body = WORKFLOW_TEMPLATE.format(
        Title=title,
        purpose=purpose,
        name=name,
        next_line=next_line,
    )

    runtime_body = RUNTIME_TEMPLATE.format(
        Title=title,
        purpose=purpose,
        lower=name,
    )

    config_body = (
        "version: 1\n\n"
        f"name: {name}\n\n"
        f"workflow: workflows/{name}.md\n"
        f"runtime: templates/runtime/runtime-{name}.md\n"
    )

    created_any = False

    created_any |= _write(wf, workflow_body)
    created_any |= _write(cfg, config_body)
    created_any |= _write(rt, runtime_body)

    registered = _append_registry(name, config_path)

    print()
    print("Scaffold complete. Remaining manual steps:")
    print()
    print(f"1. Fill the TBD sections in workflows/{name}.md:")
    print("   Preconditions / Inputs / Context / Outputs / Exit Criteria")
    print(f"2. Fill the TBD phases in templates/runtime/runtime-{name}.md")
    print("3. Register in config/menu.yaml: add a `kind: workflow` item")
    print("   under a sections entry (icon required) for discovery")
    print("4. Update workflows/README.md selection table + terminology")
    print("   if new fields are introduced")
    print("5. Validate:")
    print("   python tools/check.py")
    print("   python tools/repo-lint.py --repo-root .")

    if not (created_any or registered):

        print()
        print("Nothing created — name likely already registered.")

        return 0

    return 0


if __name__ == "__main__":
    sys.exit(main())
