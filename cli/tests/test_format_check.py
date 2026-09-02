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


def _run_single(fname, content, extra=None):
    with tempfile.TemporaryDirectory() as td:
        src = pathlib.Path(td) / "src"
        src.mkdir()
        (src / fname).write_text(content, encoding="utf-8")
        args = [str(src)] + (extra or [])
        return fc.main(args)


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


if __name__ == "__main__":
    unittest.main()