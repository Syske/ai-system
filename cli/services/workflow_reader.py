"""Read workflow / command markdown metadata (purpose, description, inputs)."""

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
                bucket.append(item)

    return required, optional
