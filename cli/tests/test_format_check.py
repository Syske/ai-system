#!/usr/bin/env python3
"""tools/format-check.py 单元测试（A 层格式化自检，2026-09-02）。

覆盖：干净通过 / 单行 Javadoc FAIL / 中文方法名 FAIL / T-xxx 泄漏 FAIL /
Map payload WARN / 目录不存在 ERROR。运行：python -m unittest cli/tests/test_format_check.py
"""
import importlib.util
import pathlib
import tempfile
import unittest

REPO = pathlib.Path(__file__).resolve().parents[2]
_TOOL = REPO / "tools" / "format-check.py"

spec = importlib.util.spec_from_file_location("format_check", _TOOL)
fc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fc)

CLEAN = """package x;
public class Clean {
    /**
     * 标准多行 Javadoc
     */
    private String tag;

    public void syncToBeisen() {
        // 业务逻辑
    }
}
"""

ONE_LINE_JAVADOC = """package x;
public class Bad {
    /** 单行 Javadoc */
    private String tag;
}
"""

CHINESE_METHOD = """package x;
public class Bad {
    public void 中文方法_场景() {
        // logic
    }
}
"""

TASK_REF = """package x;
public class Bad {
    /** 全量同步（T-001） */
    private String tag;
}
"""

MAP_PAYLOAD = """package x;
public class Bad {
    public void send() {
        Map<String, Object> content = new HashMap<>();
        content.put("eventType", "FULL_RESYNC");
        content.put("ts", 1L);
        content.put("enterpriseId", 9L);
    }
}
"""

LOG_CJK = """package x;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
public class Bad {
    private static final Logger log = LoggerFactory.getLogger(Bad.class);
    public void save() {
        log.error("落 bs_fail_task 失败，跳过该条，enterpriseId={}", 1L, e);
        log.info("开始处理：enterpriseId={}", 1L);
    }
}
"""

LOG_EN = """package x;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
public class Good {
    private static final Logger log = LoggerFactory.getLogger(Good.class);
    public void save() {
        log.error("Failed to save to bs_fail_task, skipping record, enterpriseId={}", 1L, e);
        log.info("Starting to process enterprise {}", 1L);
    }
}
"""

# ---- 第 7 项（方法显式访问修饰符）样例 ----

PKG_PRIVATE = """package x;

public class PkgPrivate
        implements Runnable {

    ReconcileDiffResult computeDiff(Map<Long, String> a) {
        return null;
    }
}
"""

PRIVATE_OK = """package x;
public class Prv {
    private void hid() {
    }

    public void pub() {
    }

    Prv() {
    }
}
"""

INTERFACE_OK = """package x;
public interface Iface {
    void tap();
}
"""

TRINARY_OK = """package x;
public class Tri {
    private Object pick(boolean b) {
        return b ? query(1) : null;
    }

    private String query(long id) {
        return null;
    }
}
"""

ENUM_WARN = """package x;
public enum Color {
    RED;
    String hex() {
        return \"#f00\";
    }
}
"""

CONTROL_FLOW_OK = """package x;
public class Ctrl {
    private void run(boolean ok, long id) {
        if (ok) {
            return;
        } else if (id > 0) {
            // do nothing
        }
        BsUserSyncMessage m = new BsUserSyncMessage(id);
    }
}
"""

TRAILING_COMMENT_DECL = """package x;
public class Trail {
    void helper() { // 行尾注释形态
    }
}
"""

PKG_PRIVATE_EXEMPTED = """package x;
public class Exempted {
    /**
     * 供同包测试直接调用（§Visibility 例外，review 重点）
     *
     * @param a 入参
     * @return 结果
     */
    ReconcileDiffResult computeReconcileDiff(Map<Long, String> a) {
        return null;
    }
}
"""

# ---- 第 8 项（@Value 配置字段）样例 ----

VALUE_DUAL = """package x;

public class Dual {
    @Value("${bs.org.sync.max-attempts:3}")
    private int maxAttempts = 3;
}
"""

VALUE_DUAL_EXEMPT = """package x;

public class DualEx {
    /**
     * 测试直构兜底，与 @Value 默认一致
     */
    @Value("${bs.org.sync.max-attempts:3}")
    private int maxAttempts = 3;
}
"""

VALUE_CLEAN = """package x;

public class Val {
    @Value("${bs.org.sync.batch-size:100}")
    private int batchSize; // 同步分批大小
}
"""

VALUE_NO_COMMENT = """package x;

public class NoCom {
    @Value("${bs.org.sync.timeout:30}")
    private int timeoutSeconds;
}
"""

VALUE_TRAILING_COMMENT = """package x;

public class Com {
    @Value("${bs.org.sync.retry:3}")
    private int retryTimes; // 重试次数
}
"""

HARDCODE_VIOLATION = """package x;

public class CfgBad {
    private String url = "https://api.example.com/v1";
    private String token = "abc123def456";
}
"""

COLL_NULL_VIOLATION = """package x;

import java.util.List;

public class CollBad {
    public List<String> names() {
        if (empty) {
            return null;
        }
        return List.of();
    }
}
"""

CONFIG_COLL_OK = """package x;

import java.util.List;

public class CfgOk {
    private String url = "${app.url}";
    private String token = "<token-placeholder>";

    public List<String> safe() {
        return List.of();
    }
}
"""

OPTIONAL_VIOLATION = """package x;

import java.util.Optional;

public class OptBad {
    private Optional<String> name;

    public String find2(Optional<String> filter) {
        return "x";
    }
}
"""

LEGACY_DATE_VIOLATION = """package x;

public class DateBad {
    public void go() {
        java.util.Date d = new java.util.Date();
        java.util.Calendar c = java.util.Calendar.getInstance();
    }
}
"""

NEW_THREAD_VIOLATION = """package x;

public class ThreadBad {
    public void go() {
        new Thread(() -> {}).start();
    }
}
"""

STD_OK = """package x;

import java.util.Optional;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.time.LocalDate;

public class StdOk {
    public Optional<String> find(long id) {
        return Optional.empty();
    }

    public LocalDate now() {
        return LocalDate.now();
    }

    public void pool() {
        ExecutorService es = Executors.newFixedThreadPool(2);
        es.execute(() -> {});
    }
}
"""

STR_EQ_VIOLATION = """package x;

public class StrEq {
    public void run(String status) {
        if (status == "OK") {
            sync();
        }
    }

    private void sync() {
    }
}
"""

LOG_VIOLATION = """package x;

public class LogBad {
    public void run() {
        try {
            risky();
        } catch (Exception e) {
            e.printStackTrace();
        }
        System.out.println("done");
    }

    private void risky() {
    }
}
"""

THROWS_VIOLATION = """package x;

public class ThrowsBad {
    private void risky() throws Exception {
        throw new Exception("x");
    }
}
"""

ALIBABA_OK = """package x;

public class AlibabaOk {
    public void run(String a, String b) {
        if (Objects.equals(a, b)) {
            sync();
        }
    }

    private void sync() {
    }
}
"""

BRACES_OK = """package x;

public class Ok {
    public void run(boolean ok) {
        if (ok) {
            sync();
        }
    }

    private void sync() {
    }
}
"""

BRACES_VIOLATION = """package x;

public class Bad {
    public void run(boolean ok, long id) {
        if (ok) sync();
        else fail();
        list.forEach(p -> {
            if (p != null) p.go();
        });
    }

    private void sync() {
    }

    private void fail() {
    }
}
"""

PLAIN_INIT = """package x;

public class Plain {
    private int plainCounter = 3;
}
"""


def _run_single(fname, content, extra=None):
    with tempfile.TemporaryDirectory() as td:
        src = pathlib.Path(td) / "src"
        src.mkdir()
        (src / fname).write_text(content, encoding="utf-8")
        args = [str(src)] + (extra or [])
        return fc.main(args)


def _run_commit_check(subject):
    """构造一次性 git 仓并提交 subject，跑 format-check --check-commit。"""
    import subprocess
    with tempfile.TemporaryDirectory() as td:
        repo = pathlib.Path(td)
        subprocess.run(["git", "init", "-q", td], check=True)
        subprocess.run(["git", "-C", td, "config", "user.email", "t@example.com"], check=True)
        subprocess.run(["git", "-C", td, "config", "user.name", "t"], check=True)
        subprocess.run(["git", "-C", td, "config", "commit.gpgsign", "false"], check=True)
        (repo / "A.java").write_text("class A {}\n", encoding="utf-8")
        subprocess.run(["git", "-C", td, "add", "-A"], check=True)
        subprocess.run(["git", "-C", td, "commit", "-q", "-m", subject], check=True)
        return fc.main([td, "--check-commit"])


class TestFormatCheck(unittest.TestCase):

    def test_clean_pass(self):
        self.assertEqual(_run_single("Clean.java", CLEAN), 0)

    def test_missing_dir_error(self):
        self.assertEqual(fc.main(["/no/such/dir-xyz"]), 2)

    def test_one_line_javadoc_fail(self):
        self.assertEqual(_run_single("Bad.java", ONE_LINE_JAVADOC), 2)

    def test_chinese_method_fail(self):
        self.assertEqual(_run_single("Bad.java", CHINESE_METHOD), 2)

    def test_task_ref_fail(self):
        self.assertEqual(_run_single("Bad.java", TASK_REF), 2)

    def test_map_payload_warn(self):
        self.assertEqual(_run_single("Bad.java", MAP_PAYLOAD), 1)

    def test_cjk_error_log_fail(self):
        self.assertEqual(_run_single("Bad.java", LOG_CJK), 2)

    def test_english_log_pass(self):
        self.assertEqual(_run_single("Good.java", LOG_EN), 0)

    # ---- 第 7 项：方法显式访问修饰符（java-alibaba.md §Visibility，仅 main，启发式 WARN）----

    def test_pkg_private_method_warn(self):
        # 跨行类声明 + package-private 方法 → WARN（exit 1）
        self.assertEqual(_run_single("PkgPrivate.java", PKG_PRIVATE), 1)

    def test_explicit_visibility_pass(self):
        # private/public 方法 + 构造器 → 不报（exit 0）
        self.assertEqual(_run_single("Prv.java", PRIVATE_OK), 0)

    def test_interface_method_skip(self):
        # 接口体方法隐式 public → 不报
        self.assertEqual(_run_single("Iface.java", INTERFACE_OK), 0)

    def test_ternary_call_no_false_positive(self):
        # 三目运算符/方法调用行 → 不报
        self.assertEqual(_run_single("Tri.java", TRINARY_OK), 0)

    def test_enum_pkg_private_warn(self):
        # 枚举体内无修饰方法 → WARN（exit 1）
        self.assertEqual(_run_single("Color.java", ENUM_WARN), 1)

    def test_control_flow_no_false_positive(self):
        # else-if / 赋值 / 构造调用行 → 不报
        self.assertEqual(_run_single("Ctrl.java", CONTROL_FLOW_OK), 0)

    def test_trailing_comment_decl_warn(self):
        # 方法声明行带行尾注释（`void helper() { // 注释`）→ 仍命中可见性检查
        self.assertEqual(_run_single("Trail.java", TRAILING_COMMENT_DECL), 1)

    def test_exempted_pkg_private_pass(self):
        # §Visibility 例外：Javadoc 首行注明「供同包测试直接调用」→ 豁免（exit 0）
        self.assertEqual(_run_single("Exempted.java", PKG_PRIVATE_EXEMPTED), 0)

    # ---- 第 8 项：@Value 配置字段（spring.md §Configuration Injection）----

    def test_value_dual_default_warn(self):
        # 占位符已带默认 + 字段初始化 → WARN（exit 1）
        self.assertEqual(_run_single("Dual.java", VALUE_DUAL), 1)

    def test_value_dual_exempt_pass(self):
        # 过渡豁免：Javadoc 注明「测试直构兜底」→ 不报双默认
        self.assertEqual(_run_single("DualEx.java", VALUE_DUAL_EXEMPT), 0)

    def test_value_clean_pass(self):
        # @Value 带默认 + 字段无初始化 + 行尾注释 → 0
        self.assertEqual(_run_single("Val.java", VALUE_CLEAN), 0)

    def test_value_no_comment_warn(self):
        # @Value 字段无注释说明 → WARN（exit 1）
        self.assertEqual(_run_single("NoCom.java", VALUE_NO_COMMENT), 1)

    def test_value_trailing_comment_pass(self):
        # @Value 字段带行尾注释 → 0
        self.assertEqual(_run_single("Com.java", VALUE_TRAILING_COMMENT), 0)

    def test_plain_init_no_false_positive(self):
        # 非 @Value 字段初始化 → 不报（exit 0）
        self.assertEqual(_run_single("Plain.java", PLAIN_INIT), 0)

    # ---- 第 9 项：单行无大括号控制语句（java-alibaba.md §Braces）----

    def test_braces_ok(self):
        self.assertEqual(_run_single("Ok.java", BRACES_OK), 0)

    def test_braces_violation_warn(self):
        # 单行 if/else 无大括号（含 lambda 内）→ WARN（exit 1）
        self.assertEqual(_run_single("Bad.java", BRACES_VIOLATION), 1)

    # ---- 第 10-12 项：§String / §Log / §Exception ----

    def test_str_eq_literal_warn(self):
        # 字符串字面量 == 比较 → WARN（exit 1）
        self.assertEqual(_run_single("StrEq.java", STR_EQ_VIOLATION), 1)

    def test_log_forbidden_warn_main_only(self):
        # main：printStackTrace/System.out.println → WARN（exit 1）
        self.assertEqual(_run_single("LogBad.java", LOG_VIOLATION), 1)

    def test_throws_exception_warn(self):
        # throws Exception → WARN（exit 1）
        self.assertEqual(_run_single("ThrowsBad.java", THROWS_VIOLATION), 1)

    def test_alibaba_rules_ok(self):
        # Objects.equals / 业务异常 / SLF4J → 不报（exit 0）
        self.assertEqual(_run_single("AlibabaOk.java", ALIBABA_OK), 0)

    # ---- 第 13-15 项：§Optional / §Date / §Thread ----

    def test_optional_field_param_warn(self):
        # Optional 字段 + 参数 → WARN（exit 1）
        self.assertEqual(_run_single("OptBad.java", OPTIONAL_VIOLATION), 1)

    def test_legacy_date_warn(self):
        # Date/Calendar/SimpleDateFormat → WARN（exit 1）
        self.assertEqual(_run_single("DateBad.java", LEGACY_DATE_VIOLATION), 1)

    def test_new_thread_warn(self):
        # new Thread() → WARN（exit 1）
        self.assertEqual(_run_single("ThreadBad.java", NEW_THREAD_VIOLATION), 1)

    def test_std_rules_ok(self):
        # Optional 返回 / LocalDate / 线程池 → 不报（exit 0）
        self.assertEqual(_run_single("StdOk.java", STD_OK), 0)

    # ---- 第 16-17 项：§Config / §Collection ----

    def test_hardcode_config_warn(self):
        # 硬编码 URL / 密钥 → WARN（exit 1）
        self.assertEqual(_run_single("CfgBad.java", HARDCODE_VIOLATION), 1)

    def test_collection_return_null_warn(self):
        # 集合方法返回 null → WARN（exit 1）
        self.assertEqual(_run_single("CollBad.java", COLL_NULL_VIOLATION), 1)

    def test_config_collection_ok(self):
        # 占位符 / 空集合返回 → 不报（exit 0）
        self.assertEqual(_run_single("CfgOk.java", CONFIG_COLL_OK), 0)

    # ---- --check-commit（commit-content.md）----

    def test_check_commit_task_format_pass(self):
        # 合规 type(scope): T-xxx → PASS（exit 0）
        self.assertEqual(_run_commit_check("feat(gate): T-015 提交信息规范收敛"), 0)

    def test_check_commit_bare_taskid_fail(self):
        # 裸「T-015 ...」（无 type 前缀）→ FAIL（exit 2，Commit Content）
        self.assertEqual(_run_commit_check("T-015 完成提交信息校验"), 2)

    def test_check_commit_non_task_pass(self):
        # 治理提交（无 T-）→ PASS（exit 0）
        self.assertEqual(_run_commit_check("style: apply format baseline"), 0)


if __name__ == "__main__":
    unittest.main()