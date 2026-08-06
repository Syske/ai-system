# Change Proposal: S4 — `aic-skill-launch` Skill Launcher

| Field | Value |
|---|---|
| Status | **Implemented** |
| Type | Structural (new command + CLI service) |
| Author | AI Maintainer |
| Created | 2026-08-05 |
| Reference | MAINTENANCE-2026-08-05.md; user request (select skill + agent, auto-trigger) |
| Process | OPERATIONS §12 Change Management |

---

## 1. Problem

The user currently triggers company/platform skills manually: open an AI
session, type the skill name, hand-write "use skill X to do Y". This is
repetitive and error-prone. The request:

> 启动扩展脚本后按需选择 skill，然后触发操作 … 让我选择 skill 和 agent（opencode、pi）

A launcher is needed: start a script → pick a skill → pick an agent
(opencode / pi) → generate the trigger prompt → copy it and launch the agent.

## 2. Context (established facts)

- opencode loads skills **on demand** via the `skill` tool; only
  name + description live in `<available_skills>`. Full SKILL.md is injected
  only when loaded.
- Global skill paths (`~/.config/opencode/skills`, `~/.claude/skills`,
  `~/.agents/skills`) all resolve to `C:\Users\syske\.agents\skills`
  (symlinked) — scan by realpath to dedupe.
- Project-local discovery walks from CWD up to the git worktree root
  (`D:\workspace\ai-workspace\ai-system` for the current workspace).
- **pi shares the same SKILL.md mechanism**: `pi-cache-optimizer`
  (`~/.pi/agent/npm/node_modules/pi-cache-optimizer/index.ts`) groups skills
  by `dirname(dirname(skill.filePath))` and reads `~/.agents/skills` — no
  separate pi skill directory. One scan serves both opencode and pi.
- **Company skills live in a dedicated `extensions/` dir** (config-driven
  `layers.skills` in `config/environments/{env}.yaml`, default
  `{workspace_root}/extensions`). The name `extensions` deliberately avoids
  auto-discovery by opencode/pi (they only scan `skills`/`.claude/skills`/
  `.agents/skills`), so company skills do not pollute agent context. The
  launcher loads them explicitly.
- ai-system already has reusable building blocks:
  - `cli/utils/menu.py` — `choose()` (filter menu), `ask_text()`
  - `cli/services/wizard.py::_select_launch` — agent pick + launch
  - `config/providers.yaml` — enabled agents (opencode / pi / claude)
  - `cli/utils/clipboard.py::copy`, `launch/opencode.ps1` pattern

## 3. Design decision — thin trigger, not full skill injection

The generated prompt must **not** embed the full SKILL.md (that recreates the
context-bloat problem). Instead it instructs the agent to load the skill via
the platform `skill` tool, then execute the task. This matches opencode's
on-demand loading model.

## 4. Options

### Option A — CLI service + new command (Recommended)

- `cli/services/skill_scan.py` — scan **extensions dir (config-driven)** first,
  then global + project-local skill roots (realpath-deduped); extract
  name/description from SKILL.md frontmatter. One scan serves opencode and pi.
- `cli/services/skill_launcher.py` — orchestrate: pick skill → pick agent
  (opencode / pi) → enter task → render prompt (thin trigger template) →
  copy → launch agent. Reuses `menu.choose`, `ask_text`,
  `Wizard._select_launch`, providers config.
- `cli/commands/aic-skill-launch.md` — command definition for the menu.
- `templates/prompts/skill-launch.md` — prompt template (instructions to load
  the selected skill via the platform skill tool and execute the task).
- Register in `config/menu.yaml` (`commands_maintenance`) + i18n.

**Impact**: new service modules + command + template + menu/i18n. Reuses the
existing wizard/menu/providers infra; one scan serves both opencode and pi.

### Option B — Pure prompt command

Only `cli/commands/aic-skill-launch.md` (markdown), no Python service. The AI
performs the selection steps manually per instructions.

**Impact**: smallest diff. But no true interactive menu, no real skill
discovery — the AI would guess skill names; contradicts the "launcher" intent.

### Option C — Standalone script in launch/

Self-contained `launch/skill-launch.ps1` + python, not part of ai-system CLI.

**Impact**: independent, but duplicates menu/providers/prompt logic and
fragments the CLI surface.

## 5. Recommendation

**Adopt Option A.** It is the smallest correct change that delivers the
launcher UX while reusing ai-system's existing interactive infrastructure.
The thin-trigger design keeps context cost ~0 at idle (skill loaded on demand).
Company skills live in the config-driven `extensions/` dir (not auto-scanned);
global/project skills come from the shared roots both opencode and pi read.

## 6. Proposed Changes (Option A)

0. **Extensions config**: create `{workspace_root}/extensions/`; add
   `layers.skills` to `config/environments/{env}.yaml` (+ template + setup.py
   generator); add `skills_root` resolver in `cli/services/environment.py`.
1. `cli/services/skill_scan.py` — scan extensions dir (config-driven) first,
   then global (`~/.agents/skills`) + project-local (CWD → git root:
   `.opencode/skills`, `.claude/skills`, `.agents/skills`), dedupe by
   realpath, return [(name, description, path)].
2. `cli/services/skill_launcher.py` — pick skill (menu), pick agent
   (reuse `_select_launch`), enter task (`ask_text`), render prompt, copy,
   launch agent.
3. `cli/commands/aic-skill-launch.md` — command definition.
4. `templates/prompts/skill-launch.md` — thin trigger template.
5. `config/menu.yaml` + `config/i18n/zh.yaml` — register command + fields.
6. Wire entry into `cli/main.py` (`aic skill-launch` subcommand or via
   existing `--copy`/`--save` output flow).

## 7. Validation Plan

- `python tools/check.py` → PASS (11 commands, wizard dry-run includes new command)
- `python tools/repo-lint.py --repo-root .` → 0 blockers/errors
- `python tools/path-audit.py` → 0 broken
- Functional: run the launcher in non-interactive mode (fallback paths),
  verify skill scan lists real skills, prompt renders without SKILL.md body.

## 8. Risks

- Global skill paths are symlinked; realpath dedupe required to avoid
  duplicate entries.
- Non-TTY mode must degrade gracefully (fallback menus already exist).
- Prompt must reference the skill by name only (no body) to avoid context
  bloat — verified by the template.

---

## Review Log

| Reviewer | Decision | Date |
|---|---|---|
| User (AI Maintainer operator) | **Approved — Option A** | 2026-08-05 |

---

## Implementation Record (2026-08-05)

Applied per approval (OPERATIONS §12 → Implement → Validate):

1. `cli/services/skill_scan.py` — skill discovery (extensions config-driven
   first, then global `~/.agents/skills`, then project-local; realpath dedupe).
2. `cli/services/skill_launcher.py` — interactive launcher (skills → agent →
   task → confirm; thin-trigger prompt).
3. `cli/services/agent_picker.py` — reusable agent selection (providers.yaml).
4. `cli/main.py` — `skill-launch` dispatch + `_INTERACTIVE_COMMANDS` +
   `_run_interactive`; `cli/services/interactive.py` — InteractiveCommand
   state machine (BACK rollback / Esc handling).
5. `templates/prompts/skill-launch.md` — thin-trigger template.
6. `cli/commands/aic-skill-launch.md` + `config/menu.yaml` + `i18n/zh.yaml`
   — command registration, skill-groups.yaml grouping/tasks config.
7. Follow-ups: extensions/ dir + setup.py scaffold, provider `command`/`icon`
   fields, `aic-skill-optimize` command (O-1..O-6).
8. `reports/MAINTENANCE-2026-08-05.md` — S4 records.

**Validation**: check.py PASS; repo-lint 0/0/9; path-audit 0 broken.
