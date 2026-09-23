#!/usr/bin/env python3
"""R2 批次（第二/三批）回归测试 —— 产物路径 / 归一化 / Lombok 判定 / 误读实证。

覆盖盲检 R2 项：
- #7 `cli.utils.file.unique_dir`：同日同描述不再覆写（追加 -N）
- #8 scan 目录改用 outputs 约定形态 `{yyMMdd}-{descriptor}`（原 `scan-YYYYMMDD-HHMMSS` 为禁用形态）
- #15 字段名归一化**单一来源**（`cli.utils.fields`），两处调用方口径一致
- #21 Lombok 判定按**花括号深度**（类内内部块收尾不得关闭判定；注解与 class 分处两行仍生效）
- #14 `_parse_next` **行为实证**：`review.md` 的 `## Next` 能解析出真实后继（原报告称"取首个 token"）

Run:
    python -m unittest cli.tests.test_r2_paths_and_gates
"""

import re
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "tools"))

from cli.utils.fields import base_field_name          # noqa: E402
from cli.utils.file import unique_dir                 # noqa: E402
from cli.services import menu_config, workflow_reader  # noqa: E402


class TestUniqueDir(unittest.TestCase):
    """#7：同日同描述必须追加 -N，不得静默覆写（文档承诺与实现一致）。"""

    def test_首次使用原路径(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td) / "260923-demo"
            self.assertEqual(unique_dir(base), base)

    def test_冲突追加序号(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td) / "260923-demo"
            base.mkdir()
            self.assertEqual(unique_dir(base).name, "260923-demo-2")
            (Path(td) / "260923-demo-2").mkdir()
            self.assertEqual(unique_dir(base).name, "260923-demo-3")


class TestScanDirConvention(unittest.TestCase):
    """#8：scan 目录形态须符合 outputs 约定（{yyMMdd}-{descriptor}）。"""

    def test_实现使用约定形态(self):
        src = (REPO_ROOT / "cli" / "services" / "command_hooks.py").read_text(encoding="utf-8")
        self.assertIn('%y%m%d', src)
        self.assertIn('-scan"', src)
        self.assertNotIn('scan-{datetime.now().strftime(\'%Y%m%d-%H%M%S\')}', src)

    def test_唯一性由unique_dir保证(self):
        src = (REPO_ROOT / "cli" / "services" / "command_hooks.py").read_text(encoding="utf-8")
        self.assertIn("unique_dir(", src)


class TestFieldNameNormalization(unittest.TestCase):
    """#15：两处调用方必须口径一致（单一来源 cli.utils.fields）。"""

    CASES = [
        "Base Branch (default: master)",
        "发布内容 (services, clusters, ...)",
        "Projects",
        "Confluence Spec Page Id",
    ]

    def test_两处一致(self):
        for field in self.CASES:
            self.assertEqual(
                workflow_reader._norm_field_name(field),
                menu_config.MenuConfig._base(field),
                field,
            )

    def test_剥离任意尾部注解(self):
        self.assertEqual(base_field_name("发布内容 (a, b)"), "发布内容")
        self.assertEqual(base_field_name("Projects"), "Projects")


class TestLombokDepthRule(unittest.TestCase):
    """#21：按花括号深度判定 —— 类内内部块收尾不得关闭 Lombok 判定。"""

    def _warns(self, content):
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "format_check_lombok", REPO_ROOT / "tools" / "format-check.py")
        fc = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(fc)
        with tempfile.TemporaryDirectory() as td:
            src = Path(td) / "src"
            src.mkdir()
            (src / "LombOk.java").write_text(content, encoding="utf-8")
            return fc.main([str(src)]), fc

    def test_注解与class分处两行且含内部块(self):
        content = (
            "package x;\n\nimport lombok.Data;\n\n@Data\nclass LombOk {\n"
            "    private String x;\n\n"
            "    public String getX() { return x; }\n\n"
            "    public void run(boolean b) {\n        if (b) {\n            return;\n        }\n    }\n\n"
            "    public String getY() { return \"y\"; }\n}\n"
        )
        code, _ = self._warns(content)
        self.assertEqual(code, 0, "Lombok 类内 getter 不应被误报")

    def test_无注解的getter仍报(self):
        content = (
            "package x;\n\nclass Plain {\n    private String x;\n\n"
            "    public String getX() { return x; }\n}\n"
        )
        code, _ = self._warns(content)
        self.assertEqual(code, 1, "无 @Data 的样板 getter 应报 WARN")


class TestParseNextMisread(unittest.TestCase):
    """#14 误读实证：`_parse_next` 遍历全部 token，能解析出真实后继。"""

    def test_review的后继为verify(self):
        from cli.services.wizard.selection import WizardSelection

        class Fake(WizardSelection):

            def __init__(self, root):
                self.root = root

        workflows = discover_workflows()
        self.assertIn("review", workflows)
        successor = Fake(REPO_ROOT)._parse_next("review", workflows)
        self.assertEqual(successor, "verify")


def discover_workflows():
    return {
        p.stem for p in (REPO_ROOT / "workflows").glob("*.md")
        if p.stem != "README"
    }


if __name__ == "__main__":
    unittest.main()
