"""format-baseline 词法分析（analyze）测试：字符串/注释互不侵扰 + 变化检出。"""
import importlib.util
import sys
import unittest
from pathlib import Path

TOOLS = str(Path(__file__).resolve().parents[2] / "tools")
spec = importlib.util.spec_from_file_location(
    "format_baseline_tool", Path(TOOLS) / "format-baseline.py")
fb = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fb)
analyze = fb.analyze


class TestAnalyze(unittest.TestCase):

    def test_url_string_not_eaten_by_line_comment(self):
        # 字符串内 `//`（URL）不触发行注释剥离；string 完整保留
        toks, strs = analyze('String u = "http://a.com/x?y=1"; int z = u.length();')
        self.assertEqual(strs, ['"http://a.com/x?y=1"'])
        self.assertIn("length", toks)

    def test_plain_code(self):
        toks, strs = analyze('int x = 1; if (x > 0) { return "ok"; }')
        self.assertEqual(toks, ["int", "x", "=", "1", ";", "if", "(", "x", ">", "0",
                                ")", "{", "return", ";", "}"])
        self.assertEqual(strs, ['"ok"'])

    def test_comment_and_wrap_insensitive(self):
        # 注释/换行/缩进变化 → token 与 string 一致（零逻辑变化判定依据）
        old = 'int f(String u) { return u + "://"; } // 注释'
        new = 'int f(String u) {\n    return u + "://";\n} /* 注 */'
        to, so = analyze(old)
        tn, sn = analyze(new)
        self.assertEqual(to, tn)
        self.assertEqual(so, sn)

    def test_string_change_detected(self):
        # 字符串内容变化应被检出（负向用例）
        to, so = analyze('return "v1";')
        tn, sn = analyze('return "v2";')
        self.assertEqual(to, tn)
        self.assertNotEqual(so, sn)


if __name__ == "__main__":
    unittest.main()