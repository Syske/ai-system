"""Reusable agent selection.

Presents the launch-agent menu. The candidate list is merged from:

- configured enabled providers (config/providers.yaml) — with an install
  status badge (✓ installed / ⚠ missing) from auto-detection
- auto-detected installed agents not in providers.yaml (e.g. qoder) — shown
  with a "(检测到)" marker, unless opted out (enabled:false / detect:false)

Returns the chosen agent name (e.g. "opencode"). Shared by skill-launch and
any other flow that needs to pick a launch agent.
"""

from cli.services.agent_detect import (
    merge_picker_entries,
    sort_by_usage,
)
from cli.utils.menu import BACK, choose, e


def pick_agent(config, title="选择代理", default=None, usage=None, record=None):
    """Present an agent-selection menu from merged providers + detection.

    Entries are ordered by usage count (descending, stable). Optional
    `usage` ({name: count}) enables the ordering; optional `record`
    (callable(name)) is invoked with the chosen agent for usage stats.

    Returns the chosen agent name, or None when cancelled / nothing available.
    """

    entries = [
        ent
        for ent in merge_picker_entries(config)
        if ent["installed"]
    ]

    entries = sort_by_usage(entries, usage)

    if not entries:

        print(
            "未检测到可用代理（providers.yaml 无启用项，且系统未发现已安装 agent CLI）。"
        )

        return None

    options = []

    for ent in entries:

        label = ent["label"]

        if ent["icon"]:
            label = ent["icon"] + label

        desc = ent["description"]

        if desc:
            label += f" — {desc}"

        options.append(label)

    names = [ent["name"] for ent in entries]

    default_idx = 0

    if default and default in names:
        default_idx = names.index(default)

    idx = choose(
        title,
        options,
        default=default_idx
    )

    if idx is BACK:
        return None

    chosen = names[idx]

    if record is not None:

        record(chosen)

    return chosen
