---
description: 启动 skill - 统一入口（launch 模式），选择 skill 与 agent，生成按需加载指令并启动
---

Unified skill launcher: pick skills (grouped multi-select from
`config/skill-groups.yaml`), pick an agent (opencode / pi / claude), and
generate a thin-trigger prompt — then copy it and launch the agent.

Single mode:

- **launch** (default): load selected skills on demand, with an optional task
  (replaces the archived skill-launch command)

(The former `optimize` mode ran the skill-optimizer meta-tool; that skill was
archived 2026-08-17 under the Value-Burden Check — see
`reports/VALUE-BURDEN-DECISION-skill-optimizer-2026-08-17.md`. The mode is
removed; this command is launch-only.)

**Inputs**: Mode (optional; `launch`); Agent (optional); Skill (optional); Task (launch mode).

**Steps**

1. **Select skills (multi-select, grouped)**: list ALL skills grouped per
   `config/skill-groups.yaml`: source groups (extensions/global/local) and
   custom combo groups (type `list`). Group titles from
   `config/i18n/{locale}.yaml`; each entry shows its source
   (`[ext]`/`[g]`/`[proj]`). Type to filter; Space toggles; Enter confirms.
   **Empty Enter selects the currently highlighted skill.**

2. **Preview + task**: preview details (frontmatter usage/trigger) + enter the
   task (presets from `config/skill-groups.yaml → tasks` or custom).

3. **Select the agent**: opencode / pi / claude from enabled providers
   (`config/providers.yaml`; label/icon/description from config; default
   highlighted). Reusable agent picker shared by all agent-selecting flows.

4. **Generate the prompt**: thin-trigger — lists skills by name + SKILL.md
   location. Never embeds full SKILL.md / workflow (context-bloat
   prevention).

5. **Echo + confirm**: summary (mode / skills / agent / task) shown; confirm
   to copy the prompt and launch the chosen agent.

**Output**

## Skill Launch Report

- 模式（launch）
- 所选 skill（名称 / 路径 / 来源：extensions / global / local）
- 所选 agent（opencode / pi / claude）
- 任务描述（launch）
- 提示词已复制、agent 已启动

**Guardrails**

- The generated prompt references skills by name + location only, never
  embeds full content (context-bloat prevention).
- Company skills live in the config-driven `extensions/` dir and are loaded
  explicitly by this launcher — never auto-discovered by agents.
- Agent names come from `config/providers.yaml` (optional `command` field);
  an unknown agent must not be launched.
- Skill grouping/combos are config-driven via `config/skill-groups.yaml`;
  skills already placed in an earlier group are deduplicated from later ones.
- Non-TTY mode degrades to numbered-input fallbacks (existing menu behavior).
