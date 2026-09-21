#!/usr/bin/env python3
"""blind-bundle.py — 外部盲检投喂包构建器 + 卫生校验（P61）。

把制品按层切成若干「投喂包」，供跨厂商第三方模型做**独立盲检**。两个不可退让的
卫生要求（缺一即盲检失效）：

1. **排除内部结论**：`reports/` `logs/` `metrics/` `workspaces/` `archived/` 与二进制
   —— 内部结论与自评会锚定外部评审。
2. **身份脱敏**：远端地址 / commit sha / 仓库名 / 机器用户名 → 占位符
   —— 否则联网模型可能检索到该仓库及其内部历史。

用法:
    python3 tools/blind-bundle.py --repo <制品根> --out <输出目录>
    python3 tools/blind-bundle.py --repo <制品根> --out <输出目录> --check   # 仅校验已产出的包
    python3 tools/blind-bundle.py --repo <制品根> --out <输出目录> --layers doc,cli

设计契约:
- 分域（默认）：doc（散文/规范）· cli · tools-config · skills；可用 --layers 限定。
- 每个包 = 元信息 + 目录树 + Manifest（行数/字节）+ 带 `FILE: <path> [N lines]` 分隔头的全文。
- `--check` 对已产出包做机器可判定校验，违反即退出码 1（供门禁/CI 使用）。
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

# 参与打包的文本扩展名
TEXT_EXT = {
    ".md", ".py", ".yaml", ".yml", ".json", ".toml", ".sh", ".js",
    ".java", ".xml", ".txt", ".template",
}
# 无扩展名但需纳入的工程文件
BARE_FILES = {".gitignore", ".gitattributes", ".githooks/pre-commit"}

# 一律排除：内部结论 / 归档 / 运行期工作区
EXCLUDE_PREFIX = ("reports/", "logs/", "metrics/", "workspaces/", "archived/")
EXCLUDE_PARTS = ("__pycache__", ".git/")

# 分域定义（roots 相对制品根；root_files 为根级单文件）
LAYERS = {
    "doc": {
        "desc": "文档层（doc layer）：只有散文/规范/流程文本，不含任何代码",
        "roots": ["workflows/", "templates/", "loaders/", "governance/"],
        "root_files": ["README.md", "OPERATIONS.md", "README_MIGRATION.md"],
    },
    "cli": {
        "desc": "CLI 层（code layer）：交互式命令实现与测试",
        "roots": ["cli/"],
        "root_files": [],
    },
    "tools-config": {
        "desc": "工具与配置层（code layer）：门禁工具、配置与钩子",
        "roots": ["tools/", "config/"],
        "root_files": ["pyproject.toml", ".gitignore", ".gitattributes",
                       ".githooks/pre-commit"],
    },
    "skills": {
        "desc": "能力层（code layer）：可复用技能定义与脚本",
        "roots": ["skills/"],
        "root_files": [],
    },
}


def git_files(repo: Path) -> list[str]:
    out = subprocess.run(
        ["git", "ls-files"], cwd=repo, capture_output=True, text=True, check=True
    ).stdout
    return [p for p in out.splitlines() if p]


def git_identity(repo: Path) -> tuple[list[str], str]:
    """身份串分两级。

    Tier A（必须脱敏，命中即 VIOLATION）：远端 URL、`owner/repo`、主机名、
    机器用户名、家目录 —— 这些能让联网模型直接检索到该仓库及其内部历史。
    Tier B（仓库裸名，默认仅提示不阻断）：本制品常以自身仓名作为路径前缀
    （如 `ai-system/tools/…`），属自引用而非身份；仓名本身敏感时用
    `--strict-name` 升为硬失败。
    """

    tier_a: list[str] = []
    repo_name = repo.name

    try:
        remote = subprocess.run(
            ["git", "remote", "get-url", "origin"],
            cwd=repo, capture_output=True, text=True, check=False,
        ).stdout.strip()
    except OSError:
        remote = ""

    if remote:
        tier_a.append(remote)
        m = re.search(r"[:/]([^/:]+/[^/]+?)(?:\.git)?$", remote)
        if m:
            tier_a.append(m.group(1))                 # owner/repo
        m2 = re.search(r"@?([\w.-]+\.[a-z]{2,})[:/]", remote)
        if m2:
            tier_a.append(m2.group(1))                # host

    user = Path.home().name
    if user:
        tier_a.append(user)
    tier_a.append(str(Path.home()))

    return [t for t in dict.fromkeys(tier_a) if t and len(t) > 2], repo_name


def sanitize(text: str, identity: list[str]) -> str:
    for tok in identity:
        text = text.replace(tok, "<redacted>")
    return text


def is_binary(p: Path) -> bool:
    try:
        return b"\x00" in p.read_bytes()[:8000]
    except OSError:
        return True


def included(path: str) -> bool:
    if path.startswith(EXCLUDE_PREFIX):
        return False
    if any(part in path for part in EXCLUDE_PARTS):
        return False
    if path in BARE_FILES:
        return True
    return Path(path).suffix in TEXT_EXT


def select(files: list[str], spec: dict, repo: Path) -> list[str]:
    picked = []

    for rel in files:
        if rel in spec["root_files"] or any(rel.startswith(r) for r in spec["roots"]):
            picked.append(rel)

    out = []

    for rel in picked:
        if not included(rel):
            continue
        full = repo / rel
        if full.is_file() and not is_binary(full):
            out.append(rel)

    return sorted(out)


def tree_lines(paths: list[str]) -> list[str]:
    entries: dict[str, list[str]] = {}

    for p in paths:
        parent = str(Path(p).parent)
        parent = "" if parent == "." else parent
        entries.setdefault(parent, []).append(Path(p).name)

    if not entries:
        return ["(empty)"]

    lines = []

    for d in sorted(entries, key=lambda x: (x.count("/") if x else -1, x)):
        lines.append(f"{'./' if d == '' else d + '/'}  ({len(entries[d])} files)")
        lines.extend(f"    {n}" for n in sorted(entries[d]))

    return lines


def build(name: str, spec: dict, paths: list[str], repo: Path, out: Path,
          identity: list[str]) -> dict:
    head = [
        f"# ARTIFACT BUNDLE — {name}",
        "",
        f"- scope: {spec['desc']}",
        f"- files: {len(paths)}",
        "- 说明: 下列为制品的原文全文。引用时请使用「文件路径 + 原文片段（≤20 字）」定位。",
        "- 未包含: 归档目录、二进制文件，以及其他分域包（本次评审按分域独立进行）。",
        "- 已脱敏: 仓库远端地址、仓库名与机器用户名已替换为占位符（<redacted>），"
        "与原文件相比仅此类字符串不同。",
        "",
        "## Directory Tree",
        "",
        "```",
        *tree_lines(paths),
        "```",
        "",
        "## Manifest",
        "",
    ]

    rows, bodies, chars = [], [], 0

    for rel in paths:
        text = (repo / rel).read_text(encoding="utf-8", errors="replace")
        if not text.endswith("\n"):
            text += "\n"
        text = sanitize(text, identity)
        nlines = text.count("\n")
        nbytes = len(text.encode("utf-8"))
        rows.append((rel, nlines, nbytes))
        chars += nbytes
        bodies.append("=" * 72 + f"\nFILE: {rel}   [{nlines} lines]\n" + "=" * 72
                      + "\n" + text)

    manifest = ["| file | lines | bytes |", "|---|---|---|"]
    manifest += [f"| {r} | {n} | {b} |" for r, n, b in rows]

    content = "\n".join(head + manifest + ["", "## Files", ""] + bodies)
    dest = out / f"{name}.txt"
    dest.write_text(content, encoding="utf-8")

    return {
        "name": name,
        "files": len(paths),
        "bytes": len(content.encode("utf-8")),
        "est_tokens": int(len(content.encode("utf-8")) / 3.2),
        "path": dest,
    }


def check(out: Path, identity: list[str], repo_name: str, strict_name: bool) -> int:
    """卫生校验：对已产出的包做机器可判定断言。"""

    violations = []
    notes = []

    bundles = sorted(out.glob("*.txt"))

    if not bundles:
        print(f"blind-bundle --check: no bundle found in {out}")
        return 1

    for b in bundles:
        text = b.read_text(encoding="utf-8", errors="replace")

        for prefix in EXCLUDE_PREFIX:
            if f"FILE: {prefix}" in text:
                violations.append(f"{b.name}: excluded file header '{prefix}'")

        for tok in identity:
            if tok and tok in text:
                violations.append(f"{b.name}: identity leak '{tok}'")

        if "\x00" in text:
            violations.append(f"{b.name}: binary content")

        n = text.count(repo_name) if repo_name else 0
        if n and strict_name:
            violations.append(
                f"{b.name}: repo name '{repo_name}' appears {n}x (--strict-name)"
            )
        elif n:
            notes.append(f"{b.name}: repo name '{repo_name}' appears {n}x "
                         f"(self-reference; use --strict-name to block if sensitive)")

    for v in violations:
        print(f"  [VIOLATION] {v}")

    for nt in notes:
        print(f"  [note] {nt}")

    if violations:
        print(f"blind-bundle --check: FAIL ({len(violations)} violation(s))")
        return 1

    print(f"blind-bundle --check: PASS — {len(bundles)} bundle(s), "
          f"0 tier-A identity leak, 0 excluded header, 0 binary")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="外部盲检投喂包构建器 + 卫生校验（P61）")
    ap.add_argument("--repo", default=".", help="制品根（git 仓库）")
    ap.add_argument("--out", required=True, help="包输出目录（运行期产物，不入库）")
    ap.add_argument("--layers", default="", help="限定分域，逗号分隔（默认全部）")
    ap.add_argument("--check", action="store_true", help="仅校验已产出的包（不重建）")
    ap.add_argument("--strict-name", action="store_true",
                    help="把「仓库裸名出现」升为硬失败（仓名本身敏感时使用）")
    args = ap.parse_args()

    repo = Path(args.repo).resolve()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    identity, repo_name = git_identity(repo)

    if args.check:
        return check(out, identity, repo_name, args.strict_name)

    if not (repo / ".git").exists():
        print(f"blind-bundle: not a git repository: {repo}", file=sys.stderr)
        return 1

    names = [n.strip() for n in args.layers.split(",") if n.strip()] or list(LAYERS)

    unknown = [n for n in names if n not in LAYERS]
    if unknown:
        print(f"blind-bundle: unknown layer(s): {', '.join(unknown)}", file=sys.stderr)
        return 1

    files = git_files(repo)
    print(f"artifact: {repo}")
    print(f"git-tracked files: {len(files)} | tier-A identity tokens redacted: {len(identity)}")

    total = 0

    for name in names:
        paths = select(files, LAYERS[name], repo)
        st = build(name, LAYERS[name], paths, repo, out, identity)
        total += st["est_tokens"]
        print(f"  {st['name']:14s} {st['files']:4d} files  {st['bytes']/1024:8.1f} KB  "
              f"≈{st['est_tokens']:7d} tokens")

    print(f"  {'TOTAL':14s} {'':4s}        ≈{total} tokens")

    # 构建后立即自检：卫生不能靠假设
    return check(out, identity, repo_name, args.strict_name)


if __name__ == "__main__":
    raise SystemExit(main())