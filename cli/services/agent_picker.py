"""Reusable agent selection.

Reads enabled providers from config/providers.yaml and presents a menu with
label + description. Returns the chosen agent name (e.g. "opencode"). Shared
by skill-launch and any other flow that needs to pick a launch agent.
"""

from cli.utils.menu import BACK, choose, e


def pick_agent(config, title="Select an agent", default=None):
    """Present an agent-selection menu from enabled providers.

    Returns the chosen agent name, or None when cancelled / no providers.
    """

    enabled = config.enabled_providers()

    if not enabled:

        print("No agents enabled in config/providers.yaml.")

        return None

    meta = config.provider_meta()

    options = []

    for name in enabled:

        m = meta.get(name, {})

        label = m.get("label") or name

        icon = e(m.get("icon") or "")

        desc = m.get("description") or ""

        if icon:
            label = icon + label

        if desc:
            label += f" — {desc}"

        options.append(label)

    default_idx = 0

    if default and default in enabled:

        default_idx = enabled.index(default)

    idx = choose(
        title,
        options,
        default=default_idx
    )

    if idx is BACK:
        return None

    return enabled[idx]
