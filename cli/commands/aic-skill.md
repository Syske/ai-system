---
description: 启动 skill - 统一入口（launch / optimize 模式），选择 skill 与 agent，生成按需加载指令并启动
---

Unified skill launcher: pick skills (grouped multi-select from
`config/skill-groups.yaml`), pick an agent (opencode / pi / claude), and
generate a thin-trigger prompt — then copy it and launch the agent.

Two modes:

- **launch** (default): load selected skills on demand, with an optional task
  (replaces the archived skill-launch command)
- **optimize**: run the skill-optimizer on the selected skills, with an
  optimization mode (static / dynamic / trace / feedback)
  (replaces the archived skill-optimize command)

**Inputs**: Mode (optional; `launch` | `optimize`); Agent (optional); Skill (optional); Task (launch mode) / Mode-optimize (optimize mode).

**Steps**

1. **Determine mode** — `launch` (default) or `optimize` (from input or ask).

2. **Select skills (multi-select, grouped)**: list ALL skills grouped per
   `config/skill-groups.yaml`: source groups (extensions/global/local) and
   custom combo groups (type `list`). Group titles from
   `config/i18n/{locale}.yaml`; each entry shows its source
   (`[ext]`/`[g]`/`[proj]`). Type to filter; Space toggles; Enter confirms.
   **Empty Enter selects the currently highlighted skill.**

3. **Mode-specific step**:
   - launch → **preview details** (frontmatter usage/trigger) + **enter the
     task** (presets from `config/skill-groups.yaml → tasks` or custom)
   - optimize → **select optimization mode**: static (compliance + LLM
     evaluation) / dynamic (insight logs, needs platform) / trace (runtime
     traces, needs data) / feedback (user input only)

4. **Select the agent**: opencode / pi / claude from enabled providers
   (`config/providers.yaml`; label/icon/description from config; default
   highlighted). Reusable agent picker shared by all agent-selecting flows.

5. **Generate the prompt**: thin-trigger — lists skills by name + SKILL.md
   location (launch) or references the skill-optimizer by location + mode
   (optimize). Never embeds full SKILL.md / workflow (context-bloat
   prevention).

6. **Echo + confirm**: summary (mode / skills / agent / task-or-mode) shown;
   confirm to copy the prompt and launch the chosen agent.

**Output**

## Skill Launch Report

- 模式（launch / optimize）
- 所选 skill（名称 / 路径 / 来源：extensions / global / local）
- 所选 agent（opencode / pi / claude）
- 任务描述（launch）或优化模式（optimize）
- 提示词已复制、agent 已启动

**Guardrails**

- The generated prompt references skills / optimizer by name + location only,
  never embeds full content (context-bloat prevention).
- Company skills live in the config-driven `extensions/` dir and are loaded
  explicitly by this launcher — never auto-discovered by agents.
- Agent names come from `config/providers.yaml` (optional `command` field);
  an unknown agent must not be launched.
- Skill grouping/combos are config-driven via `config/skill-groups.yaml`;
  skills already placed in an earlier group are deduplicated from later ones.
- optimize mode prerequisites: dynamic needs Agent Insight platform; trace
  needs trace data — the prompt must instruct the agent to verify readiness
  before running.
- skill-optimizer may take >10 min; instruct the agent to use a generous
  timeout and require user acceptance (diff review) before modifying skills.
- optimize mode: run `python tools/check.py` and
  `python tools/repo-lint.py --repo-root .` before finishing; both must exit 0.
- Non-TTY mode degrades to numbered-input fallbacks (existing menu behavior).
