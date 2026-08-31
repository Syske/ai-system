"""Wizard mixin: main step state machine.

Split from wizard.py (P0). Steps: select project → select target →
collect fields → defaults/hooks → select output → launch confirm.
"""

from cli.services.command_hooks import get_hooks
from cli.utils.menu import BACK, choose, e as _e


class WizardSteps:

    # P38 批次 2：全推导工作流（字段全可选、可由上下文/Task Card/git 推导）
    SILENT_DERIVE_WORKFLOWS = {
        "dev-setup",
        "develop",
        "review",
        "verify",
        "release",
    }

    def _steps(self):

        project = None
        target = None
        fields = []
        values = {}
        output = None

        # AI 引导意图链（多命令意图的后续命令，主命令执行后衔接）
        self.active_intent = None
        self.chain_commands = []
        # 重入预填字段（如 Change Request）：跳过重收
        self._skip_fields = set()

        step = 0

        while True:

            if step == 0:

                result = self._select_project(
                    self._header(
                        None,
                        None,
                        [],
                        {}
                    )
                )

                if result is BACK:
                    continue

                if result == "__AI_GUIDE__":

                    # AI 引导（无项目任务）：意图 intake → (意图名, 命令链)
                    intake_result = self.intake(
                        self._header(
                            None,
                            None,
                            [],
                            {}
                        )
                    )

                    if intake_result is None:
                        continue

                    self.project = None

                    intent_name, commands = intake_result

                    # 多命令意图：首个命令为主目标，其余存入链（执行后衔接）
                    self.active_intent = intent_name
                    self.chain_commands = commands[1:]
                    self._skip_fields = set()

                    first = commands[0]

                    # 意图命令可能是 workflow（如 change-impact/bugfix）
                    # 或 command（aic-*.md）。按真实注册类型分派，避免
                    # workflow 走 command_fields 导致字段错配（M8）。
                    command_path = (
                        self.root
                        / "cli"
                        / "commands"
                        / f"aic-{first}.md"
                    )

                    first_kind = (
                        "command"
                        if command_path.exists()
                        else "workflow"
                    )

                    target = (first, first_kind)

                    fields = self._fields_for(target)

                    values = {}

                    step = 2

                    continue

                project = result

                self.project = result

                step = 1

                continue

            if step == 1:

                result = self._select_target(
                    self._header(
                        project,
                        None,
                        [],
                        {}
                    ),
                    project
                )

                if result is BACK:
                    step = 0
                    continue

                target = result

                fields = self._fields_for(
                    target
                )

                values = {}

                if project:

                    for field, _ in fields:

                        if field in self._auto_fields():
                            values[field] = project

                    fields = [
                        (f, r)
                        for f, r in fields
                        if f not in self._auto_fields()
                    ]

                if self._try_derive_silent(target, fields, values):

                    step = 2 + len(fields)

                    continue

                step = 2

                continue

            index = step - 2

            if index < len(fields):

                field, required = fields[index]

                if field in self._skip_fields:
                    # 重入预填字段（如 Change Request）：跳过重收
                    step += 1
                    continue

                values.pop(field, None)

                result = self._ask_field(
                    self._header(
                        project,
                        target,
                        fields,
                        values
                    ),
                    values,
                    field,
                    required,
                    index + 1,
                    len(fields)
                )

                if result is BACK:
                    step -= 1
                    continue

                if result is None and required:

                    # 必填字段留空（None）：重问当前字段，不前进
                    print(
                        f"\n⚠ {field} 为必填项，不能跳过。\n"
                        f"请重新输入 {field}。"
                    )

                    continue

                if result is not None:
                    values[field] = result

                    # 上游字段变更 → 使依赖它的下游字段值失效
                    # （Branch 依赖 Projects；Change/Task ID 依赖项目选择）
                    self._invalidate_dependents(
                        values,
                        field
                    )

                    # Change ID 已收集：检测已有 prepare 产物（重入）
                    if field == "Change ID":
                        self._resume_change(
                            project,
                            values
                        )

                step += 1

                continue

            if index == len(fields):

                self._apply_field_defaults(
                    fields,
                    values
                )

                target_name = target[0]

                if target_name in ("skill", "skill-launch"):

                    self._save_state(
                        project,
                        target,
                        values
                    )

                    return target_name, values, "copy", None, []

                hooks = get_hooks(target_name)

                if hooks is not None:

                    ok, message = hooks.validate(
                        self,
                        values
                    )

                    if not ok:

                        print(message)

                        step = 2

                        continue

                    hooks.prepare(
                        self,
                        values
                    )

                result = self._select_output(
                    self._header(
                        project,
                        target,
                        fields,
                        values
                    )
                )

                if result is BACK:
                    step -= 1
                    continue

                output = result

                step += 1

                continue

            header = self._header(
                project,
                target,
                fields,
                values
            )

            header.append(
                f"{_e('✅ ')}output: {output}"
            )

            result = self._select_launch(
                header
            )

            if result is BACK:
                step -= 1
                continue

            self._save_state(
                project,
                target,
                values
            )

            chain_remaining = list(
                getattr(self, "chain_commands", [])
            )

            if chain_remaining:

                print(
                    f"\n▶ 意图链关联 {len(chain_remaining) + 1} 个命令，"
                    f"当前完成 {target[0]}，后续: "
                    f"{', '.join(chain_remaining)}。\n"
                    f"（各命令将依次构建提示词；主命令 {target[0]} 执行后"
                    f"继续生成 {chain_remaining[0]}）\n"
                )

            return target[0], values, output, result, chain_remaining

    def _try_derive_silent(
        self,
        target,
        fields,
        values
    ):
        """P38 批次 2：全推导工作流跳过逐项提问，静默推导 + 单次 recap 确认。

        适用条件（不满足则回退常规逐项收集）：
        - workflow 类目标且在 SILENT_DERIVE_WORKFLOWS 白名单
        - 无必填字段（P37 批次 1 已把五工作流全部降为可选/推导）
        - 已有项目/工作区锚点（否则无推导来源）
        用户选「逐项修改」或 BACK 时回退逐项流程，覆盖权保留。
        """

        name, kind = target

        if kind != "workflow" or name not in self.SILENT_DERIVE_WORKFLOWS:
            return False

        if not fields or any(required for _, required in fields):
            return False

        if not (
            values.get("Project ID")
            or values.get("Workspace ID")
        ):
            return False

        self._apply_field_defaults(fields, values)

        print(
            f"\n🔎 {name}：已按上下文推导以下输入"
            "（未列出的可选项留空）："
        )

        for field, _ in fields:

            value = values.get(field)

            print(
                f"   {field}: {value if value else '（空）'}"
            )

        idx = choose(
            "直接使用推导值继续？",
            [
                "✅ 使用推导值，继续",
                "✏️ 逐项修改",
            ],
            0,
        )

        return idx == 0

    def _resume_change(
        self,
        project,
        values
    ):
        """Change ID 已收集：检测已有 prepare 产物 → 预填 + 提示未决澄清。

        重入语义：选已有 change 时承接已有分析（proposal.md），而非重新
        收集必填项。首次运行（无产物）不干预；用户 BACK 改 Change ID 后
        重新检测。
        """
        from cli.services import change_resume

        # 先清掉上次的重入状态（换 Change ID 后重新检测）
        self._skip_fields.discard("Change Request")
        values.pop("Change Request", None)

        change_id = values.get("Change ID")
        if not (project and change_id):
            return

        resume = change_resume.read_change_artifact(
            self.workspaces,
            project,
            change_id
        )
        if not resume:
            return

        if resume["change_request"]:
            values["Change Request"] = resume["change_request"]
            self._skip_fields.add("Change Request")

        print(
            f"\n✅ 检测到已有 prepare 产物：{resume['path']}"
        )
        if resume["readiness"]:
            print(f"   Readiness: {resume['readiness']}")

        open_qs = resume["open_questions"]
        if open_qs:
            print(f"   未决澄清 {len(open_qs)} 条：")
            for q in open_qs[:6]:
                print(f"     • {q}")
            if len(open_qs) > 6:
                print(f"     … 共 {len(open_qs)} 条")

        if resume["change_request"]:
            print(
                "   Change Request 已从产物预填，跳过必填重收。\n"
            )
