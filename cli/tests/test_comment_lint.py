#!/usr/bin/env python3
"""P69 MVP 测试 —— 注释候选提取（S2）。

覆盖：
- 字符串字面量 / 文本块内的 `//` **不得**被当成注释
- 块注释内的 `//` 只算一条注释（不误拆）
- JavaDoc 识别为 javadoc 且 actionable=False（MVP 跳过）
- 行尾注释的 context_before 含本行代码；后续代码上下文跳过空行/注释行
- 所属方法 / 所属类归属（AST 权威通道 + 简单夹具下降级通道一致）
- tree-sitter 与标准库两条通道的位置/文本/类型**逐一一致**（字符偏移口径）
- CLI：--json 可解析、非法路径返回 2、目录遍历跳过 target/build

Run:
    python -m unittest cli.tests.test_comment_lint
"""

import importlib.util
import io
import json
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "tools"))


def _load(name, rel):
    spec = importlib.util.spec_from_file_location(name, REPO_ROOT / rel)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


cl = _load("comment_lint", "tools/comment-lint.py")

SAMPLE = '''package demo;

/**
 * 订单服务
 */
public class OrderService {

    // 获取用户
    public User getUser(Long id) {
        String marker = "// STRING_MARKER";
        /* BLOCK_MARKER // 块注释内的斜杠 */
        char slash = '/';
        String block = """
            // TEXTBLOCK_MARKER 文本块内不是注释
            """;
        return null; // 用户ID
    }
}
'''

# 位置/类型/文本的期望（两通道必须一致）：行号, kind, 文本片段
EXPECTED = [
    (3, cl.KIND_JAVADOC, "订单服务"),
    (8, cl.KIND_LINE, "获取用户"),
    (11, cl.KIND_BLOCK, "BLOCK_MARKER"),
    (16, cl.KIND_LINE, "用户ID"),
]


def _parsers():
    """可用通道列表（tree-sitter 缺失时只测标准库通道）。"""
    parsers = [cl.StdlibJavaParser()]
    try:
        parsers.append(cl.TreeSitterJavaParser())
    except Exception:
        pass
    return parsers


class TestLexicalCorrectness(unittest.TestCase):
    """词法正确性 —— 两通道跑同一批断言。"""

    def test_expected_comments_and_no_false_positives(self):
        for engine in _parsers():
            with self.subTest(parser=engine.name):
                comments = engine.parse(SAMPLE, "OrderService.java")
                self.assertEqual(len(comments), len(EXPECTED))
                for comment, (line, kind, snippet) in zip(comments, EXPECTED):
                    self.assertEqual(comment.line, line)
                    self.assertEqual(comment.kind, kind)
                    self.assertIn(snippet, comment.text)
                # 字符串字面量与文本块内的 `//` 绝不能成为候选
                joined = "\n".join(c.text for c in comments)
                self.assertNotIn("STRING_MARKER", joined)
                self.assertNotIn("TEXTBLOCK_MARKER", joined)

    def test_offsets_and_columns_match_source(self):
        for engine in _parsers():
            with self.subTest(parser=engine.name):
                for comment in engine.parse(SAMPLE, "OrderService.java"):
                    self.assertEqual(SAMPLE[comment.start:comment.end], comment.text)
                    line, column = cl.line_col(SAMPLE, comment.start)
                    self.assertEqual((line, column), (comment.line, comment.column))

    def test_channels_agree_on_positions(self):
        """两条通道的位置/文本/类型/偏移必须逐一一致。"""
        results = {
            engine.name: engine.parse(SAMPLE, "OrderService.java")
            for engine in _parsers()
        }
        if len(results) < 2:
            self.skipTest("只有单一解析通道可用")
        first, second = (results[name] for name in sorted(results))
        self.assertEqual(
            [c.to_dict() for c in first],
            [c.to_dict() for c in second],
        )


class TestKindAndPolicy(unittest.TestCase):
    def test_javadoc_not_actionable(self):
        comments = cl.StdlibJavaParser().parse(SAMPLE, "OrderService.java")
        javadoc = [c for c in comments if c.kind == cl.KIND_JAVADOC]
        self.assertEqual(len(javadoc), 1)
        self.assertFalse(javadoc[0].actionable)
        self.assertTrue(all(c.actionable for c in comments if c.kind != cl.KIND_JAVADOC))

    def test_single_line_block_is_javadoc(self):
        """`/** xxx */` 单行块仍属 javadoc（其拦截由 format-check 负责，本工具跳过）。"""
        source = "/** 补偿数据同步 */\nprivate String tag;\n"
        comments = cl.StdlibJavaParser().parse(source, "A.java")
        self.assertEqual(comments[0].kind, cl.KIND_JAVADOC)


class TestContext(unittest.TestCase):
    def test_trailing_comment_context_before(self):
        comments = cl.StdlibJavaParser().parse(SAMPLE, "OrderService.java")
        trailing = [c for c in comments if c.line == 16][0]
        self.assertEqual(trailing.context_before, ["return null;"])
        self.assertEqual(len(trailing.context_before), 1)   # 行尾注释不再拼上一条代码行

    def test_context_after_skips_comments_and_blanks(self):
        source = (
            "class A {\n"
            "    // 获取用户\n"
            "\n"
            "    // 又一条注释\n"
            "    User u = save();\n"
            "    return u;\n"
            "}\n"
        )
        comments = cl.StdlibJavaParser().parse(source, "A.java")
        first = comments[0]
        self.assertEqual(first.context_after, ["User u = save();", "return u;"])

    def test_indent_captured(self):
        comments = cl.StdlibJavaParser().parse(SAMPLE, "OrderService.java")
        self.assertEqual(comments[1].indent, "    ")


class TestAttribution(unittest.TestCase):
    def test_method_and_class_for_in_method_comments(self):
        """方法体内的注释：两通道都归属到方法；前导注释（声明之上）归属到类、方法为 None。"""
        for engine in _parsers():
            with self.subTest(parser=engine.name):
                comments = engine.parse(SAMPLE, "OrderService.java")
                in_body = [c for c in comments if c.line in (11, 16)]
                self.assertEqual(len(in_body), 2)
                for comment in in_body:
                    self.assertEqual(comment.method, "getUser")
                    self.assertEqual(comment.class_name, "OrderService")
                leading = [c for c in comments if c.line == 8][0]
                self.assertIsNone(leading.method)
                self.assertEqual(leading.class_name, "OrderService")

    def test_anonymous_class_is_not_a_method(self):
        source = (
            "class A {\n"
            "    Runnable r = new Runnable() {\n"
            "        // 任务体\n"
            "        public void run() { }\n"
            "    };\n"
            "}\n"
        )
        comment = cl.StdlibJavaParser().parse(source, "A.java")[0]
        self.assertEqual(comment.method, None)
        self.assertEqual(comment.class_name, "A")


class TestCli(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        (self.root / "A.java").write_text(SAMPLE, encoding="utf-8")
        (self.root / "target").mkdir()
        (self.root / "target" / "B.java").write_text("// 应被跳过\n", encoding="utf-8")

    def tearDown(self):
        self.tmp.cleanup()

    def _run(self, argv):
        out = io.StringIO()
        err = io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            code = cl.main(argv)
        return code, out.getvalue(), err.getvalue()

    def test_json_output(self):
        code, out, _ = self._run([str(self.root), "--json", "--parser", "stdlib"])
        self.assertEqual(code, 0)
        payload = json.loads(out)
        self.assertEqual(payload["parser"], "stdlib")
        self.assertEqual(payload["comments"], len(EXPECTED))
        self.assertEqual(payload["java_doc"], "skip")
        # JavaDoc 在候选中保留，但不计入进入判定的数量
        self.assertEqual(payload["actionable"], len(EXPECTED) - 1)

    def test_missing_path_returns_2(self):
        code, _, err = self._run([str(self.root / "nope.java")])
        self.assertEqual(code, 2)
        self.assertIn("路径不存在", err)

    def test_skips_build_dirs(self):
        code, out, _ = self._run([str(self.root), "--json", "--parser", "stdlib"])
        self.assertEqual(code, 0)
        paths = {c["path"] for c in json.loads(out)["candidates"]}
        self.assertTrue(all("target" not in p for p in paths))

    def test_dump_candidates_human_readable(self):
        code, out, _ = self._run([str(self.root), "--dump-candidates", "--parser", "stdlib"])
        self.assertEqual(code, 0)
        self.assertIn("注释候选：", out)


class TestDiffMode(unittest.TestCase):
    """diff 限定（S3）—— 只处理本次新增行内的注释；存量注释不被触碰。"""

    EXISTING = (
        "package demo;\n"
        "public class A {\n"
        "    // 存量注释（不得被纳入判定）\n"
        "    public void old() { }\n"
        "}\n"
    )
    WITH_NEW = (
        "package demo;\n"
        "public class A {\n"
        "    // 存量注释（不得被纳入判定）\n"
        "    public void old() { }\n"
        "\n"
        "    // 获取用户\n"
        "    public void newOne() { }\n"
        "}\n"
    )

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self.tmp.name)
        self._git("init", "-q")
        self._git("config", "user.email", "test@example.com")
        self._git("config", "user.name", "test")
        self._write(self.EXISTING)
        self._git("add", "A.java")
        self._git("commit", "-q", "-m", "init")

    def tearDown(self):
        self.tmp.cleanup()

    def _git(self, *args):
        return subprocess.run(
            ["git", "-C", str(self.repo), *args], capture_output=True, text=True
        )

    def _write(self, text, name="A.java"):
        (self.repo / name).write_text(text, encoding="utf-8")

    def _run(self, argv):
        out = io.StringIO()
        err = io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            code = cl.main(argv)
        return code, out.getvalue(), err.getvalue()

    def _json(self, *extra):
        code, out, err = self._run(
            [str(self.repo), "--diff", "--json", "--parser", "stdlib", *extra]
        )
        self.assertEqual(code, 0)
        return json.loads(out), err

    def test_only_added_line_comments_are_kept(self):
        self._write(self.WITH_NEW)
        payload, _ = self._json()
        self.assertEqual(payload["mode"], "diff")
        texts = [c["text"] for c in payload["candidates"]]
        self.assertEqual(len(texts), 1)
        self.assertIn("获取用户", texts[0])
        self.assertEqual(payload["comments"], 1)
        self.assertGreaterEqual(payload["dropped"], 1)   # 存量注释被过滤并计数

    def test_full_mode_keeps_existing_comments(self):
        self._write(self.WITH_NEW)
        code, out, _ = self._run([str(self.repo), "--json", "--parser", "stdlib"])
        self.assertEqual(code, 0)
        payload = json.loads(out)
        self.assertEqual(payload["mode"], "full")
        self.assertEqual(payload["comments"], 2)

    def test_untracked_file_is_fully_new(self):
        self._write("package demo;\n// 新增文件里的注释\nclass B { }\n", name="B.java")
        payload, _ = self._json()
        texts = [c["text"] for c in payload["candidates"]]
        self.assertEqual(len(texts), 1)
        self.assertIn("新增文件", texts[0])

    def test_pure_deletion_yields_nothing(self):
        """只删注释（无新增行）→ diff 模式不得把被删注释当候选。"""
        self._write(
            "package demo;\n"
            "public class A {\n"
            "    public void old() { }\n"
            "}\n"
        )
        payload, _ = self._json()
        self.assertEqual(payload["candidates"], [])

    def test_non_git_dir_falls_back_to_full(self):
        """非 git 目录（必须在任何仓之外）→ 退化为全量并告警。"""
        with tempfile.TemporaryDirectory() as outside:
            plain = Path(outside)
            (plain / "C.java").write_text("// 单独目录里的注释\nclass C { }\n", encoding="utf-8")
            code, out, err = self._run(
                [str(plain), "--diff", "--json", "--parser", "stdlib"]
            )
            self.assertEqual(code, 0)
            self.assertEqual(json.loads(out)["mode"], "full")
            self.assertIn("退化为全量扫描", err)

    def test_changed_alias_behaves_like_diff(self):
        self._write(self.WITH_NEW)
        code, out, _ = self._run(
            [str(self.repo), "--changed", "--json", "--parser", "stdlib"]
        )
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(out)["mode"], "diff")


if __name__ == "__main__":
    unittest.main()