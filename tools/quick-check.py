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

Output: metrics/quick-check-{date}.json (gitignored runtime artifact).
Verdict OK = no new findings; ISSUES = findings recorded (report to user).

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
METRICS = ROOT / "metrics"


def _run(cmd: list[str]) -> str:
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        return (r.stdout or "") + (r.stderr or "")
    except Exception as exc:
        return f"ERROR: {exc}"


def _parse_summary(out: str, pattern: str) -> int:
    for line in out.splitlines():
        if pattern in line:
            m = re.search(r"(\d+)", line)
            if m:
                return int(m.group(1))
    return -1


def run_checks() -> dict:
    lint = _run([sys.executable, str(HERE / "repo-lint.py"), "--repo-root", "."])
    path = _run([sys.executable, str(HERE / "path-audit.py")])
    ext = _run([sys.executable, str(HERE / "extensions-lint.py")])

    findings = []

    def _collect(out: str, source: str):
        # path-audit 的 "BROKEN (0):" 是标题行（0 个 broken = 正常），
        # 仅当 BROKEN 后跟具体路径才记录。
        lines = out.splitlines()
        for i, line in enumerate(lines):
            s = line.strip()
            if s.startswith(("[WARN]", "[ERROR]", "[FAIL]")):
                findings.append({
                    "severity": s.split()[0][1:-1],
                    "source": source,
                    "detail": s,
                })
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
