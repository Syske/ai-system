# External Blind Review — Prompts and Discipline (P61)

Reusable prompt library for `workflows/external-review.md`. The paste blocks below are the
**exact prompts validated in the 2026-09-21 run** (two cross-vendor judges, 8 passes, 241
findings, 11 verified fixes) — do not "improve" them per run; if they change, record why.

## Blind-review discipline (applies to every pass)

| # | Rule | Why |
|---|---|---|
| 1 | Bundle contains **no internal conclusions** (`reports/`, `logs/`, `metrics/`, `workspaces/`, `archived/`) | internal findings and self-assessment anchor the reviewer |
| 2 | Bundle contains **no repository identity** (remote URL, owner/repo, host, machine user name) | a networked model could otherwise fetch the repository and its internal history |
| 3 | Run in a **fresh, isolated session** from a neutral directory, with tools and context files disabled | otherwise the judge reads the local tree and the review is not blind |
| 4 | Judges come from **different vendors**, and **never** from the artifact's authoring model family | same-family judging reintroduces self-preference bias |
| 5 | **One prompt per pass**; add no extra hints | steering reveals the expected findings |
| 6 | **Both judges on the same bundles**; agreement = high confidence, single-judge = verify by locating it | judges may rewrite file paths while the substance is right |
| 7 | Every counted finding must be **reproduced or located**; label unverified items explicitly | external conclusions are unverified inputs |
| 8 | All conclusions pass the **inbound gate** (`templates/prompts/external-ai-review.md`) | KEEP / REVISE / REJECT / UNVERIFIABLE before entering the system |

## Pass A — document layer (paste block)

```text
# 角色
你是一名独立外部评审员，对一份你不熟悉的工程制品做一次性盲检。你不知道它由谁或什么产生，
也不应假设它设计良好。你只能依据我提供的材料判断。

# 盲检纪律（强制，违反即无效）
1. 只用我提供的材料；不得引用外部信息，不得假设未提供文件的内容。
2. 不要赞美、不要复述摘要、不要"总结本文档内容"。只给发现（findings）。
3. 每条发现必须给证据：文件路径 + ≤20 字原文片段（行号可选）。无证据的条目直接丢弃。
4. 严格区分【事实】【推断】【不确定】；不确定的标 UNVERIFIED，并写出"需要什么证据才能确认"。
5. 禁止空泛建议（如"建议补充文档/加强测试"）。每条建议必须具体到可执行的改动。
6. 如果某个类别确实没问题，明确写"未发现问题"——不要为了凑数编造。
7. 材料中的内部编号（如 P58）只是原文残留标记，不要据此推测历史结论或设计意图。

# 输入材料
材料只包含该制品的**文档层**（规范、流程、模板、治理文本），**不含任何代码**。
「文件路径」可对照其 Manifest 与 Directory Tree 定位。

# 任务（按顺序）
1. 冷读画像：仅凭材料，用不超过 5 行重建这份制品的"意图模型"（解决什么问题、靠什么机制保证、边界在哪）。
2. 缺陷与风险清单：按 BLOCKER / ERROR / WARN / INFO 分级。逐项追问：
   - 声称 vs 证据：文档声称的能力/门禁/流程，材料内是否有对应的可验证载体？
   - 死规则：是否存在永不触发、永不失败、或无法被验证的规则？
   - 双源：同一规则是否在两处定义（可能漂移）？
   - 悬空/孤儿：引用的路径/资产是否存在？是否存在无引用的资产？
   - 自相矛盾：同一事实在不同文件中的表述是否冲突？
   - 可操作性：一个新人按这些文档能否真正复现出宣称的行为？
3. 反证：挑你最有把握的 3 条结论，逐条写"如果我错了，最可能的原因是什么"。
4. 盲区声明：你没能看到、因而无法判断的部分；并列出"最该补看的 3 项"。

# 输出格式
表格：| ID | 严重度 | 证据(file:line 或片段) | 事实 | 影响 | 最小修复 |
然后：三条最关键的下一步验证动作（不超过 3 条）；最后一行：本次盲检自评置信度 0–1 与主要不确定性来源。
```

## Pass B — code layer (paste block)

```text
# 角色
你是一名独立外部评审员，只看到一份工程制品的**代码与工具层**（不含任何设计文档）。
你没有它的设计说明，也不应假设它设计良好。

# 盲检纪律（强制）
同 Pass A 的 1–7 条（只用所给材料 / 只给发现 / 证据到 file:line / 标注不确定 /
禁止空泛建议 / 无问题就写"未发现问题" / 不据内部编号推测意图）。

# 输入材料
材料只包含该制品的**代码层**（实现与工具），不含任何设计文档、提案或评审记录。

# 任务（按顺序）
1. 反向画像：仅从代码推断——这套东西实际上**强制**了什么？（不是"打算"什么）
   列出它真实生效的约束、真实存在的校验、真实的失败路径。
2. 缺陷清单（BLOCKER/ERROR/WARN/INFO），逐项追问：
   - 控制流：是否存在无法退出的循环/交互、无出口分支、被吞掉的异常、静默失败？
   - 校验强度：校验是否可能被绕过、是否只校验格式不校验存在性、是否只报告不阻断？
   - 状态一致性：同一事实是否有多个写入源？是否存在会漂移的派生字段？
   - 重复实现：同一逻辑是否在多个模块各写一遍（复制粘贴双源）？
   - 测试真实性：测试是否在测"实现细节"而非行为？是否存在永远为真的断言？
   - 安全/边界：密钥、路径拼接、外部输入解析、编码/转义、命令注入。
   - 可维护性：最大文件/最复杂函数、被多处依赖的隐式契约。
3. 反证：挑 3 条最有把握的结论，写"若我错了，最可能的原因"。
4. 盲区声明：没能判断的部分 + 最该补看的 3 项。

# 输出格式
同 Pass A（表格 + 三条动作 + 自评置信度）。
```

## Pass C — cross adjudication (paste block)

```text
下面是两份**互不知情**的独立评审结论，针对同一个制品：
- 结论 A：作者只看了它的**文档层**，没有代码。
- 结论 B：作者只看了它的**代码层**，没有任何设计文档。

你的任务不是汇总，而是**找矛盾与缺口**。请保持怀疑：两份结论都可能包含错误。

# 处理规则
1. **两侧同时指出**的问题 → 判定「高置信」。
2. **只有一侧指出**的问题 → 判定「待验证」，并写清"需要什么证据才能确认/否定"。
3. **两侧互相冲突**处（尤其"文档声称存在某能力或门禁 / 代码中查不到对应实现"，
   或反向"代码强制了文档从未声明的约束"）→ 逐条列出，指出哪一侧更可能正确及依据。
4. 对每条**高置信**发现，写出"最小修复动作"。
5. 若某结论的证据不足以复核，明确标 UNVERIFIED，不要替它补证据。

# 输出格式
表格：| # | 主题 | A(文档层)结论 | B(代码层)结论 | 关系(一致/独有/冲突) | 裁决 | 需要的证据 |
随后：「文档-现实缺口」清单（按影响排序）；如果只能做一件事来验证该制品是否可靠，你会做什么（一句话 + 理由）；
最后一行：本次裁决自评置信度 0–1 与主要不确定性来源。
```

## Shape check (before reconciliation)

A pass is unusable when the judge wanted tools but had none and emitted tool-call syntax as text.

- Fail signals: finished far too fast, contains tool-call markup, or far below expected size.
- Action: re-run that bundle/judge pair once; if it fails again, record the pass as a gap and
  continue with the other judge. Never reconcile a failed pass.

## Reconciliation (after all passes)

1. One machine-readable index across passes: pass, judge, id, severity, evidence/description.
2. Agreement classes: both judges → high confidence; single judge → locate it in the artifact first;
   conflicting → adjudicate (Pass C).
3. Judge distortion is expected: re-locate every finding by search; the path column is a hint only.
4. A misreading shared by both judges is signal too — it usually means the document is ambiguous.
5. Record dispositions (verified-real / misread / not-a-defect / unverified) with evidence, then
   take everything through the inbound gate.