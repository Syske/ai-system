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
        self.assertEqual(code, 2)         # SAMPLE 含 `// 获取用户` → 确定可删 → FAIL
        payload = json.loads(out)
        self.assertEqual(payload["parser"], "stdlib")
        self.assertEqual(payload["comments"], len(EXPECTED))
        self.assertEqual(payload["java_doc"], "skip")
        # JavaDoc 在候选中保留，但不计入进入判定的数量
        self.assertEqual(payload["actionable"], len(EXPECTED) - 1)
        self.assertGreaterEqual(payload["summary"]["DELETE"], 1)

    def test_missing_path_returns_3(self):
        code, _, err = self._run([str(self.root / "nope.java")])
        self.assertEqual(code, 3)
        self.assertIn("路径不存在", err)

    def test_skips_build_dirs(self):
        code, out, _ = self._run([str(self.root), "--json", "--parser", "stdlib"])
        self.assertIn(code, (1, 2))       # SAMPLE 含确定可删项与待裁定项
        paths = {c["path"] for c in json.loads(out)["candidates"]}
        self.assertTrue(all("target" not in p for p in paths))

    def test_dump_candidates_human_readable(self):
        code, out, _ = self._run([str(self.root), "--dump-candidates", "--parser", "stdlib"])
        self.assertIn(code, (1, 2))
        self.assertIn("注释候选：", out)
        self.assertIn("判定：", out)


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
        self.assertIn(code, (1, 2))       # 判定语义生效后：有 DELETE/REVIEW 即非 0
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
        self.assertIn(code, (1, 2))
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
        """只删注释（无新增行）→ diff 模式不得把被删注释当候选（无候选则 PASS）。"""
        self._write(
            "package demo;\n"
            "public class A {\n"
            "    public void old() { }\n"
            "}\n"
        )
        code, out, _ = self._run(
            [str(self.repo), "--diff", "--json", "--parser", "stdlib"]
        )
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(out)["candidates"], [])

    def test_non_git_dir_falls_back_to_full(self):
        """非 git 目录（必须在任何仓之外）→ 退化为全量并告警。"""
        with tempfile.TemporaryDirectory() as outside:
            plain = Path(outside)
            (plain / "C.java").write_text("// 单独目录里的注释\nclass C { }\n", encoding="utf-8")
            code, out, err = self._run(
                [str(plain), "--diff", "--json", "--parser", "stdlib"]
            )
            self.assertIn(code, (1, 2))
            self.assertEqual(json.loads(out)["mode"], "full")
            self.assertIn("退化为全量扫描", err)

    def test_changed_alias_behaves_like_diff(self):
        self._write(self.WITH_NEW)
        code, out, _ = self._run(
            [str(self.repo), "--changed", "--json", "--parser", "stdlib"]
        )
        self.assertIn(code, (1, 2))
        self.assertEqual(json.loads(out)["mode"], "diff")


# --------------------------------------------------------------------------- #
# S4：规则引擎
# --------------------------------------------------------------------------- #


def _classify_line(comment_text, next_line, own_line=True, blank_after=False):
    """构造单条候选并判定（把注释放在独立行，下一行给代码）。"""
    source = f"class A {{\n    {comment_text}\n{'' if not blank_after else chr(10)}    {next_line}\n}}\n"
    comments = cl.StdlibJavaParser().parse(source, "A.java")
    target = [c for c in comments if own_line == c.own_line][0]
    return cl.classify(target)


# 安全底线：承重（有语义）注释六类反例 —— 必须**零误判删**、且判定为 KEEP
MEANINGFUL_CASES = {
    "兼容性/历史": [
        "// 老版本数据可能没有 tenantId，因此这里不能使用默认租户。",
        "// Redis key 必须与旧版本保持兼容，否则存量缓存无法命中。",
        "// 该字段为兼容旧接口保留，勿删。",
    ],
    "外部契约": [
        "// 与上游 BOSS 约定的字段映射：enterpriseId ↔ companyId。",
        "// 下游 RPC 返回 code=0 才是成功，其余按失败处理。",
        "// 对齐三方支付回调签名算法，改动需双方同步。",
    ],
    "并发/时序": [
        "// 此处必须使用 afterCommit，否则 MQ 消息可能早于事务提交发送。",
        "// 下游 RPC 客户端不是线程安全的，因此这里不能使用 parallelStream。",
        "// 先删缓存再更新库，避免并发下读到旧值。",
    ],
    "性能": [
        "// 一次批量查询代替 N+1，避免逐条查库。",
        "// 该查询走 idx_tenant_status 索引，超时阈值 3s。",
        "// 缓存 5 分钟，减少下游压力。",
    ],
    "安全": [
        "// 手机号需脱敏后落库，禁止明文。",
        "// 校验签名防止重放攻击。",
        "// 越权检查：非本租户数据一律拒绝。",
    ],
    "业务规则": [
        "// 只有企业已认证时才允许发起全量同步。",
        "// 审批中的单据不允许再次提交。",
        "// 状态机：CREATED → PAID → SHIPPED，不可逆。",
    ],
}

# 泔水样本 —— 期望的规则 id（确定可删三类 + 不自动删两类）
SLOP_CASES = [
    ("// 获取用户", "User user = userService.getUser(id);", cl.RQ_OBVIOUS),
    ("// 判断用户是否为空", "if (user == null) {", cl.RQ_OBVIOUS),
    ("// 返回结果", "return result;", cl.RQ_OBVIOUS),
    ("// 遍历用户列表", "for (User user : users) {", cl.RQ_OBVIOUS),
    ("// 调用服务处理用户", "userService.process(user);", cl.RQ_OBVIOUS),
    ("// 设置用户ID", "user.setUserId(id);", cl.RQ_OBVIOUS),
    ("// 保存订单", "orderRepository.save(order);", cl.RQ_OBVIOUS),
    ("// 更新用户状态", "userMapper.updateStatus(user);", cl.RQ_OBVIOUS),
    ("// 初始化配置", "initConfig();", cl.RQ_OBVIOUS),
    ("// 查询订单列表", "List<Order> list = orderMapper.selectList(q);", cl.RQ_OBVIOUS),
    ("// 检查用户是否存在", "if (userRepository.existsById(id)) {", cl.RQ_OBVIOUS),
    ("// 打印日志", "log.info(\"done\");", cl.RQ_OBVIOUS),
    ("// 记录请求参数", "log.info(\"req={}\", req);", cl.RQ_OBVIOUS),
    ("// 创建订单", "Order order = new Order();", cl.RQ_OBVIOUS),
    ("// 转换结果类型", "ResultDto dto = converter.convert(result);", cl.RQ_OBVIOUS),
    ("// 首先，我们需要检查参数是否为空", "if (request == null) {", cl.RQ_NOISE),
    ("// 接下来处理返回结果", "return result;", cl.RQ_NOISE),
    ("// 然后调用服务保存数据", "userService.save(data);", cl.RQ_NOISE),
    ("// 最后返回结果", "return result;", cl.RQ_NOISE),
    ("// 这里我们调用服务来处理用户信息", "userService.process(user);", cl.RQ_NOISE),
    ("// 下面开始进行数据处理", "processData(data);", cl.RQ_NOISE),
    ("// ==================== 数据处理 ====================", "processData(data);", cl.RQ_SECTION),
    ("// ---------- 参数校验 ----------", "validate(req);", cl.RQ_SECTION),
    ("// 参数处理", "validate(req);", cl.RQ_SECTION),
    ("// 数据处理", "processData(data);", cl.RQ_SECTION),
    ("// 用户ID", "private Long userId;", cl.RQ_DUPLICATE),
]

# 中性样本：既不承重也不确定可删 → UNCERTAIN(REVIEW)，不得被删
NEUTRAL_CASES = [
    "// 最后一次同步的时间",
    "// 该值由前端传入",
]


class TestMeaningfulSafety(unittest.TestCase):
    """安全底线：六类承重注释零误判删（优先级高于召回率）。"""

    def test_meaningful_zero_false_deletes(self):
        for family, cases in MEANINGFUL_CASES.items():
            for text in cases:
                with self.subTest(family=family, comment=text):
                    verdict = _classify_line(text, "doSomething();")
                    self.assertEqual(
                        verdict.action, cl.ACTION_KEEP,
                        f"承重注释被误判为 {verdict.rule_id}/{verdict.action}",
                    )
                    self.assertEqual(verdict.rule_id, cl.RQ_MEANINGFUL)

    def test_meaningful_beats_obvious_pattern(self):
        """同时命中复述模式与承重信号 → 必须 KEEP（白名单优先）。"""
        verdict = _classify_line(
            "// 获取用户的租户信息，避免跨租户查询", "userService.getUser(id);"
        )
        self.assertEqual(verdict.action, cl.ACTION_KEEP)

    def test_meaningful_beats_noise_pattern(self):
        verdict = _classify_line(
            "// 首先校验签名，否则拒绝请求", "verifySign(req);"
        )
        self.assertEqual(verdict.action, cl.ACTION_KEEP)


class TestSlopDetection(unittest.TestCase):
    def test_slop_cases_hit_expected_rule(self):
        missed = []
        for text, code, expected in SLOP_CASES:
            blank = expected == cl.RQ_SECTION and "----" not in text and "====" not in text
            verdict = _classify_line(text, code, blank_after=blank)
            if verdict.rule_id != expected:
                missed.append((text, expected, verdict.rule_id))
        self.assertEqual(missed, [], f"未按预期命中：{missed}")

    def test_auto_delete_ratio(self):
        """确定可删类覆盖率 ≥ 80%（对全部泔水样本）。"""
        deleted = sum(
            1 for text, code, _ in SLOP_CASES
            if _classify_line(text, code).action == cl.ACTION_DELETE
        )
        ratio = deleted / len(SLOP_CASES)
        self.assertGreaterEqual(ratio, 0.8, f"确定可删覆盖率仅 {ratio:.0%}")

    def test_neutral_cases_are_review_not_delete(self):
        for text in NEUTRAL_CASES:
            with self.subTest(comment=text):
                verdict = _classify_line(text, "doSomething();")
                self.assertEqual(verdict.action, cl.ACTION_REVIEW)

    def test_duplicate_and_uncertain_never_auto_delete(self):
        for text, code, expected in SLOP_CASES:
            if expected not in (cl.RQ_DUPLICATE, cl.RQ_UNCERTAIN):
                continue
            with self.subTest(comment=text):
                self.assertEqual(_classify_line(text, code).action, cl.ACTION_REVIEW)

    def test_mode_guards_against_false_positive(self):
        """仅命动词模式但无代码链接 → 不得判 OBVIOUS（宁可漏删）。"""
        verdict = _classify_line("// 获取配置项的超时时间", "String other = x();")
        self.assertNotEqual(verdict.rule_id, cl.RQ_OBVIOUS)

    def test_leading_verb_required(self):
        """动词不在开头的名词短语/叙述句 → 不得判 OBVIOUS（真实代码抽查得来的误删用例）。"""
        cases = [
            ("// 待处理", "PROCESSING,"),
            ("// 总记录数", "result.setTotalRecords(cleanupResult.getRecordCount());"),
            ("// 尝试查询表是否存在", 'String query = "SELECT 1 FROM information_schema.tables";'),
            ("// 触发限流，记录日志并返回错误码 90009", 'logger.info("indexPage rate limiter");'),
            ("// Step2: 开关判断 - 有开关类型时检查", "if (switchType != null) {"),
        ]
        for text, code in cases:
            with self.subTest(comment=text):
                self.assertNotEqual(_classify_line(text, code).rule_id, cl.RQ_OBVIOUS)

    def test_field_and_enum_comments_never_auto_delete(self):
        """字段/枚举常量上的注释：标准要求写且不能是名字直译 → 名字直译是「需改」不是「可删」。"""
        sources = [
            "class A {\n"
            "    // 处理目标\n"
            "    private String processedTargets;\n"
            "}\n",
            "enum A {\n"
            "    PENDING, // 待处理\n"
            "    PROCESSING, // 处理中\n"
            "}\n",
        ]
        for source in sources:
            for comment in cl.StdlibJavaParser().parse(source, "A.java"):
                with self.subTest(comment=comment.body, source=source.splitlines()[1 if "enum" not in source else 1]):
                    self.assertNotEqual(cl.classify(comment).action, cl.ACTION_DELETE)

    def test_method_restatement_is_deletable(self):
        """方法之上的普通 `//` 复述仍属可删（与 design §7 一致：JavaDoc 不动，`//` 可删）。"""
        verdict = _classify_line(
            "// 获取用户", "public User getUser(Long id) { return null; }"
        )
        self.assertEqual(verdict.action, cl.ACTION_DELETE)


class TestExitCodes(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def _run(self, source):
        (self.root / "A.java").write_text(source, encoding="utf-8")
        out = io.StringIO()
        with redirect_stdout(out), redirect_stderr(io.StringIO()):
            code = cl.main([str(self.root), "--json", "--parser", "stdlib"])
        return code, json.loads(out.getvalue())

    def test_delete_yields_2(self):
        code, payload = self._run(
            "class A {\n"
            "    // 获取用户\n"
            "    User user = userService.getUser(id);\n"
            "}\n"
        )
        self.assertEqual(code, 2)
        self.assertGreaterEqual(payload["summary"]["DELETE"], 1)

    def test_review_only_yields_1(self):
        code, payload = self._run("class A {\n    // 该值由前端传入\n    int x = 1;\n}\n")
        self.assertEqual(code, 1)
        self.assertEqual(payload["summary"]["DELETE"], 0)
        self.assertGreaterEqual(payload["summary"]["REVIEW"], 1)

    def test_no_comment_yields_0(self):
        code, payload = self._run("class A {\n    int x = 1;\n}\n")
        self.assertEqual(code, 0)
        self.assertEqual(payload["summary"]["REVIEW"], 0)

    def test_javadoc_not_judged(self):
        """JavaDoc 跳过判定（策略 java_doc=skip）——即使内容像泔水也不进 summary。"""
        code, payload = self._run(
            "class A {\n"
            "    /**\n"
            "     * 获取用户\n"
            "     */\n"
            "    User getUser(Long id) { return null; }\n"
            "}\n"
        )
        self.assertEqual(code, 0)
        self.assertEqual(payload["summary"]["DELETE"], 0)
        self.assertEqual(payload["summary"]["REVIEW"], 0)
        self.assertEqual(payload["comments"], 1)
        self.assertEqual(payload["actionable"], 0)


class TestFixSafety(unittest.TestCase):
    """S5：安全修复 —— 默认 dry-run、只删确定类、幂等、不碰 JavaDoc。"""

    SOURCE = (
        "package demo;\n"
        "\n"
        "/**\n"
        " * 获取用户（JavaDoc 不得被碰）\n"
        " */\n"
        "public class A {\n"
        "\n"
        "    // 获取用户\n"
        "    public User getUser(Long id) {\n"
        "        int total = 0; // 总数\n"
        "        // 该值由前端传入，需要保留\n"
        "        return userService.getUser(id);\n"
        "    }\n"
        "}\n"
    )

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.file = self.root / "A.java"
        self.file.write_text(self.SOURCE, encoding="utf-8")

    def tearDown(self):
        self.tmp.cleanup()

    def _run(self, argv):
        out = io.StringIO()
        err = io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            code = cl.main(argv)
        return code, out.getvalue(), err.getvalue()

    def _check_code(self):
        out = io.StringIO()
        with redirect_stdout(out), redirect_stderr(io.StringIO()):
            code = cl.main([str(self.root), "--json", "--parser", "stdlib"])
        return code, json.loads(out.getvalue())

    def test_check_reports_delete_before_fix(self):
        code, payload = self._check_code()
        self.assertEqual(code, 2)
        self.assertEqual(payload["summary"]["DELETE"], 1)      # 仅 `// 获取用户` 为确定可删
        self.assertGreaterEqual(payload["summary"]["REVIEW"], 1)

    def test_dry_run_does_not_touch_file(self):
        code, out, _ = self._run(["fix", str(self.root), "--parser", "stdlib"])
        self.assertEqual(code, 0)
        self.assertIn("预演（未写盘）", out)
        self.assertIn("-", out)                                 # 有 unified diff
        self.assertEqual(self.file.read_text(encoding="utf-8"), self.SOURCE)

    def test_apply_removes_only_delete_class(self):
        code, out, _ = self._run(["fix", str(self.root), "--parser", "stdlib", "--apply"])
        self.assertEqual(code, 0)
        self.assertIn("已写回", out)
        text = self.file.read_text(encoding="utf-8")
        self.assertNotIn("// 获取用户", text)                    # 确定可删：整行删除
        self.assertIn("// 该值由前端传入，需要保留", text)       # REVIEW：保留
        self.assertIn("/**", text)                              # JavaDoc：不得被碰
        self.assertIn("获取用户（JavaDoc 不得被碰）", text)
        self.assertIn("public User getUser(Long id) {", text)    # 代码行不动
        self.assertTrue(text.endswith("\n"))                    # 行尾换行保持

    def test_apply_is_idempotent(self):
        self._run(["fix", str(self.root), "--parser", "stdlib", "--apply"])
        first = self.file.read_text(encoding="utf-8")
        code, out, _ = self._run(["fix", str(self.root), "--parser", "stdlib", "--apply"])
        self.assertEqual(code, 0)
        self.assertIn("（无改动）", out)
        self.assertEqual(self.file.read_text(encoding="utf-8"), first)

    def test_trailing_comment_strips_only_comment(self):
        source = (
            "class A {\n"
            "    void m() {\n"
            "        userService.process(user); // 处理用户\n"
            "    }\n"
            "}\n"
        )
        (self.root / "B.java").write_text(source, encoding="utf-8")
        code, _, _ = self._run(["fix", str(self.root / "B.java"), "--parser", "stdlib", "--apply"])
        self.assertEqual(code, 0)
        text = (self.root / "B.java").read_text(encoding="utf-8")
        self.assertIn("userService.process(user);\n", text)
        self.assertNotIn("// 处理用户", text)

    def test_fix_json_payload(self):
        code, out, _ = self._run(["fix", str(self.root), "--parser", "stdlib", "--json"])
        self.assertEqual(code, 0)
        payload = json.loads(out)
        self.assertEqual(payload["command"], "fix")
        self.assertFalse(payload["applied"])
        self.assertEqual(payload["removed"], 1)
        self.assertEqual(len(payload["files"]), 1)
        self.assertIn("-", payload["files"][0]["diff"])

    def test_report_only_caps_exit_at_warn(self):
        code, _ = self._check_code()
        self.assertEqual(code, 2)
        out = io.StringIO()
        with redirect_stdout(out), redirect_stderr(io.StringIO()):
            code = cl.main([str(self.root), "--json", "--parser", "stdlib", "--report-only"])
        self.assertEqual(code, 1)
        self.assertEqual(json.loads(out.getvalue())["summary"]["DELETE"], 1)

    def test_usage_error_exits_3(self):
        with self.assertRaises(SystemExit) as ctx:
            self._run(["--nosuchflag", str(self.root)])
        self.assertEqual(ctx.exception.code, 3)


if __name__ == "__main__":
    unittest.main()