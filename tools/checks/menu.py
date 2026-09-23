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

        # 保存原值，finally 恢复：dry-run 不得污染同进程后续检查
        # 仅保存**实际存在**的属性（selection 只有 choose，无 choose_many）
        _saved = [
            (m, attr, getattr(m, attr))
            for m in (_wsel, _wfields, _wout)
            for attr in ("choose", "choose_many")
            if hasattr(m, attr)
        ]

        try:
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

        finally:
            for _mod, _attr, _orig in _saved:
                setattr(_mod, _attr, _orig)

    except Exception as exc:
        c.error(f"wizard dry-run failed: {exc!r}")


def check_hidden_registry(c):
    """`hidden_workflows` / `hidden_commands` 的每条必须指向**存在**的目标（R4）。

    原实现完全不校验：删除/重命名工作流后，`hidden_*` 里会留下**悬空条目**
    （既不报错也不生效），隐藏机制静默失效。
    """

    import re

    from .base import ROOT, load_yaml

    menu = load_yaml(ROOT / "config" / "menu.yaml") or {}

    if "__error__" in menu:
        return          # 语法错误已由 config_yaml 检查报出

    known_workflows = {p.stem for p in (ROOT / "workflows").glob("*.md")} - {"README"}

    known_commands = {
        p.name[len("aic-"):-len(".md")]
        for p in (ROOT / "cli" / "commands").glob("aic-*.md")
    }

    for key, known, label in (
        ("hidden_workflows", known_workflows, "workflow"),
        ("hidden_commands", known_commands, "command"),
    ):

        entries = menu.get(key) or []

        if not isinstance(entries, list):
            c.error(f"config/menu.yaml: {key} 必须是列表")
            continue

        for entry in entries:

            name = re.sub(r"\s*#.*$", "", str(entry)).strip()

            if name and name not in known:

                c.error(
                    f"config/menu.yaml: {key} 含悬空条目 '{name}'"
                    f"（无此 {label}）"
                )
