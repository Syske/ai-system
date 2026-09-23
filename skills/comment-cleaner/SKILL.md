---
name: comment-cleaner
description: >
  清理本次改动新增的 AI 注释泔水：按标准判定 KEEP/DELETE/REVIEW，只删确定类，承重注释永不误删。
  用于 develop 任务实现收尾（代码质量门禁报告之后）——先 diff 级检查、再裁定 REVIEW 项、
  最后 dry-run → apply 清理并作为独立提交落库。不用于 review/verify 阶段（那两阶段不得改业务代码），
  也不做历史存量清理；JavaDoc 一律不碰。
---

# Comment Cleaner

## 目的

让「**默认不写注释，只写承重注释（load-bearing）**」在每次实现里真正落地：
删掉 AI 在本次改动中产生的信息增量为零的注释（复述代码 / 流程套话 / 分段线 / 名字直译），
同时**绝不碰**真正承载业务规则、外部契约、兼容性、并发与性能约束的注释。

定位：这是**会话内清理流程**，不是新一代检查器。机器判定由
`tools/comment-lint.py` 完成；本技能只负责「何时跑、如何裁定不确定项、如何安全落库」。

## 策略来源（唯一来源）

判定语义**不在本技能内**，只引用：

- `governance/standards/common/documentation.md` → Comment Content / Comment Quality
  （六级分类、判定顺序、安全原则、稳定规则 id `CQ-*`）
- `governance/standards/common/ai-coding-rules.md` Rule 12（Comments are not a default necessity）
- `skills/implement/decision.md`（声明级文档必需 vs 代码级注释默认不写）

## 何时使用

- **develop 任务实现收尾**：代码质量门禁报告之后、提交之前（门禁含 `comment-lint`，MVP 阶段只报不拦）。
- 用户明确提出「清理本次新增注释」时，按同一流程执行。

**不使用**：

- `review` / `verify` 阶段 —— 那两个 Runtime 不得修改业务实现（`runtime-review.md`）；发现泔水只记录。
- 历史存量清理 —— 只处理**本次 diff 新增行**；存量债需要单独的任务与用户确认。
- bugfix 收尾 —— `bugfix/anti-patterns.md` 禁止"顺手加注释/重排格式"；除非注释属于本次修复的
  **被触碰方法**，否则不改。

## 流程

1. **检查（只读）**：`python3 ai-system/tools/comment-lint.py <src> --diff`
   —— 只看本次新增行的注释；输出 `KEEP` / `DELETE` / `REVIEW` 与规则 id。
2. **读判定**：`DELETE` 是确定可删（工具已给理由）；`REVIEW` 需要**你**判断；`KEEP` 不动。
3. **裁定 REVIEW 项**（工具不对它们作任何断言，你是有上下文的一方）：
   - `CQ-DUPLICATE`（与字段/方法名重复）：若注释只是名字直译 → **删除**；若字段确需说明
     （单位/范围/来源/取值语义）→ 补上业务含义（这是**改**不是删，且不要在 cleanup 提交里顺手改文案，
     除非用户同意）。
   - `CQ-UNCERTAIN`（未归类）：问一句「读者能否从代码本身得到同样信息？」
     → 不能（含 Why/约束/来源）→ **保留原样**；能（只是复述）→ **删除**。
   - 拿不准 → **保留**。安全底线是「宁可漏删，不可误删」。
4. **清理（只删确定类）**：
   - 先预演：`python3 ai-system/tools/comment-lint.py fix <src> --diff`（打印 unified diff，不写盘）
   - 确认 diff 里**没有**你要留的注释 → 再执行：`... fix <src> --diff --apply`
   - `--apply` 只删 `DELETE` 类；JavaDoc 永不参与；幂等可重跑。
5. **落库**：
   - 清理**独立提交**（不与逻辑改动混提），提交信息按 `commit-content.md`
     （`T-<id>` 任务编号 + 类型；分支名遵守 P63 的预设格式）。
   - 重跑门禁（`comment-lint --diff --report-only` 应无 `DELETE`；format-check 等一并跑）。
   - 在诊断日志记录：删除条数 / 保留的 REVIEW 裁定 / 规则误报（若有）。

## 护栏（不可越）

- **永不自动删 JavaDoc**（`/** */` 可能属 API 契约）。
- **永不改代码**：本流程只删注释行/剥离行尾注释，不做任何文本重写（SAFE_REWRITE 关闭）。
- **永不批量清理没改过的文件**（只看本次 diff）。
- **误报要上报，不要绕过**：若某条承重注释被判 `DELETE`，这是**规则缺陷**——
  记录该注释原文与命中规则 id，报告给用户；不要偷偷改规则文档或加豁免标记。
- 反复出现的同类泔水，修**习惯**（标准/提示）而不是只删这一条。

## 输出

- 清理前：本次新增注释的三档分布与逐条 `DELETE` 清单（含规则 id）。
- 清理后：删除条数、保留的 REVIEW 裁定理由、独立提交号、门禁结果。
- 若有误报：原文 + 规则 id + 建议（交用户裁决）。