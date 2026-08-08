"""Wizard mixin: config access helpers (thin passthroughs to MenuConfig)."""


class WizardConfigAccess:
    """Thin passthroughs to MenuConfig — split from wizard.py (P0)."""

    def _t(self, path, default=None):

        return self.config.t(path, default)

    def _menu(self, key, default=None):

        return self.config.get(key, default)

    def _command_fields(self, name):

        return self.config.command_fields(name)

    def _field_icon(self, field):

        return self.config.field_icon(field)

    def _field_note(self, field):

        return self.config.field_note(field)

    def _field_choices(self, field):

        return self.config.field_choices(field)

    def _option_descriptions(self, field):

        return self.config.option_descriptions(field)

    def _command_next(self, name):

        return self.config.command_next(name)

    def _auto_fields(self):

        return self.config.auto_fields()

    def _multi_select_fields(self):

        return self.config.multi_select_fields()

    def _menu_option(self, menu, key):

        return self.config.menu_option(menu, key)
