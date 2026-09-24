r"""Quick health check — read-only, seconds, safe to run at every session.

Runs the three read-only gates and records findings to disk so issues are
traceable across sessions (ADR-0009 AI-operation-first; findings feed the
next maintenance report):

    1. tools/repo-lint.py        (structural + language)
    2. tools/path-audit.py       (broken path references)
    3. tools/extensions-lint.py  (extensions domain conventions)

Usage:
    python tools/quick-check.py                 # run + write snapshot
    python tools/quick-check.py --json          # machine-readable stdout
    python tools/quick-check.py --no-record     # run only, no disk write
    python tools/quick-check.py --history       # print recent snapshots

Output: <workspace>/metrics/quick-check-{date}.json (runtime artifact, outside every repo).
Verdict: ISSUES when BLOCKER/ERROR/FAIL items were collected (report to user);
WARNING/INFO are counted separately and never flip the verdict.

Registered in tools/README.md (check_tools_readme gate).
"""

import argparse
import json
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))

import runtime_state  # noqa: E402  （运行时态路径单一来源）

METRICS = runtime_state.METRICS_DIR


def _run(cmd: list[str]) -> str:
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        return (r.stdout or "") + (r.stderr or "")
    except Exception as exc:
        return f"ERROR: {exc}"


def run_checks() -> dict:
    # 用仓根而非 cwd：否则在非仓根目录运行时 repo-lint 会扫错目录，
    # 产出“虚假健康”结果（2026-09-21 外部盲检 V4）。
    lint = _run([sys.executable, str(HERE / "repo-lint.py"), "--repo-root", str(ROOT)])
    path = _run([sys.executable, str(HERE / "path-audit.py")])
    ext = _run([sys.executable, str(HERE / "extensions-lint.py")])

    findings = []
    warning_count = 0

    # 严重度标签有多种形态：repo-lint 非冗余模式输出 `[BLOCKER]`/`[ERROR]`（无填充），
    # 冗余模式输出 `[WARNING ]`/`[INFO    ]`（severity.ljust(8) 填充）。原白名单
    # ("[WARN]", "[ERROR]", "[FAIL]") 与实际标签不匹配 → 收集长期失效
    # （findings 恒为 0、verdict 恒 OK）。2026-09-21 外部盲检 T4 修复。
    # 判定口径：BLOCKER/ERROR/FAIL 计入 findings（影响 verdict）；WARNING/INFO 仅计数
    # （否则存量 28 条 WARN 会让每次会话起点都报 ISSUES）。
    _sev_re = re.compile(r"^\[([A-Z]+)\s*\]")
    _verdict_sev = ("BLOCKER", "ERROR", "FAIL")

    def _collect(out: str, source: str):
        nonlocal warning_count
        # path-audit 的 "BROKEN (0):" 是标题行（0 个 broken = 正常），
        # 仅当 BROKEN 后跟具体路径才记录。
        lines = out.splitlines()
        for line in lines:
            s = line.strip()
            m = _sev_re.match(s)
            if m and m.group(1) in ("BLOCKER", "ERROR", "FAIL", "WARNING", "INFO"):
                sev = m.group(1)
                if sev in _verdict_sev:
                    findings.append({
                        "severity": sev,
                        "source": source,
                        "detail": s,
                    })
                elif sev == "WARNING":
                    warning_count += 1
            elif s.startswith("BROKEN") and "(" in s:
                # BROKEN (N): 后跟缩进路径行 = 有 broken；N==0 则无
                n = s.split("(")[1].split(")")[0]
                if n.strip() != "0":
                    findings.append({
                        "severity": "ERROR",
                        "source": source,
                        "detail": s,
                    })

    _collect(lint, "repo-lint")
    _collect(path, "path-audit")
    _collect(ext, "extensions-lint")

    return {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "lint_summary": lint.strip().splitlines()[-1] if lint.strip() else "no output",
        "path_summary": path.strip().splitlines()[-1] if path.strip() else "no output",
        "extensions_summary": ext.strip().splitlines()[-1] if ext.strip() else "no output",
        "findings": findings,
        "finding_count": len(findings),
        "warning_count": warning_count,
        "verdict": "OK" if not findings else "ISSUES",
    }


def _snapshot_path(date: str) -> Path:
    return METRICS / f"quick-check-{date}.json"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="JSON stdout")
    parser.add_argument("--no-record", action="store_true",
                        help="run only, no disk write")
    parser.add_argument("--history", action="store_true",
                        help="print recent snapshots")
    args = parser.parse_args()

    if args.history:
        snaps = sorted(METRICS.glob("quick-check-*.json"))
        print(f"{len(snaps)} snapshot(s):")
        for p in snaps[-10:]:
            try:
                d = json.loads(p.read_text(encoding="utf-8"))
                print(f"  {p.name}: {d.get('verdict')} "
                      f"({d.get('finding_count')} findings)")
            except Exception:
                print(f"  {p.name}: <unreadable>")
        return 0

    result = run_checks()

    if not args.no_record:
        METRICS.mkdir(exist_ok=True)
        date = datetime.now().strftime("%Y-%m-%d")
        snap = _snapshot_path(date)
        # 同日多次运行：覆盖当日快照（每日一份），保留历史日期
        snap.write_text(json.dumps(result, ensure_ascii=False, indent=2),
                        encoding="utf-8")
        recorded = f"recorded -> {snap.name}"
    else:
        recorded = "no record (--no-record)"

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0

    print(result["lint_summary"])
    print(result["path_summary"])
    print(result["extensions_summary"])
    print(f"findings: {result['finding_count']} | verdict: {result['verdict']}")
    print(recorded)

    for f in result["findings"][:10]:
        print(f"  [{f['severity']}] {f['source']}: {f['detail'][:90]}")
    if result["finding_count"] > 10:
        print(f"  ... and {result['finding_count'] - 10} more")

    # 退出码：ISSUES 返回 1（供 AI 判断是否需要提示用户）
    return 1 if result["verdict"] == "ISSUES" else 0


if __name__ == "__main__":
    sys.exit(main())
