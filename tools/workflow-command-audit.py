#!/usr/bin/env python3
r"""workflow-command-audit.py — Workflow & command health auditor.

Reusable health assessment for the workflow and command layers. Run
periodically (quarterly review) or before restructuring:

    python tools/workflow-command-audit.py --repo-root .

Checks:

Workflows (workflows/*.md):
  - File length > 100 lines (RFC-0003 gate)
  - Next section targets an unregistered workflow or a dead cycle
  - Missing required 8-section structure (Purpose/Runtime/Preconditions/
    Inputs/Context/Outputs/Exit Criteria/Next)

Commands (cli/commands/aic-*.md):
  - File length > 100 lines (command layer must stay thin: prompt-builder)
  - Dangling command references (/aic-xxx pointing to a non-existent command)
  - Command not registered in config/menu.yaml

Output: BLOCKERS (structural, must fix), WARNINGS (health signal), plus a
summary. Exit 2 on blockers, 1 on warnings, 0 clean.
"""

import argparse
import re
import sys
from pathlib import Path

WORKFLOW_SECTIONS = [
    "Purpose",
    "Runtime",
    "Preconditions",
    "Inputs",
    "Context",
    "Outputs",
    "Exit Criteria",
    "Next",
]
CMD_REF_RE = re.compile(r"`?/aic-([a-z][a-z0-9-]+)`?")


def find_workflows(root):
    d = root / "workflows"
    return sorted(d.glob("*.md")) if d.exists() else []


def find_commands(root):
    d = root / "cli" / "commands"
    return sorted(d.glob("aic-*.md")) if d.exists() else []


def registered_commands(root):
    """Command names registered in config/menu.yaml.

    Includes both section items (name: x) and hidden_commands entries
    (- x) — hidden commands are registered-but-invisible (AI-internal,
    ADR-0009), not unregistered.
    """
    menu = root / "config" / "menu.yaml"
    if not menu.exists():
        return set()
    text = menu.read_text(encoding="utf-8")
    names = set()
    for m in re.finditer(r"name:\s*([a-z][a-z0-9-]+)", text):
        names.add(m.group(1))
    # hidden_commands 段的条目：- propose（无 name: 前缀）
    hidden_section = text.split("hidden_commands:", 1)
    if len(hidden_section) == 2:
        for m in re.finditer(
            r"^\s*-\s*([a-z][a-z0-9-]+)\s*(?:#.*)?$",
            hidden_section[1].split("\nsections:")[0],
            re.M,
        ):
            names.add(m.group(1))
    return names


def registered_workflows(root):
    reg = root / "config" / "workflow-registry.yaml"
    if not reg.exists():
        return set()
    names = set()
    for line in reg.read_text(encoding="utf-8").splitlines():
        m = re.match(r"\s{2}([a-z][a-z0-9-]+):\s", line)
        if m:
            names.add(m.group(1))
    return names


def audit_workflow(p, workflows, results):
    text = p.read_text(encoding="utf-8", errors="replace")
    lines = text.splitlines()
    n = len(lines)
    if n > 100:
        results["warnings"].append(f"{p.name}: {n} lines (>100, RFC-0003)")

    # Required sections
    for sec in WORKFLOW_SECTIONS:
        if not re.search(rf"^## {sec}", text, re.MULTILINE):
            results["blockers"].append(f"{p.name}: missing '## {sec}'")

    # Next targets
    m = re.search(r"^## Next\s*\n(.*?)(?=\n## |\Z)", text, re.MULTILINE | re.DOTALL)
    if m:
        for line in m.group(1).splitlines():
            mm = re.match(r"\s*-\s*([a-z][a-z0-9-]*)", line)
            if mm:
                target = mm.group(1)
                if target in ("none", "deployment", "external"):
                    continue
                if target not in workflows:
                    results["blockers"].append(
                        f"{p.name}: Next -> '{target}' not a registered workflow"
                    )


def audit_command(p, menu_cmds, all_cmd_names, results):
    text = p.read_text(encoding="utf-8", errors="replace")
    n = len(text.splitlines())
    if n > 100:
        results["warnings"].append(f"{p.name}: {n} lines (thin-command gate)")

    name = p.name.replace("aic-", "").replace(".md", "")
    if name not in menu_cmds:
        results["blockers"].append(f"{p.name}: not registered in config/menu.yaml")

    # Dangling command references: /aic-xxx where xxx has no command file
    for ref in CMD_REF_RE.findall(text):
        if ref == name:
            continue  # self-reference
        if ref not in all_cmd_names:
            results["blockers"].append(
                f"{p.name}: dangling reference '/aic-{ref}' (no such command)"
            )


def main():
    parser = argparse.ArgumentParser(description="Workflow & command health auditor")
    parser.add_argument("--repo-root", required=True, help="Repository root (ai-system)")
    parser.add_argument("--json", action="store_true", help="Machine-readable output")
    args = parser.parse_args()

    root = Path(args.repo_root).resolve()
    results = {"blockers": [], "warnings": []}

    workflows = registered_workflows(root)
    for p in find_workflows(root):
        if p.name == "README.md":
            continue
        audit_workflow(p, workflows, results)

    menu_cmds = registered_commands(root)
    all_cmd_names = {
        p.name.replace("aic-", "").replace(".md", "")
        for p in find_commands(root)
    }
    for p in find_commands(root):
        audit_command(p, menu_cmds, all_cmd_names, results)

    if args.json:
        import json

        print(json.dumps(results, indent=2, ensure_ascii=False))
    else:
        print(f"Workflows checked: {len(find_workflows(root)) - 1}")
        print(f"Commands checked: {len(find_commands(root))}")
        print("")
        for tag, items in (("BLOCKER", results["blockers"]), ("WARN", results["warnings"])):
            for item in items:
                print(f"  [{tag}] {item}")
        print("")
        print(
            f"Summary: {len(results['blockers'])} blockers, "
            f"{len(results['warnings'])} warnings"
        )

    if results["blockers"]:
        sys.exit(2)
    if results["warnings"]:
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
