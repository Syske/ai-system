#!/usr/bin/env python3
"""tools/format-jdt-gate.py 单元测试（C2 环境感知逻辑，2026-09-02）。

覆盖：JDK 探测优先序（--java 显式 > env.yaml > JAVA_HOME > ~/.jdks）/
闭包完整性判定 / exit code 映射逻辑。不真正执行 java（环境无关）。
"""
import importlib.util
import pathlib
import sys
import unittest
from unittest import mock

REPO = pathlib.Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("format_jdt_gate", REPO / "tools" / "format-jdt-gate.py")
fjg = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fjg)


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


if __name__ == "__main__":
    unittest.main()