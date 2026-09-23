"""Tests for the main-chain branch parser (preset-based, P63 2026-09-23).

Formats are machine-assembled from presets (`plain` default / `ipd`); hand-written
format strings are rejected (they must not parse). `render` output is guaranteed
parseable (invariant).

Run:
    python -m unittest cli.tests.test_branch_parser
"""

import unittest

from cli.services.branch_parser import (
    DEFAULT_PRESET,
    PRESETS,
    ParsedBranch,
    parse,
    render,
)


class TestPresets(unittest.TestCase):

    def test_默认预设为_plain(self):
        self.assertEqual(DEFAULT_PRESET, "plain")
        self.assertEqual(set(PRESETS), {"plain", "ipd"})

    def test_两种形态都为合法的具体名(self):
        plain = parse("cc20260921_log-volume-reduction_housekeeping-service-api")
        self.assertIsInstance(plain, ParsedBranch)
        self.assertEqual(
            (plain.date, plain.type, plain.desc, plain.service),
            ("20260921", "", "log-volume-reduction", "housekeeping-service-api"),
        )
        ipd = parse("cc20260820_ipd_italent-sync-plus_user-center-api")
        self.assertEqual(
            (ipd.date, ipd.type, ipd.desc, ipd.service),
            ("20260820", "ipd", "italent-sync-plus", "user-center-api"),
        )

    def test_无下划线的段类是可切分的前提(self):
        # service/desc 段不含下划线 → 历史陷阱：服务名含下划线必须用连字符别名
        self.assertIsNone(parse("cc20260921_desc_qa_manage"))
        self.assertIsNone(parse("cc20260921_a_b_svc"))


class TestRejectsHandWrittenFormats(unittest.TestCase):
    """「拒绝人为修改格式」的机器判据：格式串/未知形态都必须 → None。"""

    def test_模板格式串不被接受(self):
        for name in ("cc{date}_x_{desc}", "cc{date}_ipd_{desc}_{service}",
                     "cc{date}_{desc}_{service}"):
            self.assertIsNone(parse(name), name)

    def test_未知与历史形态不被接受(self):
        for name in ("feature/whatever", "task/T-013", "bugfix/cc20260921_svc",
                     "cc20260921_other_aaa_svc", "cc20260921_ipd__svc",
                     "cc20260921_ipd_desc_x_y_z", "", "   "):
            self.assertIsNone(parse(name), name)

    def test_两预设靠段数区分不歧义(self):
        # plain：cc<8>_<desc>_<service>（3 段）；ipd：cc<8>_ipd_<desc>_<service>（4 段）。
        # 故 `cc20260921_ipd_desc` 是**合法 plain 名**（desc="ipd"），不构成歧义。
        three = parse("cc20260921_ipd_desc")
        self.assertIsNotNone(three)
        self.assertEqual((three.type, three.desc, three.service), ("", "ipd", "desc"))
        four = parse("cc20260921_ipd_desc_svc")
        self.assertEqual((four.type, four.desc, four.service), ("ipd", "desc", "svc"))

    def test_场景映射驱动预设(self):
        from cli.services.branch_parser import preset_for_scenario
        # 默认：需求 → plain；bugfix → None（交 provider，主链预设不适用）
        self.assertEqual(preset_for_scenario("requirement"), "plain")
        self.assertIsNone(preset_for_scenario("bugfix"))
        # 未登记场景 → default_preset
        self.assertEqual(preset_for_scenario("whatever"), "plain")
        # 自定义：把需求改成 ipd（改配置即可，无需改代码/写正则）
        custom = {"default_preset": "plain", "scenarios": {"requirement": "ipd"}}
        self.assertEqual(preset_for_scenario("requirement", custom), "ipd")
        self.assertIsNotNone(parse(render(
            preset_for_scenario("requirement", custom),
            "20260923", "qa-opt", "svc-a"), preset="ipd"))
        # 映射到不存在的预设 → fail loud（格式串不可手写）
        with self.assertRaises(ValueError):
            preset_for_scenario("requirement", {"scenarios": {"requirement": "custom-regex"}})

    def test_指定预设必须匹配该形态(self):
        self.assertIsNone(parse("cc20260921_desc_svc", preset="ipd"))
        self.assertIsNone(parse("cc20260921_ipd_desc_svc", preset="plain"))
        self.assertIsNotNone(parse("cc20260921_ipd_desc_svc", preset="ipd"))

    def test_未知预设名_parse_返回_None(self):
        self.assertIsNone(parse("cc20260921_desc_svc", preset="nope"))

    def test_parse_never_raises(self):
        for name in (None, 123, ["x"], ""):
            try:
                parse(name)  # type: ignore[arg-type]
            except Exception:
                self.fail(f"parse({name!r}) raised")


class TestRender(unittest.TestCase):

    def test_由预设组装(self):
        self.assertEqual(
            render("plain", "20260923", "log-cleanup", "housekeeping-service-api"),
            "cc20260923_log-cleanup_housekeeping-service-api",
        )
        self.assertEqual(
            render("ipd", "20260923", "qa-opt", "svc-a"),
            "cc20260923_ipd_qa-opt_svc-a",
        )

    def test_生成物必然可解析_不变量(self):
        for preset in PRESETS:
            name = render(preset, "20260923", "some-desc", "some-svc")
            parsed = parse(name)
            self.assertIsNotNone(parsed, name)
            self.assertEqual(parsed.date, "20260923")
            self.assertEqual(parsed.desc, "some-desc")
            self.assertEqual(parsed.service, "some-svc")
            self.assertEqual(parsed.type, PRESETS[preset]["type"])

    def test_非法预设或段值_fail_loud(self):
        for args in (("custom", "20260923", "a", "b"),          # 未知预设
                     ("plain", "260923", "a", "b"),             # date 非 8 位
                     ("plain", "20260923", "", "b"),            # desc 空
                     ("plain", "20260923", "a", "qa_manage"),   # service 含下划线
                     ("plain", "20260923", "A", "b")):          # 大写
            with self.assertRaises(ValueError, msg=str(args)):
                render(*args)


if __name__ == "__main__":
    unittest.main()