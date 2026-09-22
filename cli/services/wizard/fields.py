"""Wizard mixin: field collection, defaults, and ask loop.

Split from wizard.py (P0).
"""

import re

from cli.services import providers, workflow_reader
from cli.utils.file import read_text
from cli.utils.menu import BACK, e as _e, ask_text, choose, choose_many


# P66：分支字段按**类别**匹配，不再绑字面量 "Branch"。
# 背景：P57 的「单候选自动采纳」只认 `field == "Branch"`，而 code-review /
# change-impact 的字段名是 `Branch Mapping` / `Base Branch` → 契约静默失配，从未生效。
BRANCH_EXCLUDE_HINTS = ("base", "mapping")


def is_branch_target_field(field):
    """目标/工作分支类字段（**不含** `Base Branch` 基线、`Branch Mapping` 覆盖项）。

    类别匹配而非字面量：字段名演进（`Source Branch` 等）不再导致规则失配。
    """

    low = (field or "").lower()

    return "branch" in low and not any(h in low for h in BRANCH_EXCLUDE_HINTS)


class WizardFields:

    def _fields_for(
        self,
        target
    ):

        name, kind = target

        self.target_name = name

        if kind == "command":

            self._field_defaults = {}

            # 交互命令（skill / chain）：字段收集交给 launcher 内部菜单，
            # wizard 不收集默认字段，直接进入交互流程（2026-09-11 用户反馈：
            # 选 chain 后应直接跳到「选择链路」菜单而非 Change ID 等字段询问）。
            if name in (
                "skill",
                "skill-launch",
                "chain",
                "chain-launch"
            ):
                return []

            return self._command_fields(name)

        text = read_text(
            self.root
            / "workflows"
            / f"{name}.md"
        )

        required, optional = self._parse_inputs(
            text
        )

        self._field_defaults = (
            workflow_reader.field_defaults(
                text
            )
        )

        fields = []

        for f in required:
            fields.append((f, True))

        for f in optional:
            fields.append((f, False))

        return fields

    @staticmethod
    def _parse_inputs(
        text
    ):

        return workflow_reader.parse_inputs(text)

    @staticmethod
    def _invalidate_dependents(
        values,
        field
    ):
        """Drop stale downstream values when an upstream field changes.

        Field candidates depend on earlier values: Branch is derived from
        Projects; Change ID / Task ID are derived from the project choice.
        When the user goes BACK and changes such an upstream field, the
        downstream values collected under the old choice are no longer
        valid and must be cleared (otherwise the prompt ships stale data).
        """

        upstream = {
            "Projects": {"Branch"},
            "Project ID": {"Change ID", "Task ID"},
            "Workspace ID": {"Change ID", "Task ID"},
        }

        for stale in upstream.get(field, set()):
            values.pop(stale, None)

    def _derive_fields(
        self,
        fields,
        values
    ):
        """运行期推导未收集的可推导字段（P37 批次 1，零 LLM）。

        三条衡量点：可生成/可推断 → 不让用户填。当前推导集：
        - Task ID：从 Task Card 读取（task_ids provider，已有）
        - Specification Reference：从 change 产物路径推导
        - Release Version：从 git tag / 上一版本推导（无 tag 回退日期版）
        - Change ID：Change Request 已收集时不显式问（_manual_default 已生成）
        """

        project = (
            values.get("Project ID")
            or values.get("Workspace ID")
        )

        change_id = values.get("Change ID")

        for field, _ in fields:

            if field in values and values[field]:
                continue

            if field == "Task ID" and project:

                from cli.services import providers

                tasks = providers.task_ids(
                    self,
                    values,
                    project
                )

                if len(tasks) == 1:
                    values["Task ID"] = tasks[0]

                continue

            if field == "Specification Reference" and \
                    project and change_id:

                from cli.services import change_resume

                values["Specification Reference"] = str(
                    change_resume.spec_reference_path(
                        self.workspaces,
                        project,
                        change_id
                    )
                )

                continue

            if field == "Release Version":

                from cli.services import git_version

                v = git_version.guess_release_version()

                if v:
                    values["Release Version"] = v

            # P37 批次 2：项目选择类 + 默认类推导（评估表后续批次）
            # - Project ID：wizard 已选项目推导
            # - Projects：**不推导**（P57/P58 修复）——Project ID/Workspace ID 本质是
            #   容器 id（workspaces 目录名），而 Projects 是服务名（repositories 映射/
            #   本地克隆）；把容器 id 当服务填入会被名称校验拒绝 → fail_field 重问 → 循环。
            #   留空 = 按 aic-scan.md 语义“扫描全部项目”。
            # - Analysis Target：主链进入默认 ai-system 自身
            # - Knowledge Operation：默认 collect
            if field == "Project ID" and project:
                values[field] = project
                continue

            if field == "Analysis Target" and not project:
                values[field] = "ai-system"
                continue

            if field == "Knowledge Operation" and not values.get(field):
                values[field] = "collect"
                continue

    # P66：文档化为「显式覆盖项」的分支字段（留空即由项目信息/主题推断）
    CONTAINER_DERIVED_OVERRIDE_FIELDS = ("Branch Mapping",)

    # P66：**显式 opt-in** —— 只有这些目标把 `Projects` 语义定为「本变更参与的全部服务」，
    # 因此在容器已选时可整体派生。其余目标（如 P57 的 `scan`：服务级选择即其交互目的，
    # 或 `trace`）保持候选驱动追问，不被静默覆盖。
    CONTAINER_DERIVE_TARGETS = frozenset({"code-review", "change-impact"})

    def _container_derived(self, fields, values, project, target_name=None):
        """P66：容器已确定 / 属覆盖项 / 有文档默认值的字段 → 预填并跳过提问。

        返回 `(silent, reasons)`：

        - `silent`：`{field: value|None}`，`None` 表示**不设值**（仅不再提问，
          留空由运行时的项目信息推断逻辑接管）
        - `reasons`：`{field: 依据}`，供 header/日志展示

        仅当**已选项目容器**存在时才派生；无容器、无映射 → 返回空（回退现状追问）。
        适用场景：code-review / change-impact 在前置已选项目后，不再二次追问
        项目与分支（用户 2026-09-21 反馈）。
        """

        from cli.services import providers

        # 无容器锚点 → 不派生（回退现状追问；祖先条款：不猜测）
        if not project:
            return {}, {}

        # 未 opt-in 的目标（命令/其他工作流）→ 保持既有候选驱动追问
        # （防 P57「scan 服务级选择」等契约被静默覆盖）
        if target_name is not None and target_name not in self.CONTAINER_DERIVE_TARGETS:
            return {}, {}

        silent = {}
        reasons = {}
        names = [f for f, _ in fields]

        services = providers.container_services(self, project)

        if "Projects" in names and services:
            silent["Projects"] = ", ".join(services)
            reasons["Projects"] = (
                f"容器 workspace.yaml 映射的参与服务（{len(services)} 个）"
            )

        for field in names:
            if field in self.CONTAINER_DERIVED_OVERRIDE_FIELDS:
                silent[field] = None
                reasons[field] = (
                    "显式覆盖项：留空即由项目信息/主题推断分支，无需提前指定"
                )

        for field in names:
            low = field.lower()
            if "branch" in low and "base" in low:
                default = self._field_defaults.get(field)
                if default:
                    silent[field] = default
                    reasons[field] = f"文档默认值（{default}）"

        return silent, reasons

    def _apply_field_defaults(
        self,
        fields,
        values
    ):
        """Fill skipped fields that carry an inline default like
        "Environment (default: local)" so the prompt never ships an
        empty # User Inputs for a field that has a documented default.

        Defaults are parsed once in workflow_reader.field_defaults at
        field-collection time, not re-derived here.
        """

        for field, _ in fields:

            if field in values:
                continue

            default = self._field_defaults.get(
                field
            )

            if default is not None:

                values[field] = default

        self._derive_fields(
            fields,
            values
        )

    def _ask_field(
        self,
        header,
        values,
        field,
        required,
        position,
        total
    ):

        if (
            self.environment_explicit
            and field.startswith("Environment")
        ):

            return self.environment_name

        choices = self._choices_for(
            values,
            field
        )

        # P57 契约（P66 修正为**类别匹配**）：目标分支类字段仅一个候选时直接采用，
        # 避免无意义菜单。原实现只认字面量 "Branch"，使 code-review 的
        # `Branch Mapping` / `Base Branch` 从未生效（契约静默失配）。
        # `Base Branch`（基线，有默认值）与 `Branch Mapping`（显式覆盖项）不走此路径。
        if len(choices) == 1 and is_branch_target_field(field):

            value = choices[0]

            self.history[field] = value

            return value

        suffix = (
            "必填"
            if required
            else "可选"
        )

        title = f"{field} ({suffix}) [{position}/{total}]"

        note = self._field_note(field)

        icon = _e(
            self._field_icon(field)
        )

        if choices:

            labels = self._option_descriptions(field)

            # Task ID 选项动态描述：读任务卡标题/服务，让用户不用点开卡片就知道选哪张
            if field == "Task ID" and not labels:

                project = (
                    values.get("Project ID")
                    or values.get("Workspace ID")
                    or self.project
                )

                if project:
                    labels = providers.task_card_summaries(
                        self,
                        values,
                        project
                    )

            options = []

            for c in choices:

                display = c

                if labels and c in labels:
                    display = f"{c} — {labels[c]}"

                options.append(f"{icon}{display}")

            if field in self._multi_select_fields():

                picked = choose_many(
                    title,
                    options,
                    header=header,
                    note=note,
                    max_visible=(
                        10
                        if field == "Projects"
                        else None
                    )
                )

                if picked is BACK:
                    return BACK

                if picked is None:
                    return None

                value = ", ".join(
                    choices[i] for i in picked
                )

                self.history[field] = value

                return value

            # Task ID 专属动作标签：手动输入可写任务描述/指定卡片；skip = AI 自行选卡
            manual_label = self._t(
                "field_actions.manual",
                "type manually"
            )

            skip_label = self._t(
                "field_actions.skip",
                "skip"
            )

            if field == "Task ID":

                manual_label = "手动输入（任务描述或指定卡片）"
                skip_label = "AI 自行选择"

            options.append(
                f"{_e(self._menu_option('field_actions', 'manual'))}"
                f"{manual_label}"
            )

            manual_index = len(choices)

            skip_index = None

            if not required:

                options.append(
                    f"{_e(self._menu_option('field_actions', 'skip'))}"
                    f"{skip_label}"
                )

                skip_index = manual_index + 1

            default = 0

            previous = self._previous_value(
                field
            )

            if previous in choices:
                default = choices.index(previous)

            idx = choose(
                title,
                options,
                default,
                allow_skip=not required,
                header=header,
                note=note
            )

            if idx is BACK:
                return BACK

            if idx is None:
                return None

            if (
                skip_index is not None
                and idx == skip_index
            ):
                return None

            if idx == manual_index:

                value = ask_text(
                    f"{icon}{field}: ",
                    header,
                    note=note,
                    default=self._manual_default(
                        field,
                        values
                    )
                )

                if value is BACK:
                    return BACK

                if not value:
                    # 必填空输入 → None：steps 对必填字段重问当前字段
                    return None

            else:

                value = choices[idx]

            self.history[field] = value

            return value

        prompt = (
            f"{icon}{field} ({suffix}): "
            if required
            else f"{icon}{field} ({suffix}，回车跳过): "
        )

        value = ask_text(
            prompt,
            header,
            note=note
        )

        if value is BACK:
            return BACK

        if not value:
            # 必填空输入 → None：steps 对必填字段重问当前字段
            return None

        self.history[field] = value

        return value

    def _previous_value(
        self,
        field
    ):

        previous = self.history.get(field)

        if previous:
            return previous

        if not self.project:
            return None

        pstate = (
            self.state
            .get("projects", {})
            .get(self.project, {})
        )

        if field == "Task ID":
            return pstate.get("last_task")

        if field == "Change ID":
            return pstate.get("last_change")

        return None

    def _manual_default(
        self,
        field,
        values
    ):
        """Change ID 建议默认：从 Change Request 自动生成 slug（P37 批次 1）。

        Change Request 已收集时派生 `{YYYYMM}-{slug}`（用户可编辑）；
        无 Change Request 时维持 `{YYYYMM}-` 前缀。已有 last_change /
        重入场景不建议（走既有值或已有 change 菜单）。
        """
        if field != "Change ID":
            return None

        if self._previous_value(field):
            return None

        from cli.services import change_resume

        change_request = (
            values.get("Change Request")
            or ""
        )

        return change_resume.suggest_change_id(change_request)

    def _choices_for(
        self,
        values,
        field
    ):

        field = re.sub(
            r"\s*\(default:[^)]*\)\s*$",
            "",
            field
        )

        if field in self._auto_fields():
            return providers.workspace_dirs(self)

        if field == "Mode":

            return providers.mode_choices(
                self,
                values
            )

        if field in (
            "Base Branch",
            "Zip",
            "Operation",
            "Keep Results",
            "Knowledge Operation",
            "Analysis Target",
            "Analysis Scope",
            "Review Focus",
        ):

            return self._field_choices(field)

        if field == "Workspace":
            return providers.workspace_dirs(self)

        if field == "Projects":
            # P57：有项目容器时优先呈现容器 workspace.yaml 映射的服务候选
            # （候选驱动），无容器/无映射时回退 repositories 元数据 ∪ projects/
            # 本地克隆（P58：不再依赖软链资源池）。
            project = (
                values.get("Project ID")
                or values.get("Workspace ID")
                or self.project
            )

            services = providers.container_services(self, project)

            if services:
                return services

            return providers.repo_candidates(self)

        if field == "Branch":
            return providers.branch_candidates(self, values)

        project = (
            values.get("Project ID")
            or values.get("Workspace ID")
            or self.project
        )

        if field == "Change ID" and project:
            return providers.change_dirs(
                self,
                values,
                project
            )

        if field == "Task ID" and project:
            return providers.task_ids(
                self,
                values,
                project
            )

        return []
