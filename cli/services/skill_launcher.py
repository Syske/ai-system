"""Interactive skill launcher.

Flow:
1. Pick skills (grouped multi-select, config-driven via skill-groups.yaml).
2. Preview the selected skills' details (frontmatter usage/trigger).
3. Pick an agent (opencode / pi / claude, per providers.yaml).
4. Enter the task (from presets or free text; combo default task pre-filled).
5. Render the thin-trigger prompt (instructs the agent to load the selected
   skills via the platform skill tool, then execute the task).
6. Echo a summary, copy to clipboard, and launch the chosen agent.

The prompt references skills by name/location only — it does NOT embed the
full SKILL.md, keeping context cost ~0 until the agent loads them on demand.
"""

from pathlib import Path

from cli.services import agent_picker, skill_scan
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


def _pick_agent(wizard, default=None):

    return agent_picker.pick_agent(
        wizard.config,
        title=f"{e('🤖 ')}Select an agent",
        default=default
    )


def _task_options(config, default_task):
    """Build task-preset options + custom entry.

    Returns a list of option labels; the first is "use default (if any)".
    """

    presets = []

    if default_task:
        presets.append(default_task)

    for group in config.skill_tasks():

        items = group.get("items") or []

        for item in items:
            presets.append(item)

    options = []

    for p in presets:
        options.append(p)

    return options


def _pick_task(wizard, default_task):
    """Choose a task from presets or free text. Returns the task string."""

    options = _task_options(
        wizard.config,
        default_task
    )

    if options:

        options = list(dict.fromkeys(options))

        options.append("✏️  custom...")

        idx = choose(
            f"{e('📝 ')}Select a task",
            options,
            default=0
        )

        if idx is BACK:
            return None

        if idx < len(options) - 1:
            return options[idx]

        task = ask_text(
            f"{e('📝 ')}Task — describe the task: "
        )

        if task is BACK:
            return None

        return task.strip()

    task = ask_text(
        f"{e('📝 ')}Task — what should the agent do with the selected skills? (empty = skip): "
    )

    if task is BACK:
        return None

    return task.strip()


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


def _echo(prompt, skills, agent, task):
    """Print a summary of what will be launched before confirming."""

    print()
    print(f"{e('📋 ')}Prompt summary:")
    print(f"  skills: {', '.join(s['name'] for s in skills)}")
    print(f"  agent:  {agent}")
    print(f"  task:   {task or '(none)'}")
    print()


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

    _preview_skills(picked)

    default_task = wizard.config.combo_task(
        {s["name"] for s in picked}
    )

    if agent is None:

        agent = _pick_agent(
            wizard,
            default=wizard.config.default_provider()
        )

        if agent is None:
            return None

    task = _pick_task(
        wizard,
        default_task
    )

    if task is None:
        return None

    prompt = _render_prompt(
        wizard,
        picked,
        task,
        agent
    )

    _echo(
        prompt,
        picked,
        agent,
        task
    )

    confirm = ask_text(
        f"{e('🚀 ')}Launch {agent} with these skills? (Enter to confirm, or type no): "
    )

    if confirm is BACK:
        return None

    if confirm and confirm.strip().lower() in ("no", "n", "cancel", "取消"):
        return None

    return prompt, agent
