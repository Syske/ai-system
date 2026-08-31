# Change Proposal: P39 — extensions-lint 隐藏目录误判为扩展（--fix-missing-log 污染 .git/.githooks）

| Field | Value |
|---|---|
| Status | **Implemented** |
| Type | Fix（tools/extensions-lint.py 目录过滤缺陷；触及工具代码，走 §12） |
| Author | AI Maintainer |
| Created | 2026-08-25 |
| Reference | maintain on-demand 运行（scope: prepare×tr5）中发现；quick-check-2026-08-25 WARN 链路 |
| Process | OPERATIONS §12 Change Management |

---

## 1. Problem（现状 / 缺口）

`python tools/extensions-lint.py --fix-missing-log` 将 `extensions/` 下的**隐藏目录**
也当作扩展处理，本次运行实际产出：

```
scaffolded .git/OPTIMIZATION_LOG.md
scaffolded .githooks/OPTIMIZATION_LOG.md
```

即向 `extensions/.git/` 与 `extensions/.githooks/` 内写入了 OPTIMIZATION_LOG.md
模板文件。本次已手工删除这两个误生成文件（yapi-openapi 的脚手架是正确产物，保留）。

## 2. Root-Cause（根因分析）

`extensions-lint.py` 枚举 `extensions/` 子目录时未过滤以 `.` 开头的目录
（`.git` / `.githooks` 等），也未按「含 SKILL.md 的目录」做扩展判定，
导致非扩展目录进入 lint / fix 循环。

## 3. Options（方案对比）

| Option | 说明 | 评估 |
|---|---|---|
| A. 跳过隐藏目录 | 枚举时过滤 `name.startswith('.')` | 最小修复，覆盖 .git/.githooks/.github 等全部场景（推荐） |
| B. 按 SKILL.md 存在判定 | 仅把含 SKILL.md 的目录视为扩展 | 更严格，但可能漏报「尚未建 SKILL.md 的新扩展」，与 lint 目的相悖 |

## 4. Recommendation

Option A（跳过隐藏目录），必要时叠加 Option B 的 SKILL.md 提示作为 WARN 增强。

## 5. Proposed Changes

- `tools/extensions-lint.py`：子目录枚举处增加隐藏目录过滤（`p.name.startswith('.')` → skip）
- 补一条单测或最小验证：在临时 extensions 根下放 `.git/`，断言不被 lint/fix 触达

## 6. Validation Plan

- 构造含 `.git/`、`.githooks/`、正常扩展的临时目录树运行 lint + `--fix-missing-log`
- 断言隐藏目录无任何文件写入；正常扩展检查结果不变
- 回归：真实 extensions 仓上 quick-check 结果与修复前一致（0 errors）

## 7. Risks

低风险：纯过滤逻辑新增，不影响既有合法扩展的检查路径。

## Review Log

- 2026-08-25 发现并登记（maintain on-demand run）
- 2026-08-25 用户批准落地执行（Option A）；同日实施并验证通过

## Implementation Record (2026-08-25)

Applied per approval (OPERATIONS §12 → Implement → Validate):

- `tools/extensions-lint.py` `scaffold_missing_logs()`：枚举处增加 `ext_dir.name.startswith(".")` 跳过（与 main() lint 循环既有过滤对齐）
- 验证：
  - 临时目录树回归（.git / .githooks / my-ext）：隐藏目录零写入、正常扩展正常脚手架，ASSERT OK
  - 真实仓：extensions-lint 0 errors/0 warnings；quick-check OK(0)；CLI 单测 164 OK
- 影响评估：纯过滤新增，不影响合法扩展检查路径；`--fix-missing-log` 不再触达任何隐藏目录
