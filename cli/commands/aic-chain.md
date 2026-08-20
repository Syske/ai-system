---
description: 链路口 - 按场景选择/描述，组合 工作流+命令+技能 的积木链路；建运行上下文与产物交接清单
---

Pick or describe a scenario and assemble it into a chain of building blocks
(workflow / command / skill) that runs as one task. Loose coupling with an
explicit handoff record: each run creates a run context
(`outputs/chain/{yyMMdd}-{desc}/chain-manifest.yaml`) that records every
block's produced artifact, so downstream blocks can locate upstream artifacts
without guessing paths.

**Inputs**:
- Chain (optional): pick a named chain from config/chains.yaml, or let the AI
  match a free-text scenario ("分析代码并把结果发到 wiki" → analyze-and-publish;
  "改 bug 并出转测文档" → bugfix-release-doc).

**Steps**

1. **Resolve the chain**
   - Show named chains (config/chains.yaml, AI-maintained chains via
     .aic-state.yaml → ai_chains when added).
   - User picks one, or describes the scenario; the AI matches label/scenario/name
     (and block names) with a zero-dependency keyword resolver.
   - No match → prompt the user to pick a named chain or register one; never quiet-guess.

2. **Create the run context (handoff record)**
   - `outputs/chain/{yyMMdd}-{desc}/chain-manifest.yaml` with the ordered blocks
     (type / name / args / artifact=None).
   - This is the coordination point: each block's artifact is registered here.

3. **Assemble and launch blocks in order**
   - workflow / command block → standard workflow/command prompt (PromptBuilder).
   - skill block → skill-launch prompt (reused template).
   - After each block completes, register its produced artifact path into the
     manifest (record_artifact), so the next block reads it from the manifest.

4. **Usage + evolution**
   - Record chain selection (chain_usage → .aic-state.yaml), sorted by frequency;
     the AI/maintenance may adjust or add chains over time (AI-maintained model,
     mirroring intents).

**Guardrails**

- A chain is a composition of existing blocks only; it never moves responsibility
  across modules or changes workflow/runtime behaviour.
- Builtin chains live in config/chains.yaml; AI-created chains are recorded in
  .aic-state.yaml (runtime state), not in the tracked config.
- If a scenario can't be matched, stop and ask — never invent a chain.
