# Commit Content (Commit Message Standard)

Single authoritative source for commit message requirements. Machine-checked by
`format-check.py --check-commit`; referenced from `templates/runtime/runtime-develop.md`
(Formatting gate, A layer) and `tools/README.md`.

## Format

    <type>(<scope>): T-<id> <subject>

- `type`: one of `feat|fix|docs|style|refactor|perf|test|chore|ci|revert`.
- `scope` (required): module/component, e.g. `(gate)`, `(api)`, `(tools)`.
- `T-<id>` (required when the change belongs to a task card): `T-` + 3 digits.
- `subject`: 中文描述（项目语言惯例），≤ 72 字符，无句号结尾。

Examples

    feat(gate): T-042 门禁接入可配置化 gates
    fix(api): T-015 提交信息前缀校验匹配修正
    docs(tools): README 使用流程登记

## Non-task commits (no T-<id>)

Governance/infra commits may omit the task id; keep the `type` prefix and a
clear purpose, e.g.

    style: apply format baseline（Cool4Space profile 375 条）
    chore: checkstyle 存量抑制基线

## Machine check (`format-check.py --check-commit`)

Last commit subject rules:

- contains `T-` (task id) → MUST start with `<type>(<scope>): T-\d{3}`;
  otherwise FAIL (`Commit Content`).
- no `T-` → PASS (non-task / governance commit).

## Working rules

- Commit during development follows the main-chain flow (task commits on the
  task branch); `--check-commit` runs at the Formatting gate to catch a botched
  message before the change closes.
- 脱敏原则适用：提交信息不得携带本机路径、人名-业务名或内网仓路径（公开仓场景尤甚）。