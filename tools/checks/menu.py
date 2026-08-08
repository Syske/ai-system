"""Menu / i18n / wizard integrity checks."""

from .base import ROOT, load_yaml


def check_menu(c, workflows, commands):
    menu = load_yaml(ROOT / "config" / "menu.yaml")

    if "__error__" in menu:
        c.error(f"config/menu.yaml invalid: {menu['__error__']}")
        return

    locale = menu.get("locale", "zh")

    i18n = load_yaml(ROOT / "config" / "i18n" / f"{locale}.yaml")

    if "__error__" in i18n:
        c.error(
            f"config/i18n/{locale}.yaml missing or invalid"
        )
        return

    i18n_sections = i18n.get("sections", {})

    seen = set()

    for sec in menu.get("sections", []):

        title_key = sec.get("title", "")

        if not title_key:
            c.error("config/menu.yaml: section missing title")

        elif title_key not in i18n_sections:
            c.error(
                f"config/menu.yaml section key "
                f"'{title_key}' not defined in "
                f"config/i18n/{locale}.yaml"
            )

        for item in sec.get("items") or []:

            name = item.get("name")
            kind = item.get("kind")

            if not name or kind not in ("workflow", "command"):
                c.error(
                    f"config/menu.yaml [{title_key}]: "
                    f"item missing name/kind: {item}"
                )
                continue

            key = (name, kind)

            if key in seen:
                c.error(
                    f"config/menu.yaml [{title_key}]: "
                    f"duplicate {kind} {name}"
                )

            seen.add(key)

            if kind == "workflow" and name not in workflows:
                c.error(
                    f"config/menu.yaml [{title_key}]: "
                    f"workflow '{name}' not in workflow-registry.yaml"
                )

            if kind == "command" and name not in commands:
                c.error(
                    f"config/menu.yaml [{title_key}]: "
                    f"command '{name}' has no cli/commands/aic-{name}.md"
                )

            if not item.get("icon", ""):
                c.warn(
                    f"config/menu.yaml [{title_key}]: "
                    f"{name} has no icon"
                )

    for key in ("command_fields", "command_next"):

        for name in menu.get(key, {}):

            if name not in commands:
                c.error(
                    f"config/menu.yaml {key}: "
                    f"'{name}' has no command file"
                )


def check_wizard_dry_run(c, workflows, commands):
    try:
        import cli.utils.menu as menu
        from cli.services.wizard import Wizard

        def fake_choose(
            title,
            options,
            default=0,
            allow_skip=False,
            header=None,
            note=None
        ):
            for i, opt in enumerate(options):
                if not isinstance(opt, menu.Section):
                    return i
            return 0

        # Patch the consumer module globals that wizard selection/fields
        # bind at import time (from cli.utils.menu import ... choose).
        # Patching select.choose or the package re-export does NOT affect
        # these bound names — the consumers must be patched directly.
        import cli.services.wizard.selection as _wsel
        import cli.services.wizard.fields as _wfields
        import cli.services.wizard.output as _wout

        for _mod in (_wsel, _wfields, _wout):
            _mod.choose = fake_choose
            _mod.choose_many = lambda *a, **k: None

        w = Wizard(ROOT)
        w._recommend_workflow = lambda project, ws: None

        target = w._select_target([], None)

        if target is None:
            c.error("wizard menu dry-run returned no target")

        for name in commands:
            try:
                w._fields_for((name, "command"))
            except Exception as exc:
                c.error(
                    f"command '{name}' fields fail: {exc!r}"
                )

    except Exception as exc:
        c.error(f"wizard dry-run failed: {exc!r}")
