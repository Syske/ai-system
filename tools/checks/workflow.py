"""Workflow / registry / Next-section integrity checks."""

import re

from .base import ROOT, load_yaml

NEXT_EXTERNAL = {"deployment", "none"}


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


def check_workflow_size(c):
    """RFC-0003 gate: workflow definition files must be <= 100 body lines.

    YAML frontmatter (the machine contract) is not counted — only the
    executable/readable Markdown body (P25: contract moved to frontmatter).
    """

    wf_dir = ROOT / "workflows"
    if not wf_dir.exists():
        return

    for p in sorted(wf_dir.glob("*.md")):
        if p.name == "README.md":
            continue
        text = p.read_text(encoding="utf-8", errors="replace")
        fm = re.match(r"\A---[ \t]*\n.*?\n---[ \t]*\n", text, re.DOTALL)
        if fm:
            text = text[fm.end():]
        n = len(text.splitlines())
        if n > 100:
            c.error(
                f"workflows/{p.name} exceeds RFC-0003 limit: "
                f"{n} body lines (max 100)"
            )
