# Change Proposal: P59 — 模板层作者纪律（折行≠token 优化 + 归一比对）

| Field | Value |
|---|---|
| Status | **Implemented** |
| Type | Structural (template authoring discipline) |
| Author | AI Maintainer |
| Created | 2026-09-21 |
| Reference | MAINTENANCE-2026-09-21（用户手动折行 templates/prompts/* 实测）→ 用户「接受建议」 |
| Process | OPERATIONS §12 Change Management |

---

## 1. Problem

1. 用户手动把 `templates/prompts/{workflow,command,skill-launch,external-ai-review}.md`
   的折行合并为长行（reflow），依据是"可能省 token"。
2. **实测否证**：构建全部 28 个 prompt 对比，折行版 130,934 字符 vs 原始 130,975
   → **仅省 41 字符（0.031%，≈10 tokens / 32.7k）**，且收益全来自共享头部。
3. **同时引入缺陷**：合并过程丢掉 3 处空格（`Filename:\``、`` `,` ``），
   并产生 >200 字符长行（损害 diff 可读性）。
4. **无纪律可依**：`templates/` 层此前没有 README/作者规则，"改模板前先量化、
   不拿空白当优化、批量改写需归一比对"全靠临场判断 → 同类问题会复发。

## 2. Root-Cause

- 折行是**给人看**的约定（终端 80 列 / git diff / 邮件宽度），被误当作 AI 优化手段；
  LLM 的计量单位是 token，换行⇄空格对 token 的影响是 **0～2 token/处**（噪声级）。
- 缺"改模板 → 先 `prompt-metrics` 量化 → 再决定"的纪律；缺"批量文本改写必须
  归一化逐字比对"的守卫（正是它抓出丢空格）。

## 3. Options

- **Option A（推荐）— 立模板层作者纪律**：新增 `templates/README.md`，固化
  ①不为 AI 折行/reflow ②省 token 靠内容/骨架/前缀（引用 CONTEXT_LOADING，不重抄）
  ③换行承载语义处保留 ④代码/frontmatter/表格永不 reflow ⑤批量改写必须归一比对
  ⑥占位符契约。回退本次折行，仅保留真修复（全角括号）。
- **Option B — 只记录本次结论**：写进巡检报告/诊断日志，不改仓库 → 无持久纪律，复发风险高。
- **Option C — 改 governance/standards**：把规则放标准层 → 与 CONTEXT_LOADING
  §Context Budget Discipline 职责重叠，违反单源，且越过模板层。

## 4. Recommendation

**Option A**。理由：规则归属**模板层自身**（谁改模板谁读得到），通用 token 经济
**引用** `CONTEXT_LOADING §Context Budget Discipline` 不重抄（Single Source of Truth）；
同时补齐 `templates/` 无 README 的缺口。

## 5. Proposed Changes

1. 回退 4 个模板的纯折行 hunk（`git checkout HEAD --`），**保留**真修复：
   `external-ai-review.md` 全角 `）` → 半角 `) to`（错配括号）。
2. 新增 `templates/README.md`：层职责 + 6 条作者纪律 + 验证命令。
3. 不改 `governance/standards/**`（避免与 CONTEXT_LOADING 重复）。
4. 记录：巡检报告 Fix Actions + 诊断日志（Issue Capture：单点修复 + 纪律立项）。

## 6. Validation Plan

- 单测：`python3 -m unittest cli.tests.test_prompt_builder`（16 用例）
- 门禁：`tools/check.py`（prompt 构建 smoke）、`tools/repo-lint.py`、`tools/check-contract.py`
- 体积复测：`/tmp/ab_measure.py` 口径 → 应回到 130,975 字符（折行回退生效）
- 括号错配复扫：`grep -nP '（[^）]*\)|\([^)]*）' templates/prompts/*.md` → 0

## 7. Risks

- README 与 CONTEXT_LOADING 的边界：README 只写"模板改写"专属规则，token 经济一律引用，
  避免双源。
- 回退使 3 处丢空格一并消失（回退即修复），无残留。

---

## Review Log

| Reviewer | Decision | Date |
|---|---|---|
| User (AI Maintainer operator) | **Approved**（「接受建议」） | 2026-09-21 |

---

## Implementation Record (2026-09-21)

Applied per approval (OPERATIONS §12 → Implement → Validate):
1. `git checkout HEAD --` 回退 4 个模板纯折行 hunk；保留 `external-ai-review.md`
   全角括号修复（`）` → `) to`）。
2. 新增 `templates/README.md`（层职责 + 6 条作者纪律 + 验证命令）。
3. 巡检报告 Fix Actions + 诊断日志记录（含实测数据）。
**Validation**: prompt 单测 16 OK；check.py PASS；repo-lint 28 基线；check-contract PASS；
体积复测 130,975（= 原始）；括号错配 0。