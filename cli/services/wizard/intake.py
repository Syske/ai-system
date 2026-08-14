"""Wizard mixin: project-less intent intake (AI-guided entry).

Design (ADR-0009 AI-operation-first, clarified 2026-08-13):

- The entry is an INTENT MENU, not a free-text command guess. Intents are
  maintained by the AI in config/intents.yaml (builtin) and auto-created
  from real usage (AI-maintained, stored in .aic-state.yaml).
- An intent maps to ONE OR MORE commands (chained flow, e.g.
  issue-investigation → scan + change-impact + bugfix).
- Menu order = usage frequency (projectless_usage, command-level stats;
  multi-command intents rank by max command count).
- User picks an intent from the menu, then fills that intent's fields
  (reuses command_fields machinery).
- Free text remains as a fallback: the AI interprets it and either
  recommends an existing intent or proposes creating a new one.

Flow:  intent menu → pick → fill fields → run chained commands.
"""

from cli.utils.menu import BACK, Section, choose
from cli.utils.yaml import load_yaml

# 内置意图配置文件（AI 维护；AI 新建意图写入 .aic-state.yaml）
INTENTS_FILE = "config/intents.yaml"

# 多命令意图的串联：主命令（填字段）→ 后续命令（自动衔接）
MAX_INTENTS_SHOWN = 8


class WizardIntake:

    def intents_config(self):
        """Load builtin intents from config/intents.yaml."""
        path = self.root / INTENTS_FILE
        if not path.exists():
            return []
        data = load_yaml(path)
        return data.get("intents", []) if isinstance(data, dict) else []

    def ai_intents(self):
        """Load AI-created intents from .aic-state.yaml (user-created)."""
        return self.state.get("ai_intents", [])

    def _all_intents(self):
        """Builtin + AI-created intents."""
        return list(self.intents_config()) + list(self.ai_intents())

    def _intent_usage(self, intent):
        """Usage score = max command count among the intent's commands."""
        usage = self.state.get("projectless_usage") or {}
        counts = [usage.get(c, 0) for c in intent.get("commands", [])]
        return max(counts) if counts else 0

    def intake(self, header):
        """Run the project-less intent intake. Returns (intent, commands)."""

        intents = self._all_intents()

        if not intents:
            return None

        # 按使用频率排序（降序；并列按 label）
        ranked = sorted(
            intents,
            key=lambda it: (-self._intent_usage(it), it.get("label", "")),
        )

        options = []
        for it in ranked[:MAX_INTENTS_SHOWN]:
            usage = self._intent_usage(it)
            suffix = f"（{usage}次）" if usage > 0 else ""
            options.append(
                f"{it.get('icon', '✨')} {it.get('label', it.get('name'))}{suffix}"
            )

        options.append("✍️  描述你的意图（AI 理解后推荐/新建）")
        options.append("❌  取消（返回项目选择）")

        idx = choose(
            "选择意图（按使用频率排序）——你想做什么？",
            options,
            0,
            header=header,
        )

        if idx is BACK:
            return None

        if idx == len(options) - 1:  # 取消
            return None

        if idx == len(options) - 2:  # 描述意图
            return self._intent_from_text(header)

        intent = ranked[idx]

        return intent["name"], list(intent.get("commands", []))

    def _intent_from_text(self, header):
        """Free-text intent → AI interprets → recommend existing or propose new.

        Rule-based first (zero-dependency): keyword match against builtin
        intent labels. Unmatched → offer to create a new intent (AI records
        it for future maintenance).
        """

        text = input("描述你的意图: ").strip()

        if not text:
            return self._intent_from_text(header)

        # 1) 规则匹配现有意图（按 label 关键词）
        matched = self._match_intent_label(text)

        if matched:
            print(
                f"\n决策: 选择要执行的意图\n"
                f"推荐: {matched['label']} — 根据你的描述「{text[:30]}」\n"
                f"影响: 进入该意图的字段收集与执行\n"
            )
            confirm = input("确认？[y/N] 或输入其他意图: ").strip().lower()
            if confirm in ("y", "yes", ""):
                return matched["name"], list(matched.get("commands", []))
            return self._intent_from_text(header)

        # 2) 未匹配 → 提议新建意图（AI 维护）
        print(
            f"\n未匹配到现有意图「{text[:40]}」。\n"
            f"AI 将为此创建一个新意图（记录到 ai_intents，供后续使用）。\n"
        )
        confirm = input("创建新意图并进入引导？[y/N]: ").strip().lower()

        if confirm in ("y", "yes", ""):
            return self._create_ai_intent(text)

        return self._intent_from_text(header)

    def _match_intent_label(self, text):
        """Match free text against intent labels/names (keyword, zero-dep)."""

        low = text.lower()

        for intent in self._all_intents():

            label = intent.get("label", "")
            name = intent.get("name", "")

            for kw in (label, name):

                if kw and kw.lower() in low:

                    return intent

        # 额外关键词映射（意图级）
        kw_map = {
            "巡检": "weekly-maintenance",
            "维护": "weekly-maintenance",
            "健康": "weekly-maintenance",
            "扫描": "code-search",
            "检索": "code-search",
            "查代码": "code-search",
            "初始化": "init-extensions",
            "扩展": "init-extensions",
            "评估": "skill-source-assessment",
            "三方": "skill-source-assessment",
            "打包": "package-system",
            "工作流": "create-workflow",
            "命令": "create-command",
            "技能": "launch-skill",
            "排查": "issue-investigation",
            "问题": "issue-investigation",
            "超时": "issue-investigation",
            "报错": "issue-investigation",
        }

        for kw, intent_name in kw_map.items():

            if kw in low:

                for intent in self._all_intents():

                    if intent.get("name") == intent_name:

                        return intent

        return None

    def _create_ai_intent(self, text):
        """Create a new AI-maintained intent from free text.

        Command mapping is heuristic (keyword → projectless command); the
        AI refines the mapping on future use. Stored in .aic-state.yaml →
        ai_intents (persisted, sorted by usage like builtin intents).
        """

        # 从关键词推断关联命令
        command = self._infer_command(text)

        intent = {
            "name": self._slug(text),
            "label": text[:30],
            "icon": "✨",
            "commands": [command] if command else [],
            "builtin": False,
        }

        ai_intents = self.state.setdefault("ai_intents", [])

        # 去重：同名意图已存在则复用
        for it in ai_intents:

            if it.get("name") == intent["name"]:

                return it["name"], list(it.get("commands", []))

        ai_intents.append(intent)

        self.store.save()

        print(
            f"\n已创建新意图「{intent['label']}」（AI 维护，后续将按使用频率排序）。\n"
        )

        return intent["name"], list(intent.get("commands", []))

    def _infer_command(self, text):
        """Keyword → projectless command (best-effort; AI refines later)."""

        low = text.lower()

        for cmd, keywords in (
            ("maintain", ("巡检", "维护", "健康", "maintain")),
            ("scan", ("扫描", "检索", "查", "search", "scan")),
            ("extensions-init", ("扩展", "初始化", "init", "extensions")),
            ("skill-source", ("评估", "三方", "skill-source")),
            ("pack", ("打包", "pack")),
            ("workflow", ("工作流", "workflow")),
            ("command", ("命令", "command")),
            ("skill", ("技能", "skill")),
        ):

            for kw in keywords:

                if kw.lower() in low:

                    return cmd

        return None

    def record_usage(self, target):
        """Increment the usage counter for a project-less command."""

        if target not in self._projectless_commands():

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

    def _projectless_commands(self):
        """All commands reachable from any intent (builtin + AI-created)."""

        cmds = set()

        for intent in self._all_intents():

            cmds.update(intent.get("commands", []))

        return cmds

    def _slug(self, text):
        """kebab-case slug from free text (best-effort)."""

        import re

        s = re.sub(r"[^\w\u4e00-\u9fff]+", "-", text.lower()).strip("-")

        return s[:40] or "intent"
