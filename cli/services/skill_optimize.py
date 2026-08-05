"""Interactive skill-optimize launcher (as an InteractiveCommand).

Collects the parameters to run skill-optimizer and renders a thin-trigger
prompt for the chosen agent (opencode / pi / claude) to execute it.

Flow (uniform step state machine, BACK rolls back one step):
1. Pick skills to optimize (grouped multi-select).
2. Pick the optimization mode (static / dynamic / trace / feedback).
3. Pick an agent to run skill-optimizer.
4. Echo a summary and confirm.

The prompt references the skill-optimizer workflow by location and the
selected skills by name — it does NOT embed the full skill-optimizer
workflow, keeping context cost ~0 until the agent loads it on demand.
"""

from pathlib import Path

from cli.services import agent_picker, skill_scan
from cli.services.interactive import BACK_, InteractiveCommand, NEXT, QUIT
from cli.services.wizard import Wizard
from cli.utils.menu import BACK, Section, ask_text, choose, choose_many, e
from cli.utils.file import read_text

_PROMPT_TEMPLATE = Path("templates") / "prompts" / "skill-optimize.md"

MODES = (
    ("static", "static compliance + LLM evaluation (no extra data)"),
    ("dynamic", "insight run logs (needs Agent Insight platform)"),
    ("trace", "runtime trace data (needs trace data source)"),
    ("feedback", "user-provided feedback only"),
)


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
    """Group skills per config/skill-groups.yaml (reused from skill-launch)."""

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


def _render_prompt(wizard, skills, mode, mode_desc, agent):

    template = read_text(
        wizard.root / _PROMPT_TEMPLATE
    )

    skills_md = "\n".join(
        f"- {s['name']} ({s['path']}) [{s['source']}]"
        for s in skills
    )

    values = {
        "skill_list": skills_md,
        "mode": mode,
        "mode_desc": mode_desc,
        "agent": agent or "opencode",
    }

    result = template

    for k, v in values.items():
        result = result.replace("{{" + k + "}}", str(v))

    return result


class SkillOptimizeLauncher(InteractiveCommand):

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
            f"{e('🔧 ')}Select skills to optimize (Space toggles, Enter confirms, empty Enter = current)",
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

        print()
        print(f"{e('🔍 ')}Selected skills:")

        for s in self.state["skills"]:
            print(f"  • {s['name']} [{_source_mark(s['source'])}]")

        print()

        return NEXT

    def _step_pick_mode(self):

        options = [
            f"{e('🧪 ')}{name} — {desc}"
            for name, desc in MODES
        ]

        idx = choose(
            f"{e('⚙️ ')}Select optimization mode",
            options
        )

        if idx is BACK:
            return BACK_

        self.state["mode"] = MODES[idx][0]

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

    def _step_confirm(self):

        skills = self.state.get("skills", [])
        mode = self.state.get("mode", "static")
        agent = self.state.get("agent", "")

        mode_desc = dict(MODES).get(mode, "")

        prompt = _render_prompt(
            self.wizard,
            skills,
            mode,
            mode_desc,
            agent
        )

        print()
        print(f"{e('📋 ')}Prompt summary:")
        print(f"  skills: {', '.join(s['name'] for s in skills)}")
        print(f"  mode:   {mode}")
        print(f"  agent:  {agent}")
        print()

        confirm = ask_text(
            f"{e('🚀 ')}Launch {agent} to optimize these skills? (Enter to confirm, or type no): "
        )

        if confirm is BACK:
            return BACK_

        if confirm and confirm.strip().lower() in ("no", "n", "cancel", "取消"):
            return BACK_

        return ("done", prompt, agent)

    steps = [
        _step_pick_skills,
        _step_pick_mode,
        _step_pick_agent,
        _step_confirm,
    ]


def run(wizard, agent=None):
    """Convenience wrapper: run SkillOptimizeLauncher, return (prompt, agent)."""

    result = SkillOptimizeLauncher(
        wizard,
        agent=agent
    ).run()

    if result is None:
        return None

    return result
