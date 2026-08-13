"""Wizard mixin: project-less intent intake (AI-guided entry).

Used when the user picks "AI 引导" (no project) in the project step.
Two rails:
  1. Quick candidates — the user's most-used project-less commands,
     ranked by usage count (workspaces/.aic-state.yaml →
     projectless_usage), Enter = pick.
  2. Intent text — free-text description; the AI maps it to a workflow
     or command via keyword rules (zero-dependency; LLM enhancement later),
     then presents a decision point (decision/recommend/impact).

After execution the caller bumps the usage counter (record_usage).
"""

from cli.utils.menu import BACK, Section, choose

PROJECTLESS_COMMANDS = (
    "maintain",
    "scan",
    "extensions-init",
    "skill-source",
    "pack",
    "workflow",
    "command",
    "skill",
)

# 规则映射：关键词 → 目标（零依赖意图识别；可后续换 LLM）
INTENT_RULES = [
    (("巡检", "维护", "maintain", "健康", "检查系统"), "maintain"),
    (("扫描", "检索", "查代码", "scan", "搜索关键词", "搜一下", "扫一下", "查一下"), "scan"),
    (("初始化", "扩展目录", "extensions", "init", "新环境"), "extensions-init"),
    (("三方", "skill 来源", "评估技能", "skill-source", "吸收", "评估.*skill", "评估.*技能"), "skill-source"),
    (("打包", "pack", "迁移包"), "pack"),
    (("新建工作流", "workflow"), "workflow"),
    (("新建命令", "command"), "command"),
    (("启动技能", "skill", "launch"), "skill"),
]

# 可选最大快捷候选数
MAX_CANDIDATES = 5


class WizardIntake:

    def intake(self, header):
        """Run the project-less intent intake. Returns a target name or BACK.

        Target may be a command (maintain/scan/...) — the caller resolves
        it via the normal target resolution path.
        """

        # 1. 快捷候选（按使用次数排序）
        usage = self.state.get("projectless_usage") or {}

        ranked = sorted(
            ((cmd, usage.get(cmd, 0)) for cmd in PROJECTLESS_COMMANDS
             if usage.get(cmd, 0) > 0),
            key=lambda x: (-x[1], x[0]),
        )

        options = []

        for cmd, count in ranked[:MAX_CANDIDATES]:

            options.append(
                f"⭐ {cmd} ({count}次)"
            )

        options.append(
            "✍️  描述你的意图（如：跑下巡检 / 初始化扩展）"
        )

        options.append(
            "❌  取消（返回项目选择）"
        )

        default = 0

        idx = choose(
            "你想做什么？[回车=快捷] 或 描述意图",
            options,
            default,
            header=header,
        )

        if idx is BACK:
            return BACK

        if idx == len(options) - 1:  # 取消
            return BACK

        if idx == len(options) - 2:  # 描述意图
            return self._intent_input(header)

        return ranked[idx][0]

    def _intent_input(self, header):
        """Free-text intent → rule-based recommendation → decision point."""

        text = input("描述你的意图: ").strip()

        if not text:

            return self._intent_input(header)

        target = self._match_intent(text)

        if target is None:

            print(
                "\n未识别到明确意图（规则未命中）。\n"
                "  可尝试: 跑下巡检 / 扫描代码 / 初始化扩展 / 评估三方技能\n"
            )

            return self._intent_input(header)

        print(
            f"\n决策: 选择要执行的流程\n"
            f"推荐: {target} — 根据你的描述「{text[:30]}」\n"
            f"影响: 进入 {target} 的字段收集与执行\n"
        )

        confirm = input(
            f"确认进入 {target}？[y/N] 或输入其他意图: "
        ).strip().lower()

        if confirm in ("y", "yes", ""):
            return target

        return self._intent_input(header)

    def _match_intent(self, text):
        """Rule-based intent → target mapping (first hit wins).

        Keywords are matched as substrings; patterns containing regex
        metacharacters (., *, ^, $) are matched as regex.
        """

        low = text.lower()

        for keywords, target in INTENT_RULES:

            for kw in keywords:

                kl = kw.lower()

                if any(ch in kl for ch in ".*^$"):

                    import re

                    if re.search(kl, low):

                        return target

                elif kl in low:

                    return target

        return None

    def record_usage(self, target):
        """Increment the usage counter for a project-less command."""

        if target not in PROJECTLESS_COMMANDS:

            return

        usage = self.state.setdefault(
            "projectless_usage", {}
        )

        usage[target] = usage.get(target, 0) + 1

        usage.setdefault("last_used", {})
        usage["last_used"]["command"] = target
        usage["last_used"]["at"] = __import__(
            "datetime"
        ).datetime.now().isoformat(timespec="seconds")

        self.store.save()
