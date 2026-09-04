#!/usr/bin/env python3
"""checkstyle 增量门禁 wrapper（H2，2026-09-03）。

git status 驱动只查本 change 的 .java，避免 develop 每会话全量扫描（实测 platform-api
全量 1m20s）；相对仓根路径传参，与 suppressions（-g 生成于仓根）files 匹配一致。

用法：
    python3 tools/checkstyle/checkstyle-gate.py <src> [--config <xml>]
        [--full] [--dry-run-list] [--java <path>] [--jar <path>]

行为：
- git 仓：changed/staged/untracked .java（相对仓根）→ checkstyle 只查这些文件；
  changed 空 → 秒级 PASS；非 git 仓 → 全量 <src>。
- --full：跳过增量，全量扫描。
- --dry-run-list：仅打印本次将检查的文件列表（调试/测试；无需 JRE/jar）。
- 执行顺序：clean 短路与 dry-run-list 均不依赖 JRE/jar（CI 无环境也能跑）；
  环境探测只在真实扫描前进行。
- exit：0 PASS（error=0；warning 收集不阻断）；1 有 error 阻断；3 ENV 缺失；
  2 参数/运行错误。

依赖探测顺序：
- JRE：--java → ~/.local/jre17/bin/java → PATH java
- jar：--jar → ~/.local/lib/checkstyle/checkstyle-*-all.jar
"""
import argparse
import subprocess
import sys
from pathlib import Path

JRE_DEFAULT = Path.home() / ".local" / "jre17" / "bin" / "java"
JAR_DEFAULT = Path.home() / ".local" / "lib" / "checkstyle"


def _find_java(explicit):
    if explicit and Path(explicit).exists():
        return explicit
    if JRE_DEFAULT.exists():
        return str(JRE_DEFAULT)
    for cand in ("java", "/usr/bin/java"):
        r = subprocess.run(["bash", "-lc", f"command -v {cand}"], capture_output=True, text=True)
        if r.returncode == 0 and r.stdout.strip():
            return r.stdout.strip()
    return None


def _find_jar(explicit):
    if explicit and Path(explicit).exists():
        return str(explicit)
    if JAR_DEFAULT.is_dir():
        hits = sorted(JAR_DEFAULT.glob("checkstyle-*-all.jar"))
        if hits:
            return str(hits[-1])
    return None


def changed_java_files(repo_root, src_dir):
    """git status 驱动：已改动/新增 .java（相对仓根）。非 git 返回 None。"""
    try:
        r = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=str(repo_root), capture_output=True, text=True, timeout=30,
        )
    except Exception:
        return None
    if r.returncode != 0:
        return None
    rels = []
    for line in r.stdout.splitlines():
        p = line[3:].strip()  # 跳过 XY 状态
        if p.endswith(".java") and not p.startswith('"') and not p.endswith(" -> "):
            rels.append(p)
    return sorted(set(rels))


def main(argv=None):
    ap = argparse.ArgumentParser(description="checkstyle 增量门禁 wrapper")
    ap.add_argument("src_dir", help="Java 源目录（仓内）")
    ap.add_argument("--config", default=None,
                    help="checkstyle.xml（规则集）；缺省探测仓根 checkstyle.xml，仓内无资产 → skip（模板语义）")
    ap.add_argument("--java", default=None)
    ap.add_argument("--jar", default=None)
    ap.add_argument("--full", action="store_true", help="跳过增量，全量扫描 src")
    ap.add_argument("--dry-run-list", action="store_true", help="仅打印将检查文件列表")
    args = ap.parse_args(argv)

    src = Path(args.src_dir)
    if not src.is_dir():
        print(f"checkstyle-gate: ERROR — 源目录不存在: {src}", file=sys.stderr)
        return 2

    # ---- 环境无关步骤（CI/无 JRE 环境也必须可用）：仓根 + changed 计算 ----
    try:
        root = subprocess.check_output(
            ["git", "-C", str(src), "rev-parse", "--show-toplevel"],
            text=True, timeout=30, stderr=subprocess.DEVNULL,
        ).strip()
    except Exception:
        root = None

    targets = None
    mode = "full"
    if not args.full and root:
        rels = changed_java_files(root, src)
        if rels is None:
            mode = "full"   # git 异常 → 全量
        elif not rels:
            print("checkstyle-gate: PASS（本 change 无改动 .java 文件）")
            return 0
        else:
            mode = "incremental"
            targets = [str(Path(root) / rel) for rel in rels]
    if args.full or not root:
        mode = "full"

    if args.dry_run_list:
        print(f"checkstyle-gate: [{mode}] {len(targets) if targets else 'ALL'} files")
        for t in (targets or [str(src)]):
            print(" ", t)
        return 0

    # ---- 仓内资产存在性（模板语义：Missing assets → skip with a note）----
    config = args.config or (str(Path(root) / "checkstyle.xml") if root else None)
    if config is None or not Path(config).exists():
        print("checkstyle-gate: SKIP（仓内无 checkstyle.xml/suppressions.xml 资产，"
              "未基线仓；需显式 --config 或先跑格式基线）→ exit 0", file=sys.stderr)
        return 0

    # ---- 环境探测（短路/dry-run 之后：无 JRE 时仅真实扫描受影响）----
    java = _find_java(args.java)
    jar = _find_jar(args.jar)
    if not java or not jar:
        print("checkstyle-gate: ENV 缺失（JRE17/checkstyle jar）→ 跳过（exit 3）", file=sys.stderr)
        return 3

    cmd = [java, "-jar", jar, "-c", str(Path(config).resolve())]
    if targets:
        cmd += targets
    else:
        cmd += [str(src)]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=1800)
    out = (r.stdout or "") + (r.stderr or "")
    n_err = sum(1 for ln in out.splitlines() if "[ERROR]" in ln)
    n_warn = sum(1 for ln in out.splitlines() if "[WARN]" in ln)
    # 门禁语义：error 阻断（exit 1）/ warning 收集（exit 0）
    if n_err:
        print(f"checkstyle-gate: FAIL（{mode}）errors={n_err} warnings={n_warn}（error 阻断）")
        print(out[-4000:])
        return 1
    if n_warn or "Checkstyle ends with" in out:
        print(f"checkstyle-gate: PASS（{mode}）warnings={n_warn}（仅收集，不阻断）")
        return 0
    if r.returncode == 0:
        print(f"checkstyle-gate: PASS（{mode}）")
        return 0
    print(f"checkstyle-gate: ERROR（rc={r.returncode}）: {out[-1500:]}")
    return 2


if __name__ == "__main__":
    sys.exit(main())