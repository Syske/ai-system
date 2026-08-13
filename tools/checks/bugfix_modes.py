"""bugfix-modes.yaml availability gate (check.py item 15).

Ensures every configured bugfix mode is actually usable:

- config/workflows/bugfix-modes.yaml is valid YAML with the required keys
- each mode's phases reference known phase names
- branch.template placeholders are all known ({date}/{type}/{desc}/{service})
- branch.parser (if set) resolves to an existing provider script that
  implements the contract (script name / method / return fields)
- default mode is registered

Contract owner: templates/runtime/runtime-bugfix.md Phase 4.6.
Provider scaffold: tools/branch-parser-scaffold.py.
"""

import importlib.util
import inspect
import re
from pathlib import Path

from .base import ROOT, load_yaml

CONFIG = ROOT / "config" / "workflows" / "bugfix-modes.yaml"

# 已知阶段：新增阶段必须同步登记到这里（与 config 文件头注释一致）。
KNOWN_PHASES = {
    "analysis", "reproduce", "root-cause", "plan",
    "branch", "implement", "regress", "commit", "verify", "doc",
    "report",
}

KNOWN_PLACEHOLDERS = {"date", "type", "desc", "service"}

# 契约：与 templates/runtime/runtime-bugfix.md Phase 4.6 保持一致。
CONTRACT_SCRIPT = "branch_parser.py"
CONTRACT_METHOD = "parse"
CONTRACT_PARAM = "branch_name"
CONTRACT_FIELDS = {"date", "type", "desc", "service"}


def check_bugfix_modes(c):
    cfg = load_yaml(CONFIG)

    if "__error__" in cfg:
        c.error(f"{CONFIG.name} invalid: {cfg['__error__']}")
        return

    if "modes" not in cfg or not isinstance(cfg["modes"], dict):
        c.error(f"{CONFIG.name}: missing 'modes' mapping")
        return

    default = cfg.get("default")
    if default not in cfg["modes"]:
        c.error(f"{CONFIG.name}: default '{default}' not in modes")

    for name, mode in cfg["modes"].items():

        if not isinstance(mode, dict):
            c.error(f"{CONFIG.name} [{name}]: mode must be a mapping")
            continue

        # 1. phases 引用已知阶段
        phases = mode.get("phases", [])
        if not isinstance(phases, list):
            c.error(f"{CONFIG.name} [{name}]: 'phases' must be a list")
        else:
            unknown = [p for p in phases if p not in KNOWN_PHASES]
            if unknown:
                c.error(
                    f"{CONFIG.name} [{name}]: unknown phases "
                    f"{sorted(unknown)} (known: "
                    f"{sorted(KNOWN_PHASES)})"
                )

        # 2. branch.template 占位符合法
        branch = mode.get("branch", {})
        tmpl = branch.get("template", "") if isinstance(branch, dict) else ""
        if tmpl:
            used = set(re.findall(r"\{(\w+)\}", tmpl))
            unknown_ph = used - KNOWN_PLACEHOLDERS
            if unknown_ph:
                c.error(
                    f"{CONFIG.name} [{name}]: unknown template "
                    f"placeholders {sorted(unknown_ph)} (known: "
                    f"{sorted(KNOWN_PLACEHOLDERS)})"
                )

        # 3. parser 解析可用（若配置）
        parser = branch.get("parser") if isinstance(branch, dict) else None
        if parser:
            resolved = _resolve_parser(parser)
            if resolved is None:
                c.error(
                    f"{CONFIG.name} [{name}]: parser '{parser}' "
                    "does not resolve to an existing "
                    f"extensions/<name>/scripts/{CONTRACT_SCRIPT}"
                )
            else:
                _check_parser_contract(c, name, parser, resolved)


def _resolve_parser(parser: str):
    """Resolve a logical parser name to its script path.

    Contract (extensions/README.md): providers register a parser by placing
    branch_parser.py in extensions/<name>/scripts/.
    """
    ext_root = ROOT.parent / "extensions"
    if not ext_root.is_dir():
        return None
    for ext_dir in sorted(ext_root.iterdir()):
        if not ext_dir.is_dir():
            continue
        # 解析规则：目录名 = 逻辑名，或其 scripts/ 下声明归属。
        script = ext_dir / "scripts" / CONTRACT_SCRIPT
        if script.is_file() and ext_dir.name == parser:
            return script
    return None


def _check_parser_contract(c, name, parser, script: Path):
    """Load the provider script and verify the contract signature."""

    spec = importlib.util.spec_from_file_location(
        f"branch_parser_{parser}", script
    )
    if spec is None or spec.loader is None:
        c.error(f"{CONFIG.name} [{name}]: cannot load parser '{parser}'")
        return
    mod = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(mod)
    except Exception as exc:
        c.error(
            f"{CONFIG.name} [{name}]: parser '{parser}' "
            f"failed to import: {exc}"
        )
        return

    if not hasattr(mod, CONTRACT_METHOD):
        c.error(
            f"{CONFIG.name} [{name}]: parser '{parser}' missing "
            f"method '{CONTRACT_METHOD}()'"
        )
        return

    sig = inspect.signature(getattr(mod, CONTRACT_METHOD))
    params = list(sig.parameters)
    if params != [CONTRACT_PARAM]:
        c.error(
            f"{CONFIG.name} [{name}]: parser '{parser}' signature "
            f"must be {CONTRACT_METHOD}({CONTRACT_PARAM}) -> "
            f"ParsedBranch | None, got {params}"
        )
        return

    probe = getattr(mod, CONTRACT_METHOD)("__contract_probe__")
    if probe is None:
        return  # 合法：无法解析返回 None

    fields = set(getattr(probe, "__dataclass_fields__", {}))
    if fields != CONTRACT_FIELDS:
        c.error(
            f"{CONFIG.name} [{name}]: parser '{parser}' return "
            f"fields {sorted(fields)} != contract "
            f"{sorted(CONTRACT_FIELDS)}"
        )
