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
from cli.utils.menu import BACK, ask_text, choose
from cli.utils.file import read_text

_PROMPT_TEMPLATE = Path("templates") / "prompts" / "skill-launch.md"


def _skill_options(skills):

    source_mark = {
        "extensions": "ext",
        "global": "g",
        "local": "proj",
    }

    options = []

    for s in skills:

        label = s["name"]

        mark = source_mark.get(s["source"], s["source"])

        label += f" [{mark}]"

        if s["description"]:
            label += f" — {s['description']}"

        options.append(label)

    return options


def _pick_skill(wizard, skills):

    options = _skill_options(skills)

    if not options:

        print("No skills found in extensions/, global, or project-local roots.")

        return None

    idx = choose(
        "Select a skill",
        options
    )

    if idx is BACK:
        return None

    return skills[idx]


def _pick_agent(wizard, default=None):

    return agent_picker.pick_agent(
        wizard.config,
        title="Select an agent",
        default=default
    )


def _render_prompt(wizard, skill, task, agent):

    template = read_text(
        wizard.root / _PROMPT_TEMPLATE
    )

    values = {
        "skill_name": skill["name"],
        "skill_path": skill["path"],
        "skill_source": skill["source"],
        "task": task,
        "agent": agent or "opencode",
    }

    result = template

    for k, v in values.items():
        result = result.replace("{{" + k + "}}", str(v))

    return result


def run(wizard, agent=None):
    """Run the interactive skill launcher.

    Returns (prompt, agent) when a skill and agent were chosen, else None.
    """

    skills = skill_scan.scan(
        wizard.root,
        wizard.environment_name
    )

    if not skills:

        print("No skills found.")

        return None

    skill = _pick_skill(
        wizard,
        skills
    )

    if skill is None:
        return None

    if agent is None:

        agent = _pick_agent(
            wizard,
            default=wizard.config.default_provider()
        )

        if agent is None:
            return None

    task = ask_text(
        "Task — what should the agent do with this skill? (empty = skip): "
    )

    if task is BACK:
        return None

    if not task:
        task = ""

    prompt = _render_prompt(
        wizard,
        skill,
        task,
        agent
    )

    return prompt, agent
