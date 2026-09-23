#!/usr/bin/env python3
"""技能层契约测试 —— R1：技能脚本零契约测试的补齐（agentdebug 校验 + 枚举口径）。

R1 背景（2026-09-21 盲检）：`skills/` 下脚本此前无契约测试；同时三个工具对
"技能目录"存在三种口径。本文件覆盖：

1. `agentdebug_validate` 的校验契约（缺字段/非法枚举 → errors；重复 issue → warnings）
2. **技能枚举单一来源**（`tools/skill_index.py`）：三工具口径一致、容器目录不计为技能、
   其下嵌套技能必须在内
3. `generate_contract` 的缺键契约（补齐 R1 点名的两个脚本之一，另一个见 test_t7_fail_loud）

Run:
    python -m unittest cli.tests.test_skills_contracts
"""

import importlib.util
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SKILL_SCRIPTS = REPO_ROOT / "skills" / "agent-debug-diagnosis" / "scripts"

sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "tools"))
sys.path.insert(0, str(SKILL_SCRIPTS))          # agentdebug 脚本互相 import 同目录模块


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


COMMON = _load("agentdebug_common", SKILL_SCRIPTS / "agentdebug_common.py")
VALIDATE = _load("agentdebug_validate", SKILL_SCRIPTS / "agentdebug_validate.py")
STATIC = _load("agentdebug_static", SKILL_SCRIPTS / "agentdebug_static.py")
SKILL_INDEX = _load("skill_index", REPO_ROOT / "tools" / "skill_index.py")


class TestAgentdebugValidateContract(unittest.TestCase):
    """agentdebug 校验：非法输入必须报错，合法输入必须放行。"""

    def _run_issues(self, issues):
        errors, warnings = [], []
        VALIDATE.validate_issues(issues, errors, warnings)
        return errors, warnings

    def _valid_issue(self, **overrides):
        issue = {
            "id": "I-1",
            # MODULES / SEVERITIES 是集合（无序）→ 取排序首项作合法值
            "module": sorted(COMMON.MODULES)[0],
            "severity": sorted(COMMON.SEVERITIES)[0],
            "errorType": "NPE",
            "traceStepIndex": 3,
        }
        issue.update(overrides)
        return issue

    def test_合法_issue_无错误(self):
        errors, _ = self._run_issues([self._valid_issue()])
        self.assertEqual(errors, [])

    def test_缺_id_报错(self):
        errors, _ = self._run_issues([self._valid_issue(id="")])
        self.assertTrue(any("缺少 id" in e for e in errors), errors)

    def test_非法_module_报错(self):
        errors, _ = self._run_issues([self._valid_issue(module="not-a-module")])
        self.assertTrue(any("module 非法" in e for e in errors), errors)

    def test_非法_severity_报错(self):
        errors, _ = self._run_issues([self._valid_issue(severity="urgent")])
        self.assertTrue(any("severity 非法" in e for e in errors), errors)

    def test_缺_errorType_报错(self):
        errors, _ = self._run_issues([self._valid_issue(errorType="")])
        self.assertTrue(any("缺少 errorType" in e for e in errors), errors)

    def test_重复_issue_仅告警(self):
        errors, warnings = self._run_issues([self._valid_issue(), self._valid_issue(id="I-2")])
        self.assertEqual(errors, [])
        self.assertTrue(any("重复" in w for w in warnings), warnings)

    def test_非对象条目_报错(self):
        errors, _ = self._run_issues(["not-an-object"])
        self.assertTrue(any("必须是对象" in e for e in errors), errors)

    def test_step_records_缺_modules_报错(self):
        errors, warnings = [], []
        VALIDATE.validate_step_records([{"step": 1}], errors, warnings)
        self.assertTrue(any("缺少 modules" in e for e in errors), errors)

    def test_step_records_模块不匹配_报错(self):
        errors, warnings = [], []
        modules = {m: {"module": "wrong-name", "content": ""} for m in COMMON.MODULES}
        VALIDATE.validate_step_records([{"step": 1, "modules": modules}], errors, warnings)
        self.assertTrue(any("不匹配" in e for e in errors), errors)


class TestSkillEnumerationSingleSource(unittest.TestCase):
    """R1：技能枚举口径必须唯一（容器目录不计为技能，其下嵌套技能必须在内）。"""

    def setUp(self):
        self.skills, self.containers = SKILL_INDEX.skill_dirs(REPO_ROOT)
        self.names = {p.name for p in self.skills}
        self.container_names = {p.name for p in self.containers}

    def test_容器目录不计为技能_但被识别(self):
        self.assertNotIn("architecture", self.names)
        self.assertIn("architecture", self.container_names)

    def test_容器下嵌套技能在内(self):
        nested = {p.name for p in self.skills if p.parent.name == "architecture"}
        self.assertEqual(
            nested,
            {"architecture-base", "context-architect", "design-review",
             "platform-governor", "provider-architect", "runtime-architect",
             "workflow-architect"},
        )

    def test_每个技能都有入口文件(self):
        for p in self.skills:
            self.assertIsNotNone(SKILL_INDEX.find_entrypoint(p), p)

    def test_三工具口径一致(self):
        """repo-lint / repo-metrics / dependency-graph 必须取自同一枚举。"""

        rl = _load("repo_lint_enum", REPO_ROOT / "tools" / "repo-lint.py")
        rm = _load("repo_metrics_enum", REPO_ROOT / "tools" / "repo-metrics.py")
        dg = _load("dep_graph_enum", REPO_ROOT / "tools" / "dependency-graph.py")

        lint_names = {p.name for p in rl.find_skills(REPO_ROOT)}
        metric_count, metric_names = rm.count_skills(REPO_ROOT)
        graph_names = set(dg.find_skills(REPO_ROOT))

        self.assertEqual(lint_names, self.names)
        self.assertEqual(graph_names, self.names)
        self.assertEqual(set(metric_names), self.names)
        self.assertEqual(metric_count, len(self.names))


if __name__ == "__main__":
    unittest.main()

class TestAgentdebugSilentFailureFixes(unittest.TestCase):
    """R2 批次：agentdebug 的静默失败修复（前驱记录 / triage 首要类型 / 校验短路）。"""

    def _record(self, step, system="", **extra):
        record = {
            "step": step,
            "traceStepIndex": step,
            "modules": {"system": {"content": system}},
        }
        record.update(extra)
        return record

    # ── #1 previous_record：不连续序号不得静默返回 None

    def test_前驱记录_序号不连续时取列表前驱(self):
        records = [self._record(1), self._record(3), self._record(4)]
        self.assertEqual(
            STATIC.previous_record(records, 3)["step"], 1
        )
        self.assertEqual(
            STATIC.previous_record(records, 4)["step"], 3
        )
        self.assertIsNone(STATIC.previous_record(records, 1))

    def test_前驱记录_未命中返回None(self):
        self.assertIsNone(STATIC.previous_record([self._record(1)], 9))

    # ── #2 triage：取命中数最多的类型，其余写入 notes（原按 dict 序取首个）

    def test_triage_取最多命中类型并列出其他(self):
        records = [
            self._record(1, "HTTP 401 Unauthorized"),
            self._record(2, "401 unauthorized"),
            self._record(3, "unauthorized"),
            # 须匹配 CONTEXT_OVERFLOW_RE（contextoverflow / context_overflow /
            # context length exceeded / context window exceeded）
            self._record(4, "context length exceeded"),
            self._record(5, "context window exceeded"),
        ]
        result = STATIC.run_phase0_triage(records)
        fatal = result["fatalDiagnosis"]
        self.assertIsNotNone(fatal, result)
        self.assertEqual(fatal["errorType"], "tool_systemic.auth_failure")
        self.assertTrue(
            any("context_overflow" in note for note in result["notes"]),
            result["notes"],
        )

    def test_triage_无系统性风险时正常返回(self):
        result = STATIC.run_phase0_triage([self._record(1, "all good")])
        self.assertIsNone(result["fatalDiagnosis"])

    # ── #4 issueRefs 在 issues 为空时必须报错（原静默跳过）

    def test_issueRefs_issues为空时报错(self):
        findings = [{
            "id": "F-1",
            "issueRefs": [{"issueId": "I-9", "role": "root"}],
        }]
        errors, warnings = [], []
        VALIDATE.validate_findings(findings, [], errors, warnings)
        self.assertTrue(
            any("issues 为空" in e for e in errors), errors
        )

    def test_issueRefs_存在性仍受校验(self):
        findings = [{
            "id": "F-1",
            "issueRefs": [{"issueId": "I-9", "role": "root"}],
        }]
        errors, warnings = [], []
        VALIDATE.validate_findings(findings, [self._valid_issue()], errors, warnings)
        self.assertTrue(any("不存在" in e for e in errors), errors)

    # ── #5 criticalModule="unknown" 合法（原判非法却又特判跳过 → 自相矛盾）

    def test_root_cause_unknown_合法(self):
        errors, warnings = [], []
        VALIDATE.validate_root_cause(
            {"criticalModule": "unknown", "summary": "未能归因到具体模块"}, errors, warnings
        )
        self.assertEqual(errors, [])

    def test_root_cause_真正非法值仍报错(self):
        errors, warnings = [], []
        VALIDATE.validate_root_cause(
            {"criticalModule": "not-a-module", "summary": "x"}, errors, warnings
        )
        self.assertTrue(any("非法" in e for e in errors), errors)

    def _valid_issue(self):
        return {
            "id": "I-1",
            "module": sorted(COMMON.MODULES)[0],
            "severity": sorted(COMMON.SEVERITIES)[0],
            "errorType": "NPE",
            "traceStepIndex": 3,
        }

    # ── #6 classify_action_error：括号显式（"not found" 无 "/" 不判路径不存在）

    def test_分类_no_such_file_判路径不存在(self):
        self.assertEqual(
            STATIC.classify_action_error("No such file: a.txt", "")[0],
            "nonexistent_path",
        )

    def test_分类_裸_not_found_不判路径不存在(self):
        self.assertEqual(
            STATIC.classify_action_error("not found", "")[0],
            "parameter_error",
        )
