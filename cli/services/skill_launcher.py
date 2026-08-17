"""Interactive skill launcher (as an InteractiveCommand).

Flow (uniform step state machine):
1. Pick skills (grouped multi-select, config-driven via skill-groups.yaml).
2. Preview the selected skills' details (frontmatter usage/trigger).
3. Pick an agent (opencode / pi / claude, per providers.yaml).
4. Enter the task (from presets or free text; combo default task pre-filled).
5. Render the thin-trigger prompt and echo a summary, then confirm.

Every step honors BACK (rolls back one step; first step → quit, so the
caller — e.g. the wizard — can re-select instead of hard-exiting).

The prompt references skills by name/location only — it does NOT embed the
full SKILL.md, keeping context cost ~0 until the agent loads them on demand.
"""

from pathlib import Path

from cli.services import agent_picker, skill_scan
from cli.services.interactive import BACK_, InteractiveCommand, NEXT, QUIT
from cli.services.wizard import Wizard
from cli.utils.menu import BACK, Section, ask_text, choose, choose_many, e
from cli.utils.file import read_text

_PROMPT_TEMPLATE = Path("templates") / "prompts" / "skill-launch.md"


def _source_mark(source):

    marks = {
        "extensions": f"{e('🧩 ')}ext",
        "global": f"{e('🌍 ')}g",
        "local": f"{e('📁 ')}proj",
    }

    return marks.get(source, source)


def _skill_label(skill):

    label = skill["name"]

    label += f" [{_source_mark(skill['source'])}]"

    if skill["description"]:
        label += f" — {skill['description']}"

    return label


def _group_skills(config, skills):
    """Group skills per config/skill-groups.yaml.

    Returns (options, skills_by_index):
    - options: list of Section headers + skill labels (for choose_many)
    - skills_by_index: mapping option index -> skill dict (selectable only)
    """

    groups = config.skill_groups()

    skills_by_index = {}

    options = []

    assigned = set()

    for group in groups:

        gtype = group.get("type")
        value = group.get("value")

        members = []

        if gtype == "source":

            for s in skills:

                if (
                    s["source"] == value
                    and s["name"] not in assigned
                ):
                    members.append(s)

        elif gtype == "list":

            names = set(group.get("skills") or [])

            for s in skills:

                if (
                    s["name"] in names
                    and s["name"] not in assigned
                ):
                    members.append(s)

        if not members:
            continue

        title = config.skill_group_title(group.get("title", ""))

        options.append(Section(title))

        for s in members:

            idx = len(options)

            options.append(_skill_label(s))

            skills_by_index[idx] = s

            assigned.add(s["name"])

    remaining = [
        s
        for s in skills
        if s["name"] not in assigned
    ]

    if remaining:

        title = config.skill_group_title("skill_group_other")

        options.append(Section(title))

        for s in remaining:

            idx = len(options)

            options.append(_skill_label(s))

            skills_by_index[idx] = s

    return options, skills_by_index


def _preview_skills(skills):
    """Print the selected skills' details (name, source, usage, trigger)."""

    print()
    print(f"{e('🔍 ')}Selected skills:")

    for s in skills:

        print(f"  • {s['name']} [{_source_mark(s['source'])}]")

        if s.get("usage"):
            print(f"    usage: {s['usage']}")

        if s.get("trigger"):
            print(f"    trigger: {s['trigger']}")

    print()


def _skill_block(skill):

    return (
        f"- {skill['name']} ({skill['path']}) [{skill['source']}]"
    )


def _render_prompt(wizard, skills, task, agent):

    template = read_text(
        wizard.root / _PROMPT_TEMPLATE
    )

    skills_md = "\n".join(
        _skill_block(s)
        for s in skills
    )

    values = {
        "skill_list": skills_md,
        "task": task,
        "agent": agent or "opencode",
    }

    result = template

    for k, v in values.items():
        result = result.replace("{{" + k + "}}", str(v))

    return result


class SkillLauncher(InteractiveCommand):

    def __init__(self, wizard, agent=None):

        super().__init__(wizard)

        self.forced_agent = agent

    def _step_pick_skills(self):

        skills = skill_scan.scan(
            self.wizard.root,
            self.wizard.environment_name
        )

        if not skills:

            print("No skills found.")

            return QUIT

        options, skills_by_index = _group_skills(
            self.wizard.config,
            skills
        )

        picked = choose_many(
            f"{e('🧩 ')}Select skills (Space toggles, Enter confirms, empty Enter = current)",
            options,
            enter_selects_current=True
        )

        if picked is BACK:
            return QUIT

        if not picked:
            return BACK_

        self.state["skills"] = [
            skills_by_index[i]
            for i in picked
        ]

        _preview_skills(self.state["skills"])

        return NEXT

    def _step_pick_agent(self):

        if self.forced_agent:

            self.state["agent"] = self.forced_agent

            return NEXT

        agent = agent_picker.pick_agent(
            self.wizard.config,
            title=f"{e('🤖 ')}Select an agent",
            default=self.wizard.config.default_provider()
        )

        if agent is None:
            return BACK_

        self.state["agent"] = agent

        return NEXT

    def _step_pick_task(self):

        picked = self.state.get("skills", [])

        default_task = self.wizard.config.combo_task(
            {s["name"] for s in picked}
        )

        presets = []

        if default_task:
            presets.append(default_task)

        for group in self.wizard.config.skill_tasks():

            for item in group.get("items") or []:
                presets.append(item)

        if presets:

            options = list(dict.fromkeys(presets))

            options.append(f"{e('✏️ ')}custom...")

            idx = choose(
                f"{e('📝 ')}Select a task",
                options,
                default=0
            )

            if idx is BACK:
                return BACK_

            if idx < len(options) - 1:

                self.state["task"] = options[idx]

                return NEXT

            task = ask_text(
                f"{e('📝 ')}Task — describe the task: "
            )

            if task is BACK:
                return BACK_

            self.state["task"] = task.strip()

            return NEXT

        task = ask_text(
            f"{e('📝 ')}Task — what should the agent do with the selected skills? (empty = skip): "
        )

        if task is BACK:
            return BACK_

        self.state["task"] = task.strip()

        return NEXT

    def _step_confirm(self):

        skills = self.state.get("skills", [])
        agent = self.state.get("agent", "")
        task = self.state.get("task", "")

        prompt = _render_prompt(
            self.wizard,
            skills,
            task,
            agent
        )

        print()
        print(f"{e('📋 ')}Prompt summary:")
        print(f"  skills: {', '.join(s['name'] for s in skills)}")
        print(f"  agent:  {agent}")
        print(f"  task:   {task or '(none)'}")
        print()

        confirm = ask_text(
            f"{e('🚀 ')}Launch {agent} with these skills? (Enter to confirm, or type no): "
        )

        if confirm is BACK:
            return BACK_

        if confirm and confirm.strip().lower() in ("no", "n", "cancel", "取消"):
            return BACK_

        return ("done", prompt, agent)

    steps = [
        _step_pick_skills,
        _step_pick_task,
        _step_pick_agent,
        _step_confirm,
    ]


def run(wizard, agent=None):
    """Convenience wrapper: run SkillLauncher, return (prompt, agent) or None."""

    result = SkillLauncher(
        wizard,
        agent=agent
    ).run()

    if result is None:
        return None

    return result


def run_skill(wizard, agent=None, mode=None):
    """Unified /aic-skill entry: mode=launch (default)."""

    if mode and str(mode).strip().lower() not in ("launch", ""):

        print(
            f"{e('⚠️ ')}Unknown skill mode '{mode}' — defaulting to launch."
        )

    return run(wizard, agent)
