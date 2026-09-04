#!/usr/bin/env python3
"""tools/checkstyle/checkstyle-gate.py 单元测试（H2 增量门禁，2026-09-03）。

覆盖：changed 提取（仅 .java）/ 干净仓快速 PASS / 增量 dry-run-list 相对路径 /
违规检出 exit=1（依赖本机 JRE17+jar，缺失时跳过）。运行：
    python -m unittest cli.tests.test_checkstyle_gate
"""
import importlib.util
import pathlib
import subprocess
import tempfile
import unittest
import unittest.mock

REPO = pathlib.Path(__file__).resolve().parents[2]
_TOOL = REPO / "tools" / "checkstyle" / "checkstyle-gate.py"
CONFIG = REPO / "tools" / "checkstyle" / "checkstyle.xml"

spec = importlib.util.spec_from_file_location("checkstyle_gate", _TOOL)
cg = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cg)

JRE = pathlib.Path.home() / ".local" / "jre17" / "bin" / "java"
JAR_DIR = pathlib.Path.home() / ".local" / "lib" / "checkstyle"
HAVE_ENV = JRE.exists() and any(JAR_DIR.glob("checkstyle-*-all.jar")) if JAR_DIR.is_dir() else False


def _mk_repo():
    td = tempfile.TemporaryDirectory()
    root = pathlib.Path(td.name)
    subprocess.run(["git", "init", "-q", td.name], check=True)
    subprocess.run(["git", "-C", td.name, "config", "user.email", "t@e"], check=True)
    subprocess.run(["git", "-C", td.name, "config", "user.name", "t"], check=True)
    return td, root


def _commit(root, rel, content):
    f = root / rel
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text(content, encoding="utf-8")
    subprocess.run(["git", "-C", str(root), "add", "-A"], check=True)
    subprocess.run(["git", "-C", str(root), "commit", "-qm", "feat: T-001 init"], check=True)


GOOD = "package x;\npublic class Good {\n    public void ok() {\n    }\n}\n"
BAD = "package x;\nimport java.util.List;\npublic class Bad {\n    public void ok() {\n    }\n}\n"


class TestCheckstyleGate(unittest.TestCase):

    def test_changed_files_only_java(self):
        td, root = _mk_repo()
        try:
            _commit(root, "src/main/java/x/Good.java", GOOD)
            (root / "note.txt").write_text("hi")
            subprocess.run(["git", "-C", td.name, "add", "-A"], check=True)
            (root / "src/main/java/x/New.java").write_text(GOOD, encoding="utf-8")
            rels = cg.changed_java_files(str(root), root / "src")
            self.assertEqual(rels, ["src/main/java/x/New.java"])
        finally:
            td.cleanup()

    def test_clean_repo_pass(self):
        td, root = _mk_repo()
        try:
            _commit(root, "src/main/java/x/Good.java", GOOD)
            self.assertEqual(cg.main([str(root / "src"), "--config", str(CONFIG)]), 0)
        finally:
            td.cleanup()

    def test_dry_run_list_incremental(self):
        td, root = _mk_repo()
        try:
            _commit(root, "src/main/java/x/Good.java", GOOD)
            (root / "src/main/java/x/Bad.java").write_text(BAD, encoding="utf-8")
            rc = cg.main([str(root / "src"), "--config", str(CONFIG), "--dry-run-list"])
            self.assertEqual(rc, 0)
        finally:
            td.cleanup()

    def test_no_assets_skip(self):
        # 未基线仓（仓根无 checkstyle.xml 资产）且无 --config → SKIP（exit 0）
        td, root = _mk_repo()
        try:
            _commit(root, "src/main/java/x/Good.java", GOOD)
            self.assertEqual(cg.main([str(root / "src")]), 0)
        finally:
            td.cleanup()

    def test_clean_repo_pass_without_env(self):
        # CI/无环境回归：clean 短路不依赖 JRE/jar（mock 探测返回 None 仍应 0）
        td, root = _mk_repo()
        try:
            _commit(root, "src/main/java/x/Good.java", GOOD)
            with unittest.mock.patch.object(cg, "_find_java", return_value=None), \
                 unittest.mock.patch.object(cg, "_find_jar", return_value=None):
                self.assertEqual(cg.main([str(root / "src"), "--config", str(CONFIG)]), 0)
        finally:
            td.cleanup()

    def test_dry_run_list_without_env(self):
        # 无环境：dry-run-list 不依赖 JRE/jar
        td, root = _mk_repo()
        try:
            _commit(root, "src/main/java/x/Good.java", GOOD)
            (root / "src/main/java/x/Bad.java").write_text(BAD, encoding="utf-8")
            with unittest.mock.patch.object(cg, "_find_java", return_value=None), \
                 unittest.mock.patch.object(cg, "_find_jar", return_value=None):
                self.assertEqual(
                    cg.main([str(root / "src"), "--config", str(CONFIG), "--dry-run-list"]), 0)
        finally:
            td.cleanup()

    @unittest.skipUnless(HAVE_ENV, "本机无 JRE17/checkstyle jar，跳过真实运行")
    def test_violation_exit_1(self):
        td, root = _mk_repo()
        try:
            _commit(root, "src/main/java/x/Good.java", GOOD)
            (root / "src/main/java/x/Bad.java").write_text(BAD, encoding="utf-8")
            rc = cg.main([str(root / "src"), "--config", str(CONFIG)])
            self.assertEqual(rc, 1)
        finally:
            td.cleanup()

    @unittest.skipUnless(HAVE_ENV, "本机无 JRE17/checkstyle jar，跳过真实运行")
    def test_clean_after_fix(self):
        td, root = _mk_repo()
        try:
            _commit(root, "src/main/java/x/Bad.java", BAD)
            (root / "src/main/java/x/Bad.java").write_text(GOOD, encoding="utf-8")
            self.assertEqual(cg.main([str(root / "src"), "--config", str(CONFIG)]), 0)
        finally:
            td.cleanup()


if __name__ == "__main__":
    unittest.main()