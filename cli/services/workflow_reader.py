"""Read workflow / command markdown metadata (purpose, description, inputs)."""

import re

from cli.utils.file import read_text


def purpose(root, name):

    try:

        text = read_text(
            root
            / "workflows"
            / f"{name}.md"
        )

    except OSError:

        return ""

    section = None

    for line in text.splitlines():

        stripped = line.strip()

        if stripped.startswith("## "):
            section = stripped[3:]
            continue

        if section == "Purpose" and stripped:
            return stripped

    return ""


def command_description(root, name):

    path = (
        root
        / "cli"
        / "commands"
        / f"aic-{name}.md"
    )

    if not path.exists():

        path = (
            root
            / "cli"
            / "commands"
            / f"{name}.md"
        )

    try:

        text = read_text(path)

    except OSError:

        return ""

    for line in text.splitlines():

        stripped = line.strip()

        if stripped.startswith("description:"):

            return stripped.split(
                ":",
                1
            )[1].strip()

    return ""


def short(text, limit=58):

    if len(text) <= limit:
        return text

    return text[: limit - 1] + "…"


def parse_inputs(text):

    required = []
    optional = []

    section = None
    bucket = None

    for line in text.splitlines():

        stripped = line.strip()

        if stripped.startswith("## "):
            section = stripped[3:]
            bucket = None
            continue

        if section != "Inputs":
            continue

        if stripped == "Required:":
            bucket = required
            continue

        if stripped == "Optional:":
            bucket = optional
            continue

        if (
            stripped.startswith("- ")
            and bucket is not None
        ):

            item = stripped[2:].strip()

            if item and item != "None":

                bucket.append(
                    _norm_field_name(item)
                )

    return required, optional


def _norm_field_name(item):
    """Strip inline annotations from a field name.

    `Base Branch (default: master)` → `Base Branch`
    `发布内容 (services, clusters, ...)` → `发布内容`

    The md Inputs section is the single semantic source; annotations are
    metadata, not part of the field identity (wizard/CLI keys use the
    bare name).
    """

    return re.sub(
        r"\s*\([^)]*\)\s*$",
        "",
        item
    ).strip()


def field_defaults(text):
    """Extract inline "(default: X)" from the Inputs field names.

    Returns {field_name: default}. The md Inputs section is the single
    semantic source for input metadata (name, required, default).
    """

    defaults = {}

    section = None

    for line in text.splitlines():

        stripped = line.strip()

        if stripped.startswith("## "):
            section = stripped[3:]
            continue

        if section != "Inputs":
            continue

        if not stripped.startswith("- "):
            continue

        item = stripped[2:].strip()

        if not item or item == "None":
            continue

        match = re.search(
            r"\(default:\s*([^)]+)\)",
            item
        )

        if not match:

            # 也支持 `; default X;` 格式（如 bugfix Mode）
            match = re.search(
                r";\s*default\s+([^;]+?)\s*(?:;|$)",
                item
            )

        if match:

            defaults[
                _norm_field_name(item)
            ] = (
                match.group(1).strip()
            )

    return defaults
