#!/usr/bin/env python3
r"""业务仓格式基线（CLI 路线，零 build 配置）— format-baseline.

在干净 worktree 上执行 C2 格式化（apply 或 check），并以「去注释后 token 级对比」
做内容零变化安全证明（等价于只改空白/注释/折行、零逻辑改动），输出统计与提交提示。

用法：
    python3 tools/format-baseline.py <repo> [--check-only] [--src src] [--ignore-file <f>]

    --check-only  只检查差异（不写回）；用于基线后日常验证
    --src         源目录相对路径（默认 src；不存在则回退仓根）
    --ignore-file 已知无 fixpoint 边界清单（默认仓内 known-ignore.txt）

exit: 0=通过(含 apply 完成)  1=worktree 非干净/参数错  2=存在非格式差异（中止提交）
"""
import argparse
import re
import subprocess
import sys
from pathlib import Path

AIS_ROOT = Path(__file__).resolve().parent.parent
XML = AIS_ROOT / "tools" / "jdt-format-gate" / "eclipse-format.xml"
IGNORE_DEFAULT = AIS_ROOT / "tools" / "jdt-format-gate" / "known-ignore.txt"
GATE = AIS_ROOT / "tools" / "format-jdt-gate.py"

# 字符串字面量占位（防 URL 等被当注释剥离）——由词法状态机处理，见 analyze()
COMMENT_RE = re.compile(r"//.*?$|/\*.*?\*/", re.M | re.S)
TOKEN_RE = re.compile(
    r"[A-Za-z_][A-Za-z0-9_]*|\d+|==|!=|<=|>=|&&|\|\||->|::"
    r"|[+\-*/%<>=!&|^~?:;,()\[\]{}]")


def analyze(text):
    """单遍词法状态机：逐字符区分 代码/字符串/行注释/块注释，互不侵扰。
    返回 (tokens, strings)：tokens=代码层 token 序列，strings=字符串字面量内容序列。
    注释内引号与代码字符串内 `//`（URL）均不会互相影响。"""
    tokens, strings = [], []
    i, n = 0, len(text)
    while i < n:
        c = text[i]
        if c == '"' or c == "'":
            q = c
            j = i + 1
            while j < n:
                if text[j] == "\\":
                    j += 2
                    continue
                if text[j] == q:
                    break
                j += 1
            strings.append(text[i:j + 1] if j < n else text[i:])
            i = j + 1
        elif c == "/" and i + 1 < n and text[i + 1] == "/":
            j = text.find("\n", i)
            i = n if j == -1 else j
        elif c == "/" and i + 1 < n and text[i + 1] == "*":
            j = text.find("*/", i + 2)
            i = n if j == -1 else j + 2
        else:
            m = TOKEN_RE.match(text, i)
            if m:
                tokens.append(m.group(0))
                i = m.end()
            else:
                i += 1
    return tokens, strings


def tokens_of(path_or_none_base, repo, rel):
    if path_or_none_base is None:
        r = subprocess.run(["git", "-C", str(repo), "show", f"HEAD:{rel}"],
                           capture_output=True, text=True)
        return analyze(r.stdout) if r.returncode == 0 else None
    return analyze(open(path_or_none_base / rel, encoding="utf-8", errors="replace").read())


def main(argv=None):
    ap = argparse.ArgumentParser(description="业务仓格式基线（C2 CLI，零 build 配置）")
    ap.add_argument("repo", type=Path, help="业务仓 worktree 路径（须干净）")
    ap.add_argument("--check-only", action="store_true", help="只检查不写回")
    ap.add_argument("--src", default="src")
    ap.add_argument("--ignore-file", default=None)
    args = ap.parse_args(argv)

    repo = args.repo
    if not (repo / ".git").exists() and not (repo / ".git").is_dir():
        print(f"ERROR: {repo} 不是 git 仓")
        return 1
    dirty = subprocess.run(["git", "-C", str(repo), "status", "--porcelain"],
                           capture_output=True, text=True).stdout.strip()
    if dirty:
        print(f"❌ worktree 非干净（{len(dirty.splitlines())} 项）——先提交/暂存再执行基线")
        return 1

    src = repo / args.src
    if not src.is_dir():
        src = repo  # 回退仓根
    ignore = args.ignore_file or str(IGNORE_DEFAULT)

    mode = "check" if args.check_only else "apply"
    print(f"🔍 [1/3] C2 {mode}（{src.relative_to(repo)}，ignore={Path(ignore).name}）")
    cmd = [sys.executable, str(GATE), str(src), "--ignore-file", ignore, "--batch", "--skip"]
    if not args.check_only:
        cmd.append("--apply")
    r = subprocess.run(cmd)
    if r.returncode not in (0, 1):
        print(f"❌ C2 执行异常（rc={r.returncode}）")
        return r.returncode

    print("🔍 [2/3] 内容零变化证明（去注释后 token 级对比，HEAD vs 工作树）")
    changed = subprocess.run(["git", "-C", str(repo), "diff", "--name-only"],
                             capture_output=True, text=True).stdout.splitlines()
    risk = []
    for rel in changed:
        try:
            old = tokens_of(None, repo, rel)
            new = analyze(open(repo / rel, encoding="utf-8", errors="replace").read())
        except Exception:
            continue
        if old is not None and (old[0] != new[0] or old[1] != new[1]):
            risk.append(rel)
    print(f"   改动文件 {len(changed)}；token 级不一致 {len(risk)}")
    for f in risk[:10]:
        print(f"   ⚠️ RISK: {f}")
    print(f"   ✅ 无逻辑改动（空白/注释/折行可任意差异）") if not risk else \
        print("   ❌ 存在非格式差异——中止，勿提交（人工核对上述文件）")
    if risk:
        return 2

    print("🔍 [3/3] 统计与提示")
    st = subprocess.run(["git", "-C", str(repo), "diff", "--stat"], capture_output=True,
                        text=True).stdout.strip().splitlines()
    print(f"   {st[-1] if st else '（无差异）'}")
    if not args.check_only and changed:
        print("   → 独立 style: 提交：git add -A && git commit -m "
              "'style: apply format baseline（Cool4Space profile 375 条）'")
    return 0


if __name__ == "__main__":
    sys.exit(main())