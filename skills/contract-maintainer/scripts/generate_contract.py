#!/usr/bin/env python3
"""
generate_contract.py — 基于 Spec YAML 块 + switch_scenarios.yml 生成 interop_contract.yml

用法:
  python generate_contract.py \\
      --spec-dir specs/ \\
      --switch specs/switch_scenarios.yml \\
      --manual contracts/contract_manual.yml \\
      --output contracts/interop_contract.yml
"""
import argparse
import re
import sys
import yaml
import textwrap
from datetime import datetime
from pathlib import Path
from typing import Any


MANUAL_REQUIRED_FIELDS = {"id", "调用方", "被调用方", "类型", "接口/主题"}
SCENARIO_REQUIRED_FIELDS = {"id", "service"}


def parse_spec_yaml_blocks(spec_dir: str) -> list[dict]:
    """从 Spec Markdown 文件中提取所有 YAML 代码块，携带 _source 和 _fields"""
    interactions = []
    spec_dir = Path(spec_dir)
    for md_file in sorted(spec_dir.rglob("*.md")):
        content = md_file.read_text(encoding="utf-8")
        blocks = re.findall(r"```yaml\n(.*?)\n```", content, re.DOTALL)
        for block in blocks:
            try:
                data = yaml.safe_load(block)
                if data:
                    if "rpc" in data:
                        for rpc in data["rpc"]:
                            rpc["_source"] = str(md_file.relative_to(spec_dir.parent))
                            if "request" in rpc and isinstance(rpc["request"], dict):
                                rpc["_fields"] = list(rpc["request"].keys())
                            interactions.append(rpc)
                    if "mq" in data:
                        for mq in data["mq"]:
                            mq["_source"] = str(md_file.relative_to(spec_dir.parent))
                            if "schema" in mq and isinstance(mq["schema"], dict):
                                mq["_fields"] = list(mq["schema"].keys())
                            interactions.append(mq)
            except yaml.YAMLError:
                pass
    return interactions


def load_yaml(path: str) -> dict:
    p = Path(path)
    if not p.exists():
        print(f"[WARN] 文件不存在，按空数据继续: {path}")
        return {}
    return yaml.safe_load(p.read_text(encoding="utf-8")) or {}


def build_rpc_entry(rpc: dict) -> dict:
    return {
        "id": f"{rpc['caller']}-{rpc['callee']}-{rpc['name']}",
        "调用方": rpc["caller"],
        "被调用方": rpc["callee"],
        "类型": "RPC",
        "协议": rpc.get("protocol", "SOFA RPC"),
        "接口/主题": rpc["name"],
        "description": rpc.get("description", ""),
        "_source": rpc.get("_source", ""),
        "_fields": rpc.get("_fields", []),
    }


def build_mq_entry(mq: dict) -> dict:
    return {
        "id": f"{mq.get('producer','')}-{mq.get('consumer','')}-{mq['topic']}",
        "调用方": mq.get("consumer", ""),
        "被调用方": mq.get("producer", ""),
        "类型": "MQ",
        "协议": "RocketMQ",
        "接口/主题": mq["topic"],
        "description": mq.get("description", ""),
        "_source": mq.get("_source", ""),
        "_fields": mq.get("_fields", []),
    }


def build_scenario_entry(sc: dict) -> dict:
    return {
        "id": f"{sc['id']}-contract",
        "场景引用": sc["id"],
        "服务": sc.get("service", ""),
        "类型": _infer_type(sc),
        "description": sc.get("description", ""),
        "触发条件": sc.get("trigger", ""),
        "切库规则": sc.get("source_of_enterprise_id", ""),
        "异常处理": sc.get("error_handling", ""),
        "_source": f"switch_scenarios.yml/{sc['id']}",
    }


def _infer_type(sc: dict) -> str:
    trigger = sc.get("trigger", "")
    if "MQ" in trigger or "Topic" in trigger:
        return "MQ"
    return "Internal"


def cross_validate(spec_entries: list[dict], scenario_entries: list[dict]) -> list[str]:
    """交叉校验 Spec 与场景清单的一致性（仅警告，不阻断）"""
    warnings = []

    scenario_ids = {s["场景引用"] for s in scenario_entries}

    for se in scenario_entries:
        matched = False
        for spec_e in spec_entries:
            svc = se.get("服务", "")
            trigger = se.get("触发条件", "")
            if svc and (svc in spec_e.get("调用方", "") or svc in spec_e.get("被调用方", "")):
                matched = True
                break
            if trigger and trigger in spec_e.get("接口/主题", ""):
                matched = True
                break
        if not matched:
            warnings.append(
                f"[WARN] 场景 {se['场景引用']} 未能在 Spec YAML 块中找到匹配交互，可能已过期"
            )

    for spec_e in spec_entries:
        name = spec_e.get("name", spec_e.get("接口/主题", ""))
        caller = spec_e.get("调用方", "")
        callee = spec_e.get("被调用方", "")
        found = False
        for se in scenario_entries:
            svc = se.get("服务", "")
            if svc and (svc == caller or svc == callee):
                found = True
                break
        if not found:
            warnings.append(
                f"[WARN] Spec 交互 {name}({caller}→{callee}) 在 switch_scenarios.yml 中无对应场景"
            )

    return warnings


def validate_fields(spec_entries: list[dict], scenario_entries: list[dict]) -> list[str]:
    """校验切库字段在对应 Spec 的 request/schema 中存在，不存在则阻断

    仅在 Spec YAML 块包含 request/schema（即有 _fields）时才做字段级校验。
    若 Spec 中有交互但无 _fields（手动条目或初始阶段），标记为 WARN 而非 ERROR。
    """
    errors = []
    for se in scenario_entries:
        enterprise_field = se.get("切库规则", "")
        if not enterprise_field:
            continue
        svc = se.get("服务", "")
        matched_any = False     # 找到至少一个匹配的交互
        checked_field = False   # 至少检查了一个 _fields
        for spec in spec_entries:
            if not (spec.get("调用方") == svc or spec.get("被调用方") == svc):
                continue
            matched_any = True
            available = spec.get("_fields", [])
            if not available:
                continue
            checked_field = True
            if enterprise_field not in available:
                errors.append(
                    f"[ERROR] 场景 {se['场景引用']} 的切库规则 '{enterprise_field}' "
                    f"不在 {spec['接口/主题']} 的请求/Schema 字段中 "
                    f"(可用: {available})"
                )
        if not matched_any:
            continue  # 无匹配交互时跳过（WARN 已在 cross_validate 中给出）
        if matched_any and not checked_field:
            # 有匹配交互但均无 _fields（手动条目无 request/schema），仅 WARN
            print(f"[WARN] 场景 {se['场景引用']} 的匹配交互均无 _fields，跳过字段校验")
    return errors


def validate_manual_entry(entry: dict, index: int) -> list[str]:
    """校验单条手动条目的格式"""
    errors = []
    for field in MANUAL_REQUIRED_FIELDS:
        if field not in entry or not entry[field]:
            errors.append(f"[ERROR] 手动条目 #{index} 缺少必填字段 '{field}'")
    eid = entry.get("id", f"#unknown-{index}")
    etype = entry.get("类型", "")
    if etype not in ("RPC", "MQ", "Internal"):
        errors.append(f"[ERROR] 手动条目 [{eid}] 类型 '{etype}' 无效 (须为 RPC/MQ/Internal)")
    return errors


def validate_manual_entries(entries: list[dict]) -> list[str]:
    """校验所有手动条目"""
    errors = []
    for i, entry in enumerate(entries):
        errors.extend(validate_manual_entry(entry, i))
    return errors


def validate_scenario_entry(sc: dict, index: int) -> list[str]:
    """校验单条场景条目的格式"""
    errors = []
    for field in SCENARIO_REQUIRED_FIELDS:
        if field not in sc or not sc[field]:
            errors.append(f"[ERROR] 场景 #{index} 缺少必填字段 '{field}'")
    return errors


def validate_scenario_entries(entries: list[dict]) -> list[str]:
    errors = []
    for i, sc in enumerate(entries):
        errors.extend(validate_scenario_entry(sc, i))
    return errors


def format_entry_yaml(entry: dict) -> str:
    """格式化单条契约为 YAML 字符串，注入 description 为注释"""
    parts = [f"  - id: {entry['id']}"]
    if entry.get("description"):
        for line in textwrap.wrap(entry["description"], width=72):
            parts.append(f"    # {line}")
    for key in ["场景引用", "调用方", "被调用方", "类型", "协议", "接口/主题"]:
        if key in entry and entry[key]:
            parts.append(f"    {key}: {entry[key]}")
    for key in ["触发条件", "切库规则", "异常处理"]:
        val = entry.get(key, "")
        if not val:
            continue
        if "\n" in val:
            lines = val.split("\n")
            parts.append(f"    {key}: |")
            for l in lines:
                parts.append(f"      {l.strip()}")
        else:
            parts.append(f"    {key}: {val}")
    parts.append("")
    return "\n".join(parts)


def deduplicate(entries: list[dict]) -> list[dict]:
    seen: set[str] = set()
    result: list[dict] = []
    for e in entries:
        eid = e["id"]
        if eid in seen:
            continue
        seen.add(eid)
        result.append(e)
    return result


def generate(args: argparse.Namespace):
    spec_dir = args.spec_dir
    switch_path = args.switch
    manual_path = args.manual
    output_path = args.output

    has_error = False

    # 1. 解析 Spec YAML 块
    spec_data = parse_spec_yaml_blocks(spec_dir)
    auto_entries: list[dict] = []
    for item in spec_data:
        if "caller" in item and "callee" in item:
            auto_entries.append(build_rpc_entry(item))
        elif "topic" in item:
            auto_entries.append(build_mq_entry(item))

    # 2. 解析场景清单
    switch_data = load_yaml(switch_path)
    scenario_raw = switch_data.get("scenarios", [])
    scenario_entries = [build_scenario_entry(sc) for sc in scenario_raw]

    # 2a. 校验场景清单格式
    scenario_errors = validate_scenario_entries(scenario_raw)
    for e in scenario_errors:
        print(e)
        has_error = True

    # 3. 读取手动补充条目
    manual_entries: list[dict] = []
    if manual_path and Path(manual_path).exists():
        manual_data = load_yaml(manual_path)
        manual_entries = manual_data.get("interactions", [])

    # 3a. 校验手动条目格式
    manual_errors = validate_manual_entries(manual_entries)
    for e in manual_errors:
        print(e)
        has_error = True

    if has_error:
        print("[FAIL] 格式校验未通过，已终止生成。请修复后重试。")
        sys.exit(1)

    # 4. 合并：自动 > 手动，重复时警告
    auto_ids = {e["id"] for e in auto_entries}
    manual_filtered: list[dict] = []
    for me in manual_entries:
        mid = me.get("id", "")
        if mid in auto_ids:
            print(f"[WARN] 手动条目 {mid} 已被自动条目覆盖，建议从 manual 中移除")
        else:
            manual_filtered.append(me)

    all_entries = deduplicate(auto_entries + manual_filtered + scenario_entries)

    # 5. 交叉校验（仅警告）
    warnings = cross_validate(auto_entries, scenario_entries)

    # 5a. 校验切库字段（硬错误）
    # 仅在 Spec YAML 块含 request/schema 字段时校验；无 _fields 的交互跳过
    field_errors = validate_fields(auto_entries + manual_filtered, scenario_entries)
    for e in field_errors:
        print(e)
    if field_errors:
        print("[FAIL] 切库字段校验未通过，已终止生成。请修复 switch_scenarios.yml 或 Spec YAML 块后重试。")
        sys.exit(1)

    # 6. 输出
    output = [
        "# =============================================================",
        "# 服务间交互契约 — AUTO-GENERATED",
        f"# 生成时间: {datetime.now().isoformat()}",
        "# 源文件:",
        f"#   Spec YAML 块: {spec_dir}/*.md",
        f"#   场景清单:      {switch_path}",
        f"#   手动补充:      {manual_path or '(无)'}",
        "#",
        "# 警告: 此文件由脚本自动生成，禁止手动修改。",
        "# 所有变更必须通过修改源文件后重新生成完成。",
        "# =============================================================",
        "",
        "interactions:",
    ]

    for entry in all_entries:
        output.append(format_entry_yaml(entry))

    if warnings:
        output.append("# =============================================================")
        output.append("# VALIDATION_WARNINGS")
        output.append("# =============================================================")
        for w in warnings:
            output.append(f"# {w}")
        output.append("")

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    Path(output_path).write_text("\n".join(output), encoding="utf-8")
    print(f"[OK] 契约已生成: {output_path}")
    print(f"     自动条目: {len(auto_entries)}, 手动: {len(manual_filtered)}, 场景: {len(scenario_entries)}")
    if field_errors:
        print(f"     字段校验: {len(field_errors)} 个错误（已阻断）")
    if warnings:
        print(f"     交叉校验: {len(warnings)} 个警告")
        for w in warnings:
            print(f"       {w}")


def main():
    parser = argparse.ArgumentParser(description="生成服务间交互契约")
    parser.add_argument("--spec-dir", default="specs", help="Spec Markdown 目录")
    parser.add_argument("--switch", default="specs/switch_scenarios.yml", help="场景清单文件")
    parser.add_argument("--manual", default=None, help="手动补充条目文件")
    parser.add_argument("--output", default="contracts/interop_contract.yml", help="输出路径")
    args = parser.parse_args()
    generate(args)


if __name__ == "__main__":
    main()
