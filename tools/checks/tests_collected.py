"""测试声明 vs 收集一致性校验（P60 门禁自校验）。

故障类别：测试方法被定义在模块级 `if __name__ == "__main__":` 块内 → unittest
加载时该块不执行，方法永不定义、永不收集；直接运行文件时也晚于 `unittest.main()`
注册 → “测试全绿”存在虚假信心。此类失效对既有门禁完全无信号
（2026-09-21 外部盲检 V1：声明 336 / 收集 331）。

校验项：
1. 根因形态：模块级 `if __name__` 块内出现 `def test_` → ERROR（直接定位，不依赖加载）
2. 声明 vs 收集：逐 cli/tests/test_*.py 比对 `def test_` 声明数与 unittest 收集数 →
   不一致 → ERROR（差异量 + 定位提示）
"""

import re
import sys
import unittest

from .base import ROOT

# 任意缩进的测试方法声明（含模块级，后者同样不会被 unittest 收集）
DECLARED_TEST_RE = re.compile(r"^\s*def (test_\w+)", re.M)

# 模块级 `if __name__ == "__main__":`（单/双引号）
MAIN_GUARD_RE = re.compile(r"^if __name__ == ['\"]__main__['\"]:\s*$")

INDENTED_TEST_RE = re.compile(r"^\s+def (test_\w+)")


def nested_test_methods(path):

    """模块级 `if __name__` 块内定义的 def test_ 方法名（根因形态）。"""

    names = []

    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()

    for i, line in enumerate(lines):

        if not MAIN_GUARD_RE.match(line.rstrip()):
            continue

        j = i + 1

        while j < len(lines):

            cur = lines[j]

            if not cur.strip():
                j += 1
                continue

            if not cur[0].isspace():          # 块结束
                break

            m = INDENTED_TEST_RE.match(cur)

            if m:
                names.append(m.group(1))

            j += 1

    return names


def check_tests_collected(c):

    tests_dir = ROOT / "cli" / "tests"

    if not tests_dir.exists():
        c.warn("cli/tests not found, skipped")
        return

    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))

    for path in sorted(tests_dir.glob("test_*.py")):

        rel = path.relative_to(ROOT)

        nested = nested_test_methods(path)

        if nested:
            c.error(
                f"{rel}: test method(s) defined inside the module-level "
                f"`if __name__ == \"__main__\"` block -> never collected: "
                + ", ".join(nested)
            )
            continue

        declared = len(DECLARED_TEST_RE.findall(path.read_text(encoding="utf-8")))

        try:
            suite = unittest.TestLoader().loadTestsFromName(f"cli.tests.{path.stem}")
            collected = suite.countTestCases()
        except Exception as exc:                       # noqa: BLE001
            c.warn(f"{rel}: cannot collect tests ({exc})")
            continue

        if declared != collected:
            c.error(
                f"{rel}: declared {declared} test method(s) but unittest "
                f"collects {collected} (diff {declared - collected})"
            )