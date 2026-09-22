"""Config YAML integrity — every `config/**/*.yaml` must parse and be a mapping.

Fail-loud follow-through of the P60 principle (2026-09-21): a hand edit inside a
YAML block scalar (`- **…` — the leading dash turned `*` into an alias) broke
`config/maintenance.yaml`, yet `check.py` still reported PASS with exit 0, i.e. a
malformed config file was **committable with no gate signal**. Declarative
configuration is an input to nearly every runtime, so a silent parse failure is
the worst possible failure mode: the runtime falls back to defaults and the
mistake surfaces much later.

This module deliberately does NOT reuse `base.load_yaml`, which swallows parse
errors into `{"__error__": …}`; here a broken document is an ERROR carrying
file/line/column so the report is actionable.
"""

from pathlib import Path

import yaml

from .base import ROOT

CONFIG_ROOT = ROOT / "config"


def strict_load(path):
    """Parse one YAML file strictly.

    Returns `(data, error)` — exactly one of them is meaningful: `error` is a
    human-readable message (with line/column when available) or None.
    """
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        return None, f"unreadable: {exc}"

    try:
        return yaml.safe_load(text), None
    except yaml.YAMLError as exc:
        mark = getattr(exc, "problem_mark", None)
        where = f" at line {mark.line + 1}, column {mark.column + 1}" if mark else ""
        problem = getattr(exc, "problem", None) or exc.__class__.__name__
        return None, f"YAML parse error{where}: {problem}"


def check_config_yaml(c):
    """Validate every YAML document under `config/`."""

    if not CONFIG_ROOT.exists():
        c.error("config/ directory not found — config YAML cannot be validated")
        return

    files = sorted(CONFIG_ROOT.rglob("*.yaml")) + sorted(CONFIG_ROOT.rglob("*.yml"))

    if not files:
        c.warn("config/ holds no YAML files — nothing validated")
        return

    for path in files:
        try:
            rel = path.relative_to(ROOT).as_posix()
        except ValueError:
            # 路径不在仓根之下（符号链接 / 测试注入的临时根）：门禁必须继续报告，
            # 不得崩溃——"输入异常"是 ERROR 语义，不是异常语义（P60 fail-loud）。
            rel = str(path)

        data, error = strict_load(path)

        if error:
            c.error(f"{rel}: {error}")
        elif data is None:
            c.warn(f"{rel}: empty YAML document")
        elif not isinstance(data, dict):
            c.error(
                f"{rel}: top level must be a mapping, got {type(data).__name__}"
            )