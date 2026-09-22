"""Wizard state persistence (workspaces/.aic-state.yaml)."""

import sys

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

        except Exception as exc:

            # fail loud：状态文件损坏/不可读不得静默当作"无状态"
            # （否则默认项目高亮/最近目标等记忆静默丢失，行为难以解释）
            print(
                f"[aic] WARN: 读取状态文件失败 {self.path}: {exc}",
                file=sys.stderr
            )

            return {}

    def save(self):

        try:

            save_yaml(
                self.path,
                self.data
            )

        except OSError as exc:

            print(
                f"[aic] WARN: 写入状态文件失败 {self.path}: {exc}",
                file=sys.stderr
            )

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
