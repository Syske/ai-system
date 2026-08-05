# Skill Optimization

You are about to run the skill-optimizer for one or more skills.

## Skill Optimizer

Location: skills/skill-optimizer (SKILL.md + workflow.md)

Load the skill-optimizer instructions and workflow from that location before
starting. Follow its steps strictly: 引导 → 环境准备 → 执行优化 → Review → 加载.

## Skills to optimize

{{skill_list}}

## Optimization mode

Mode: {{mode}}

{{mode_desc}}

## Execution Rules

1. Load the skill-optimizer SKILL.md + workflow.md (at the location above)
   using the platform skill tool before starting.
2. Follow the workflow steps strictly; run all commands from the
   skill-optimizer directory.
3. Before running, verify environment readiness (model connectivity for
   static; Insight platform for dynamic; trace data for trace).
4. For each selected skill, run `opt.sh --action optimize --mode {{mode}}`.
5. Present the diff and require the user to review / accept / revert before
   finishing. Do not modify the target skills without explicit acceptance.

## Agent

{{agent}}

---

Begin execution.
