# AI Repository Operations Manual

This document defines how this AI engineering repository should be used, maintained, and evolved.

It applies to both human developers and AI agents.

---

# 0. Core Principle

This repository is not a code repository.

It is an **AI Execution System** composed of:

* Skills (behavior units)
* Workflows (orchestration)
* Playbooks (engineering knowledge) — *planned: no `playbooks/` directory yet (see RFC-0001 / ADR-0002 status notes)*
* Knowledge (project context) — *planned: only `governance/memory/` placeholders exist*
* Templates (output formats)
* Checklists (validation rules)

All operations must respect this separation of concerns.

---

# 1. Entry Points (How to Start Work)

Workflow contracts live in `workflows/` (see `workflows/README.md` for the selection table).

## 1.1 Cold Start (once per environment)

```text
bootstrap
```

Produces Environment Context and initializes the workspace.

---

## 1.2 New Requirement (main chain)

> 主链拓扑以 `workflows/README.md`（Entry & Main Chain）为唯一来源，此处仅为使用说明。

```text
prepare → spec → dev-setup → develop (one task card per cycle) → review → verify → release
```

Rules:

* Always enter through prepare. Never jump straight to spec.
* prepare Blocked → collect clarifications, do not proceed.
* spec produces independent task cards; dev-setup confirms branches before develop.
* First-time change set scaffold is driven by the methodology provider during spec (/aic-propose or openspec-cn new change); the chosen kebab-case name becomes the Change ID. Run it inside workspaces/{project_id}/ — openspec-cn locates the project by working directory.
* Slash commands are only discovered from a platform's own command paths. From the workspace root, generate the prompt instead: `python -m cli.main propose --project <project_id> --request "<description>"` (also works for explore / apply / archive).
* Run `python -m cli.main` with no arguments for an interactive picker: project first (last project starred), then workflow/command (recommendation derived from the previous workflow's Next contract, or from change-set facts for a fresh project), then remaining inputs with Project/Workspace ID auto-filled and last task/change pre-selected. Full-screen arrow-key selection (alternate screen, restored on exit), entries annotated with Purpose/description, Left/Backspace back, Esc cancels anywhere, explicit skip entries for optional fields; numbered-input fallback when piped or non-TTY (b = back, < = back in text fields). Session state persists in workspaces/.aic-state.yaml. The final step can launch opencode or pi at the workspace root with the prompt already in the clipboard.
* develop implements exactly one task card on branch task/{task-id}.
* review and verify are mandatory gates; failures return to develop, never spawn new cards.
* release READY hands off to deployment (outside this workflow set).

---

## 1.3 Bug Fix (short chain)

> 独立入口分支以 `workflows/README.md`（Independent entry）为唯一来源，此处仅为使用说明。

```text
bugfix → review → verify
```

Requires Project Context and Workspace Context from a previous dev-setup.

### 1.3.1 BugFix 运行模式（配置驱动）

bugfix 支持多种运行模式，行为差异**全部收敛到配置**，流程文档不散落条件分支：

- 配置唯一来源：`config/workflows/bugfix-modes.yaml`（模式结构 / phases / 分支模板 / 解析器）
- 运行开关：`config/environments/{env}.yaml → bugfix.mode`（机器级，不入库）
- 门禁：`tools/checks/bugfix_modes.py`（check.py 第 15 项）——新增/修改模式必须通过
  结构、phases、模板占位符、解析器契约四重校验，配置错字或死引用无法静默通过

| 模式 | 适用 | 阶段链 |
|------|------|--------|
| `standard`（默认） | 常规缺陷诊断修复 | analysis → reproduce → root-cause → plan → implement → regress → report |
| `hotfix` | 现网问题，基于 master 直接修复，走完整发布前链路 | analysis → reproduce → root-cause → plan → **branch** → implement → regress → **commit** → verify → **doc** |

hotfix 模式要点：

- `plan` 后为**方案确认门禁**（approval_gate），修复方案须经人工确认才切分支
- 分支按 `branch.template` 生成，默认 `cc{date}_{type}{desc}_{service}`
  （如 `cc20260813_fix_thread_leak_housekeeping-service-api`）
- 编译后端沿用 `build.backend`（idea / maven），由 bugfix skill 按环境配置委派
- 验证通过后按需生成转测文档（`hotfix-test-doc` 工作流）

### 1.3.2 分支名解析器（契约 / 实现分离）

分支命名是公司/平台特有规范，采用**契约归 ai-system、实现归扩展**的架构：

- 契约（ai-system，稳定不变）：`templates/runtime/runtime-bugfix.md` Phase 4.6
  - 脚本 `scripts/branch_parser.py` / 方法 `parse(branch_name) -> ParsedBranch | None`
  - 返回字段 `{date, type, desc, service}`；无法解析返回 `None`（不抛异常）
- 实现（扩展提供者）：`extensions/<name>/scripts/branch_parser.py`，由拥有规范的一方
  维护公司特定正则；ai-system 不内置任何公司特定分支规范
- 脚手架：`tools/branch-parser-scaffold.py init <provider>` 非破坏生成契约骨架 +
  契约测试，提供者只需填实现；新平台（不同分支规范）运行同一 init 即可接入
- 新接入步骤：scaffold → 填实现 → 加测试实例 → 在 `bugfix-modes.yaml` 注册
  `branch.parser` → 门禁自动校验

新增/修改模式或解析器后必须运行：

```text
python tools/check.py
python tools/repo-lint.py --repo-root .
```

---

## 1.4 Urgent Interruption

An urgent request during an active task is L3 by default
(see governance/AI_OPERATING_RULES.md, Change Control):

1. Suspend the current task: commit or stash, persist state.
2. Run the bugfix short chain (or route the request to prepare / spec).
3. Resume the suspended task with its Task Card.

---

## 1.5 Requirement Change on an In-Flight Change

A requirement-level change point on the active change set is L3 by default:

1. Suspend the active task: commit or stash, persist state.
2. prepare (scoped): assess impact — affected scenario specs, contracts, task cards.
3. spec: update the change set in place (specs delta, contracts, task cards, global plan).
4. Consistency check: Proposal → Design → Spec → Contracts → Tasks.
5. Resume develop with updated Task Cards. Completed cards invalidated by the change revert to open.

Never open a second change set while the current one is not archived.

Trigger:

```text
python -m cli.main prepare --change <change_id> --request "<change point>" --mode re-entry
python -m cli.main spec    --change <change_id> --mode re-entry
python -m cli.main develop --project <project_id> --task <task_id>
```

---

## 1.6 Reconcile Code-Ahead Drift

Code was changed but spec / task cards were not updated.

Locate owners from the branch diff first: `python -m cli.main trace --project <project_id>`
(diffs the current branch against master; `--code` narrows focus, `--base` overrides the baseline).
trace maps each changed file to task card / spec scenario / contract, then — after confirmation —
backfills the in-flight change set, or scaffolds a new change set for untracked but approved behaviour.

1. Run verify as a diagnostic to list the gaps (specification-verification report).
2. Arbitrate each gap — decide which side is the truth (check git log / diff for intent):
   - Code is right (approved change, never recorded) → backfill the artifacts:
     `prepare --change <change_id> --request "backfill: <behaviour already implemented>" --mode re-entry`,
     then spec updates the change set in place (specs delta, task cards, acceptance evidence).
   - Spec is right (unapproved drift) → return to develop and correct the code.
3. Re-run review → verify to close the gate.

Prevention: Change Control (L1 / L2 / L3) plus the mandatory Deviations report make silent code-only changes a rule violation.

---

## 1.7 System Health and Knowledge

```text
maintain     AI routine maintenance (quick-check pre-flight + mode-based inspection)
knowledge    knowledge lifecycle managed by AI inside the maintenance cycle
```

Knowledge lifecycle triggers (matching `knowledge` workflow operations):

```text
collect   — after each release or retrospective
review    — monthly: de-duplicate, check contradiction, check stale entries;
             also scan logs/ for recurring (≥2x) observations never captured
             to Coding Memory / env.yaml / a proposal → triage (capture /
             machine-config / proposal); skip single-shot transient entries
archive   — quarterly: archive outdated entries, update the index
```

AI manages knowledge as part of the maintenance cycle (not a standalone
user menu entry). `governance/memory/` is validated by `tools/check.py`
(entry format, index integrity, language).

AI-operation-first health flow (ADR-0009):

- Session start: AI runs `python tools/quick-check.py` (read-only, seconds);
  findings recorded to `metrics/quick-check-{date}.json` (traceable).
- Due maintenance: AI checks `ai-system/config/maintenance.yaml →
  next_maintenance`; when due, prompts the user for authorization.
- The user decides only whether to run and which Mode/Scope.

---

## 1.8 Repository Maintenance

Use:

```text
repository-maintainer skill
```

Modes:

* weekly
* monthly
* on-demand

Trigger (AI-operation-first, ADR-0009):

```text
python -m cli.main maintain --mode weekly
```

- AI runs `tools/quick-check.py` at session start (read-only pre-flight).
- AI prompts for authorization when `maintenance.next_maintenance` is due.
- The user decides whether to run and which Mode/Scope; execution, report
  generation, and next-maintenance scheduling are AI-owned.
- analysis (AI system health) and knowledge lifecycle run as internal
  stages of the maintenance cycle, not standalone menu entries.

The maintain command runs repo-lint / repo-metrics, the repository-maintainer inspection for the selected mode, and the governance consistency spot checks (workflow eight-section contract, registry minimality, reference integrity, doc-reality alignment).

Used for:

* architecture review
* dependency analysis
* duplication detection
* capability analysis
* lifecycle cleanup recommendations

### 1.8.1 维护职责分离（Maintenance Responsibility Split）

维护分两个独立域，分开触发：

| 域 | 入口 | 关注 | 频率 |
|----|------|------|------|
| **aic 工具巡检** | `python tools/quick-check.py` | aic 工具自身健康：repo-lint（结构/语言）、path-audit（引用）、extensions-lint（扩展域）、CLI 测试、命令注册 | 会话启动自动 + on-demand |
| **系统维护** | `python -m cli.main maintain --mode <mode>` | ai-system 架构：workflow 八段契约、governance 一致性、层级/目录、能力矩阵、知识生命周期 | weekly/monthly/quarterly |

- quick-check 结果落盘 `metrics/quick-check-{date}.json`（趋势可查）。
- 架构维护经验（CI 无 extensions / pyc 缓存 / 目录层级模拟等）不常驻本文，
  记录在各次维护报告（reports/MAINTENANCE-*/CACHE-OPTIMIZATION-*）与
  `reports/` 索引中，按需查阅。

### 1.8.2 现场诊断数据命名与归档（Diagnostic Data Naming & Archive）

Live diagnostic captures (watchdog / capture / JMX dumps) must carry a service identity
and follow a traceable, convention-able name so multi-service environments do not mix
files and cross-person trace-back is possible:

- **Name**: embed `{service}-{pod}-{timestamp}` in the filename / header (e.g.
  `openapi-gateway-pod-a-20260820T1130.log`), not a bare timestamp.
- **Keep the raw source with the analysis**: archive the capture under the workflow's
  conventioned output dir, e.g. `outputs/bugfix/{yyMMdd}-{desc}/…`, alongside the root
  cause report, so evidence stays with its conclusion.
- **Reference, don't re-collect**: point the analysis to the archived capture path;
  do not rely on a Downloads path that may move.

This is guidance for the external capture tooling + the debug diagnosis skill
(`skills/agent-debug-diagnosis`); it is not a structural change to ai-system.

---

## 1.9 Cross-Cutting Discipline

* Context loading order: Task → Spec → Contract → Standards → Repository. Never load the entire repository.
* Change control: L1 apply and record / L2 stop and confirm / L3 stop and route to spec.
* Every completion reports Deviations ("None" if empty).

## 1.10 Menu & Command Maintenance

The wizard menu is **configuration-driven** (`config/menu.yaml`) — no code changes are needed to add, regroup, or restyle menu entries.

* **Add a command**: write `cli/commands/aic-<name>.md` (discovered automatically), then register in `config/menu.yaml` under a `sections` entry (`kind: command`) and optionally add its fields under `command_fields`.
* **Add a workflow**: register it in `config/workflow-registry.yaml` first, then add a `sections` entry (`kind: workflow`, optional `number` for the main chain).
* **Group / order**: adjust the `sections` list order and `title`. Entries that are discovered but not registered in any section fall into the "… — Other" fallback sections automatically.
* **Emoji**: each item has its own `icon`. Icons are suppressed by default on non-emoji terminals and can be forced with `AIC_ICONS=emoji` (or disabled with `AIC_ICONS=off`).
* **Field forms** (`command_fields`, `default_command_fields`): which fields a command prompts for.
* **Field presentation** (`field_icons`, `field_choices`, `menu_options`): icons, static choice lists, fixed-option menu icons.
* **Behavioral flags** (`auto_fields`, `multi_select_fields`, `command_next`): auto-filled fields, multi-select fields, and recommended-next-workflow mapping.

### 1.10.0 Copy / Internationalization

User-facing copy (section titles, field hint notes, per-option descriptions)
is **not** in `config/menu.yaml`. Structure uses stable keys; the display text
lives in a locale file selected by `config/menu.yaml → locale`:

* `config/i18n/zh.yaml` — default locale (Chinese)
* Section titles in `sections[].title` are keys resolved via `i18n.sections.*`;
  field notes via `i18n.field_notes.*`; option descriptions via `i18n.option_descriptions.*`.

To change copy: edit the locale file. To add a language: copy it to
`config/i18n/<lang>.yaml` and set `locale: <lang>` in `config/menu.yaml`.
`tools/check.py` fails when a section key has no locale entry.

Dynamic choices (workspace/project/branch directories, git branches) are still resolved by code at runtime.

### 1.10.1 Naming Strategy

* **Workflow**: `kebab-case`, one word preferred (`prepare`, `develop`, `release`). Entry points: `workflows/<name>.md` + `config/workflows/<name>.yaml` + `templates/runtime/runtime-<name>.md`. Full table in `workflows/README.md`.
* **Command**: `aic-<kebab-name>.md` under `cli/commands/`. The `aic-` prefix is the ai-system command namespace (replaces openspec's `opsx-`); the wizard strips it for display. Name describes the operation (`scan`, `trace`, `pack`).
* **Field name**: PascalCase identity-style (`Project ID`, `Code Reference`, `Keep Results`) — consistent with `governance/repo-lint.md` conventions.

### 1.10.2 Grouping Strategy

Grouping is defined by the `sections` order in `config/menu.yaml`. Section
titles are user-facing (Chinese); the item `kind` (workflow/command) is internal.

* **Workflows**
  * `开发主链`: the numbered chain `prepare → spec → dev-setup → develop → review → verify → release` (1-7).
  * `修复流程`: parallel entry `bugfix`.
  * `初始化`: `extensions-init` (AI-driven bootstrap/extensions init; 4-word group name).
  * `代码分析`: standalone business-analysis workflows `code-review`, `change-impact` (review/impact for business code; the command `scan`'s chain/impact operations delegate to `change-impact`).
  * `变更管理`: change-lifecycle workflows `proposal` (idea → solution document; AI-triggered `propose`/`apply`/`archive` commands also belong here but are hidden).
  * `其他流程`: discovered but ungrouped workflows (automatic).
* **Commands**
  * `代码检索`: `scan`, `trace` (lightweight keyword scan / branch-diff reconciliation; heavy impact analysis delegates to `change-impact` workflow).
  * `技能管理`: `skill`, `skill-source` (skill usage + third-party skill assessment).
  * `系统维护`: `maintain`, `workflow`, `command`, `pack`, `extensions-init` (system health, asset scaffolding, packaging, environment onboarding).
  * `其他命令`: discovered but ungrouped commands (automatic).

Group names are 4 characters in Chinese (代码分析/技能管理/系统维护/变更管理)
for visual consistency. Hidden (AI-internal) commands — `propose`/`apply`/
`archive`/`explore` (change lifecycle), `bootstrap`/`analysis`/`knowledge`
(AI-internal workflows) — are registered but not shown in the user menu
(hidden_workflows / hidden_commands, ADR-0009 AI-operation-first).

Boundary note (user-facing): `系统能力` builds system capabilities (environment,
analysis, knowledge — outputs feed later work); `系统维护` keeps the system
healthy and portable (routine checks, packaging).

A workflow belongs in the Main chain when it is a mandatory step of the change
lifecycle; in Branch when it is an alternative path into the chain; in Support
when it is standalone tooling. A command is grouped by its primary purpose.

---

# 2. Skill Usage Rules

## 2.1 When to Use Skills

Skills are used for:

* implementation behavior
* decision logic
* execution steps

Examples:

* implement
* mock-test
* java-maven
* review-changes
* bugfix

---

## 2.2 When NOT to Create New Skills

Do NOT create a new Skill when:

* existing Skill can be extended
* logic belongs to Playbook (knowledge)
* logic belongs to Workflow (orchestration)
* logic belongs to Checklist (validation)
* logic is project-specific context

---

## 2.3 Skill Modification Rule

Before modifying any Skill:

1. Run repository-maintainer analysis
2. Check dependency impact
3. Validate workflow impact
4. Ensure backward compatibility
5. Require approval for structural changes

---

# 3. Workflow Rules

Workflows are responsible for orchestration only.

A Workflow MUST:

* coordinate multiple Skills
* define execution order
* define stopping conditions
* define handoff points

A Workflow MUST NOT:

* contain implementation logic
* duplicate Playbook content
* duplicate Skill logic

---

# 4. Playbook Rules

Playbooks contain reusable engineering knowledge.

They include:

* best practices
* common failure patterns
* diagnostic methods
* recommended solutions

Playbooks MUST NOT:

* define execution flows
* define workflows
* define step-by-step orchestration

---

# 5. Knowledge Rules

Knowledge contains project-specific context:

* architecture
* domain model
* terminology
* integration rules
* system constraints

Knowledge MUST be:

* descriptive, not procedural
* stable, rarely modified
* referenced by Skills and Workflows

---

# 6. Templates & Checklists

## Templates

Used for:

* reports
* specs
* reviews
* summaries

Must be reusable and stateless.

---

## Checklists

Used for validation:

* implementation checklist
* test checklist
* review checklist
* release checklist

Must be:

* deterministic
* consistent
* reusable across Skills

---

# 7. Repository Lifecycle Rules

All assets follow lifecycle:

* Draft
* Experimental
* Stable
* Deprecated
* Archived

Rules:

* No automatic archival
* No deletion without governance review
* Deprecated assets must have migration path

---

# 8. Quality Gates

Before merging or approving any change:

## Mandatory Checks:

* No duplicated Skill responsibility
* No duplicated Playbook knowledge
* No Workflow duplication
* No circular dependencies
* No orphan assets
* Naming convention compliance
* FrontMatter completeness
* Backward compatibility preserved

---

# 9. Repository Maintenance Rules

## 9.1 Weekly Maintenance

Run:

```text
repository-maintainer mode=weekly
```

Outputs:

* duplication report
* dependency graph
* orphan analysis
* quick health score

---

## 9.2 Monthly Maintenance

Run:

```text
repository-maintainer mode=monthly
```

Outputs:

* architecture review
* capability matrix
* lifecycle report
* evolution suggestions

---

## 9.3 Quarterly Maintenance

Focus:

* workflow redesign
* capability restructuring
* playbook consolidation
* knowledge cleanup

---

# 10. repo-lint.py Usage

Must be executed:

* before any release
* before merging structural changes
* during CI pipeline

Checks:

* Skill structure validity
* Workflow consistency
* dependency cycles
* missing references
* naming violations
* duplication signals

# 11. System Integrity Check (check.py)

After any ai-system modification, run the integrity gate:

```text
python tools/check.py
```

It must exit `0` before committing/merging. It verifies the system still
runs and the configuration is consistent:

* All Python sources compile and CLI modules import
* `config/menu.yaml` structure and referential integrity (sections, icons,
  command fields, field notes/choices, multi-select/auto fields, command_next)
* `config/workflow-registry.yaml` chain (config → workflow → runtime paths)
* Command files: `aic-` prefix, kebab-case, no `opsx-` remnants, no duplicates
* Prompt build smoke: every registered workflow and command builds a prompt
* Wizard dry-run: the config-driven target menu builds and fields resolve
  without a TTY (catches menu/config errors that would block `aic`)
* `tools/repo-lint.py` runs with zero BLOCKER/ERROR

Failure (exit `1`) means the system may be unrunnable after the change —
fix before proceeding.

---

# 12. Change Management Process

All structural changes MUST follow:

1. Analyze (repository-maintainer)
2. Propose (RFC if needed)
3. Review
4. Approve
5. Implement
6. Validate (repo-lint.py)
7. Report

No direct structural changes allowed without review.

---

# 13. Governance Priority Rule

If conflict exists:

1. Governance (highest priority)
2. RFC
3. Workflow
4. Skill
5. Playbook
6. Knowledge
7. Templates / Checklists

Governance always overrides implementation.

---

# 14. Design Philosophy

This repository evolves under these principles:

* Prefer composition over duplication
* Prefer reuse over creation
* Prefer clarity over flexibility
* Prefer governance over ad hoc decisions
* Prefer long-term maintainability over short-term convenience

Every change must reduce long-term maintenance cost.

---

# 15. Golden Rule

Before adding anything new, always ask:

> Does this belong to Skill, Workflow, Playbook, Knowledge, Template, or Checklist?

If not clearly classified → STOP and analyze via repository-maintainer.

---

# 16. Final Statement

This repository is not a collection of prompts.

It is a structured AI execution system.

Its correctness depends not on size, but on:

* consistency
* separation of concerns
* governance discipline
* controlled evolution
