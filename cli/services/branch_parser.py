"""Main-chain branch parser (provider contract).

Contract (mirrors the bugfix branch.parser contract in
templates/runtime/runtime-bugfix.md Phase 4.6):

  method:    parse(branch_name: str) -> ParsedBranch | None
  fields:    ParsedBranch = {date, type, desc, service}  (all str, "" when absent)
  behavior:  blank / unparseable -> return None (never raise)

Main-chain branch format — **preset-based, machine-assembled** (P63, 2026-09-23):

  The format is NOT hand-written. `PRESETS` holds the only legal formats; the AI
  assembles the concrete branch name from a preset after the user describes the
  requirement, and the user confirms the CONCRETE NAME (never a format string).

    plain : cc{date}_{desc}_{service}        <- default (non-iteration requirements)
    ipd   : cc{date}_ipd_{desc}_{service}    <- requirement rides an iteration (TR)

  Format strings supplied by hand (`cc{date}_x_{desc}`) are **rejected**: `parse()`
  recognizes the presets only, so they return None. An org-specific format stays
  possible through a provider under `extensions/<name>/scripts/branch_parser.py`
  (config: `branch.parser` logic name, code-reviewed path) — this module is the
  ai-system default inline implementation.

  Segment classes are fixed (`{date}` = 8 digits, `{desc}` / `{service}` =
  `[a-z0-9-]+`, i.e. **no underscore**): that is what makes the name deterministic
  to split. History: a service with an underscore (`qa_manage`) could not be parsed,
  forcing the hyphenated alias `qa-manage`.

The branch name is decided at requirement-confirmation time and frozen afterwards
(immutable; no rename, no `project-context.branches` edit) — the only exception is
a newly added project, with explicit authorization.
"""

import re
from dataclasses import dataclass
from pathlib import Path

# 段字符类：`{date}` 8 位数字；`{desc}`/`{service}` 小写字母/数字/连字符，**不含下划线**。
# 不含下划线是「可确定性切分」的前提（P63 §1.2.3 陷阱）。
_PLACEHOLDER_CLASSES = {
    "date": r"\d{8}",
    "desc": r"[a-z0-9-]+",
    "service": r"[a-z0-9-]+",
}

# 预制形态（preset）：唯一合法的分支格式来源。
# type 段：模板里的字面量标记（plain 无标记 → ""），即 ParsedBranch.type 的取值。
PRESETS: dict[str, dict[str, str]] = {
    "plain": {"template": "cc{date}_{desc}_{service}", "type": ""},
    "ipd": {"template": "cc{date}_ipd_{desc}_{service}", "type": "ipd"},
}
DEFAULT_PRESET = "plain"


def _compile_preset(name: str) -> re.Pattern:
    """把预设模板编译为正则；相邻占位符（无法确定性切分）→ 直接报错。"""

    template = PRESETS[name]["template"]
    tokens = re.split(r"(\{date\}|\{desc\}|\{service\})", template)
    parts: list[str] = []
    prev_placeholder = False

    for token in tokens:
        key = token[1:-1] if token.startswith("{") else ""
        if key in _PLACEHOLDER_CLASSES:
            if prev_placeholder:
                raise ValueError(
                    f"preset '{name}': 相邻占位符无法确定性切分（模板 {template}）"
                )
            parts.append(f"(?P<{key}>{_PLACEHOLDER_CLASSES[key]})")
            prev_placeholder = True
        else:
            if token:
                parts.append(re.escape(token))
            prev_placeholder = False

    return re.compile("^" + "".join(parts) + "$")


_COMPILED: dict[str, re.Pattern] = {name: _compile_preset(name) for name in PRESETS}


@dataclass
class ParsedBranch:
    date: str = ""      # YYYYMMDD
    type: str = ""      # "ipd" for the ipd preset, "" for plain
    desc: str = ""
    service: str = ""


def parse(branch_name: str, preset: str | None = None) -> ParsedBranch | None:
    """Parse a main-chain branch name. Returns None when unparseable (never raises).

    `preset=None` tries every preset (they are distinguishable — plain has one
    literal segment less); pass a preset name to require that specific form.
    Hand-written format strings are not recognized → None.
    """

    if not isinstance(branch_name, str) or not branch_name.strip():
        return None

    name = branch_name.strip()
    candidates = [preset] if preset else list(PRESETS)

    for key in candidates:
        pattern = _COMPILED.get(key)
        if pattern is None:
            return None
        m = pattern.match(name)
        if m:
            g = m.groupdict()
            return ParsedBranch(
                date=g["date"],
                type=PRESETS[key]["type"],
                desc=g["desc"],
                service=g["service"],
            )
    return None


def render(preset: str, date: str, desc: str, service: str = "") -> str:
    """Assemble a branch name from a preset. Output is guaranteed parseable.

    Unknown preset / malformed segment → ValueError (fail loud): the format comes
    from the preset, never from a hand-written template.
    """

    spec = PRESETS.get(preset)
    if spec is None:
        raise ValueError(
            f"未知分支预设 '{preset}'；合法值: {sorted(PRESETS)}（格式串不可手写）"
        )

    values = {"date": date, "desc": desc, "service": service}
    for key, value in values.items():
        if not re.fullmatch(_PLACEHOLDER_CLASSES[key], str(value or "")):
            raise ValueError(
                f"分支 {preset} 的 {{{key}}} 段非法: {value!r}"
                f"（要求 {_PLACEHOLDER_CLASSES[key]}）"
            )

    out = spec["template"]
    for key, value in values.items():
        out = out.replace("{" + key + "}", value)
    return out


def preset_for_scenario(scenario: str, mapping: dict | None = None) -> str | None:
    """场景 → 预设（读 `config/branch-formats.yaml`，单一来源，可配置）。

    调整「某场景默认用哪种形态」= 改那个配置文件，**不是**改代码、更不是写正则。

    返回 None 表示该场景**不归主链预设管**（如 bugfix → extensions provider），
    调用方应转向 provider 解析；不要在那种场景下调 render（会 fail loud）。
    """

    if mapping is None:
        mapping = _load_branch_formats()

    scenarios = mapping.get("scenarios") or {}
    value = scenarios.get(scenario)
    if value is None:
        return None if scenario in scenarios else mapping.get("default_preset") or DEFAULT_PRESET

    name = str(value).strip()
    if not name:
        return None
    if name not in PRESETS:
        raise ValueError(
            f"场景 '{scenario}' 映射到未知预设 '{name}'；"
            f"合法值: {sorted(PRESETS)}（格式串不可手写）"
        )
    return name


def _load_branch_formats() -> dict:
    """读 `config/branch-formats.yaml`；不可用则回退默认（不抛异常）。"""

    try:
        import yaml  # 局部导入：无配置环境（如 provider 单独跑）不应因此失败

        config = Path(__file__).resolve().parents[2] / "config" / "branch-formats.yaml"
        return yaml.safe_load(config.read_text(encoding="utf-8")) or {}
    except Exception:
        return {}


