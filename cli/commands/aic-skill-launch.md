---
description: 启动 skill - 选择 skill 与 agent（opencode/pi），生成按需加载指令并启动
---

Launch a skill with a chosen agent: pick a skill (from the config-driven extensions dir, global, or project-local roots), pick an agent (opencode / pi / claude), enter the task, and generate a thin-trigger prompt that instructs the agent to load the skill on demand — then copy it and launch the agent.

**Inputs**: Agent (optional; pick from enabled providers); Skill (optional; pick interactively); Task (optional).

**Steps**

1. **Select skills (multi-select, grouped)**: the launcher lists ALL skills grouped per `config/skill-groups.yaml` (config-driven, aligned with menu.yaml): source groups (extensions/global/local) and custom combo groups (type `list`). Group titles come from `config/i18n/{locale}.yaml`. Each entry shows its source (`[ext]`/`[g]`/`[proj]`). Type to filter by keyword; Space toggles selection; Enter confirms. **Empty Enter selects the currently highlighted skill.**

2. **Preview details**: the selected skills' frontmatter (usage / trigger, when present) is shown so you can confirm the choice before proceeding.

3. **Enter the task**: pick from task presets (`config/skill-groups.yaml → tasks`) or type custom text. A list-combo group with a `task` field pre-fills its default task (e.g. hotfix combo → 转测文档 template).

4. **Select the agent**: choose opencode / pi / claude from enabled providers (`config/providers.yaml`; label/icon/description from provider config; default highlighted). This is a reusable agent picker shared by all agent-selecting flows.

5. **Generate the prompt**: the launcher renders a thin-trigger prompt that lists the selected skills by name + SKILL.md location and instructs the agent to load each via the platform skill tool — it does NOT embed the full SKILL.md (keeps context ~0 until loaded on demand).

6. **Echo + confirm**: a summary (skills / agent / task) is shown; confirm to copy the prompt and launch the chosen agent.

**Output**

## Skill Launch Report

- 所选 skill（名称 / 路径 / 来源：extensions / global / local）
- 所选 agent（opencode / pi / claude）
- 任务描述
- 提示词已复制、agent 已启动

**Guardrails**

- The generated prompt must reference the skills by name + location only, never embed the full SKILL.md (context-bloat prevention).
- Company skills live in the config-driven `extensions/` dir and are loaded explicitly by this launcher — they are deliberately NOT auto-discovered by agents.
- Agent names come from `config/providers.yaml` (label/description configurable; optional `command` field for the actual launch command, e.g. `npx pi`); an unknown agent must not be launched.
- Skill grouping/combos are config-driven via `config/skill-groups.yaml` (not hardcoded); skills already placed in an earlier group are deduplicated from later groups.
- Skill list shows ALL sources (extensions/global/project) with keyword type-to-filter; no skill is hidden by default.
- Non-TTY mode degrades to numbered-input fallbacks (existing menu behavior).
