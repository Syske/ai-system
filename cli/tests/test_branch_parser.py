"""Tests for the main-chain branch parser (cc{date}_ipd_{desc}_{service}, 暂定)."""

import unittest

from cli.services.branch_parser import ParsedBranch, parse, render


class TestMainChainBranchParser(unittest.TestCase):

    def test_parse_valid(self):
        p = parse("cc20260820_ipd_italent-sync-plus_user-center-api")
        self.assertIsInstance(p, ParsedBranch)
        self.assertEqual(p.date, "20260820")
        self.assertEqual(p.type, "ipd")
        self.assertEqual(p.desc, "italent-sync-plus")
        self.assertEqual(p.service, "user-center-api")

    def test_parse_blank_and_unparseable(self):
        self.assertIsNone(parse(""))
        self.assertIsNone(parse("  "))
        self.assertIsNone(parse("feature/whatever"))
        self.assertIsNone(parse("task/T-013"))          # 旧纪律格式不再适用
        self.assertIsNone(parse("cc20260820_other_aaa_svc"))  # type 必须 ipd
        self.assertIsNone(parse("cc20260820_ipd__svc"))           # desc 为空
        self.assertIsNone(parse("cc20260820_ipd_desc"))           # 缺 service

    def test_parse_never_raises(self):
        for name in (None, 123, ["x"]):
            try:
                parse(name)  # type: ignore[arg-type]
            except Exception:
                self.fail(f"parse({name!r}) raised")

    def test_render_default_template(self):
        name = render("", date="20260820", desc="italent-sync-plus", service="user-center-api")
        self.assertEqual(
            name,
            "cc20260820_ipd_italent-sync-plus_user-center-api",
        )

    def test_render_custom_template(self):
        name = render(
            "cc{date}_ipd_{desc}_{service}",
            date="20260820",
            desc="abc",
            service="svc",
        )
        self.assertEqual(name, "cc20260820_ipd_abc_svc")


if __name__ == "__main__":
    unittest.main()
