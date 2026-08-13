"""Menu and i18n configuration access.

Centralizes loading of config/menu.yaml and config/i18n/{locale}.yaml and the
lookup helpers used by the wizard, so the wizard stays an orchestrator.
"""

import re
from pathlib import Path

from cli.utils.yaml import load_yaml


class MenuConfig:

    def __init__(self, root):

        # Accept both Path and str; resolve to absolute so relative paths
        # (e.g. ".") do not silently load an empty menu.
        self.root = Path(root).resolve()

        self.menu = self._load(
            "menu.yaml"
        )

        self.i18n = self._load_i18n()

        self.provider_config = self._load(
            "providers.yaml"
        )

        self.skill_groups_config = self._load(
            "skill-groups.yaml"
        )

    def _load(self, name):

        try:

            return load_yaml(
                self.root
                / "config"
                / name
            ) or {}

        except Exception:

            return {}

    def _load_i18n(self):

        locale = self.menu.get(
            "locale",
            "zh"
        )

        return self._load(
            f"i18n/{locale}.yaml"
        )

    def get(self, key, default=None):

        return self.menu.get(
            key,
            default or {}
        )

    def t(self, path, default=None):
        """Recursive lookup of a dot-path in the i18n tree."""

        node = self.i18n

        for part in path.split("."):

            if not isinstance(node, dict):
                break

            node = node.get(part)

            if node is None:
                break

        if node is None:
            return default

        return node

    def command_fields(self, name):

        fields = self.get(
            "command_fields"
        ).get(name)

        if fields:
            return [
                (f[0], bool(f[1]))
                for f in fields
            ]

        default = self.get(
            "default_command_fields"
        )

        if default:
            return [
                (f[0], bool(f[1]))
                for f in default
            ]

        return []

    def field_icon(self, field):

        value = (
            self.get("field_icons")
            .get(field, "")
        )

        if not value:
            value = (
                self.get("field_icons")
                .get(self._base(field), "")
            )

        return value

    def field_note(self, field):

        note = self.t(
            f"field_notes.{field}"
        )

        if not note:
            note = self.t(
                f"field_notes.{self._base(field)}"
            )

        return note

    def field_choices(self, field):

        return (
            self.get("field_choices")
            .get(field)
            or self.get("field_choices")
            .get(self._base(field), [])
        )

    def option_descriptions(self, field):

        desc = self.t(
            f"option_descriptions.{field}"
        )

        if not desc:
            desc = self.t(
                f"option_descriptions.{self._base(field)}"
            )

        return desc

    @staticmethod
    def _base(field):
        """Strip a '(default: X)' suffix so lookups also match the base name."""

        return re.sub(
            r"\s*\(default:[^)]*\)\s*$",
            "",
            field
        )

    def command_next(self, name):

        return (
            self.get("command_next")
            .get(name)
        )

    def auto_fields(self):

        return set(
            self.get("auto_fields")
        )

    def multi_select_fields(self):

        return set(
            self.get("multi_select_fields")
        )

    def hidden_workflows(self):

        return set(
            self.get("hidden_workflows")
        )

    def menu_option(self, menu, key):

        return (
            self.get("menu_options")
            .get(menu, {})
            .get(key, "")
        )

    def enabled_providers(self):

        providers = (
            self.provider_config
            .get("providers", {})
        )

        if not isinstance(providers, dict):
            return []

        return [
            name
            for name, cfg in providers.items()
            if cfg.get("enabled", True)
        ]

    def provider_meta(self):
        """Return {name: {label, description}} for all configured providers."""

        providers = (
            self.provider_config
            .get("providers", {})
        )

        if not isinstance(providers, dict):
            return {}

        meta = {}

        for name, cfg in providers.items():

            if not isinstance(cfg, dict):
                continue

            meta[name] = {
                "label": cfg.get("label") or name,
                "icon": cfg.get("icon") or "",
                "description": cfg.get("description") or "",
            }

        return meta

    def provider_command(self, name):
        """Return the launch command for a provider.

        Falls back to the provider name itself (assumed to be on PATH).
        Supports a `command` field (e.g. `npx pi`) for providers whose
        executable is not directly on PATH.
        """

        providers = (
            self.provider_config
            .get("providers", {})
        )

        cfg = providers.get(name)

        if not isinstance(cfg, dict):
            return name

        return cfg.get("command") or name

    def skill_groups(self):
        """Return the configured skill group definitions (ordered)."""

        groups = (
            self.skill_groups_config
            .get("groups", [])
        )

        if not isinstance(groups, list):
            return []

        return groups

    def skill_group_title(self, key):
        """Resolve a skill-group title key via i18n."""

        return self.t(
            f"sections.{key}",
            key
        )

    def skill_tasks(self):
        """Return the task-preset config: [{title, items: [...]}].

        Falls back to an empty list when unset.
        """

        tasks = (
            self.skill_groups_config
            .get("tasks", [])
        )

        if not isinstance(tasks, list):
            return []

        return tasks

    def combo_task(self, skill_names):
        """Return the default task template for a list-combo group whose
        skills all appear in skill_names (or the first matching group).

        Returns "" when no list group matches.
        """

        for group in self.skill_groups():

            if group.get("type") != "list":
                continue

            names = set(group.get("skills") or [])

            if names and names.issubset(skill_names):

                return group.get("task") or ""

        return ""

    def default_provider(self):

        return (
            self.provider_config
            .get("default", {})
            .get("provider")
        )

    def sections(self):

        return self.get("sections")
