"""Read workflow / command markdown metadata (purpose, description, inputs).

Workflow assets use the shared skill/workflow syntax (P25): an optional
YAML frontmatter carrying the machine contract (workflow.inputs) followed by
a Markdown body. Input parsing is frontmatter-first with a fallback to the
legacy inline `## Inputs` parsing, so pre-P25 workflow files behave the same.
"""

import re

from cli.services.frontmatter import read_frontmatter
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


def _norm_field_name(item):
    """Strip inline annotations from a field name.

    `Base Branch (default: master)` → `Base Branch`
    `发布内容 (services, clusters, ...)` → `发布内容`

    Annotations are metadata, not part of the field identity.
    """

    return re.sub(
        r"\s*\([^)]*\)\s*$",
        "",
        item
    ).strip()


def _inputs_struct(inputs):
    """Normalize a structured workflow.inputs ({required:[], optional:[...]} or list).

    Returns (required, optional) lists of field names.
    """

    required = []
    optional = []

    if isinstance(inputs, dict):

        for name in (inputs.get("required") or []):
            required.append(_norm_field_name(str(name)))

        for it in (inputs.get("optional") or []):
            if isinstance(it, dict):
                optional.append(_norm_field_name(str(it.get("name") or "")))
            else:
                optional.append(_norm_field_name(str(it)))

    elif isinstance(inputs, list):

        for it in inputs:

            if isinstance(it, dict):

                name = str(it.get("name") or "")

                if it.get("required"):
                    required.append(_norm_field_name(name))
                else:
                    optional.append(_norm_field_name(name))

            else:

                optional.append(_norm_field_name(str(it)))

    return required, optional


def _frontmatter_defaults(inputs):
    """Collect defaults from a structured workflow.inputs."""

    defaults = {}

    def collect(it):

        if isinstance(it, dict):

            name = _norm_field_name(str(it.get("name") or ""))

            if "default" in it and name:
                defaults[name] = it.get("default")

    if isinstance(inputs, dict):

        for entry in (inputs.get("required") or []):
            collect(entry)

        for entry in (inputs.get("optional") or []):
            collect(entry)

    elif isinstance(inputs, list):

        for entry in inputs:
            collect(entry)

    return defaults


def parse_inputs(text):
    """Required/optional field names, frontmatter-first, fallback to inline.

    Returns (required, optional).
    """

    # 1) frontmatter 权威（若有 workflow.inputs）
    data, _ = read_frontmatter(text)

    wf = data.get("workflow") or {}

    if isinstance(wf, dict) and wf.get("inputs"):
        return _inputs_struct(wf["inputs"])

    # 2) 回退：旧内联 ## Inputs 解析
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


def field_defaults(text):
    """Extract field defaults, frontmatter-first then inline `(default: X)`.

    Returns {field_name: default}.
    """

    # 1) frontmatter 权威
    data, _ = read_frontmatter(text)

    wf = data.get("workflow") or {}

    if isinstance(wf, dict) and wf.get("inputs"):
        return _frontmatter_defaults(wf["inputs"])

    # 2) 回退：旧内联 (default: X)
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


def output_base(root, name):
    """Artifact base dir for a workflow from `workflow.outputs.base` in frontmatter.

    Machine-readable location so chain-manifest / external skills can find a
    workflow's artifacts deterministically. Returns "" when absent.
    """

    try:

        text = read_text(
            root
            / "workflows"
            / f"{name}.md"
        )

    except OSError:

        return ""

    data, _ = read_frontmatter(text)

    wf = data.get("workflow") or {}

    if isinstance(wf, dict):

        outputs = wf.get("outputs")

        if isinstance(outputs, dict):

            return str(outputs.get("base") or "")

    return ""
