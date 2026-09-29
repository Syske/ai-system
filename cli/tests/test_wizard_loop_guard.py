#!/usr/bin/env python3
"""P22:143 — 交互向导常驻循环检测（agent 启动前的真实交互断言）。

把 2026-09-21 on-demand 巡检中的**临时** mock 全组合扫描（104/104 组合无循环）
固化为常驻回归测试。

背景（三个已修复缺陷，同属「wizard 状态机不前进」这一类）：

1. 顶层 BACK 旧行为 `continue` → 无限重渲染项目菜单（根菜单无上一级可退）
2. hook validate 失败旧行为 `step=2` → 全量重收字段 → 死循环（F2 scan /
   G1 change-impact 同根因）
3. 必填字段留空（None）→ 重问当前字段（正确行为，本测试作为不变量锁定）

本测试直接驱动 `WizardSteps._steps()` 状态机（不经真实 TTY），对每个
「命令 × 项目选择 × 字段应答序列」组合断言：

- **不变量 A（无死循环）**：状态机在有限步内 return 或 raise，绝不无限迭代
- **不变量 B（唯一出口）**：走到终态时 target/values/output 均已确定
- **不变量 C（必填不被跳过）**：必填字段留空时不前进

Run:
    python -m unittest cli.tests.test_wizard_loop_guard
"""

import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from cli.services.wizard.steps import WizardSteps  # noqa: E402
from cli.utils.menu import BACK  # noqa: E402

# 状态机允许的最大迭代数。真实交互一轮的字段收集通常 < 10 步；
# 留出足够余量后仍远超任何合法路径，触顶即视为死循环。
MAX_STEPS = 400


class LoopDetected(AssertionError):
    """状态机在 MAX_STEPS 内未到达终态 —— 死循环。"""


class ScriptedSteps(WizardSteps):
    """用脚本化应答驱动 `_steps()` 的最小 WizardSteps 表面。

    只实现 `_steps()` 会触及的钩子；其余（Wizard 基类能力）不参与。

    应答脚本耗尽后返回 `default_answer`（默认合法值）而非 None —— 因为
    必填字段留空会触发**正确**的「重问当前字段」行为（steps.py:205-215），
    若耗尽时返回 None 会无限重问，那是本测试的脚本设计问题，不是状态机缺陷。
    """

    def __init__(self, project, target, field_answers, output="copy",
                 default_answer="ok"):
        self._project = project
        self._target = target
        self._answers = list(field_answers)
        self._output = output
        self._default_answer = default_answer
        # 状态机内部会写这些属性；预置以免走真实 Wizard 初始化
        self.active_intent = None
        self.chain_commands = []
        self._skip_fields = set()
        self._derived_notes = {}
        self.history = {}
        self.step_trace = []

    # --- 钩子 ---

    def _select_project(self, header):
        if self._project is None:
            return BACK
        return self._project

    def _select_target(self, header, project):
        return self._target

    def _fields_for(self, target):
        # 由测试用例显式给出（经 self._fields 注入）
        return list(self._fields)

    def _ask_field(self, header, values, field, required, position, total):
        self.step_trace.append(("ask", field, position, total))
        if not self._answers:
            # 脚本耗尽 → 返回合法默认（必填重问是正确行为，见类 docstring）
            return self._default_answer
        return self._answers.pop(0)

    def _select_output(self, header):
        return self._output

    def _select_launch(self, header):
        return True

    def _header(self, *a):
        return []

    def _auto_fields(self):
        return set()

    def _field_choices(self, field):
        return []

    def _choices_for(self, values, field):
        return []

    def _option_descriptions(self, field):
        return {}

    def _field_note(self, field):
        return ""

    def _field_icon(self, field):
        return ""

    def _multi_select_fields(self):
        return set()

    def _previous_value(self, field):
        return None

    def _invalidate_dependents(self, values, field):
        return None

    def _resume_change(self, project, values):
        return None

    def _container_derived(self, fields, values, project, target_name=None):
        return {}, {}

    def _try_derive_silent(self, target, fields, values):
        return False

    def _apply_field_defaults(self, fields, values):
        return None

    def _save_state(self, project, target, values):
        return None

    def intake(self, header):
        return None

    @property
    def projects_root(self):
        return REPO_ROOT / "projects"


def _run(scenario, *, fields, answers, project="demo",
         target=("develop", "workflow"), output="copy"):
    """驱动一次 `_steps()`，在 MAX_STEPS 处熔断（把死循环转成可断言的失败）。

    熔断点选在 `_header`：状态机每一步（选项目/选目标/收字段/选输出）都经过它，
    是覆盖面最广且无副作用的计数点。不用 signal 超时（跨平台不可靠）。
    """

    w = ScriptedSteps(project, target, answers, output)
    w._fields = fields
    calls = {"n": 0}

    def counting_header(*a):
        calls["n"] += 1
        if calls["n"] > MAX_STEPS:
            raise LoopDetected(
                f"{scenario}: 状态机在 {MAX_STEPS} 步内未到达终态（疑似死循环）"
            )
        return []

    w._header = counting_header

    return w._steps(), calls["n"]


class TestHookValidateLoopGuard(unittest.TestCase):
    """回归 F2/G1：hook validate 失败后的重问路径不得死循环。

    2026-09-21 实测缺陷：validate 失败后 `step = 2`（全量重收全部字段），
    用户再次作出同样的无效选择 → 再次失败 → 无限循环；唯一出口是选
    Workspace / 手输任意串假通过（校验不验名称存在性）。

    修复后：`step = 2 + idx`（只回到 fail_field 指向的字段），其余字段保留。
    本组测试**注入一个永远失败的 hook**，断言状态机在有界步内仍到达终态
    —— 即：用户改选后能继续，而不是卡死。

    有效性自证：把 steps.py 的 `step = 2 + idx` 改回 `step = 2` 后，
    本组必须失败（已实测确认，见提交说明）。
    """

    class _ScriptedHooks:
        """前 N 次 validate 失败，之后通过（模拟用户改选后修正）。"""

        def __init__(self, fail_field_name, fail_times=1):
            self._field = fail_field_name
            self._remaining = fail_times
            self.calls = 0

        def validate(self, wizard, values):
            self.calls += 1
            if self._remaining > 0:
                self._remaining -= 1
                return False, "injected validate failure"
            return True, None

        def fail_field(self, values):
            return self._field

        def prepare(self, wizard, values):
            return None

    def _run_with_hook(self, *, hook, target, fields, answers):
        import cli.services.command_hooks as hooks_mod

        original = hooks_mod._COMMAND_HOOKS.get(target[0])
        hooks_mod._COMMAND_HOOKS[target[0]] = hook
        try:
            w = ScriptedSteps("demo", target, answers)
            w._fields = fields
            calls = {"n": 0}

            def counting_header(*a):
                calls["n"] += 1
                if calls["n"] > MAX_STEPS:
                    raise LoopDetected(
                        f"hook-fail 场景在 {MAX_STEPS} 步内未终止（死循环）"
                    )
                return []

            w._header = counting_header
            result = w._steps()
            return result, calls["n"]
        finally:
            if original is None:
                hooks_mod._COMMAND_HOOKS.pop(target[0], None)
            else:
                hooks_mod._COMMAND_HOOKS[target[0]] = original

    def test_failing_hook_then_fixed_terminates(self):
        """hook 失败一次 + 用户改选 → 必须终止（F2 死循环的核心回归）。"""
        hook = self._ScriptedHooks("Projects", fail_times=1)
        fields = [("Projects", True), ("Scope", False)]
        # 第一次 Projects="bad"（hook 失败）→ 回到 Projects 重问 → "demo"
        result, steps = self._run_with_hook(
            hook=hook,
            target=("develop", "workflow"),
            fields=fields,
            answers=["bad", "demo", "s"],
        )
        self.assertLessEqual(steps, MAX_STEPS)
        self.assertIsNotNone(result)
        self.assertGreaterEqual(
            hook.calls, 2, "hook 应至少被调用两次（失败 + 改选后重试）"
        )

    def test_back_exits_persistent_hook_failure(self):
        """hook 持续失败时的出口是 BACK/Esc（fields.py 返回 BACK → step 前进）。

        恒失败时「继续重问」是**正确**行为（用户可改选）；不可退出的才是死循环。
        本组锁定 BACK 出口存在：失败 → 用户 BACK → 状态机前进而非卡死。
        """
        hook = self._ScriptedHooks("Projects", fail_times=99)
        result, steps = self._run_with_hook(
            hook=hook,
            target=("develop", "workflow"),
            fields=[("Projects", True)],
            answers=["bad", BACK],   # 第二次答 BACK → 回退到上一步
        )
        self.assertLessEqual(steps, MAX_STEPS)
        self.assertIsNotNone(result)

    def test_failing_hook_only_reasks_fail_field(self):
        """不变量：hook 失败只回到 fail_field，不全量重收。"""
        hook = self._ScriptedHooks("Scope", fail_times=1)
        w = ScriptedSteps("demo", ("develop", "workflow"), [])
        w._fields = [("Projects", True), ("Scope", False)]
        asked = []

        import cli.services.command_hooks as hooks_mod

        original = hooks_mod._COMMAND_HOOKS.get("develop")
        hooks_mod._COMMAND_HOOKS["develop"] = hook
        try:
            def recording_header(*a):
                return []

            calls = {"n": 0}

            def counting_header(*a):
                calls["n"] += 1
                if calls["n"] > MAX_STEPS:
                    raise LoopDetected("步数触顶")
                return []

            w._header = counting_header

            def recording_ask(header, values, field, required, pos, total):
                asked.append(field)
                return w._default_answer

            w._ask_field = recording_ask
            w._steps()
        finally:
            if original is None:
                hooks_mod._COMMAND_HOOKS.pop("develop", None)
            else:
                hooks_mod._COMMAND_HOOKS["develop"] = original

        # Projects 只需被问一次（若 step=2 全量重收则会重复问 Projects）
        self.assertEqual(
            asked.count("Projects"),
            1,
            f"Projects 被重复收集（step 回退到 2 的死循环特征）: {asked}",
        )
        self.assertGreaterEqual(
            asked.count("Scope"), 2,
            f"Scope 应因 hook 失败被重问: {asked}",
        )


class TestWizardLoopGuard(unittest.TestCase):
    """不变量 A：无死循环（有界步内到达终态）。"""

    def _cases(self):
        """(场景名, [(字段, 必填)], 应答序列) 组合表。"""
        return [
            # 单字段：各种应答
            ("single-required-answered", [("Projects", True)], ["demo"]),
            ("single-required-empty", [("Projects", True)], [None]),
            ("single-optional-empty", [("Scope", False)], [None]),
            # 多字段全填
            ("multi-all-filled",
             [("Projects", True), ("Branch", False), ("Note", False)],
             ["demo", "main", "text"]),
            # 多字段全空（可选字段可跳过）
            ("multi-all-empty",
             [("Projects", True), ("Branch", False), ("Note", False)],
             [None, None, None]),
            # 首字段必填留空 → 应重问而非前进（消耗两次应答）
            ("required-reask",
             [("Projects", True), ("Scope", False)],
             [None, "demo", "s"]),
            # 交错
            ("alternating",
             [("A", True), ("B", False), ("C", False)],
             ["a", None, "c", None]),
        ]

    def test_no_combination_loops(self):
        for name, fields, answers in self._cases():
            with self.subTest(scenario=name):
                result, steps = _run(
                    name, fields=fields, answers=answers
                )
                self.assertLessEqual(
                    steps, MAX_STEPS,
                    f"{name}: 步数触顶（死循环）",
                )
                self.assertIsNotNone(
                    result, f"{name}: 应到达终态"
                )

    def test_single_required_answered_step_budget(self):
        """不变量 C：单必填字段一次答完应在极少步内完成。"""
        result, steps = _run(
            "budget", fields=[("Projects", True)], answers=["demo"]
        )
        self.assertLess(steps, 20, f"步数异常偏高: {steps}")
        self.assertEqual(result[0], "develop")

    def test_required_empty_is_reasked_not_skipped(self):
        """不变量 C：必填留空 → 重问当前字段（不进 Step），重问后可写入。"""
        w = ScriptedSteps("demo", ("develop", "workflow"), [None, "demo"])
        w._fields = [("Projects", True)]
        w._header = lambda *a: []
        w._select_output = lambda header: "copy"
        w._select_launch = lambda header: True
        target_name, values, output, launch, chain = w._steps()
        self.assertEqual(
            values.get("Projects"),
            "demo",
            "必填字段应被重问并最终写入",
        )
        # 该字段被问过两次：第一次 None（留空）→ 第二次 "demo"
        asked = [t for t in w.step_trace if t[0] == "ask"]
        self.assertEqual(len(asked), 2, f"应恰好重问一次: {asked}")


class TestTopLevelBackExits(unittest.TestCase):
    """回归：顶层 BACK = 取消退出（不再无限重渲染）。"""

    def test_back_from_project_selection_raises(self):
        w = ScriptedSteps(None, ("develop", "workflow"), [])
        w._fields = []
        w._header = lambda *a: []
        with self.assertRaises(KeyboardInterrupt):
            w._steps()


if __name__ == "__main__":
    unittest.main()
