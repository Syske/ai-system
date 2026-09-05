#!/usr/bin/env python3
"""tools/format-jdt-gate.py 单元测试（C2 环境感知逻辑，2026-09-02）。

覆盖：JDK 探测优先序（--java 显式 > env.yaml > JAVA_HOME > ~/.jdks）/
闭包完整性判定 / exit code 映射逻辑。不真正执行 java（环境无关）。
"""
import importlib.util
import pathlib
import sys
import tempfile
import unittest
from unittest import mock

REPO = pathlib.Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("format_jdt_gate", REPO / "tools" / "format-jdt-gate.py")
fjg = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fjg)


CLEAN_JAVA = "package x;\npublic class Good {\n    public void ok() {\n    }\n}\n"


def _mk_clean_git_repo():
    import subprocess as sp
    td = tempfile.TemporaryDirectory()
    root = pathlib.Path(td.name)
    sp.run(["git", "init", "-q", td.name], check=True)
    sp.run(["git", "-C", td.name, "config", "user.email", "t@e"], check=True)
    sp.run(["git", "-C", td.name, "config", "user.name", "t"], check=True)
    (root / "src").mkdir(parents=True)
    (root / "src" / "A.java").write_text(CLEAN_JAVA, encoding="utf-8")
    sp.run(["git", "-C", td.name, "add", "-A"], check=True)
    sp.run(["git", "-C", td.name, "commit", "-qm", "feat: T-001 init"], check=True)
    return td, root


class TestJdtGate(unittest.TestCase):

    def test_closure_ready_missing(self):
        self.assertFalse(fjg._closure_ready(pathlib.Path("/no/such/lib")))

    def test_closure_ready_names(self):
        # 只要所有必需 jar 文件名在目录中就绪（不校验内容）
        with mock.patch.object(pathlib.Path, "is_dir", return_value=True), \
             mock.patch.object(pathlib.Path, "glob", return_value=[
                 pathlib.Path(n) for _, n in fjg.JDT_JARS]):
            self.assertTrue(fjg._closure_ready(pathlib.Path("/fake/lib")))

    def test_find_java_explicit_wins(self):
        explicit = pathlib.Path("/usr/bin/java")
        with mock.patch.object(pathlib.Path, "exists", return_value=True), \
             mock.patch.object(pathlib.Path, "is_dir", return_value=False), \
             mock.patch("os.access", return_value=True):
            self.assertEqual(fjg.find_java(str(explicit)), explicit)

    def test_find_java_none(self):
        # 环境解耦：clear=True 清掉 CI runner 预设的 JAVA_HOME；exists mock 阻断
        # 任何真实 JDK 路径命中（GitHub runner 预装 temurin-17 于 /usr/lib/jvm）
        with mock.patch.object(fjg, "_read_env_yaml", return_value={}), \
             mock.patch.dict("os.environ", {}, clear=True), \
             mock.patch("shutil.which", return_value=None), \
             mock.patch("pathlib.Path.is_dir", return_value=False), \
             mock.patch("pathlib.Path.glob", return_value=[]), \
             mock.patch("pathlib.Path.exists", return_value=False):
            self.assertIsNone(fjg.find_java(None))

    def test_dry_run_exit_mapping(self):
        # wrapper rc=0 时判定为 PASS(0)
        with mock.patch.object(fjg, "run", return_value=mock.Mock(
                returncode=0, stdout="JdtFormatCheck: files=2 differ=0 diffLines=0", stderr="")), \
             mock.patch.object(pathlib.Path, "exists", return_value=True):
            self.assertEqual(fjg.dry_run("/j", "/lib", "/build", "/x.xml", "/src"), 0)
        # wrapper rc=1（差异）→ WARN/FAIL 按 differ 数
        with mock.patch.object(fjg, "run", return_value=mock.Mock(
                returncode=1, stdout="JdtFormatCheck: files=2 differ=1 diffLines=5", stderr="")), \
             mock.patch.object(pathlib.Path, "exists", return_value=True):
            self.assertEqual(fjg.dry_run("/j", "/lib", "/build", "/x.xml", "/src"), 1)
        with mock.patch.object(fjg, "run", return_value=mock.Mock(
                returncode=1, stdout="JdtFormatCheck: files=2 differ=9 diffLines=100", stderr="")), \
             mock.patch.object(pathlib.Path, "exists", return_value=True):
            self.assertEqual(fjg.dry_run("/j", "/lib", "/build", "/x.xml", "/src"), 2)
        # wrapper 非 0/1 → ENV(3)
        with mock.patch.object(fjg, "run", return_value=mock.Mock(
                returncode=2, stdout="", stderr="boom")), \
             mock.patch.object(pathlib.Path, "exists", return_value=True):
            self.assertEqual(fjg.dry_run("/j", "/lib", "/build", "/x.xml", "/src"), 3)


    def test_dry_run_files_list_writes_list_file(self):
        # --files-list：files-list.txt 写入 build_dir 且 cmd 带 --files-file；子集生效
        import tempfile
        with tempfile.TemporaryDirectory() as td:
            build = pathlib.Path(td)
            with mock.patch.object(fjg, "run", return_value=mock.Mock(
                    returncode=0, stdout="JdtFormatCheck: files=1 differ=0 diffLines=0",
                    stderr="")), \
                 mock.patch.object(pathlib.Path, "exists", return_value=True):
                rc = fjg.dry_run("/j", td, str(build), "/x.xml", "/src",
                                 files_list=["a.java", "b/c.java"])
                self.assertEqual(rc, 0)
                cmd = fjg.run.call_args[0][0]
                self.assertIn("--files-file", cmd)
            txt = (build / "files-list.txt").read_text(encoding="utf-8")
            self.assertIn("a.java", txt)
            self.assertIn("b/c.java", txt)

    def test_main_files_list_parsed(self):
        # main 参数解析：--files-list 逗号/空格分隔 → 传给 dry_run
        import tempfile
        with tempfile.TemporaryDirectory() as td:
            with mock.patch.object(fjg, "dry_run", return_value=0) as dr, \
                 mock.patch.object(fjg, "find_java", return_value="/j"), \
                 mock.patch.object(fjg, "find_lib_dir", return_value=("/lib", "/build")), \
                 mock.patch.object(fjg, "_closure_ready", return_value=True):
                rc = fjg.main([td, "--batch", "--files-list", "a.java,b.java c.java"])
                self.assertEqual(rc, 0)
                self.assertEqual(dr.call_args.kwargs.get("files_list"),
                                 ["a.java", "b.java", "c.java"])

if __name__ == "__main__":
    unittest.main()
    def test_dry_run_apply_flag(self):
        # --apply 透传：apply=True 命令追加 --apply，且返回 0（写回完成即成功）
        with mock.patch.object(fjg, "run", return_value=mock.Mock(
                returncode=0,
                stdout="JdtFormatCheck: files=2 differ=1 diffLines=9 [apply 完成]", stderr="")), \
             mock.patch.object(pathlib.Path, "exists", return_value=True):
            self.assertEqual(fjg.dry_run("/j", "/lib", "/build", "/x.xml", "/src", apply=True), 0)
            cmd = fjg.run.call_args[0][0]
            self.assertIn("--apply", cmd)

    def test_changed_clean_repo_shortcut(self):
        # --changed 且无改动：环境探测前短路，无需 JDK/JDT（应 0）
        td, root = _mk_clean_git_repo()
        try:
            args = [str(root / "src"), "--batch", "--changed"]
            self.assertEqual(fjg.main(args), 0)
        finally:
            td.cleanup()

    def test_changed_non_git_falls_back(self):
        # 非 git 目录：--changed 不短路（继续环境流程；无 JDK → batch skip/3）
        import unittest.mock as mock
        with tempfile.TemporaryDirectory() as td:
            (pathlib.Path(td) / "src").mkdir()
            with mock.patch.object(fjg, "dry_run", return_value=0) as dr:
                args = [str(pathlib.Path(td) / "src"), "--batch", "--changed"]
                fjg.main(args)
                dr.assert_called_once()  # 回退：仍然走到 dry_run

    def test_dry_run_ignore_file_flag(self):
        # --ignore-file 透传：ignore_file 非空时命令追加
        with mock.patch.object(fjg, "run", return_value=mock.Mock(
                returncode=0, stdout="JdtFormatCheck: files=2 differ=0 diffLines=0", stderr="")), \
             mock.patch.object(pathlib.Path, "exists", return_value=True):
            self.assertEqual(fjg.dry_run("/j", "/lib", "/build", "/x.xml", "/src",
                                         ignore_file="/ig.txt"), 0)
            cmd = fjg.run.call_args[0][0]
            self.assertIn("--ignore-file", cmd)
            self.assertEqual(cmd[cmd.index("--ignore-file") + 1], "/ig.txt")
