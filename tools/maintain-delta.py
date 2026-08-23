#!/usr/bin/env python3
r"""maintain-delta.py — 巡检增量感知（Q1-1，省 token/时间）。

维护命令每次全量重跑所有审计，但每周实际变化很小（如本周仅 templates +1）。
本工具对比「上次完整巡检后的 git HEAD」与当前 HEAD，输出紧凑的变化范围判定，
让 AI 只跑受影响子集；零变化时跳过全量审计（仅 quick-check + 状态卫生）。

Usage:
    python tools/maintain-delta.py --check             # 判定 FIRST_RUN / NO_CHANGES / CHANGED
    python tools/maintain-delta.py --check --json      # JSON 输出
    python tools/maintain-delta.py --record            # 记录当前 HEAD+日期（完整巡检完成后调用）

状态文件: metrics/maintain-delta-state.json（gitignored 运行时数据，非版本控制）。
"""

import argparse
import datetime
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

STATE = ROOT / "metrics" / "maintain-delta-state.json"

# 区域 → 受影响时建议运行的审计
AREA_TOOLS = {
    "workflows": "workflow-command-audit",
    "config": "check.py(2,3,6) + workflow-command-audit",
    "templates": "check.py(5 prompt build) + repo-lint",
    "cli": "CLI 单测 + check.py",
    "tools": "repo-lint + check.py + CLI 单测",
    "governance": "repo-lint(Rule 3) + check.py(8 memory)",
    "skills": "repo-lint + extensions-lint(如涉扩展)",
    "reports": "proposal-audit",
    "rfc": "check.py(11 ADR)",
}

AREA_PREFIXES = {
    "workflows": ("workflows/",),
    "config": ("config/",),
    "templates": ("templates/",),
    "cli": ("cli/",),
    "tools": ("tools/",),
    "governance": ("governance/", "loaders/", "OPERATIONS.md"),
    "skills": ("skills/",),
    "reports": ("reports/",),
    "rfc": ("rfc/",),
}


def git(args):
    return subprocess.run(
        ["git"] + args,
        cwd=str(ROOT),
        capture_output=True,
        text=True,
    ).stdout.strip()


def current_head():
    return git(["rev-parse", "HEAD"]) or ""


def load_state():
    try:
        return json.loads(STATE.read_text(encoding="utf-8"))
    except Exception:
        return None


def save_state(head, date):
    STATE.parent.mkdir(parents=True, exist_ok=True)
    STATE.write_text(
        json.dumps(
            {"head": head, "date": date, "mode": "weekly"},
            ensure_ascii=False,
            indent=1,
        ),
        encoding="utf-8",
    )


def changed_areas(old, new):
    files = [f for f in git(["diff", "--name-only", old, new]).splitlines() if f]
    areas = set()
    for f in files:
        for area, prefixes in AREA_PREFIXES.items():
            if any(f.startswith(p) for p in prefixes):
                areas.add(area)
    return sorted(areas), files


def check_verdict():
    head = current_head()
    state = load_state()

    if state is None:
        return {
            "verdict": "FIRST_RUN",
            "head": head,
            "message": "无上次巡检记录 → 全量审计",
        }

    if state.get("head") == head:
        return {
            "verdict": "NO_CHANGES",
            "head": head,
            "since": state.get("date"),
            "message": (
                f"自 {state.get('date')} 完整巡检后 ai-system 无提交变化 → "
                "跳过全量审计，仅 quick-check + 状态卫生"
            ),
        }

    areas, files = changed_areas(state.get("head"), head)
    commits = len(git(["log", "--oneline", f"{state.get('head')}..{head}"]).splitlines())

    return {
        "verdict": "CHANGED",
        "head": head,
        "since": state.get("date"),
        "commits": commits,
        "files": len(files),
        "areas": areas,
        "suggested_tools": sorted({AREA_TOOLS[a] for a in areas}),
        "message": (
            f"自 {state.get('date')} 起 {commits} 提交 / {len(files)} 文件变化，"
            f"涉及区域: {', '.join(areas) or '（未分类）'} → 跑对应子集"
        ),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    parser.add_argument("--check", action="store_true", help="判定变化范围")
    parser.add_argument("--record", action="store_true", help="记录当前 HEAD（完整巡检后）")
    parser.add_argument("--json", action="store_true", help="JSON 输出（配合 --check）")
    args = parser.parse_args()

    if args.record:
        head = current_head()
        date = datetime.date.today().isoformat()
        save_state(head, date)
        print(f"recorded: head={head[:12]} date={date} -> {STATE}")
        return 0

    if args.check:
        v = check_verdict()
        if args.json:
            print(json.dumps(v, ensure_ascii=False))
        else:
            print(f"[maintain-delta] verdict={v['verdict']} | {v['message']}")
            if v.get("areas"):
                print(f"  areas: {', '.join(v['areas'])}")
                print(f"  suggested: {'; '.join(v['suggested_tools'])}")
        # 零变化 / 首次运行不算失败；CHANGED 也不算失败（信息性判定）
        return 0

    parser.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
