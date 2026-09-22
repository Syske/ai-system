#!/usr/bin/env python3
r"""C2 profile 校准评估器（P65 Option B / C 的量化仪器，只读）。

用途：给定源目录或文件样本，对**多个候选 profile**（在现行 eclipse-format.xml 上
覆盖指定 alignment 等设置）批量跑 JDT 干跑，输出"文件数 / 差异文件数 / 差异行数 /
二次格式化收敛性 / 最长行 / >120 列行数"对照表，用于回答：

  - 校准某些设置会引发多大 diff（存量基线体量 vs 增量噪声）
  - 格式化结果是否收敛（有无 format↔format 振荡 → 决定 known-ignore.txt 需求）
  - "行 ≤ 120"是否可达（JDT 的 lineSplit 是目标值，受折行策略支配）

**只读**：源目录仅被读取，格式化产物写入 `--work`（默认 /tmp/jdt-profile-eval）；
绝不写业务仓。

用法：
    python3 tools/jdt-profile-eval.py --src <dir-or-file> [--src ...] \
        [--limit 40] [--candidates C0,C1] [--java <path>] [--classpath <spec>]

候选（内置，基于现行 profile 覆盖）：
    C0-baseline         现行 profile（基线）
    C1-args17           方法调用/实例化参数 0 → 17（逐参数折行，缩进 1）
    C2-args49           同上 → 49（缩进 3）
    C3-only-mi17        仅方法调用参数 0 → 17
    C1c-args17+cond17   C1 + 条件表达式 0 → 17
    C2c-args49+cond17   C2 + 条件表达式 0 → 17
"""

import argparse
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
AI_ROOT = HERE.parent

PROFILE_DEFAULT = AI_ROOT / "tools" / "jdt-format-gate" / "eclipse-format.xml"
LIB_DEFAULT = Path.home() / ".local" / "lib" / "jdt-gate"
BUILD_DEFAULT = AI_ROOT / "tools" / "jdt-format-gate" / "build"
WORK_DEFAULT = Path("/tmp/jdt-profile-eval")

FMT = "org.eclipse.jdt.core.formatter."

MI = FMT + "alignment_for_arguments_in_method_invocation"
ALLOC = FMT + "alignment_for_arguments_in_allocation_expression"
COND = FMT + "alignment_for_conditional_expression"

CANDIDATES = {
    "C0-baseline": {},
    "C1-args17": {MI: "17", ALLOC: "17"},
    "C2-args49": {MI: "49", ALLOC: "49"},
    "C3-only-mi17": {MI: "17"},
    "C1c-args17+cond17": {MI: "17", ALLOC: "17", COND: "17"},
    "C2c-args49+cond17": {MI: "49", ALLOC: "49", COND: "17"},
}

STATS_RE = re.compile(r"files=(\d+) differ=(\d+) diffLines=(\d+)")


def build_profile(base_text, overrides):
    """在 profile 文本上覆盖设置；返回 (text, missing_keys)。

    只替换已存在的 `<setting id=… value=…/>`；不存在的键回报为 missing，
    调用方据此判断候选是否与 profile 版本匹配（fail loud，不静默忽略）。
    """
    missing = []
    text = base_text
    for key, value in overrides.items():
        pattern = f'<setting id="{re.escape(key)}" value="[^"]*"/>'
        if not re.search(pattern, text):
            missing.append(key)
            continue
        text = re.sub(pattern, f'<setting id="{key}" value="{value}"/>', text, count=1)
    return text, missing


def parse_stats(output):
    """从 JdtFormatCheck 输出解析 (files, differ, diffLines)；缺失返回 (None, None, None)。"""
    match = STATS_RE.search(output)
    if not match:
        return (None, None, None)
    return tuple(int(x) for x in match.groups())


def scan_long_lines(dump_dir, limit=120):
    """统计格式化产物中的最长行与超限行数。"""
    worst, over = 0, 0
    for path in Path(dump_dir).rglob("*.java"):
        for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
            worst = max(worst, len(line))
            if len(line) > limit:
                over += 1
    return worst, over


def collect_sources(specs, work_dir, limit):
    """把 `--src` 收集成一个待扫目录（目录→就地读取；文件→拷贝）。

    返回 (scan_dir, file_count)。目录情形不拷贝（避免大仓复制），直接读；
    仅当传入单个文件时才建立汇总目录。
    """
    dirs = [Path(s) for s in specs if Path(s).is_dir()]
    files = [Path(s) for s in specs if Path(s).is_file()]

    if len(dirs) == 1 and not files:
        return dirs[0], len(list(dirs[0].rglob("*.java")))

    pool = work_dir / "sample"
    if pool.exists():
        shutil.rmtree(pool)
    pool.mkdir(parents=True)

    count = 0
    for src_dir in dirs:
        for path in sorted(src_dir.rglob("*.java")):
            if count >= limit:
                break
            name = f"{src_dir.name}__{path.name}"
            target = pool / name
            dedup = 1
            while target.exists():
                target = pool / f"{src_dir.name}__{dedup}_{path.name}"
                dedup += 1
            shutil.copy2(path, target)
            count += 1
    for path in files:
        if count >= limit:
            break
        target = pool / path.name
        dedup = 1
        while target.exists():
            target = pool / f"{dedup}_{path.name}"
            dedup += 1
        shutil.copy2(path, target)
        count += 1
    return pool, count


def run_candidate(profile_path, scan_dir, dump_dir, classpath, timeout):
    """跑一次干跑 + 一次收敛复跑；返回 (stats, conv_differ, raw_head)。"""
    if dump_dir.exists():
        shutil.rmtree(dump_dir)
    dump_dir.mkdir(parents=True)

    result = subprocess.run(
        ["java", "-cp", classpath, "JdtFormatCheck", str(profile_path),
         str(scan_dir), "--dump-dir", str(dump_dir)],
        capture_output=True, text=True, timeout=timeout,
    )
    output = result.stdout + result.stderr
    stats = parse_stats(output)

    conv_dir = dump_dir.parent / (dump_dir.name + "-refmt")
    if conv_dir.exists():
        shutil.rmtree(conv_dir)
    conv_dir.mkdir(parents=True)
    conv = subprocess.run(
        ["java", "-cp", classpath, "JdtFormatCheck", str(profile_path),
         str(dump_dir), "--dump-dir", str(conv_dir)],
        capture_output=True, text=True, timeout=timeout,
    )
    conv_stats = parse_stats(conv.stdout + conv.stderr)

    return stats, conv_stats[1], output.strip().splitlines()[:2]


def main(argv=None):
    parser = argparse.ArgumentParser(description="C2 profile 校准评估（只读）")
    parser.add_argument("--src", action="append", default=[],
                        help="源目录或文件（可重复）")
    parser.add_argument("--profile", default=str(PROFILE_DEFAULT))
    parser.add_argument("--work", default=str(WORK_DEFAULT))
    parser.add_argument("--limit", type=int, default=40,
                        help="多源汇总时的文件上限")
    parser.add_argument("--candidates", default=",".join(CANDIDATES),
                        help="逗号分隔的候选名（默认全部）")
    parser.add_argument("--classpath", default=None,
                        help="JDT classpath（默认 <lib>/*:<build>）")
    parser.add_argument("--timeout", type=int, default=3600)
    args = parser.parse_args(argv)

    if not args.src:
        print("ERROR: 至少需要一个 --src（目录或文件）", file=sys.stderr)
        return 2

    work = Path(args.work)
    work.mkdir(parents=True, exist_ok=True)
    profile_path = Path(args.profile)
    if not profile_path.is_file():
        print(f"ERROR: profile 不存在: {profile_path}", file=sys.stderr)
        return 2

    classpath = args.classpath or f"{LIB_DEFAULT}/*:{BUILD_DEFAULT}"
    base_text = profile_path.read_text(encoding="utf-8")

    scan_dir, count = collect_sources(args.src, work, args.limit)
    print(f"扫描对象: {scan_dir}（{count} 个 .java）\n")

    rows = []
    for name in [c.strip() for c in args.candidates.split(",") if c.strip()]:
        overrides = CANDIDATES.get(name)
        if overrides is None:
            print(f"ERROR: 未知候选 '{name}'（可选: {', '.join(CANDIDATES)}）",
                  file=sys.stderr)
            return 2

        text, missing = build_profile(base_text, overrides)
        if missing:
            print(f"[{name}] 警告：profile 中不存在这些键，已跳过覆盖: "
                  f"{', '.join(missing)}", file=sys.stderr)

        candidate_path = work / f"profile-{name}.xml"
        candidate_path.write_text(text, encoding="utf-8")

        started = time.time()
        stats, conv_differ, _ = run_candidate(
            candidate_path, scan_dir, work / f"dump-{name}", classpath, args.timeout)
        worst, over = scan_long_lines(work / f"dump-{name}")
        rows.append((name, stats, conv_differ, worst, over, time.time() - started))
        print(f"[{name}] files={stats[0]} differ={stats[1]} diffLines={stats[2]} "
              f"| 二次 differ={conv_differ} | 最长行={worst} | >120 行={over}")

    baseline = next((r for r in rows if r[0].startswith("C0")), None)
    print("\n| 候选 | files | differ | diffLines | Δ diffLines | 二次 differ | 最长行 | >120 行 | 耗时 |")
    print("|---|---|---|---|---|---|---|---|---|")
    for name, stats, conv_differ, worst, over, elapsed in rows:
        delta = "-"
        if baseline and baseline[1][2] is not None and stats[2] is not None:
            delta = f"{stats[2] - baseline[1][2]:+d}"
        print(f"| {name} | {stats[0]} | {stats[1]} | {stats[2]} | {delta} | "
              f"{conv_differ} | {worst} | {over} | {elapsed:.0f}s |")
    return 0


if __name__ == "__main__":
    sys.exit(main())