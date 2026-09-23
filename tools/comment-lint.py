#!/usr/bin/env python3
r"""注释质量检查（P69 MVP）。

只针对**本次改动新增的 Java 注释**做质量判定；策略（六级分类、规则 id、判定顺序、
安全原则）见 `governance/standards/common/documentation.md` → Comment Content / Comment Quality。
本工具**不重复**已有检查：单行块 `/** xxx */` 与注释内任务编号由 `tools/format-check.py` 拦截，
注释语言由 `tools/repo-lint.py` 检查。

阶段（P69 §5.2）：
  S2 候选提取（已落地）：注释候选 = file/行列/偏移/文本/kind/缩进/前后代码/所属方法/所属类
  S3 diff 限定（已落地）：只处理 `git diff` 新增行内的注释
  S4 规则引擎（已落地）：六级分类 + 白名单优先命中，输出 KEEP/DELETE/REVIEW
  S5 CLI 与安全（本阶段已落地）：check / fix（默认 dry-run，--apply 才写回）/ --report-only
  S6 门禁注册

解析通道（探测式导入，两条通道的输出必须一致）：
  tree-sitter  `tree-sitter-language-pack` 提供 java 语法，环境存在时默认
  stdlib       标准库词法状态机（无第三方依赖时的降级通道）

安全底线（贯穿全部阶段）：**宁可漏删，不可误删**。

用法：
    python3 tools/comment-lint.py [check] <path> [--diff|--changed] [--parser auto|tree-sitter|stdlib]
                                   [--dump-candidates] [--json] [--report-only]
    python3 tools/comment-lint.py fix <path> [--diff|--changed] [--dry-run|--apply] [--json]
exit code: 0=PASS（无 DELETE、无 REVIEW）  1=WARN（有需裁定的 REVIEW）  2=FAIL（存在确定可删的 DELETE）
           3=用法/IO/环境错误（--report-only 时封顶为 1）
"""

import argparse
import difflib
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
    own_line: bool = True     # 是否独占一行（行尾注释为 False）
    blank_after: bool = False  # 注释之后紧跟的行是否为空行（或文件到此结束）

    @property
    def actionable(self):
        """是否进入规则判定：JavaDoc 跳过（MVP 策略，可被配置覆盖）。"""
        return self.kind != KIND_JAVADOC

    @property
    def body(self):
        """去掉注释标记与首尾空白后的正文（单行注释去掉 `//`，块注释保留原样）。"""
        text = self.text
        if self.kind == KIND_LINE:
            text = text[2:]
        return text.strip()

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
            "own_line": self.own_line,
            "blank_after": self.blank_after,
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


def make_comment(source, rel_path, start, end, kind, method=None, class_name=None):
    """由位置与类型组装候选（两条解析通道共用，保证字段口径一致）。"""
    before, after = context_of(source, start, end)
    line, column = line_col(source, start)
    line_start = source.rfind("\n", 0, start) + 1
    lines = source.splitlines()
    end_line = source.count("\n", 0, end)
    next_line = lines[end_line + 1] if end_line + 1 < len(lines) else ""
    return Comment(
        path=rel_path,
        line=line,
        column=column,
        start=start,
        end=end,
        text=source[start:end],
        kind=kind,
        indent=source[line_start:start],
        context_before=before,
        context_after=after,
        method=method,
        class_name=class_name,
        own_line=not source[line_start:start].strip(),
        blank_after=not next_line.strip(),
    )


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
        return make_comment(
            source, rel_path, start, end, kind,
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
            method, class_name = _attribute(scopes, start)
            candidates.append(
                make_comment(source, rel_path, start, end, kind, method, class_name)
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
# S4：规则引擎（确定性）
#
# 判定顺序**唯一**，白名单优先命中；判定语义的唯一来源是标准：
# `governance/standards/common/documentation.md` 的注释内容章节（Comment Content / Comment Quality）。
#   1 CQ-MEANINGFUL     提供代码无法表达的信息 → KEEP（优先命中）
#   2 CQ-SECTION-HEADER 分段线 / 分隔标题      → DELETE
#   3 CQ-AI-NOISE       流程套话                 → DELETE
#   4 CQ-OBVIOUS        复述代码                 → DELETE
#   5 CQ-DUPLICATE      与方法名 / 字段名重复   → REVIEW（不自动删）
#   6 CQ-UNCERTAIN      兜底                     → REVIEW（不自动删）
#
# 安全设计：
#   · 白名单**先**命中——只要注释带承重信号（兼容/并发/性能/契约/原因…）就永不进入删除类
#   · OBVIOUS 必须同时满足「动词模式」与「与下一行代码的链接」两个条件（仅模式不删）
#   · 宁可漏删：任何不确定信号都落到 REVIEW，不落到 DELETE
# --------------------------------------------------------------------------- #

ACTION_KEEP = "KEEP"
ACTION_DELETE = "DELETE"
ACTION_REVIEW = "REVIEW"

RQ_MEANINGFUL = "CQ-MEANINGFUL"
RQ_SECTION = "CQ-SECTION-HEADER"
RQ_NOISE = "CQ-AI-NOISE"
RQ_OBVIOUS = "CQ-OBVIOUS"
RQ_DUPLICATE = "CQ-DUPLICATE"
RQ_UNCERTAIN = "CQ-UNCERTAIN"

# 承重信号词（白名单）：兼容性 / 历史 / 外部契约 / 并发时序 / 性能 / 安全 / 原因与约束
MEANINGFUL_SIGNALS = (
    # 兼容性、历史原因
    "兼容", "历史", "存量", "旧版本", "老版本", "遗留", "迁移", "不能删", "勿删", "不得删",
    "保留原", "保持原", "为了兼容",
    # 外部契约、上下游
    "契约", "协议", "上游", "下游", "第三方", "外部系统", "对方", "回调", "签名",
    "对齐", "保持一致", "接口约定", "字段映射",
    # 并发、时序、事务
    "并发", "线程安全", "加锁", "锁", "异步", "事务", "afterCommit", "幂等", "重试",
    "顺序", "时序", "竞态", "阻塞", "死锁",
    # 性能
    "性能", "批量", "缓存", "索引", "慢查询", "超时", "耗时", "内存", "避免", "减少查询",
    "一次查询", "N+1",
    # 安全
    "安全", "加密", "脱敏", "敏感", "鉴权", "越权", "注入", "防重放", "签名校验",
    # 业务规则与约束（含原因连词）
    "业务", "规则", "口径", "语义", "约定", "策略", "阈值", "权限", "角色", "状态机", "审批",
    "原因", "因为", "由于", "为了", "否则", "务必", "必须", "禁止", "不能", "不可", "不得",
    "只有", "才允许", "不允许", "仅在", "条件", "前提", "认证", "校验通过",
)

# 流程套话（AI 叙述生成过程，而非业务语义）
NOISE_MARKERS = ("首先", "其次", "接下来", "然后", "最后", "下面", "上述")
NOISE_PHRASES = (
    "这里我们", "我们这里", "接下来我们", "我们需要", "让我们", "此处我们",
    "下面开始", "下面进行", "开始进行", "开始处理",
)
NOISE_PATTERN = re.compile(r"进行.{0,6}处理|处理流程|如下所示|将会")

# 复述代码：动词模式 → 期望在下一行代码中出现的英文 token（大小写不敏感）
OBVIOUS_VERBS = {
    "获取": ("get", "fetch", "query", "load", "find"),
    "查询": ("get", "query", "find", "select", "search"),
    "读取": ("get", "read", "load"),
    "设置": ("set",),
    "赋值": ("set",),
    "返回": ("return",),
    "判断": ("if", "is", "equals", "null", "empty"),
    "检查": ("check", "verify", "if", "null", "empty"),
    "校验": ("check", "verify", "validate"),
    "遍历": ("for", "each", "stream", "iterator"),
    "循环": ("for", "while"),
    "调用": ("call", "invoke", "process", "handle", "send"),
    "创建": ("create", "new", "build"),
    "初始化": ("init",),
    "构建": ("build", "create", "new"),
    "转换": ("convert", "map", "to"),
    "保存": ("save", "insert", "persist", "update"),
    "更新": ("update",),
    "删除": ("delete", "remove"),
    "新增": ("add", "insert", "create"),
    "打印": ("print", "log", "debug"),
    "记录": ("log", "record", "trace"),
    "处理": ("process", "handle"),
    "发送": ("send", "publish", "push"),
    "接收": ("receive", "consume", "on"),
    "统计": ("count", "sum", "size"),
}

# 名词 → 英文 token（与 OBVIOUS_VERBS 共同构成「注释 ↔ 下一行代码」的链接词表）
NOUN_TOKENS = {
    "用户": ("user",), "参数": ("param", "arg"), "结果": ("result",), "列表": ("list", "users"),
    "集合": ("list", "set", "map"), "数据": ("data",), "信息": ("info", "data"),
    "服务": ("service",), "消息": ("message", "msg"), "订单": ("order",),
    "配置": ("config", "properties"), "状态": ("status", "state"), "类型": ("type",),
    "时间": ("time", "date"), "值": ("value",), "对象": ("object", "dto", "vo"),
    "数据库": ("database", "mapper", "dao", "repository"), "缓存": ("cache", "redis"),
    "日志": ("log",), "异常": ("exception", "error", "fail"), "请求": ("request", "req"),
    "响应": ("response", "resp", "result"), "文件": ("file",), "数量": ("count", "size"),
}

ASCII_TOKEN = re.compile(r"[A-Za-z_$][\w$]*")
DECORATION = re.compile(r"^[\s=*#~+\-_─—]{4,}$")
# 装饰符包裹的标题（如 `===== 数据处理 =====` / `----- 参数校验 -----`）
DECORATION_DELIMITED = re.compile(r"^[=*#~+\-─—_]{3,}\s*[^=*#~+\-─—_]+?\s*[=*#~+\-─—_]{3,}$")
BARE_LABEL = re.compile(r"^[\u4e00-\u9fff ]{2,6}$")
PUNCTUATION = re.compile(r"[，。：；、！？,.:;!?()（）]", )
DECLARATION = re.compile(
    r"\b(class|interface|enum|record)\s+[A-Za-z_$]"                     # 类型声明
    r"|\b[A-Za-z_$][\w$]*\s*\([^;]*\)\s*(?:throws[^{]*)?\{"          # 方法声明
    r"|\b(?:public|private|protected|static|final|volatile|transient)\b[^;]*;"  # 字段声明
)
# 字段声明（无括号，与调用语句区分）与枚举常量行
FIELD_DECLARATION = re.compile(r"\b(?:public|private|protected|static|final|volatile|transient)\b[^;()]*;")
ENUM_CONSTANT = re.compile(r"^[A-Z][A-Z0-9_]*\s*,?$")


STEP_PREFIX = re.compile(r"^(?:step\s*\d+\s*[:：.、]?|\d+\s*[.、)）]|[①②③④⑤⑥⑦⑧⑨⑩])\s*", re.IGNORECASE)
ADVERB_PREFIX = re.compile(r"^(?:先|再|接着|然后)\s*")


@dataclass
class Verdict:
    """一条注释的判定结果。"""

    rule_id: str
    action: str
    reason: str

    def to_dict(self):
        return {"rule_id": self.rule_id, "action": self.action, "reason": self.reason}


def classify(comment):
    """按唯一判定顺序分类；返回 (Verdict)。"""
    body = comment.body
    if not body:
        return Verdict(RQ_UNCERTAIN, ACTION_REVIEW, "空注释正文，需人工确认")

    hit = _meaningful_signal(body)
    if hit:
        return Verdict(RQ_MEANINGFUL, ACTION_KEEP, f"承重信号：{hit}")

    if _is_section_header(comment, body):
        return Verdict(RQ_SECTION, ACTION_DELETE, "分段线/分隔标题，无信息增量")

    if _is_ai_noise(body):
        return Verdict(RQ_NOISE, ACTION_DELETE, "流程套话，叙述生成过程而非业务语义")

    if _is_obvious(comment, body):
        return Verdict(RQ_OBVIOUS, ACTION_DELETE, "复述下一行代码（动词模式 + 代码链接双命中）")

    if _is_duplicate(comment, body):
        return Verdict(RQ_DUPLICATE, ACTION_REVIEW, "与方法名/字段名重复（名字直译）")

    return Verdict(RQ_UNCERTAIN, ACTION_REVIEW, "未识别出承重信息，也未确认为低价值")


def classify_all(candidates):
    """批量判定，返回 [(comment, verdict)]。"""
    return [(c, classify(c)) for c in candidates]


def _meaningful_signal(body):
    """白名单：命中即承重（优先命中，保证永不误删有语义注释）。"""
    for signal in MEANINGFUL_SIGNALS:
        if signal in body:
            return signal
    return None


def _is_section_header(comment, body):
    """分段线（纯装饰）· 装饰符包裹的标题 · 独立成段的中文短标签（后面跟空行）。"""
    if DECORATION.match(body) or DECORATION_DELIMITED.match(body):
        return True
    return bool(
        comment.own_line
        and comment.blank_after
        and BARE_LABEL.match(body)
        and not PUNCTUATION.search(body)
    )


def _is_ai_noise(body):
    """流程套话：话语标记（要求后跟顿号/逗号或直接跟复述类动词，避免「最后一次…」这类误伤）
    或第一人称叙述短语、典型套话句式。"""
    for marker in NOISE_MARKERS:
        rest = body[len(marker):]
        if body.startswith(marker) and rest:
            if rest[0] in "，,、":
                return True
            if any(rest.startswith(verb) for verb in OBVIOUS_VERBS):
                return True
    for phrase in NOISE_PHRASES:
        if phrase in body:
            return True
    return bool(NOISE_PATTERN.search(body))


def _link_tokens(body):
    """可与代码链接的**名词 / 标识符** token（不含动词）。

    动词只用于识别「这是复述句式」（见 `_leading_verb`）；真正的链接必须落在名词或标识符上。
    这条区分来自历史 diff **全量审计**：`// 删除转码流` 的下一行是 `deleteRateLimiter.tryAcquire(...)`，
    仅因变量名带 `delete` 而命中链接 —— 属巧合而非复述（真误删）。
    """
    tokens = []
    for word, mapped in NOUN_TOKENS.items():
        if word in body:
            tokens.extend(mapped)
    tokens.extend(match.lower() for match in ASCII_TOKEN.findall(body))
    return tokens


def _leading_verb(body):
    """注释**开头**的复述类动词（容忍 `Step2:` / `①` / `先` 这类短前缀）。

    只认开头动词而不认句中动词：这是精度护栏——像「待处理」「总记录数」「尝试查询…」
    这类名词短语/叙述句里的动词不构成「复述代码」，宁可漏删交给 REVIEW。
    """
    cleaned = STEP_PREFIX.sub("", body.strip())
    cleaned = ADVERB_PREFIX.sub("", cleaned)
    for verb in OBVIOUS_VERBS:
        if cleaned.startswith(verb):
            return verb
    return None


def _field_attached(comment):
    """注释是否贴在**字段 / 枚举常量**上（行上或行尾）。

    这类注释按标准属「必须写、且不能是名字直译」——名字直译是**需改**而非**可删**，
    所以不得进入确定可删类，交 REVIEW（documentation.md → Fields / Comment Quality）。
    """
    if comment.own_line:
        code = comment.context_after[0] if comment.context_after else ""
    else:
        code = comment.context_before[0] if comment.context_before else ""
    if not code:
        return False
    return bool(FIELD_DECLARATION.search(code) or ENUM_CONSTANT.match(code.strip()))


def _is_obvious(comment, body):
    """复述代码：必须**同时**满足「开头动词」与「名词/标识符链接」（仅模式不删）。

    链接对象：独立行注释 → 后续代码行；**行尾注释 → 本行代码 + 后续代码行**
    （行尾注释描述的就是它所在那一行，看上后方会永远比不中）。
    字段/枚举常量上的注释排除在外（见 `_field_attached`）。
    """
    if not _leading_verb(body):
        return False
    if _field_attached(comment):
        return False
    parts = list(comment.context_after)
    if not comment.own_line:
        parts = list(comment.context_before) + parts
    code = " ".join(parts).lower()
    if not code:
        return False
    return any(token in code for token in _link_tokens(body))


def _is_duplicate(comment, body):
    """与方法名/字段名重复：注释紧贴在声明之上，且内容词全被标识符覆盖（名字直译）。"""
    if len(body) > 16 or not comment.own_line or not comment.context_after:
        return False
    declaration = comment.context_after[0]
    if not DECLARATION.search(declaration):
        return False
    if any(verb in body for verb in OBVIOUS_VERBS):      # 带动词的不算纯名字直译
        return False
    tokens = _link_tokens(body)
    if not tokens:
        return False
    code = declaration.lower()
    return all(token in code for token in tokens)


# --------------------------------------------------------------------------- #
# S5：安全修复（只删确定类）
#
# 原则：
#   · 只动 `ACTION_DELETE`（确定可删），永不碰 JavaDoc、永不重写文本（SAFE_REWRITE 关闭）
#   · 默认 **dry-run**（打印 unified diff）；`--apply` 才写回，且打印实际删除的注释
#   · 行级重写（不靠字符偏移拼接）：独立行注释删整行，行尾注释只剥离注释部分
# --------------------------------------------------------------------------- #

MAIN_COMMANDS = ("check", "fix")


class _ArgumentParser(argparse.ArgumentParser):
    """用法错误退出码 3（与 2=FAIL 区分）。"""

    def error(self, message):
        self.print_usage(sys.stderr)
        print(f"[ERROR] {message}", file=sys.stderr)
        raise SystemExit(3)


def plan_deletions(judged):
    """按文件汇总确定可删项：整行删除（独立行注释）或行尾剥离（行尾注释）。"""
    plan = {}
    for comment, verdict in judged:
        if verdict.action != ACTION_DELETE:
            continue
        entry = plan.setdefault(comment.path, {"lines": set(), "strip": {}})
        if comment.own_line:
            last_line = comment.line + comment.text.count("\n")
            entry["lines"].update(range(comment.line, last_line + 1))
        else:
            entry["strip"][comment.line] = comment.column - 1
    return plan


def rewrite_lines(text, entry):
    """按计划重写文本：整行删除 + 行尾剥离；保持原行尾换行形态。"""
    kept = []
    for number, line in enumerate(text.splitlines(), start=1):
        if number in entry["lines"]:
            continue
        if number in entry["strip"]:
            line = line[: entry["strip"][number]].rstrip()
        kept.append(line)
    return "\n".join(kept) + ("\n" if text.endswith("\n") else "")


def apply_plan(plan, apply=False):
    """预演或执行：返回 [(path, 原文本, 新文本)]；apply=False 不写盘。"""
    results = []
    for path in sorted(plan):
        file_path = Path(path)
        try:
            text = file_path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as exc:
            print(f"[WARN] 跳过不可读文件 {path}: {exc}", file=sys.stderr)
            continue
        new_text = rewrite_lines(text, plan[path])
        if new_text == text:
            continue
        if apply:
            file_path.write_text(new_text, encoding="utf-8")
        results.append((path, text, new_text))
    return results


def _run_fix(args, judged):
    """fix 子命令：预演/执行确定可删项的删除，并自检残留。"""
    plan = plan_deletions(judged)
    deleted = sum(len(entry["lines"]) + len(entry["strip"]) for entry in plan.values())
    changes = apply_plan(plan, apply=args.apply)
    mode = "已写回" if args.apply else "预演（未写盘）"

    if args.json:
        payload = {
            "command": "fix",
            "applied": bool(args.apply),
            "removed": deleted,
            "files": [
                {
                    "path": path,
                    "diff": "".join(
                        difflib.unified_diff(
                            old.splitlines(keepends=True), new.splitlines(keepends=True),
                            fromfile=path, tofile=path,
                        )
                    ),
                }
                for path, old, new in changes
            ],
        }
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0

    print(f"fix {mode}：确定可删 {deleted} 条，涉及文件 {len(changes)} 个")
    for path, old, new in changes:
        print(f"--- {path}")
        print("".join(difflib.unified_diff(
            old.splitlines(keepends=True), new.splitlines(keepends=True),
            fromfile=path, tofile=path,
        )).rstrip("\n"))
    if not changes:
        print("（无改动）")
    return 0


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
    argv = list(sys.argv[1:] if argv is None else argv)
    command = "check"
    if argv and argv[0] in ("check", "fix"):
        command = argv.pop(0)

    parser = _ArgumentParser(
        description="注释质量检查（P69 MVP）—— 候选提取 + diff 限定 + 规则判定 + 安全修复"
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
    parser.add_argument(
        "--report-only",
        action="store_true",
        help="只报不拦：退出码封顶为 1（供 MVP 阶段门禁使用）",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="fix 子命令：真正写回文件（默认只做 dry-run 预演）",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="fix 子命令：只预览 unified diff（与默认行为一致，显式写法）",
    )
    args = parser.parse_args(argv)

    if not Path(args.path).exists():
        print(f"[ERROR] 路径不存在: {args.path}", file=sys.stderr)
        return 3

    cfg = load_config()
    choice = args.parser or cfg.get("parser", "auto")
    try:
        engine = make_parser(choice)
    except Exception as exc:                 # 请求了不可用的通道，不静默降级
        print(f"[ERROR] 无法启用解析通道 {choice}: {exc}", file=sys.stderr)
        return 3

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
    judged = classify_all(actionable)
    by_action = {}
    by_rule = {}
    for _comment, verdict in judged:
        by_action[verdict.action] = by_action.get(verdict.action, 0) + 1
        by_rule[verdict.rule_id] = by_rule.get(verdict.rule_id, 0) + 1
    failures = by_action.get(ACTION_DELETE, 0)
    reviews = by_action.get(ACTION_REVIEW, 0)
    exit_code = 2 if failures else (1 if reviews else 0)
    if args.report_only and exit_code == 2:
        exit_code = 1                      # MVP 阶段门禁：只报不拦

    if command == "fix":
        return _run_fix(args, judged)

    if args.json:
        payload = {
            "parser": engine.name,
            "mode": mode,
            "dropped": dropped,
            "java_doc": cfg.get("java_doc", "skip"),
            "comments": len(candidates),
            "actionable": len(actionable),
            "summary": {
                "KEEP": by_action.get(ACTION_KEEP, 0),
                "DELETE": failures,
                "REVIEW": reviews,
                "by_rule": by_rule,
            },
            "candidates": [c.to_dict() for c in candidates],
            "verdicts": [
                dict(c.to_dict(), verdict=v.to_dict())
                for c, v in judged
            ],
        }
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return exit_code

    by_kind = {}
    for candidate in candidates:
        by_kind[candidate.kind] = by_kind.get(candidate.kind, 0) + 1
    print(f"注释候选：{len(candidates)} 条（进入判定 {len(actionable)} 条，"
          f"JavaDoc 策略={cfg.get('java_doc', 'skip')}）")
    print(f"解析通道：{engine.name} · 模式：{mode}"
          + (f"（本次未纳入判定的存量注释 {dropped} 条）" if mode == "diff" else ""))
    for kind, count in sorted(by_kind.items()):
        print(f"  {kind}: {count}")
    print(f"判定：确定可删 DELETE={failures} · 需裁定 REVIEW={reviews} · "
          f"承重保留 KEEP={by_action.get(ACTION_KEEP, 0)}")
    for rule_id, count in sorted(by_rule.items()):
        print(f"  {rule_id}: {count}")
    for comment, verdict in judged:
        if verdict.action == ACTION_DELETE:
            print(f"  [DELETE] {comment.path}:{comment.line} {comment.body[:50]}"
                  f"  ← {verdict.rule_id}")
    if args.dump_candidates:
        for comment, verdict in judged:
            print(f"  {comment.path}:{comment.line}:{comment.column} "
                  f"[{verdict.action}/{verdict.rule_id}] {comment.body[:50]}")
            print(f"      ctx_after={comment.context_after[:1]} "
                  f"method={comment.method} class={comment.class_name}")
    return exit_code


if __name__ == "__main__":
    sys.exit(main())