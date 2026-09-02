#!/usr/bin/env python3
r"""develop 代码格式与规范泄漏自检（A 层，2026-09-02）。

env 决策（卸载 google-java-format / 停用 pi-lens Java formatter）后，
人工自检升级为脚本辅助自检。纯 python3、无 JDK/Maven 依赖（绕开编译
环境阻断），检查 ai-system 已立规范的可机械判定项。

检查项（FAIL=必须修复，WARN=建议人工核验）：
1. 单行 Javadoc（`/** xxx */`）→ FAIL（documentation.md → Javadoc Format）
2. 中文/Unicode 方法名 → FAIL（testing.md → Naming / documentation.md → Identifiers）
3. 注释内任务编号泄漏（`（T-001）` / T-00x 出现在注释行）→ FAIL（Comment Content）
4. `Map<String, Object>` + `.put("` 手工组装（疑似消息体 payload）→ WARN
   （rocketmq-conventions §4.1，启发式：方法内 Map 后连续 put）
5. 4 空格缩进比例偏低（启发式，阈值宽容）→ WARN
6. `--check-commit`：最近提交 subject 以 `T-\d+` 开头 → FAIL（Commit Content）

用法：
    python3 tools/format-check.py <src-dir> [--check-commit]
    python3 tools/format-check.py . --check-commit   # 含最近提交 subject 检查
exit code: 0=PASS  1=WARN  2=FAIL
"""
import argparse
import re
import subprocess
import sys
from pathlib import Path

CJK = re.compile(r"[\u4e00-\u9fff]")
ONE_LINE_JAVADOC = re.compile(r"/\*\*[^*]*\*/")          # 同行闭合的单行 Javadoc 块
METHOD_SIG = re.compile(
    r"(?:public|protected|private)\s+[\w<>\[\],\s]+\s+([^\s(]+)\s*\("  # 方法名 token
)
TASK_REF = re.compile(r"T-\d{3}")                              # T-001 等
MAP_DECL = re.compile(r"Map<String,\s*Object>\s+\w+\s*=\s*new\s+HashMap<>\(\)")
PUT_REF = re.compile(r'\.put\("')
COMMIT_TASK_PREFIX = re.compile(r"^(feat|fix|docs|style|refactor|perf|test|chore|ci|revert)\([^)]*\):\s*T-\d{3}")
# 生产日志消息：error/warn 必须英文（documentation.md → Log Content）；info 提示
# log.error( "中文" ) / log.warn( "中文" )
LOG_CJK_ERROR = re.compile(r"log\.(error|warn)\(\s*\"[^\"]*[\u4e00-\u9fff]")
LOG_CJK_INFO = re.compile(r"log\.(info|debug)\(\s*\"[^\"]*[\u4e00-\u9fff]")


def _is_comment_line(line: str) -> bool:
    s = line.strip()
    return s.startswith(("//", "/*", "*", "/**", "*/"))


def check_file(path: Path, findings):
    """对单个 .java 文件执行可机械判定的检查，结果并入 findings。"""
    src = path.read_text(encoding="utf-8", errors="replace")
    lines = src.splitlines()

    # 1. 单行 Javadoc
    for i, ln in enumerate(lines, 1):
        if ONE_LINE_JAVADOC.search(ln):
            findings.append(("FAIL", f"单行 Javadoc（应多行块，documentation.md）: {path}:{i}"))

    # 2. 中文/Unicode 方法名
    for i, ln in enumerate(lines, 1):
        m = METHOD_SIG.search(ln)
        if m and CJK.search(m.group(1)):
            findings.append(("FAIL", f"中文方法名「{m.group(1)}」（testing.md Naming）: {path}:{i}"))

    # 3. 注释内任务编号泄漏
    for i, ln in enumerate(lines, 1):
        if TASK_REF.search(ln) and (_is_comment_line(ln) or "（T-" in ln):
            findings.append(("FAIL", f"注释内任务编号泄漏（Comment Content）: {path}:{i}"))

    # 4. Map 手工组装 payload（启发式 WARN：仅 main 代码——test 中 Map 常为参数构造合法；
    #    Map<String,Object> 声明后 20 行内 ≥2 次 put 提示消息体场景）
    _is_main = "/test/" not in str(path).replace("\\", "/")
    if _is_main:
        for m in MAP_DECL.finditer(src):
            tail = src[m.end():m.end() + 1200]
            if len(PUT_REF.findall(tail)) >= 2:
                line_no = src[:m.start()].count("\n") + 1
                findings.append(("WARN", f"Map 手工组装 payload（§4.1 建议强类型对象）: {path}:{line_no}"))

    # 5. 4 空格缩进比例（启发式：忽略空行/注释行/制表符行）
    non_meet = total = 0
    for ln in lines:
        if not ln.strip() or _is_comment_line(ln) or ln.startswith("\t"):
            continue
        lead = len(ln) - len(ln.lstrip(" "))
        if lead % 4 != 0:
            non_meet += 1
        total += 1
    if total and non_meet / total > 0.15:
        findings.append(("WARN", f"缩进非 4 空格比例 {non_meet}/{total}（启发式，建议人工核验）: {path}"))

    # 6. 生产日志消息语言（error/warn 英文强制；info 提示）
    for i, ln in enumerate(lines, 1):
        if LOG_CJK_ERROR.search(ln):
            findings.append(("FAIL", f"日志消息含中文（error/warn 须英文，Log Content）: {path}:{i}"))
        elif LOG_CJK_INFO.search(ln):
            findings.append(("WARN", f"日志消息含中文（新写代码 info 建议英文）: {path}:{i}"))


def _changed_java_files(src_dir):
    """git status 驱动的本 change 改动 .java 文件（develop 完成时语义）。

    非 git 仓 / git 不可用 → None（调用方回退全量）。
    """
    try:
        top = subprocess.check_output(
            ["git", "-C", str(src_dir), "rev-parse", "--show-toplevel"],
            text=True,
        ).strip()
        out = subprocess.check_output(
            ["git", "-C", top, "status", "--porcelain"], text=True
        )
        base = Path(src_dir).resolve()
        top = Path(top).resolve()
        res = []
        for ln in out.splitlines():
            if not ln.strip():
                continue
            path = ln[3:].strip().strip('"')
            p = (top / path).resolve()
            if p.suffix == ".java" and p.exists() and base in p.parents:
                res.append(p)
        return res
    except Exception:
        return None


def main(argv=None):
    ap = argparse.ArgumentParser(description="develop 格式与规范泄漏自检（A 层）")
    ap.add_argument("src_dir", nargs="?", default=".", help="Java 源目录（默认 .）")
    ap.add_argument("--changed", action="store_true",
                    help="仅查本 change（git status）改动的 .java，排除存量债噪音")
    ap.add_argument("--check-commit", action="store_true", help="额外检查最近提交 subject")
    args = ap.parse_args(argv)

    root = Path(args.src_dir)
    if not root.is_dir():
        print(f"format-check: ERROR — 源目录不存在: {root}", file=sys.stderr)
        return 2

    files = None
    if args.changed:
        files = _changed_java_files(root)
        if files is None:
            print("format-check: WARN — 非 git 仓，回退全量扫描", file=sys.stderr)
        elif not files:
            print("format-check: PASS（本 change 无改动 .java 文件）")
            return 0

    findings = []
    if files is not None:
        for p in sorted(files):
            check_file(p, findings)
    else:
        for p in sorted(root.rglob("*.java")):
            check_file(p, findings)

    if args.check_commit:
        try:
            subj = subprocess.check_output(
                ["git", "log", "-1", "--format=%s"], text=True
            ).strip()
            if COMMIT_TASK_PREFIX.match(subj):
                findings.append(("FAIL", f"最近提交 subject 以任务编号开头（Commit Content）: {subj}"))
        except Exception:
            pass  # 非 git 目录或 git 不可用：跳过

    if not findings:
        print("format-check: PASS（无格式/规范泄漏）")
        return 0

    has_fail = any(s == "FAIL" for s, _ in findings)
    has_warn = any(s == "WARN" for s, _ in findings)
    for sev, msg in findings:
        print(f"[{sev}] {msg}")
    print(f"format-check: {'FAIL' if has_fail else 'WARN' if has_warn else 'PASS'} "
          f"（FAIL={sum(1 for s,_ in findings if s=='FAIL')} "
          f"WARN={sum(1 for s,_ in findings if s=='WARN')}）")
    return 2 if has_fail else (1 if has_warn else 0)


if __name__ == "__main__":
    sys.exit(main())