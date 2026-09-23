#!/usr/bin/env python3
"""P62 回归测试 —— 任务提交 `T-<id>` 的可追溯性门禁（分支名为机器判据）。

P62 背景（2026-09-23 Implemented）：标准要求任务提交带 `T-<id>`，但门禁只能校验
"含 T- 时的格式"，**缺失无法拦**；实践因此 18/18 省略。根因有二：
① 纯习惯漂移（卡编号 `T-011` 本已合规却仍省略）；
② **门禁逼出的规避** —— 有些变更按计划位置编号（`1.1`），`T-1.1` 必然 FAIL `T-\\d{3}`，
   于是 AI 学会整个省掉 `T-`。

修复：以**分支名**（治理已冻结的任务分支命名）判定"是否任务提交"，
`feat|fix|refactor|perf|test` 缺 `T-<id>` → FAIL；`chore|docs|style|ci|revert` 与
merge 豁免；非任务分支不受约束；历史不追溯。

Run:
    python -m unittest cli.tests.test_p62_commit_traceability
"""

import importlib.util
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
FORMAT_CHECK = REPO_ROOT / "tools" / "format-check.py"


def _load(name, rel):
    spec = importlib.util.spec_from_file_location(name, REPO_ROOT / rel)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


FC = _load("format_check_p62", "tools/format-check.py")


class TestTaskIdPredicateUnit(unittest.TestCase):
    """纯函数层：哪个提交需要 T-<id>。"""

    def test_任务分支强制型类型缺_id(self):
        branch = "cc20260923_ipd_demo_housekeeping-service-api"
        self.assertTrue(FC._missing_task_id("fix(svc): 删除慢操作判据", branch))
        self.assertTrue(FC._missing_task_id("feat(svc): 新能力", branch))
        self.assertTrue(FC._missing_task_id("test(svc): 用例", "bugfix/cc20260923_svc"))
        self.assertTrue(FC._missing_task_id("fix(svc): 无编号热修", "task/123"))

    def test_合规提交不判缺(self):
        b = "cc20260923_ipd_demo_svc"
        self.assertFalse(FC._missing_task_id("fix(svc): T-011 修好了", b))

    def test_治理类与_merge_豁免(self):
        b = "cc20260923_ipd_demo_svc"
        for subj in ("chore(svc): 基线对齐", "docs(svc): 补说明",
                     "style(svc): 格式化", "ci: 调整", "revert(svc): 回退"):
            self.assertFalse(FC._missing_task_id(subj, b), subj)
        self.assertFalse(FC._missing_task_id("Merge branch 'x'", b))

    def test_非任务分支不受约束(self):
        for branch in ("master", "main", "", "HEAD", "feature/foo", "release/2026"):
            self.assertFalse(FC._missing_task_id("fix(svc): 无编号", branch), branch)

    def test_分支形态判据(self):
        # 主链 cc<yyyymmdd>_…、task/*、bugfix/*
        for branch in ("cc20260923_ipd_desc_svc", "cc20260923_desc_svc",
                       "task/T-011", "bugfix/cc20260923_svc", "bugfix/x"):
            self.assertTrue(bool(FC.TASK_BRANCH_RE.match(branch)), branch)
        for branch in ("master", "main", "cc2026923_x", "feature/cc1_x", "topic/cc_x"):
            self.assertFalse(bool(FC.TASK_BRANCH_RE.match(branch)), branch)


class TestGateInRealRepo(unittest.TestCase):
    """端到端：真临时 git 仓里造分支/提交，跑门禁本体。"""

    def _git(self, repo, *args):
        return subprocess.run(
            ["git", "-c", "user.email=t@t", "-c", "user.name=t", *args],
            cwd=repo, capture_output=True, text=True)

    def _gate(self, repo):
        p = subprocess.run([sys.executable, str(FORMAT_CHECK), str(repo), "--check-commit"],
                           capture_output=True, text=True)
        return p.returncode, p.stdout + p.stderr

    def setUp(self):
        self._td = tempfile.TemporaryDirectory()
        self.repo = Path(self._td.name) / "svc"
        self.repo.mkdir()
        self._git(self.repo, "init", "-q", "-b", "master")
        (self.repo / "A.java").write_text("package p;\nclass A {}\n", encoding="utf-8")
        self._git(self.repo, "add", "-A")
        self._git(self.repo, "commit", "-q", "-m", "init")
        self._git(self.repo, "checkout", "-q", "-b",
                  "cc20260923_ipd_demo_housekeeping-service-api")

    def tearDown(self):
        self._td.cleanup()

    def _commit(self, msg, body="package p;\nclass A {  }\n"):
        (self.repo / "A.java").write_text(body, encoding="utf-8")
        self._git(self.repo, "add", "-A")
        self._git(self.repo, "commit", "-q", "-m", msg)

    def test_事故场景_任务分支缺T_必须FAIL(self):
        self._commit("fix(housekeeping-service): 删除慢操作判据改用独立毫秒配置")
        rc, out = self._gate(self.repo)
        self.assertEqual(rc, 2, out)
        self.assertIn("Task-branch rule", out)
        self.assertIn("cc20260923_ipd_demo_housekeeping-service-api", out)

    def test_合规提交PASS(self):
        self._commit("fix(housekeeping-service): T-011 删除慢操作判据改用独立毫秒配置")
        rc, out = self._gate(self.repo)
        self.assertEqual(rc, 0, out)

    def test_治理类在任务分支豁免(self):
        self._commit("chore(housekeeping-service): 格式基线对齐")
        rc, out = self._gate(self.repo)
        self.assertEqual(rc, 0, out)

    def test_计划位置编号写进subject仍是格式错(self):
        # 结构性冲突的显式留证：T-1.1 不属于 T-\d{3}
        self._commit("fix(housekeeping-service): T-1.1 卡子编号写进 subject")
        rc, out = self._gate(self.repo)
        self.assertEqual(rc, 2, out)
        self.assertIn("不符合 type(scope): T-xxx 格式", out)

    def test_非任务分支无T_仍PASS(self):
        self._git(self.repo, "checkout", "-q", "master")
        self._commit("fix(housekeeping-service): 主分支上无卡直接修")
        rc, out = self._gate(self.repo)
        self.assertEqual(rc, 0, out)


class TestStandardIsSSOT(unittest.TestCase):

    def test_标准声明分支判据与豁免(self):
        text = (REPO_ROOT / "governance" / "standards" / "common"
                / "commit-content.md").read_text(encoding="utf-8")
        for needle in ("Task-branch rule", "Task Card id ≠ plan position",
                       "Grandfathering", "chore|docs|style|ci|revert"):
            self.assertIn(needle, text, needle)

    def test_任务卡模板编号为三位数字(self):
        text = (REPO_ROOT / "templates" / "prompts" / "tasks-template.md").read_text(
            encoding="utf-8")
        self.assertIn("# T-{编号}", text)
        self.assertIn("tasks/cards/T-{编号}.md", text)
        self.assertIn("3 位数字", text)

    def test_运行时不复制条款(self):
        text = (REPO_ROOT / "templates" / "runtime" / "runtime-develop.md").read_text(
            encoding="utf-8")
        self.assertIn("commit-content.md", text)   # 引用即可，不得另立一套


if __name__ == "__main__":
    unittest.main()