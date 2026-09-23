#!/usr/bin/env python3
"""
spec_updater.py — spec-updater Skill 的 CLI 辅助脚本

功能:
  1. info       项目结构检查（初始化检查）+ openspec-cn validate
  2. build      构建契约（S4: 触发 contract-maintainer 生成脚本 + 校验）
  3. summary    生成目录结构摘要（S5 辅助）
"""
import argparse
import subprocess
import sys
from datetime import datetime
from pathlib import Path


DEFAULT_CHANGE = "wecom-live-integration"
# 以本文件位置解析仓根，避免依赖 cwd 或历史 .opencode/ 布局
# （2026-09-21 外部盲检 T6a C9：原写死 ".opencode/skills/…" → exists() 恒假，委派流程静默失效）。
_REPO_ROOT = Path(__file__).resolve().parents[3]     # skills/spec-updater/scripts/x.py → 仓根
GENERATE_SCRIPT = _REPO_ROOT / "skills" / "contract-maintainer" / "scripts" / "generate_contract.py"


def _change_dir(change: str) -> Path:
    return Path(f"openspec/changes/{change}")


def _run(cmd: list[str], cwd=None) -> subprocess.CompletedProcess:
    try:
        return subprocess.run(cmd, cwd=cwd or Path.cwd(), text=True, encoding="utf-8")
    except FileNotFoundError:
        result = subprocess.CompletedProcess(cmd, -1)
        result.stdout = ""
        result.stderr = f"[ERROR] 命令未找到: {cmd[0]}"
        return result


def _capture(cmd: list[str], cwd=None) -> subprocess.CompletedProcess:
    try:
        return subprocess.run(cmd, cwd=cwd or Path.cwd(), capture_output=True, text=True, encoding="utf-8")
    except FileNotFoundError:
        result = subprocess.CompletedProcess(cmd, -1)
        result.stdout = ""
        result.stderr = f"[ERROR] 命令未找到: {cmd[0]}"
        return result


def _validate_change(change: str) -> tuple[bool, str]:
    result = _capture(["openspec-cn", "validate", change])
    ok = result.returncode == 0
    summary = result.stdout.strip() if ok else result.stdout.strip() or result.stderr.strip()
    return ok, summary


def cmd_info(change: str):
    cdir = _change_dir(change)
    specs_dir = cdir / "specs"
    contracts_dir = cdir / "contracts"
    switch_file = specs_dir / "switch_scenarios.yml"
    output_file = contracts_dir / "interop_contract.yml"

    print("=" * 60)
    print(f"spec-updater 初始化检查 ({datetime.now().strftime('%Y-%m-%d %H:%M')})")
    print(f"  变更集: {change}")
    print("=" * 60)

    checks = [
        ("openspec-cn CLI", _capture(["openspec-cn", "--version"]).returncode == 0),
        ("变更目录", cdir.exists()),
        ("Specs 目录", specs_dir.exists()),
        ("Spec 文件", len(list(specs_dir.rglob("*.md"))) > 0 if specs_dir.exists() else False),
        ("switch_scenarios.yml", switch_file.exists()),
        ("contracts 目录", contracts_dir.exists()),
        ("interop_contract.yml", output_file.exists()),
        ("generate_contract.py", GENERATE_SCRIPT.exists()),
    ]

    all_ok = True
    for name, ok in checks:
        status = "✓" if ok else "✗"
        print(f"  [{status}] {name}")
        if not ok:
            all_ok = False

    if specs_dir.exists():
        spec_files = sorted(specs_dir.rglob("*.md"))
        print(f"\n  Spec 文件 ({len(spec_files)}):")
        for f in spec_files:
            print(f"    - {f.relative_to(cdir)}")

    print(f"\n  > openspec-cn validate {change}")
    ok, summary = _validate_change(change)
    if ok:
        print(f"    ✓ 校验通过")
    else:
        print(f"    ⚠ 存在问题（不影响结构检查，建议修复）")
        for line in summary.split("\n")[:6]:
            if line.strip():
                print(f"      {line.strip()}")

    print()
    if all_ok:
        print("所有项就绪，可以开始工作。")
    else:
        missing = [name for name, ok in checks if not ok]
        print(f"以下项目未就绪，请先设置: {', '.join(missing)}")
        sys.exit(1)


def cmd_build(change: str):
    cdir = _change_dir(change)
    specs_dir = cdir / "specs"
    switch_file = specs_dir / "switch_scenarios.yml"
    contracts_dir = cdir / "contracts"
    manual_file = contracts_dir / "contract_manual.yml"
    output_file = contracts_dir / "interop_contract.yml"

    if not GENERATE_SCRIPT.exists():
        print(f"[ERROR] generate_contract.py 不存在: {GENERATE_SCRIPT}")
        print("请确认 contract-maintainer Skill 已正确安装。")
        sys.exit(1)

    if not specs_dir.exists():
        print(f"[ERROR] Specs 目录不存在: {specs_dir}")
        sys.exit(1)

    args = [
        sys.executable,
        str(GENERATE_SCRIPT),
        "--spec-dir", str(specs_dir),
        "--output", str(output_file),
    ]

    if switch_file.exists():
        args.extend(["--switch", str(switch_file)])
        if manual_file.exists():
            args.extend(["--manual", str(manual_file)])
    else:
        print(f"[WARN] switch_scenarios.yml 不存在，场景条目将不会加入契约")
        print(f"[WARN] 后续可手动创建 {switch_file} 后重新生成")

    print(f"[RUN] python {GENERATE_SCRIPT.relative_to(_REPO_ROOT)} ...")
    print("=" * 60)

    result = _run(args)
    if result.returncode != 0:
        print(f"\n[FAIL] 契约生成失败 (exit code {result.returncode})")
        sys.exit(result.returncode)

    print(f"[OK] 契约已同步: {output_file}")

    print(f"\n[RUN] openspec-cn validate {change} ...")
    print("=" * 60)
    ok, summary = _validate_change(change)
    print(summary)
    if not ok:
        print(f"\n[WARN] openspec-cn 校验发现待修复项（不影响契约生成）")


def cmd_summary(change: str):
    cdir = _change_dir(change)
    specs_dir = cdir / "specs"
    switch_file = specs_dir / "switch_scenarios.yml"
    contracts_dir = cdir / "contracts"
    output_file = contracts_dir / "interop_contract.yml"

    print(f"变更目录: {cdir}")
    print()

    spec_files = list(specs_dir.rglob("*.md"))
    print(f"Spec 文件 ({len(spec_files)}):")
    for f in spec_files:
        rel = f.relative_to(specs_dir)
        content = f.read_text(encoding="utf-8")
        req_section = "## 修改需求" in content or "## 需求" in content
        yaml_blocks = content.count("```yaml")
        marker = ""
        if req_section:
            marker += " [有需求]"
        if yaml_blocks > 0:
            marker += f" [{yaml_blocks}个YAML块]"
        print(f"  - {rel}{marker}")

    print(f"\nswitch_scenarios.yml: ", end="")
    if switch_file.exists():
        content = switch_file.read_text(encoding="utf-8")
        sc_count = content.count("- id: SW-")
        print(f"存在 ({sc_count} 个场景)")
    else:
        print("不存在")

    print(f"\ninterop_contract.yml: ", end="")
    if output_file.exists():
        content = output_file.read_text(encoding="utf-8")
        line_count = len(content.splitlines())
        int_count = content.count("- id: ")
        print(f"存在 ({line_count} 行, ~{int_count} 条目)")
    else:
        print("不存在")

    print(f"\n[RUN] openspec-cn show {change} --json --deltas-only ...")
    print("=" * 60)
    result = _capture(["openspec-cn", "show", change, "--json", "--deltas-only"])
    if result.returncode == 0 and result.stdout.strip():
        print("增量需求解析成功（见上方 JSON）")
    else:
        err = result.stderr.strip() or "变更可能缺少'为什么'部分，或当前无增量"
        print(f"增量解析状态: {err}")


def main():
    parser = argparse.ArgumentParser(description="spec-updater 辅助脚本")
    parser.add_argument("action", choices=["info", "build", "summary"],
                        help="操作: info=初始化检查, build=构建契约, summary=结构摘要")
    # R4：移除硬编码项目名默认值（原 default="wecom-live-integration"：
    # 共享脚本写死某项目 → 不传参时**静默操作错误项目**）。改为必填。
    parser.add_argument("--change", default=None,
                        help="变更集名称（必填；不再使用项目相关的隐式默认值）")
    args = parser.parse_args()

    if not args.change:

        print(
            "ERROR: 必须显式指定 --change（原硬编码默认值已移除：共享脚本不得写死项目名）",
            file=sys.stderr
        )
        return 2

    if args.action == "info":
        cmd_info(args.change)
    elif args.action == "build":
        cmd_build(args.change)
    elif args.action == "summary":
        cmd_summary(args.change)


if __name__ == "__main__":
    # R4：传播 main() 的返回码（原 `main()` → 无论返回何值都以 0 退出，失败不可见）
    import sys as _sys

    _sys.exit(main())
