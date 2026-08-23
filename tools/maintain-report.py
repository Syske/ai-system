#!/usr/bin/env python3
r"""maintain-report.py — 巡检报告骨架自动生成（Q1-3，省 AI 手写 token）。

从已有 JSON/工具输出自动拼装 MAINTENANCE-{date}.md 的「工具校验结果 /
指标对比 / quick-check 趋势 / 提案状态」四节；巡检发现 / 一致性抽查结论 /
修复清单等叙事节留给 AI 填写。非破坏：目标文件已存在时不覆盖。

Usage:
    python tools/maintain-report.py --date 2026-08-23
    python tools/maintain-report.py --date 2026-08-23 --dry-run   # 只打印不写盘
"""

import argparse
import glob
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
METRICS = ROOT / "metrics"
REPORTS = ROOT / "reports"


def run(args):
    return subprocess.run(
        [sys.executable] + args,
        cwd=str(ROOT),
        capture_output=True,
        text=True,
    ).stdout.strip()


def load_json(path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def quick_check_section(date):
    qc = load_json(METRICS / f"quick-check-{date}.json")
    if qc is None:
        return "- quick-check: 无当日 JSON（未运行或未记录）\n"
    rows = [
        ("quick-check", f"verdict **{qc.get('verdict', '?')}**（findings {qc.get('finding_count', '?')}）"),
        ("lint", qc.get("lint_summary", "?")),
        ("path", qc.get("path_summary", "?")),
        ("extensions", qc.get("extensions_summary", "?")),
    ]
    return "\n".join(f"| {k} | {v} |" for k, v in rows) + "\n"


def metrics_diff_section(date):
    snap = load_json(METRICS / f"maintain-{date}.json")
    if snap is None:
        return "- 指标快照 maintain-{date}.json 缺失\n"

    # 上期 = 快照 timestamp 小于本期的最新一份（文件名含 20260820 无横线形态，
    # 不能按字典序选）
    cur_ts = snap.get("timestamp", "")
    prev_data = None
    for p in sorted(glob.glob(str(METRICS / "maintain-*.json"))):
        if "maintain-" + date + ".json" in p:
            continue
        d = load_json(Path(p))
        if d and d.get("timestamp", "") < cur_ts:
            prev_data = d

    def get(d, k, sub=None):
        if d is None:
            return "?"
        v = d.get(k)
        if sub and isinstance(v, dict):
            return v.get(sub, "?")
        return v if isinstance(v, (int, float, str)) else "?"

    def size(d, name):
        if d is None:
            return "?"
        s = d.get("skills", {}).get("sizes", {})
        return s.get(name, "?")

    lines = [
        "| 指标 | 上期 | 本期 | 变化 |",
        "|---|---|---|---|",
        f"| Skills | {prev_data and prev_data.get('skills', {}).get('count') or '?'} | {snap.get('skills', {}).get('count')} | = |",
        f"| Workflows | {prev_data and prev_data.get('workflows', {}).get('count') or '?'} | {snap.get('workflows', {}).get('count')} | = |",
        f"| RFC | {prev_data and prev_data.get('rfc', {}).get('count') or '?'} | {snap.get('rfc', {}).get('count')} | = |",
        f"| Governance | {prev_data and prev_data.get('governance', {}).get('count') or '?'} | {snap.get('governance', {}).get('count')} | = |",
        f"| Templates | {prev_data and prev_data.get('templates', {}).get('count') or '?'} | {snap.get('templates', {}).get('count')} | = |",
    ]
    return "\n".join(lines) + "\n"


def quick_check_trend_section():
    snaps = sorted(glob.glob(str(METRICS / "quick-check-*.json")))
    if not snaps:
        return "- 无 quick-check 历史\n"
    lines = ["| 日期 | verdict | findings |", "|---|---|---|"]
    for p in snaps:
        d = load_json(Path(p))
        if d:
            date = Path(p).stem.replace("quick-check-", "")
            lines.append(
                f"| {date} | {d.get('verdict', '?')} | {d.get('finding_count', '?')} |"
            )
    return "\n".join(lines) + "\n"


def proposal_section():
    out = run(["tools/proposal-audit.py", "--json"])
    try:
        d = json.loads(out)
    except Exception:
        return "- proposal-audit --json 输出异常\n"

    closed = {"Implemented", "Approved", "Rejected", "Archived"}
    open_props = [
        p["file"] for p in d.get("proposals", [])
        if p.get("status") not in closed
    ]
    items = d.get("open_items", [])

    lines = [
        f"- proposal-audit: 0 gate error / {len(d.get('warnings', []))} warn / "
        f"{len(open_props)} 开放提案 / {len(items)} open action items"
    ]
    for w in d.get("warnings", []):
        lines.append(f"  - WARN {w}")
    for p in open_props:
        lines.append(f"  - 开放: {p}")
    for it in items:
        lines.append(
            f"  - {it.get('file', '?')}:{it.get('line', '?')} {it.get('item', '')}"
        )
    return "\n".join(lines) + "\n"


def render(date):
    return (
        f"# 系统巡检报告 — {date}（weekly）\n\n"
        "- 类型: 系统巡检（MAINTENANCE）\n"
        f"- 模式: weekly\n- 日期: {date}\n\n"
        "---\n\n"
        "## 一、工具校验结果（自动生成，AI 核对补充说明）\n\n"
        + quick_check_section(date)
        + "\n### 指标对比（自动生成，需 AI 核对变化原因）\n\n"
        + metrics_diff_section(date)
        + "\n---\n\n"
        "## 二、巡检发现（AI 填写，按严重度分级）\n\n"
        "<!-- 高 / 中 / 低 / 信息 -->\n\n"
        "---\n\n"
        "## 三、一致性抽查结论（AI 填写，逐项通过/失败）\n\n"
        "---\n\n"
        "## 四、修复动作与建议清单（AI 填写）\n\n"
        "---\n\n"
        "## 五、quick-check 趋势（自动生成）\n\n"
        + quick_check_trend_section()
        + "\n## 六、提案状态（自动生成）\n\n"
        + proposal_section()
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    parser.add_argument("--date", required=True, help="报告日期 YYYY-MM-DD")
    parser.add_argument("--dry-run", action="store_true", help="只打印不写盘")
    args = parser.parse_args()

    content = render(args.date)

    if args.dry_run:
        print(content)
        return 0

    target = REPORTS / f"MAINTENANCE-{args.date}.md"
    if target.exists():
        print(f"exists, not overwriting: {target}")
        return 0

    target.write_text(content, encoding="utf-8")
    print(f"generated skeleton: {target}（AI 填写巡检发现/一致性/修复清单节）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
