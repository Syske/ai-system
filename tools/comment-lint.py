#!/usr/bin/env python3
r"""注释质量检查（P69 MVP）。

只针对**本次改动新增的 Java 注释**做质量判定；策略（六级分类、规则 id、判定顺序、
安全原则）见 `governance/standards/common/documentation.md` → Comment Content / Comment Quality。
本工具**不重复**已有检查：单行块 `/** xxx */` 与注释内任务编号由 `tools/format-check.py` 拦截，
注释语言由 `tools/repo-lint.py` 检查。

阶段（P69 §5.2）：
  S2 候选提取（已落地）：注释候选 = file/行列/偏移/文本/kind/缩进/前后代码/所属方法/所属类
  S3 diff 限定（本阶段已落地）：只处理 `git diff` 新增行内的注释
  S4 规则引擎 · S5 CLI 与安全（fix） · S6 门禁注册

解析通道（探测式导入，两条通道的输出必须一致）：
  tree-sitter  `tree-sitter-language-pack` 提供 java 语法，环境存在时默认
  stdlib       标准库词法状态机（无第三方依赖时的降级通道）

安全底线（贯穿全部阶段）：**宁可漏删，不可误删**。

用法：
    python3 tools/comment-lint.py <path> [--diff|--changed]
                                  [--parser auto|tree-sitter|stdlib]
                                  [--dump-candidates] [--json]
exit code: 0=提取成功  2=用法/IO/环境错误（规则判定与 1/2 语义在 S4/S5 接入）
"""

import argparse
import json
import re
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

AIS = Path(__file__).resolve().parents[1]
CONFIG = AIS / "config" / "comment-lint.yaml"

KIND_LINE = "line"
KIND_BLOCK = "block"
KIND_JAVADOC = "javadoc"

SKIP_DIRS = {"target", "build", "out", ".git", "node_modules", "__pycache__", ".idea"}

DEFAULT_CONFIG = {
    # JavaDoc 不参与自动删除（可能属 API 契约）
    "java_doc": "skip",
    # auto = 有 tree-sitter 用之，否则降级标准库词法
    "parser": "auto",
}


# --------------------------------------------------------------------------- #
# 候选数据结构
# --------------------------------------------------------------------------- #


@dataclass
class Comment:
    """一条注释候选（偏移为 Python str 的字符偏移，两条解析通道口径一致）。"""

    path: str
    line: int          # 1-based 行号
    column: int        # 1-based 字符列号
    start: int         # 起始字符偏移（含 `//` 或 `/*`）
    end: int           # 结束字符偏移（不含行尾换行）
    text: str          # 注释原文
    kind: str          # line / block / javadoc
    indent: str        # 注释所在行的前导空白
    context_before: list = field(default_factory=list)
    context_after: list = field(default_factory=list)
    method: str = None
    class_name: str = None

    @property
    def actionable(self):
        """是否进入规则判定：JavaDoc 跳过（MVP 策略，可被配置覆盖）。"""
        return self.kind != KIND_JAVADOC

    def to_dict(self):
        return {
            "path": self.path,
            "line": self.line,
            "column": self.column,
            "start": self.start,
            "end": self.end,
            "text": self.text,
            "kind": self.kind,
            "indent": self.indent,
            "context_before": list(self.context_before),
            "context_after": list(self.context_after),
            "method": self.method,
            "class_name": self.class_name,
            "actionable": self.actionable,
        }


# --------------------------------------------------------------------------- #
# 通用工具
# --------------------------------------------------------------------------- #


def load_config():
    """读取行为参数（config 缺失或 PyYAML 不可用时退回默认值）。"""
    cfg = dict(DEFAULT_CONFIG)
    try:
        import yaml
    except ImportError:
        return cfg
    if CONFIG.exists():
        try:
            data = yaml.safe_load(CONFIG.read_text(encoding="utf-8")) or {}
        except Exception:
            return cfg
        if isinstance(data, dict):
            cfg.update({k: v for k, v in data.items() if v is not None})
    return cfg


def line_col(source, offset):
    """字符偏移 → (1-based 行号, 1-based 字符列号)。"""
    line = source.count("\n", 0, offset) + 1
    last_nl = source.rfind("\n", 0, offset)
    return line, offset - (last_nl + 1) + 1


def char_offset(src_bytes, byte_offset):
    """tree-sitter 的字节偏移 → 字符偏移（与标准库通道同一口径）。"""
    return len(src_bytes[:byte_offset].decode("utf-8", "replace"))


def _is_comment_line(stripped):
    return stripped.startswith(("//", "/*", "*"))


def context_of(source, start, end):
    """取注释的紧邻代码上下文：context_before 最多 1 条，context_after 最多 2 条。

    before 语义：行尾注释 → 本行注释之前的代码；独立行注释 → 上一条代码行。
    after 语义：后续代码行（跳过空行与纯注释行），最多的 2 条。
    """
    lines = source.splitlines()

    before = []
    line_start = source.rfind("\n", 0, start) + 1
    same_line = source[line_start:start].strip()
    if same_line:                      # 行尾注释：本行代码即紧邻前文（不再看上一条代码行，避免噪音）
        before.append(same_line)
    else:
        first_line = source.count("\n", 0, start)
        for idx in range(first_line - 1, -1, -1):
            if idx >= len(lines):
                continue
            stripped = lines[idx].strip()
            if not stripped or _is_comment_line(stripped):
                continue
            before.append(stripped)
            break

    after = []
    last_line = source.count("\n", 0, end)
    for idx in range(last_line + 1, len(lines)):
        stripped = lines[idx].strip()
        if not stripped or _is_comment_line(stripped):
            continue
        after.append(stripped)
        if len(after) >= 2:
            break
    return before, after


# --------------------------------------------------------------------------- #
# 解析通道 1：tree-sitter（AST）
# --------------------------------------------------------------------------- #

TS_TYPE_NODES = {
    "class_declaration",
    "interface_declaration",
    "enum_declaration",
    "record_declaration",
    "annotation_type_declaration",
}
TS_METHOD_NODES = {"method_declaration", "constructor_declaration"}


class TreeSitterJavaParser:
    """tree-sitter java 语法通道（权威通道）。"""

    name = "tree-sitter"

    def __init__(self):
        from tree_sitter_language_pack import get_parser

        self._parser = get_parser("java")

    def parse(self, source, rel_path):
        src_bytes = source.encode("utf-8")
        tree = self._parser.parse(src_bytes)
        found = []
        _walk_comments(tree.root_node, found)
        candidates = []
        for node in found:
            start = char_offset(src_bytes, node.start_byte)
            end = char_offset(src_bytes, node.end_byte)
            candidates.append(
                self._build(source, rel_path, start, end, node)
            )
        return candidates

    def _build(self, source, rel_path, start, end, node):
        text = source[start:end]
        if node.type == "line_comment":
            kind = KIND_LINE
        elif text.startswith("/**") and not text.startswith("/**/"):
            kind = KIND_JAVADOC
        else:
            kind = KIND_BLOCK
        before, after = context_of(source, start, end)
        line, column = line_col(source, start)
        return Comment(
            path=rel_path,
            line=line,
            column=column,
            start=start,
            end=end,
            text=text,
            kind=kind,
            indent=source[source.rfind("\n", 0, start) + 1 : start],
            context_before=before,
            context_after=after,
            method=_ts_ancestor_name(node, TS_METHOD_NODES),
            class_name=_ts_ancestor_name(node, TS_TYPE_NODES),
        )


def _walk_comments(node, out):
    if node.type in ("line_comment", "block_comment"):
        out.append(node)
        return
    for child in node.children:
        _walk_comments(child, out)


def _ts_ancestor_name(node, types):
    parent = node.parent
    while parent is not None:
        if parent.type in types:
            name = parent.child_by_field_name("name")
            if name is not None:
                return name.text.decode("utf-8", "replace")
            return None
        parent = parent.parent
    return None


# --------------------------------------------------------------------------- #
# 解析通道 2：标准库词法状态机（降级通道）
# --------------------------------------------------------------------------- #


class StdlibJavaParser:
    """无第三方依赖的词法通道：识别注释/字符串/字符/文本块，并推算作用域归属。"""

    name = "stdlib"

    def parse(self, source, rel_path):
        spans, cleaned = _lex(source)
        scopes = _scopes(cleaned)
        candidates = []
        for start, end, kind in spans:
            text = source[start:end]
            before, after = context_of(source, start, end)
            line, column = line_col(source, start)
            method, class_name = _attribute(scopes, start)
            candidates.append(
                Comment(
                    path=rel_path,
                    line=line,
                    column=column,
                    start=start,
                    end=end,
                    text=text,
                    kind=kind,
                    indent=source[source.rfind("\n", 0, start) + 1 : start],
                    context_before=before,
                    context_after=after,
                    method=method,
                    class_name=class_name,
                )
            )
        return candidates


def _skip_quoted(source, index, quote):
    """跳过字符串/字符字面量，返回闭合引号之后的下标（处理反斜杠转义）。"""
    i = index + 1
    n = len(source)
    while i < n:
        ch = source[i]
        if ch == "\\":
            i += 2
            continue
        if ch == quote:
            return i + 1
        if ch == "\n" and quote == "'":     # 非法字符字面量，防越界
            return i
        i += 1
    return n


def _lex(source):
    """返回 (注释跨度列表, 等长 cleaned 文本)；cleaned 用空格替换注释，保留换行以对齐行号。"""
    spans = []
    buf = list(source)
    i = 0
    n = len(source)
    while i < n:
        ch = source[i]
        if ch == "/" and i + 1 < n:
            nxt = source[i + 1]
            if nxt == "/":
                stop = source.find("\n", i)
                stop = n if stop == -1 else stop
                spans.append((i, stop, KIND_LINE))
                _blank(buf, i, stop)
                i = stop
                continue
            if nxt == "*":
                stop = source.find("*/", i + 2)
                stop = n if stop == -1 else stop + 2
                if source.startswith("/**", i) and not source.startswith("/**/", i):
                    kind = KIND_JAVADOC
                else:
                    kind = KIND_BLOCK
                spans.append((i, stop, kind))
                _blank(buf, i, stop)
                i = stop
                continue
        if ch == '"':
            if source.startswith('"""', i):          # 文本块（Java 15+）
                stop = source.find('"""', i + 3)
                stop = n if stop == -1 else stop + 3
                _blank(buf, i, stop)
                i = stop
                continue
            i = _skip_quoted(source, i, '"')
            continue
        if ch == "'":
            i = _skip_quoted(source, i, "'")
            continue
        i += 1
    return spans, "".join(buf)


def _blank(buf, start, stop):
    for k in range(start, min(stop, len(buf))):
        if buf[k] != "\n":
            buf[k] = " "


def _scopes(cleaned):
    """扫描 cleaned 文本，返回块作用域区间 [(start, end, kind, name)]，kind ∈ type/method/block。"""
    stack = []
    ranges = []
    boundary = 0
    for idx, ch in enumerate(cleaned):
        if ch == "{":
            kind, name = _classify_header(cleaned[boundary:idx])
            stack.append((idx, kind, name))
            boundary = idx + 1
        elif ch == "}":
            if stack:
                start, kind, name = stack.pop()
                ranges.append((start, idx, kind, name))
            boundary = idx + 1
        elif ch == ";":
            boundary = idx + 1
    for start, kind, name in stack:          # 语法不完整（未闭合）
        ranges.append((start, len(cleaned), kind, name))
    return ranges


NON_METHOD_KEYWORDS = re.compile(
    r"\b(if|for|while|switch|catch|synchronized|do|else|return|assert|try)\b"
)
TYPE_HEADER = re.compile(r"\b(class|interface|enum|record)\s+([A-Za-z_$][\w$]*)")
ANON_HEADER = re.compile(r"\bnew\s+[A-Za-z_$][\w$.<>,\s]*\(")
METHOD_HEADER = re.compile(
    r"([A-Za-z_$][\w$]*)\s*\([^()]*\)\s*(?:throws\s+[\w\s,.$]+)?$"
)


def _classify_header(header):
    head = header.strip()
    if not head:
        return "block", None
    match = TYPE_HEADER.search(head)
    if match:
        return "type", match.group(2)
    if ANON_HEADER.search(head):             # 匿名类：作用域属类型，但无名
        return "type", None
    match = METHOD_HEADER.search(head)
    if match and not NON_METHOD_KEYWORDS.search(head):
        return "method", match.group(1)
    return "block", None


def _attribute(ranges, offset):
    """注释偏移落在哪个作用域：返回 (最内层方法名, 最内层类名)。"""
    method = None
    class_name = None
    method_at = -1
    class_at = -1
    for start, end, kind, name in ranges:
        if not (start <= offset < end) or not name:
            continue
        if kind == "method" and start > method_at:
            method, method_at = name, start
        elif kind == "type" and start > class_at:
            class_name, class_at = name, start
    return method, class_name


# --------------------------------------------------------------------------- #
# S3：diff 限定（只处理本次改动新增行内的注释）
#
# 语义与仓内既有增量门禁一致（三处各自持有同口径实现，本工具沿用同一形态）：
#   改动文件 = `git status --porcelain`（含未跟踪；rename 取新路径）
#   新增行   = `git diff -U0 HEAD -- <rel>` 的 hunk 头（新增侧行号）
#   非 git 仓 / 无 HEAD 提交 / 未跟踪文件 → 整文件视为新增（同 format-check 的回退语义）
# --------------------------------------------------------------------------- #

HUNK_RE = re.compile(r"^@@ -\d+(?:,\d+)? \+(\d+)(?:,(\d+))? @@")


def git_repo_root(start):
    """返回 git 仓库根；非 git 仓返回 None。"""
    try:
        out = subprocess.run(
            ["git", "-C", str(start), "rev-parse", "--show-toplevel"],
            capture_output=True, text=True, timeout=30,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    if out.returncode != 0:
        return None
    return Path(out.stdout.strip())


def git_changed_java_files(repo_root, target):
    """`git status --porcelain` 取改动中的 .java（含未跟踪）；target 为文件时只关心它自身。"""
    try:
        out = subprocess.run(
            ["git", "-C", str(repo_root), "status", "--porcelain"],
            capture_output=True, text=True, timeout=60,
        )
    except (OSError, subprocess.SubprocessError):
        return []
    if out.returncode != 0:
        return []

    files = []
    for raw in out.stdout.splitlines():
        entry = raw[3:].strip()
        if " -> " in entry:                     # rename：取新路径
            entry = entry.split(" -> ", 1)[1]
        entry = entry.strip('"')
        path = (repo_root / entry).resolve()
        if path.suffix != ".java":
            continue
        if target.is_file() and path != target.resolve():
            continue
        if target.is_dir() and not str(path).startswith(str(target.resolve())):
            continue
        files.append(path)
    return sorted(files)


def git_added_lines(repo_root, path):
    """文件相对 HEAD 的新增行号集合；未跟踪/无 HEAD/非 git 语义 → None（整文件视为新增）。"""
    try:
        rel = path.resolve().relative_to(repo_root)
    except ValueError:
        return None
    try:
        out = subprocess.run(
            ["git", "-C", str(repo_root), "diff", "-U0", "HEAD", "--", str(rel)],
            capture_output=True, text=True, timeout=60,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    if out.returncode != 0:                    # 无 HEAD（首提交）等
        return None
    if not out.stdout.strip():                 # 未跟踪或无差异 → 改动收集已限定文件，此处整文件视为新增
        return None

    added = set()
    for line in out.stdout.splitlines():
        match = HUNK_RE.match(line)
        if not match:
            continue
        start = int(match.group(1))
        count = int(match.group(2) or 1)
        added.update(range(start, start + count))
    return added


def comment_lines(comment):
    """注释覆盖的行号区间（多行块注释返回整个区间）。"""
    return range(comment.line, comment.line + comment.text.count("\n") + 1)


def filter_added(candidates, added_map):
    """只保留落在新增行内的注释；added_map 值为 None 表示整文件视为新增。"""
    kept, dropped = [], 0
    for comment in candidates:
        added = added_map.get(comment.path)
        if added is None or any(line in added for line in comment_lines(comment)):
            kept.append(comment)
        else:
            dropped += 1
    return kept, dropped


def discover_diff_targets(root):
    """diff 模式的扫描范围（改动中的 .java）；非 git 仓返回 None。"""
    target = Path(root)
    repo_root = git_repo_root(target if target.is_dir() else target.parent)
    if repo_root is None:
        return None
    return repo_root, target


# --------------------------------------------------------------------------- #
# 候选提取与 CLI
# --------------------------------------------------------------------------- #


def make_parser(choice):
    """构造解析通道；choice ∈ auto/tree-sitter/stdlib。"""
    if choice == "stdlib":
        return StdlibJavaParser()
    if choice == "tree-sitter":
        return TreeSitterJavaParser()
    try:
        return TreeSitterJavaParser()
    except Exception:
        return StdlibJavaParser()


def iter_java_files(root):
    root = Path(root)
    if root.is_file():
        return [root] if root.suffix == ".java" else []
    files = []
    for path in sorted(root.rglob("*.java")):
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        files.append(path)
    return files


def _rel_path(path, cwd):
    try:
        return str(path.resolve().relative_to(cwd))
    except ValueError:
        return str(path)


def _read_source(path):
    """读取源文件；不可读时告警并返回 None（不阻断整体扫描）。"""
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        print(f"[WARN] 跳过不可读文件 {path}: {exc}", file=sys.stderr)
        return None


def collect(root, parser):
    """遍历 java 文件，返回候选列表（path 相对当前工作目录，便于阅读）。"""
    cwd = Path.cwd()
    candidates = []
    for path in iter_java_files(root):
        source = _read_source(path)
        if source is None:
            continue
        candidates.extend(parser.parse(source, _rel_path(path, cwd)))
    return candidates


def collect_changed(repo_root, target, parser):
    """diff 模式：只保留改动文件中**新增行**内的注释，返回 (候选, 被过滤掉的存量条数)。"""
    cwd = Path.cwd()
    candidates = []
    added_map = {}
    for path in git_changed_java_files(repo_root, target):
        source = _read_source(path)
        if source is None:
            continue
        rel = _rel_path(path, cwd)
        added_map[rel] = git_added_lines(repo_root, path)
        candidates.extend(parser.parse(source, rel))
    return filter_added(candidates, added_map)


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="注释质量检查（P69 MVP）—— 当前阶段：候选提取 + diff 限定"
    )
    parser.add_argument("path", help="Java 文件或目录")
    parser.add_argument(
        "--diff",
        "--changed",
        dest="diff",
        action="store_true",
        help="只处理 git diff 新增行内的注释（同仓内既有增量门禁语义）",
    )
    parser.add_argument(
        "--parser",
        choices=["auto", "tree-sitter", "stdlib"],
        default=None,
        help="解析通道（默认取 config/comment-lint.yaml 的 parser）",
    )
    parser.add_argument("--dump-candidates", action="store_true", help="逐条打印候选")
    parser.add_argument("--json", action="store_true", help="以 JSON 输出")
    args = parser.parse_args(argv)

    if not Path(args.path).exists():
        print(f"[ERROR] 路径不存在: {args.path}", file=sys.stderr)
        return 2

    cfg = load_config()
    choice = args.parser or cfg.get("parser", "auto")
    try:
        engine = make_parser(choice)
    except Exception as exc:                 # 请求了不可用的通道，不静默降级
        print(f"[ERROR] 无法启用解析通道 {choice}: {exc}", file=sys.stderr)
        return 2

    mode = "full"
    dropped = 0
    candidates = []
    if args.diff:
        resolved = discover_diff_targets(args.path)
        if resolved is None:
            print("[WARN] 非 git 仓库，--diff 退化为全量扫描", file=sys.stderr)
        else:
            repo_root, target = resolved
            mode = "diff"
            candidates, dropped = collect_changed(repo_root, target, engine)
    if mode == "full":
        candidates = collect(args.path, engine)

    actionable = [
        c for c in candidates
        if cfg.get("java_doc", "skip") != "skip" or c.actionable
    ]

    if args.json:
        payload = {
            "parser": engine.name,
            "mode": mode,
            "dropped": dropped,
            "java_doc": cfg.get("java_doc", "skip"),
            "comments": len(candidates),
            "actionable": len(actionable),
            "candidates": [c.to_dict() for c in candidates],
        }
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0

    by_kind = {}
    for candidate in candidates:
        by_kind[candidate.kind] = by_kind.get(candidate.kind, 0) + 1
    print(f"注释候选：{len(candidates)} 条（进入判定 {len(actionable)} 条，"
          f"JavaDoc 策略={cfg.get('java_doc', 'skip')}）")
    print(f"解析通道：{engine.name} · 模式：{mode}"
          + (f"（本次未纳入判定的存量注释 {dropped} 条）" if mode == "diff" else ""))
    for kind, count in sorted(by_kind.items()):
        print(f"  {kind}: {count}")
    if args.dump_candidates:
        for candidate in candidates:
            flag = "" if candidate.actionable else " [skip]"
            print(f"  {candidate.path}:{candidate.line}:{candidate.column}{flag} "
                  f"{candidate.text.strip()[:60]}")
            print(f"      ctx_after={candidate.context_after[:1]} "
                  f"method={candidate.method} class={candidate.class_name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())