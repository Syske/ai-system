# Change Proposal: P26 — 开发主链分支创建规则（cc{date}_ipd_{desc}_{service}，暂定）+ 创建后不可变

| Field | Value |
|---|---|
| Status | **Proposed** |
| Type | Structural (workflow/runtime/纪律 + 分支契约) |
| Author | AI Maintainer |
| Created | 2026-08-20 |
| Reference | 用户需求：主链分支创建规则 + 创建后不允许修改；参考 hotfix-branch-parser 契约形态 |
| Process | OPERATIONS §12 Change Management |

---

## 1. Problem

1. **主链不创建分支**：dev-setup 只解析/确认用户指定的已存在分支（`project-context.yaml branches`），无生成逻辑 → `cc{date}_ipd_...` 纪律无法保证落地。
2. **命名校验两套口径且不强制**：旧「Branch Naming Convention」是通用前缀（feat/ 等）且仅警告；与"需求确认定死、创建后不可改"的目标不符。
3. **无 round-trip 解析契约**：主链无 branch.parser 契约（只有 bugfix hotfix 有），trace（分支→任务卡对账）无法程序化复用分支语义。
4. **无"创建后不可变"约束**：分支/project-context.branches 可被随意改，跨阶段漂移无迹可查。

## 2. Clarified Design（用户 8 点定案）

| 点 | 结论 |
|---|---|
| 格式 | **暂定** `cc{date}_ipd_{desc}_{service}`（date=需求确认日期 YYYYMMDD，type=ipd 固定，desc=需求简述 kebab，service=服务名） |
| 规则归属 | 命名规则入 **Task Card `branch` 字段**（模板占位 {date}/{desc}/{service}），需求确认时确定公共部分，之后不变；规则可由用户指定/修改 |
| 校验/创建/回填 | dev-setup 以 project-context 为准；**为空时创建并回填**（经分支扩展 provider，缺省用 ai-system 内联解析器） |
| 不可变 | 创建后分支名/project-context.branches **冻结**；唯一例外=新增项目（需授权 L3）；CI 层简单实现、后续增强 |
| 链路判断 | 分支规则按链路选择：主链用 Task Card 模板；bugfix hotfix 用既有 cc{date}_{type}{desc}_{service}+parser |
| 独立分支 | 每服务独立分支（service 入名），除分支名外其余一致 |
| trace 复用 | **复用**：分支解析结果（ParsedBranch{date,type,desc,service}）供 trace 对账 |
| CI | 简单实现（check.py 契约自检），后续增强（git 分支保护） |

## 3. Options

- **Option A — 轻量（纪律+校验，不动契约）**：AI_OPERATING_RULES + runtime-dev-setup 加纪律与冻结 guardrail；命名校验内联。缺点：无 provider 契约、trace 复用靠描述。
- **Option B — 完整契约（A+B）**（**Recommended**）：A + 主链 branch.parser 契约（ai-system 默认内联实现，provider 可覆盖）+ trace 复用 + check.py 契约自检。

## 4. Recommendation

采用 **Option B（A+B）**：契约形状对齐 bugfix hotfix（`parse->ParsedBranch{date,type,desc,service}`、never raise），主链默认模板 `cc{date}_ipd_{desc}_{service}`（暂定），Task Card 携带 `branch` 模板，dev-setup 校验/创建/回填/冻结，trace 复用，CI 简单自检。

## 5. Proposed Changes

- [x] `cli/services/branch_parser.py`：主链分支解析器（parse/render，默认 `cc{date}_ipd_{desc}_{service}`，never raise）+ 契约文档
- [x] `governance/AI_OPERATING_RULES.md` Workspace Discipline：分支命名/不可变/链路判断/独立分支纪律
- [x] `templates/runtime/runtime-dev-setup.md`：分支以 project-context 为准 → 空则创建并回填 → 冻结检查（Stop 报告）；provider 契约注
- [x] `templates/runtime/runtime-spec.md`：Task Card 增加 `branch` 字段（模板，需求确认时定死）
- [x] `cli/commands/aic-trace.md`：trace 复用分支解析（date/desc/service；T-xxx 仍取提交）
- [x] `tools/checks/workflow.py` + `__init__.py`：`check_branch_parser` 契约自检（B3 简单 CI 强制）
- [x] `cli/tests/test_branch_parser.py`：5 用例（有效/非法/never raise/render）
- [ ] 分支扩展 provider（extensions/ 提供者，按需；契约已预留）
- [ ] CI 增强（git 分支保护，后续）

## 6. Validation Plan

- `python tools/check.py` PASS（含 check_branch_parser）
- `python -m unittest discover -s cli/tests`（新增 test_branch_parser）
- repo-lint / workflow-audit / path-audit 全绿

## 7. Risks

- **格式为"暂定"**：`cc{date}_ipd_...` 若团队调整，需同步 parser/template/纪律（单一模板源已收敛到 Task Card `branch` 字段 + branch_parser）。
- **行为变更**：主链从"用户指定分支"变为"按模板创建/校验 + 冻结"；project-context 为空时自动创建并回填，需用户知情确认。
- **兼容**：旧分支（task/{task-id} 等）parse 为 None → dev-setup 会 Stop 报告（不静默接受），需引导迁移或确认例外。

---

## Review Log

| Reviewer | Decision | Date |
|---|---|---|

## Implementation Record (2026-08-20)

<!-- 实施后追加 -->
