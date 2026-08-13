---
description: 优化 skill - 选技能/模式/agent，生成触发 skill-optimizer 的指令并启动
---

> **Deprecated (2026-08-08)**: superseded by the unified **`/aic-skill`**
> command (mode=optimize). This command remains for backward compatibility;
> new usage should go through `/aic-skill`.

Launch the skill-optimizer for selected skills: pick skills (grouped multi-select), pick the optimization mode (static / dynamic / trace / feedback), pick an agent (opencode / pi / claude), and generate a thin-trigger prompt instructing the agent to run skill-optimizer — then copy it and launch the agent.

**Inputs**: Agent (optional); Skill (optional); Mode (optional).

**Steps**

1. **Select skills**: the launcher lists ALL skills grouped per `config/skill-groups.yaml`. Type to filter; Space toggles; Enter confirms. **Empty Enter selects the current highlighted skill.**

2. **Select mode**: static (compliance + LLM evaluation) / dynamic (insight logs, needs platform) / trace (runtime traces, needs data) / feedback (user input only).

3. **Select the agent**: opencode / pi / claude from `config/providers.yaml`.

4. **Generate the prompt**: a thin-trigger prompt referencing the skill-optimizer workflow by location + the selected skills + mode — it does NOT embed the full workflow (keeps context ~0 until loaded on demand).

5. **Echo + confirm**: summary shown; confirm to copy the prompt and launch the agent.

**Output**

## Skill Optimize Report

- 所选 skill（名称/路径/来源）
- 优化模式（static / dynamic / trace / feedback）
- 所选 agent
- 提示词已复制、agent 已启动

**Guardrails**

- The prompt references the skill-optimizer by location only; never embed its full workflow (context-bloat prevention).
- Mode prerequisites: dynamic needs Agent Insight platform; trace needs trace data. The prompt must instruct the agent to verify readiness before running.
- skill-optimizer may take >10 minutes; instruct the agent to use a generous timeout and to require user acceptance (diff review) before modifying target skills.
- Skill grouping is config-driven via `config/skill-groups.yaml`; agent names via `config/providers.yaml` (optional `command` field).
- Run `python tools/check.py` and `python tools/repo-lint.py --repo-root .` before finishing; both must exit 0.
