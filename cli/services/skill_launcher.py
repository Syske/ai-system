"""Interactive skill launcher.

Flow:
1. Pick a skill (extensions/global/local, menu with type-to-filter).
2. Pick an agent to launch (opencode / pi / claude, per providers.yaml).
3. Enter the task description.
4. Render the thin-trigger prompt (instructs the agent to load the selected
   skill via the platform skill tool, then execute the task).
5. Copy to clipboard and launch the chosen agent.

The prompt references the skill by name/location only — it does NOT embed the
full SKILL.md, keeping context cost ~0 until the agent loads it on demand.
"""

from pathlib import Path

from cli.services import agent_picker, skill_scan
from cli.services.wizard import Wizard
from cli.utils.menu import BACK, Section, ask_text, choose_many, e
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


def _pick_skills(wizard, skills):
    """Multi-select skills (grouped). Returns a list of skill dicts."""

    options, skills_by_index = _group_skills(
        wizard.config,
        skills
    )

    if not options:

        print("No skills found in extensions/, global, or project-local roots.")

        return None

    picked = choose_many(
        f"{e('🧩 ')}Select skills (Space toggles, Enter confirms)",
        options
    )

    if picked is BACK:
        return None

    if not picked:
        return []

    return [skills_by_index[i] for i in picked]


def _pick_agent(wizard, default=None):

    return agent_picker.pick_agent(
        wizard.config,
        title=f"{e('🤖 ')}Select an agent",
        default=default
    )


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


def run(wizard, agent=None):
    """Run the interactive skill launcher.

    Returns (prompt, agent) when skills and an agent were chosen, else None.
    """

    skills = skill_scan.scan(
        wizard.root,
        wizard.environment_name
    )

    if not skills:

        print("No skills found.")

        return None

    picked = _pick_skills(
        wizard,
        skills
    )

    if picked is None:
        return None

    if not picked:

        print("No skill selected.")

        return None

    if agent is None:

        agent = _pick_agent(
            wizard,
            default=wizard.config.default_provider()
        )

        if agent is None:
            return None

    task = ask_text(
        f"{e('📝 ')}Task — what should the agent do with the selected skills? (empty = skip): "
    )

    if task is BACK:
        return None

    if not task:
        task = ""

    prompt = _render_prompt(
        wizard,
        picked,
        task,
        agent
    )

    return prompt, agent
