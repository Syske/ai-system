# Commit Content (Commit Message Standard)

Single authoritative source for commit message requirements. Machine-checked by
`format-check.py --check-commit`; referenced from `templates/runtime/runtime-develop.md`
(Formatting gate, A layer) and `tools/README.md`.

## Format

    <type>(<scope>): T-<id> <subject>

- `type`: one of `feat|fix|docs|style|refactor|perf|test|chore|ci|revert`.
- `scope` (required): module/component, e.g. `(gate)`, `(api)`, `(tools)`.
- `T-<id>` (required when the change belongs to a task card): `T-` + **3 digits**.
  The id is the **Task Card id** — the card file/header id produced per
  `templates/prompts/tasks-template.md` (`# T-{编号}: …`, file `tasks/cards/T-011.md`).
- `subject`: 中文描述（项目语言惯例），≤ 72 字符，无句号结尾。

Examples

    feat(gate): T-042 门禁接入可配置化 gates
    fix(api): T-015 提交信息前缀校验匹配修正
    docs(tools): README 使用流程登记

### Id level — Task Card id ≠ plan position

Only the **Task Card id** belongs in the subject. A card's plan position (e.g. `1.1`, `1.2
within section 1 of the plan) and any other reference go in the **body** (`Refs:` / `Task:`),
never in the subject.

Why this note exists: cards used to be numbered by plan position (`1.1.md`) in some changes,
where `T-1.1` fails the `T-\d{3}` format — the AI then learned to drop `T-` entirely
("subject 无 T-，task 引用入 body") to avoid a FAIL, i.e. **the gate drove the omission**
(evidence: P62; real amends in the develop logs). Cards MUST be numbered `T-\d{3}` per the
template; a legacy plan-position card's reference goes in the body.

## Non-task commits (no T-<id>)

Governance/infra commits may omit the task id; keep the `type` prefix and a
clear purpose, e.g.

    style: apply format baseline（Cool4Space profile 375 条）
    chore: checkstyle 存量抑制基线

## Task-branch rule (enforced)

On a **task branch** — main chain `cc<yyyymmdd>_ipd_…`, or `task/*` / `bugfix/*` — a
non-merge commit whose type is in the enforcement set
(`feat|fix|refactor|perf|test`) **MUST** carry `T-<id>`.

- Exempt on task branches: `chore|docs|style|ci|revert` (governance or infra commits) and
  merge commits (`Merge …`).
- **Grandfathering**: existing history is never rewritten and never judged retroactively;
  the rule applies to commits made after 2026-09-23.
- Rationale: "does this commit belong to a task?" is machine-decidable from the **branch name**
  (already frozen by the branch-naming governance), so the gate no longer has to guess from
  the message itself (the guess is why a *missing* id could not be caught).

## Machine check (`format-check.py --check-commit`)

Last commit subject rules:

- contains `T-` (task id) → MUST start with `<type>(<scope>): T-\d{3}`;
  otherwise FAIL (`Commit Content`).
- no `T-`, but HEAD is a **task branch** (see the task-branch rule) and the type is in the
  enforcement set → **FAIL** (`Commit Content`) — the missing-id case the old check could not see.
- no `T-` and not a task-branch enforced commit → PASS (non-task / governance commit).

## Working rules

- Commit during development follows the main-chain flow (task commits on the
  task branch); `--check-commit` runs at the Formatting gate to catch a botched
  message before the change closes.
- 脱敏原则适用：提交信息不得携带本机路径、人名-业务名或内网仓路径（公开仓场景尤甚）。