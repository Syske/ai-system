"""Main-chain external capability loader.

Loads the optional external skills registered per main-chain stage from
config/main-chain-capabilities.yaml (from extensions/). Defaults to empty;
each entry is extensible and `enabled: false` disables it without removal.
"""

from pathlib import Path

from cli.utils.yaml import load_yaml

CAPS_FILE = "config/main-chain-capabilities.yaml"


def external_capabilities(root, stage):
    """Enabled external skills for a main-chain stage (e.g. 'prepare').

    Returns a list of dicts {skill, path, desc, enabled}. Empty by default.
    """

    path = Path(root) / CAPS_FILE

    if not path.exists():
        return []

    data = load_yaml(path)

    if not isinstance(data, dict):
        return []

    caps = (data.get("capabilities") or {}).get(stage)

    if not isinstance(caps, list):
        return []

    out = []

    for c in caps:

        if not isinstance(c, dict):
            continue

        if c.get("enabled", True):

            out.append(c)

    return out
