# Skill Invocation

You are about to execute a task using a specialized skill.

## Skill

Name: {{skill_name}}

Location: {{skill_path}}

Source: {{skill_source}}

## Execution Rules

1. Load the skill's full instructions from its SKILL.md at the location above
   using the platform skill tool (`skill({ name: "{{skill_name}}" })` or
   equivalent) before starting.
2. Follow the skill's instructions strictly.
3. Do not skip validation or guardrail steps defined by the skill.
4. Do not invent missing information; stop and ask when required input is
   unavailable.

## Task

{{task}}

## Agent

{{agent}}

---

Begin execution.
