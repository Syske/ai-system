#!/usr/bin/env python3
"""Tests for `tools/proposal-audit.py` 的开放项提取（OPEN_TODO）。

回归背景（2026-09-21 修复）：`OPEN_TODO` 原用 `^\\s*-\\s*\\[\\s*\\]`，而 `\\s` **含换行** ——
当某个 `- [ ]` 项**前面是空行**时，`^\\s*` 会从上一行行首起匹配并吞掉换行，
于是 `text[m.start():].splitlines()[0]` 取到**空串**，开放项文本丢失（只剩文件名与行号）。
改为字符类 `[ \\t]` + 捕获文本组后修复。

本测试守护：项文本必须非空、行号正确、缩进/多种前缀均可解析。

Run:
    python -m unittest cli.tests.test_proposal_audit_open_items
"""

import importlib.util
import re
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

spec = importlib.util.spec_from_file_location(
    "proposal_audit", REPO_ROOT / "tools" / "proposal-audit.py")
pa = importlib.util.module_from_spec(spec)
sys.modules["proposal_audit"] = pa
spec.loader.exec_module(pa)


def items(text):
    return [(text[:m.start()].count("\n") + 1, m.group("text").strip())
            for m in pa.OPEN_TODO.finditer(text)]


class TestOpenItemExtraction(unittest.TestCase):

    def test_item_after_blank_line_keeps_text(self):
        """回归：项前一空行曾导致文本丢失（`\\s` 含换行）。"""
        text = "## 遗留\n\n- [ ] C2（按需）：引入 IDEA 引擎\n"
        self.assertEqual(items(text), [(3, "C2（按需）：引入 IDEA 引擎")])

    def test_item_after_text_line(self):
        text = "说明文字\n- [ ] 第一项\n"
        self.assertEqual(items(text), [(2, "第一项")])

    def test_multiple_items_with_mixed_spacing(self):
        text = "- [ ] A 项\n\n- [x] 已完成（不计）\n- [ ]   B 项（多余空格）\n"
        self.assertEqual([text_ for _, text_ in items(text)],
                         ["A 项", "B 项（多余空格）"])

    def test_indented_item(self):
        text = "  - [ ] 缩进项\n"
        self.assertEqual(items(text)[0][1], "缩进项")

    def test_marker_variants_with_spaces_inside_brackets(self):
        text = "- [ ] 标准\n- [  ] 括号内多空格\n"
        self.assertEqual([t for _, t in items(text)], ["标准", "括号内多空格"])

    def test_item_at_first_line(self):
        text = "- [ ] 首行项\n文本\n"
        self.assertEqual(items(text), [(1, "首行项")])

    def test_empty_item_still_reported_as_empty(self):
        """`- [ ]` 后面确实没文字时，允许为空（不算丢文本）。"""
        self.assertEqual(items("- [ ] \n"), [(1, "")])

    def test_regex_never_consumes_newline(self):
        """守护：标记正则不得跨行匹配（这是原始缺陷的形态）。"""
        match = pa.OPEN_TODO.search("\n\n- [ ] X\n")
        self.assertEqual(match.group(0), "- [ ] X")
        self.assertNotIn("\n", match.group(0))


class TestRepositoryProposals(unittest.TestCase):

    def test_every_open_item_has_text(self):
        """真实报告：所有开放项都必须带文本（否则审计板不可读）。"""
        blank = []
        for path in sorted((REPO_ROOT / "reports").glob("*.md")):
            if not (path.name.startswith("P") or path.name.startswith("MAINTENANCE-")):
                continue
            for line_no, text_ in items(path.read_text(encoding="utf-8", errors="ignore")):
                if not text_:
                    blank.append(f"{path.name}:{line_no}")
        self.assertEqual(blank, [], f"开放项文本为空的条目: {blank}")


if __name__ == "__main__":
    unittest.main()