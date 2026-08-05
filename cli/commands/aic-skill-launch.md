---
description: 启动 skill - 选择 skill 与 agent（opencode/pi），生成按需加载指令并启动
---

Launch a skill with a chosen agent: pick a skill (from the config-driven extensions dir, global, or project-local roots), pick an agent (opencode / pi / claude), enter the task, and generate a thin-trigger prompt that instructs the agent to load the skill on demand — then copy it and launch the agent.

**Inputs**: Agent (optional; pick from enabled providers); Skill (optional; pick interactively); Task (optional).

**Steps**

1. **Select the skill**: the launcher lists skills from (in priority order) the extensions root (`layers.skills` in `config/environments/{env}.yaml`, default `{workspace_root}/extensions`), the global root (`~/.agents/skills`, shared by opencode and pi), and project-local roots (`.opencode/skills`, `.claude/skills`, `.agents/skills` up to the git root). Pick one with the filter menu.

2. **Select the agent**: choose opencode / pi / claude (from `config/providers.yaml` enabled providers).

3. **Enter the task**: describe what the agent should do with the skill (optional; empty = load the skill and report readiness).

4. **Generate the prompt**: the launcher renders a thin-trigger prompt that references the skill by name + SKILL.md location and instructs the agent to load it via the platform skill tool — it does NOT embed the full SKILL.md (keeps context ~0 until loaded on demand).

5. **Copy + launch**: the prompt is copied to the clipboard and the chosen agent is launched at the workspace root.

**Output**

## Skill Launch Report

- 所选 skill（名称 / 路径 / 来源：extensions / global / local）
- 所选 agent（opencode / pi / claude）
- 任务描述
- 提示词已复制、agent 已启动

**Guardrails**

- The generated prompt must reference the skill by name + location only, never embed the full SKILL.md (context-bloat prevention).
- Company skills live in the config-driven `extensions/` dir and are loaded explicitly by this launcher — they are deliberately NOT auto-discovered by agents.
- Agent names come from `config/providers.yaml`; an unknown agent must not be launched.
- Non-TTY mode degrades to numbered-input fallbacks (existing menu behavior).
