"""Wizard state persistence (workspaces/.aic-state.yaml)."""

from cli.utils.yaml import load_yaml, save_yaml


class StateStore:

    def __init__(self, path):

        self.path = path

        self.data = self._load()

    def _load(self):

        try:

            return load_yaml(
                self.path
            ) or {}

        except Exception:

            return {}

    def save(self):

        try:

            save_yaml(
                self.path,
                self.data
            )

        except OSError:

            pass

    def get(self, *keys, default=None):

        node = self.data

        for key in keys:

            if not isinstance(node, dict):
                return default

            node = node.get(key)

            if node is None:
                return default

        return node

    def set(self, *keys, value):

        node = self.data

        for key in keys[:-1]:

            node = node.setdefault(key, {})

        node[keys[-1]] = value
