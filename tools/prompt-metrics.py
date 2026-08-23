#!/usr/bin/env python3
r"""prompt-metrics.py — 提示词体积与缓存友好性实测（Q2：R1/R2 重定义）。

构建全部 workflow + command 提示词并记录：
- 各提示词体积（chars / 估算 token ≈ chars/4）与合计 —— R2（提示词级成本趋势）
- 前缀稳定性：同工作流不同输入下静态前缀/动态后缀占比 —— token 缓存命中友好性
- 结果写入 metrics/prompt-{date}.json（gitignored 运行时数据），供 maintain-report 引用

Usage:
    python tools/prompt-metrics.py                    # 测 + 记录 metrics/prompt-{date}.json
    python tools/prompt-metrics.py --json             # 紧凑 JSON 输出
"""

import argparse
import datetime
import glob
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
METRICS = ROOT / "metrics"


def measure(workflows, commands):
    """构建全部提示词，返回 {workflow: {size, prefix, suffix}, ...} 与汇总。"""

    sys.path.insert(0, str(ROOT))
    from cli.services.prompt_builder import PromptBuilder

    b = PromptBuilder()

    rows = {}

    for name in sorted(workflows):
        p1 = b.build(name, {})
        p2 = b.build(name, {"Project ID": "prefix-probe"})
        i = p1.find("# Task")
        prefix = p1[:i] if i > 0 else p1
        rows[name] = {
            "kind": "workflow",
            "size": len(p1),
            "tokens_est": len(p1) // 4,
            "prefix_chars": len(prefix),
            "prefix_stable": p1[:i] == p2[:i] if i > 0 else True,
        }

    for f in sorted(glob.glob(str(ROOT / "cli" / "commands" / "aic-*.md"))):
        name = Path(f).stem[len("aic-"):]
        p1 = b.build(name, {})
        rows[name] = {
            "kind": "command",
            "size": len(p1),
            "tokens_est": len(p1) // 4,
            "prefix_chars": 0,
            "prefix_stable": None,
        }

    total = sum(r["size"] for r in rows.values())
    stable = [
        n for n, r in rows.items()
        if r["prefix_stable"]
    ]

    return {
        "rows": rows,
        "summary": {
            "prompts": len(rows),
            "total_chars": total,
            "total_tokens_est": total // 4,
            "workflow_avg_chars": (
                sum(r["size"] for n, r in rows.items() if r["kind"] == "workflow")
                // max(1, sum(1 for r in rows.values() if r["kind"] == "workflow"))
            ),
            "prefix_stable_count": len(stable),
            "prefix_stable_workflows": stable,
        },
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    parser.add_argument("--json", action="store_true", help="JSON 输出")
    parser.add_argument("--date", default=None, help="记录日期（默认今天）")
    args = parser.parse_args()

    import yaml

    registry = yaml.safe_load(
        (ROOT / "config" / "workflow-registry.yaml").read_text(encoding="utf-8")
    )["workflows"]

    data = measure(registry, [])
    date = args.date or datetime.date.today().isoformat()
    data["date"] = date

    target = METRICS / f"prompt-{date}.json"
    METRICS.mkdir(parents=True, exist_ok=True)
    target.write_text(
        json.dumps(data, ensure_ascii=False, indent=1),
        encoding="utf-8",
    )

    s = data["summary"]

    if args.json:
        print(json.dumps(data, ensure_ascii=False))
        return 0

    print(f"prompt-metrics recorded -> {target}")
    print(
        f"workflows={sum(1 for r in data['rows'].values() if r['kind']=='workflow')} "
        f"commands={sum(1 for r in data['rows'].values() if r['kind']=='command')}"
    )
    print(
        f"total={s['total_chars']} chars (~{s['total_tokens_est']} tok) "
        f"workflow_avg={s['workflow_avg_chars']} chars"
    )
    print(
        f"prefix_stable={s['prefix_stable_count']}/{len(data['rows'])} "
        f"(workflows: {', '.join(s['prefix_stable_workflows'])})"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
