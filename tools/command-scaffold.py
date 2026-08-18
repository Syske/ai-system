r"""Scaffold a new command and print its registration checklist.

Usage:
    python tools/command-scaffold.py <name>
    python tools/command-scaffold.py <name> --description "What this command does"
    python tools/command-scaffold.py --list              # list existing commands + descriptions

Generates (non-destructive, never overwrites existing files):
    cli/commands/aic-<name>.md     command definition skeleton

Prints the menu.yaml / i18n registration checklist (sections entry,
command_fields, field_icons, optional command_hooks.py). Idempotent: refuses
when the command file already exists.

After scaffolding, the operator fills in the Steps / Output / Guardrails
sections and then runs:
    python tools/check.py
    python tools/repo-lint.py --repo-root .

Run the necessity assessment FIRST (layer classification, overlap check via
--list, Evolution Principle, user confirmation) — see cli/commands/aic-command.md.
"""

import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent

NAME_RE = re.compile(r"^[a-z][a-z0-9]*(?:-[a-z0-9]+)*$")

COMMAND_TEMPLATE = """---
description: {description}
---

{description}

**Steps**

1. TBD

**Output**

## {Title} Report

- 范围 / 描述
- 结论

（按 outputs-convention：`outputs/{lower}/{yyMMdd}-{descriptor}/`，
  descriptor 为主题 kebab-case ≤30 字符；同日重跑追加 -N）

**Guardrails**

- TBD
"""


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


def _list_commands():

    cmd_dir = ROOT / "cli" / "commands"

    rows = []

    for path in sorted(cmd_dir.glob("aic-*.md")):

        name = path.stem[len("aic-"):]

        description = ""

        text = path.read_text(encoding="utf-8")

        for line in text.splitlines():

            stripped = line.strip()

            if stripped.startswith("description:"):

                description = stripped.split(
                    ":",
                    1
                )[1].strip()

                break

        rows.append((name, description))

    if not rows:

        print("no commands registered")

        return

    width = max(len(name) for name, _ in rows)

    for name, description in rows:

        print(f"{name.ljust(width)}  {description}")


def main():

    if len(sys.argv) < 2:

        print(__doc__)

        return 1

    if sys.argv[1] == "--list":

        _list_commands()

        return 0

    name = sys.argv[1]

    if not NAME_RE.match(name):

        print(
            "ERROR: command name must be kebab-case "
            "(lowercase letters, digits, hyphens), got: "
            f"'{name}'"
        )

        return 1

    description = "TBD command description"

    args = sys.argv[2:]

    i = 0

    while i < len(args):

        if args[i] == "--description":

            i += 1

            if i < len(args):
                description = args[i]

        i += 1

    title = _title(name)

    cmd_path = ROOT / "cli" / "commands" / f"aic-{name}.md"

    body = COMMAND_TEMPLATE.format(
        description=description,
        Title=title,
    )

    created = _write(cmd_path, body)

    print()
    print("Scaffold complete. Remaining manual steps:")
    print()
    print(f"1. Fill the Steps / Output / Guardrails in cli/commands/aic-{name}.md")
    print("2. Register in config/menu.yaml:")
    print("   - sections entry: { name, kind: command, icon } (icon required)")
    print("   - command_fields: field definitions [[name, required], ...]")
    print("   - field_icons: per-field icons")
    print("3. Add i18n copy in config/i18n/{locale}.yaml:")
    print("   - field_notes / option_descriptions for new fields")
    print("4. Add command hooks in cli/services/command_hooks.py (only if needed)")
    print("5. Validate:")
    print("   python tools/check.py")
    print("   python tools/repo-lint.py --repo-root .")

    if not created:

        print()
        print("Nothing created — command file already exists.")

        return 0

    return 0


if __name__ == "__main__":
    sys.exit(main())
