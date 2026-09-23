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
import typing
from pathlib import Path

from .base import ROOT, load_yaml

CONFIG = ROOT / "config" / "workflows" / "bugfix-modes.yaml"

# 已知阶段：新增阶段必须同步登记到这里（与 config 文件头注释一致）。
# R4：以配置为权威 —— 阶段集从 `config/workflows/bugfix-modes.yaml` 的
# `phases` 反读（并集）；下列常量仅作配置不可用时的回退（避免"改配置忘了改代码"）。
KNOWN_PHASES_FALLBACK = {
    "analysis", "reproduce", "root-cause", "plan",
    "branch", "implement", "regress", "commit", "verify", "doc",
    "report", "mr",
}


def known_phases():
    """返回配置中出现的全部阶段（并集）；配置不可用时回退常量。"""

    from .base import ROOT, load_yaml

    config = load_yaml(ROOT / "config" / "workflows" / "bugfix-modes.yaml") or {}

    phases = set()

    def collect(node):

        if isinstance(node, dict):
            for key, value in node.items():
                if key == "phases" and isinstance(value, list):
                    phases.update(str(v) for v in value)
                else:
                    collect(value)
        elif isinstance(node, list):
            for item in node:
                collect(item)

    collect(config)

    return phases or set(KNOWN_PHASES_FALLBACK)


KNOWN_PHASES = known_phases()

KNOWN_PLACEHOLDERS = {"date", "type", "desc", "service"}

# 契约：与 templates/runtime/runtime-bugfix.md Phase 4.6/6.6 保持一致。
CONTRACT_SCRIPT = "branch_parser.py"
CONTRACT_METHOD = "parse"
CONTRACT_PARAM = "branch_name"
CONTRACT_FIELDS = {"date", "type", "desc", "service"}

# MR provider 契约（templates/runtime/runtime-bugfix.md Phase 6.6）。
MR_SCRIPT = "submit_mr.py"
MR_METHOD = "submit"
MR_PARAMS = ["source_branch", "target_branch", "title", "description"]
MR_FIELDS = {"url", "id"}


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
                if _extensions_available():
                    c.error(
                        f"{CONFIG.name} [{name}]: parser '{parser}' "
                        "does not resolve to an existing "
                        f"extensions/<name>/scripts/{CONTRACT_SCRIPT}"
                    )
                else:
                    c.warn(
                        f"{CONFIG.name} [{name}]: parser '{parser}' not "
                        f"verified — extensions/ unavailable (CI/env "
                        "without the extensions repo); run extensions-init "
                        "to provision"
                    )
            else:
                _check_parser_contract(c, name, parser, resolved)

        # 4. mr.provider 解析可用（若配置）
        mr = mode.get("mr", {})
        provider = mr.get("provider") if isinstance(mr, dict) else None
        if provider:
            script = _resolve_mr_provider(provider)
            if script is None:
                if _extensions_available():
                    c.error(
                        f"{CONFIG.name} [{name}]: mr.provider '{provider}' "
                        "does not resolve to an existing "
                        f"extensions/<name>/scripts/{MR_SCRIPT}"
                    )
                else:
                    c.warn(
                        f"{CONFIG.name} [{name}]: mr.provider '{provider}' "
                        f"not verified — extensions/ unavailable (CI/env "
                        "without the extensions repo); run extensions-init "
                        "to provision"
                    )
            else:
                _check_mr_contract(c, name, provider, script)

        # 5. mr 阶段依赖校验：phases 含 mr 必须有 mr.provider
        if "mr" in phases and not provider:
            c.warn(
                f"{CONFIG.name} [{name}]: phases contains 'mr' "
                "but no mr.provider configured"
            )


def _extensions_available() -> bool:
    """True when the extensions repo (sibling of ai-system) is present.

    extensions/ is a SEPARATE repository (e.g. Codeup). CI checkouts of
    ai-system alone do not include it — provider contract verification is
    then degraded to a warning, not an error (the extension is an optional
    runtime provider, provisioned by extensions-init).
    """
    return (ROOT.parent / "extensions").is_dir()


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


def _resolve_mr_provider(provider: str):
    """Resolve a logical MR provider name to its script path.

    Contract: providers register by placing submit_mr.py in
    extensions/<name>/scripts/.
    """
    ext_root = ROOT.parent / "extensions"
    if not ext_root.is_dir():
        return None
    for ext_dir in sorted(ext_root.iterdir()):
        if not ext_dir.is_dir():
            continue
        script = ext_dir / "scripts" / MR_SCRIPT
        if script.is_file() and ext_dir.name == provider:
            return script
    return None


def _return_dataclasses(func, mod):
    """静态解析 func 的返回注解 → 非 None 的候选类型（无法解析返回 []）。"""

    try:
        hints = typing.get_type_hints(func, vars(mod))
    except Exception:                       # noqa: BLE001
        return []

    ret = hints.get("return")

    if ret is None:
        return []

    candidates = typing.get_args(ret) or [ret]

    return [t for t in candidates if t is not type(None)]


def _check_return_contract(c, name, label, func, expected_fields, mod):
    """静态校验返回类型（**不执行** provider 代码）。

    2026-09-21 外部盲检 T5：原实现以 `"__contract_probe__"` 调**活探针**——
    ① 该输入任何 parser/MR provider 都解析不出 → 恒返回 None → 字段校验成为
       **死代码**（fail-open：契约从未被验证）；
    ② 门禁期间**执行** provider 代码（MR provider 可能真的发起建 MR 调用）。
    改为静态解析返回注解：能解析则校验字段；无法解析 → WARN（失效必须响亮，P60）。
    """

    candidates = _return_dataclasses(func, mod)

    if not candidates:
        c.warn(
            f"{CONFIG.name} [{name}]: {label} return annotation "
            f"missing/unresolvable -> contract fields NOT verified "
            f"(annotate the return as '-> X | None')"
        )
        return

    for t in candidates:
        fields = set(getattr(t, "__dataclass_fields__", {}))
        if fields != expected_fields:
            c.error(
                f"{CONFIG.name} [{name}]: {label} return "
                f"fields {sorted(fields)} != contract {sorted(expected_fields)}"
            )
            return


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

    _check_return_contract(
        c, name, f"parser '{parser}'",
        getattr(mod, CONTRACT_METHOD), CONTRACT_FIELDS, mod,
    )


def _check_mr_contract(c, name, provider, script: Path):
    """Load the provider script and verify the MR contract signature."""

    spec = importlib.util.spec_from_file_location(
        f"submit_mr_{provider}", script
    )
    if spec is None or spec.loader is None:
        c.error(f"{CONFIG.name} [{name}]: cannot load mr provider '{provider}'")
        return
    mod = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(mod)
    except Exception as exc:
        c.error(
            f"{CONFIG.name} [{name}]: mr provider '{provider}' "
            f"failed to import: {exc}"
        )
        return

    if not hasattr(mod, MR_METHOD):
        c.error(
            f"{CONFIG.name} [{name}]: mr provider '{provider}' "
            f"missing method '{MR_METHOD}()'"
        )
        return

    sig = inspect.signature(getattr(mod, MR_METHOD))
    params = list(sig.parameters)
    if params != MR_PARAMS:
        c.error(
            f"{CONFIG.name} [{name}]: mr provider '{provider}' signature "
            f"must be {MR_METHOD}({', '.join(MR_PARAMS)}) "
            f"-> MrResult | None, got {params}"
        )
        return

    _check_return_contract(
        c, name, f"mr provider '{provider}'",
        getattr(mod, MR_METHOD), MR_FIELDS, mod,
    )
