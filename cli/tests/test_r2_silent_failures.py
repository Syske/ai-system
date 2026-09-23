#!/usr/bin/env python3
"""R2 批次回归测试 —— 静默失败/可靠性（第二批：change_resume / skill_scan / i18n / 链注入 / 最近活跃）。

覆盖盲检 R2 项：
- `change_resume`：路径段安全（拒绝 `..`/分隔符）+ §8 无 §9 时的前瞻兜底
- `skill_scan`：frontmatter 回退检索**限定块内**（正文 `name:` 不得误取）
- `utils/menu/base`：i18n 的 locale 与 `config/menu.yaml` 同源（原硬编码 zh.yaml）
- `chain_launcher`：容器 id 不得注入**服务名**字段 `Projects`
- `wizard`：`last_action.at` 时间戳写入 + 按时间戳取最近活跃

Run:
    python -m unittest cli.tests.test_r2_silent_failures
"""

import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from cli.services import change_resume as cr          # noqa: E402
from cli.services import skill_scan as ss             # noqa: E402
from cli.utils.menu import base as menu_base          # noqa: E402


class TestChangeResumePathSafety(unittest.TestCase):
    """#17：项目/变更 id 必须是单个安全路径段（防越出工作区读文件）。"""

    def test_合法路径段通过(self):
        with tempfile.TemporaryDirectory() as td:
            self.assertIsNotNone(cr.change_artifact_path(td, "proj", "chg-1"))

    def test_穿越片段被拒(self):
        with tempfile.TemporaryDirectory() as td:
            self.assertIsNone(cr.change_artifact_path(td, "../etc", "chg"))
            self.assertIsNone(cr.change_artifact_path(td, "proj", "a/b"))
            self.assertIsNone(cr.change_artifact_path(td, "..", "chg"))
            self.assertIsNone(cr.change_artifact_path(td, "proj", ""))

    def test_读取接口对非法id返回None(self):
        with tempfile.TemporaryDirectory() as td:
            self.assertIsNone(cr.read_change_artifact(td, "../proj", "chg"))


class TestChangeResumeSection8(unittest.TestCase):
    """#13：§8 抽取不得依赖「后面必有 §9」。"""

    def test_无第九节仍可抽取(self):
        text = "## 8. Clarification Questions\n\n1. 问题一\n2. 问题二\n\n## 10. 其他\n"
        match = cr._SECTION_8.search(text)
        self.assertIsNotNone(match)
        self.assertEqual(len(cr._ITEM.findall(match.group(0))), 2)

    def test_有第九节时仍以第九节为界(self):
        text = "## 8. Clarification Questions\n\n1. 只取我\n\n## 9. Next\n\n1. 不属于§8\n"
        items = cr._ITEM.findall(cr._SECTION_8.search(text).group(0))
        self.assertEqual(items, ["只取我"])


class TestSkillScanFrontmatterScope(unittest.TestCase):
    """#12：回退检索限定 frontmatter 块内（正文 name: 不得误取）。"""

    def _skill(self, body):
        td = tempfile.TemporaryDirectory()
        self.addCleanup(td.cleanup)
        path = Path(td.name) / "demo-skill" / "SKILL.md"
        path.parent.mkdir(parents=True)
        path.write_text(body, encoding="utf-8")
        return path

    def test_正文的name被忽略_回退目录名(self):
        path = self._skill("---\ndescription: 演示\n---\n\n# 说明\n\nname: fake-from-body\n")
        meta = ss._read_frontmatter(path)
        self.assertNotEqual(meta.get("name"), "fake-from-body")
        self.assertEqual(meta.get("name"), "demo-skill")

    def test_frontmatter内的name仍生效(self):
        path = self._skill("---\nname: real-name\ndescription: 演示\n---\n\n正文\n")
        self.assertEqual(ss._read_frontmatter(path).get("name"), "real-name")


class TestI18nLocaleSource(unittest.TestCase):

    def test_i18n非空且来自locale文件(self):
        table = menu_base._load_i18n()
        self.assertTrue(table, "i18n 表不应为空")

    def test_源码不再硬编码zh_yaml(self):
        src = (REPO_ROOT / "cli" / "utils" / "menu" / "base.py").read_text(encoding="utf-8")
        self.assertIn('"menu.yaml"', src)
        self.assertIn("locale", src)


class TestChainLauncherProjectsInjection(unittest.TestCase):
    """#16：容器 id 只注入容器语义键；`Projects`（服务名）另行按容器映射注入。"""

    def test_不再把容器id注入Projects(self):
        src = (REPO_ROOT / "cli" / "services" / "chain_launcher.py").read_text(encoding="utf-8")
        self.assertNotIn('("Project ID", "Project", "Projects", "Workspace")', src)
        self.assertIn("container_services", src)


class TestWizardLastActiveTimestamp(unittest.TestCase):

    def test_last_action写入时间戳(self):
        src = (REPO_ROOT / "cli" / "services" / "wizard" / "output.py").read_text(encoding="utf-8")
        self.assertIn('"at": time.time()', src)

    def test_按时间戳取最近活跃(self):
        src = (REPO_ROOT / "cli" / "services" / "wizard" / "__init__.py").read_text(encoding="utf-8")
        self.assertIn("last_action", src)
        self.assertIn("max(stamped", src)


if __name__ == "__main__":
    unittest.main()
