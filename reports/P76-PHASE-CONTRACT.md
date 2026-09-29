# Change Proposal: P76 — Phase Contract（Phase 一等契约：第九段 + Activation 语义 + Declares 校验）

| Field | Value |
|---|---|
| Status | **Implemented** (S1 + S2 both delivered 2026-09-29) |
| Type | Capability（Phase 从 runtime 内部章节提升为一等机器契约）+ Fix（code-review 重复内容 + bugfix Phase 6 契约破损） |
| Author | AI Maintainer |
| Created | 2026-09-28 |
| Reference | 用户 2026-09-28 逐条决策（Q1 独立价值 / Q2 强制声明可验证产出 / Q3 Activation 统一命名 + 默认 always；`## Phases` 选「配置为结构真源 + workflow 九段入口 + 渲染注入」；`phase("<id>").active/completed/passed` 三状态；`Declares ⊆ Workflow Outputs` 单向；code-review 最小压缩不放宽 100 行；`passed` 取 (a) 且不新增 gate）；`rfc/RFC-0003`（100 行体量门禁）；`tools/workflow-command-audit.py:36-45`（八段 `WORKFLOW_SECTIONS`）；`cli/services/prompt_builder.py:110-138`（渲染注入点）；`templates/runtime/runtime-bugfix.md:248-270`（Phase 6）；`templates/runtime/runtime-verify.md:214-250`（既有 PASS/FAIL 判据） |
| Process | OPERATIONS §12 Change Management |

---

## 1. Problem

### 1.1 Phase 是事实上的执行单元，却没有任何机器契约

实测 Phase 分布（`templates/runtime/runtime-*.md`）：

| runtime | Phase 数 | 条件执行 Phase |
|---|---|---|
| bugfix | **12** | 5（4.5 / 4.6 / 6.5 / 6.6 / 6.7） |
| dev-setup | 10 | 0 |
| release / spec | 9 / 9 | 0 |
| review / verify / external-review | 8 / 8 / 8 | 0 |
| prepare | 7 | 0 |

但 Phase **只以 markdown 章节形式存在于 runtime 内部**，没有任何机器可校验的结构化契约。三个直接后果：

**F1 — 条件执行语义对 agent 不可见。**
`runtime-bugfix.md` 的 5 个 hotfix-only Phase 靠散文表达：

| Phase | 现有措辞（`runtime-bugfix.md`） |
|---|---|
| 4.5 | "Activate only when the configured mode sets `approval_gate` … and the current run is in that mode" |
| 4.6 | "…`phases` contains `branch`" |
| 6.5 | "…`phases` contains `commit`" |
| 6.6 | "…contains `mr` **AND the branch is committed and pushed**（the push happens in Phase 6.5, **conditionally on this phase being enabled**）" |
| 6.7 | "…contains `doc` **AND regression verification passed**（or `doc.trigger` is `on-verify-pass` **and Phase 6 passed**）" |

`_skeletonize_runtime`（`prompt_builder.py:579-618`）只把 Phase **标题 + 首句要求**注入 prompt。标题里的 `(hotfix mode only, …)` 后缀与正文首句 "Activate only when…" **都不在骨架里** —— agent 在 prompt 中**看不到某些阶段可能不执行**。

**F2 — 跨 Phase 依赖用散文表达，且区分不了状态。**
6.6 说的是"branch is committed and pushed"（= `completed` 语义），6.7 说的是"regression verification passed"（= `passed` 语义）。二者被同一种散文句式承载，机器无法区分「执行完成」与「验证通过」——而这两者在门禁上强度完全不同（完成 ≠ 通过）。

**F3 — Phase 产出无契约。**
实测 `grep "Input:|Output:|carried|depends on" templates/runtime/*.md` 几乎零命中；`runtime-develop.md:150` 的 `Output:` 段是唯一例外。而 `workflows/*.md` 的 `## Outputs` 与 `runtime` 的 `# Outputs` **只有 runtime 级别的汇总比对**（`check_outputs_consistency`，`tools/checks/workflow.py:128-160`）——**哪个 Phase 负责哪个产物，无任何记录**。

### 1.2 bugfix Phase 6 的契约破损（本提案顺带修复）

按用户要求「`passed` 必须有明确判据，否则作为 Contract Gap 修复」，实测 Phase 6：

```
# Phase 6 — Regression Verification        (runtime-bugfix.md:248)
Invoke:
- testing          ← skills/ 39 个目录中不存在
- verification     ← skills/ 39 个目录中不存在
Verify:
- Original defect resolved / Existing behaviour unchanged / Regression tests pass
Generate: Regression Report
```

**G1 — `Invoke` 指向不存在的 skill。** `ls skills/` 全清单无 `testing` / `verification`（只有 `mock-test`）。对照 `runtime-verify.md`（自身即 verification）**根本没有 Invoke 段**。这两个名字是失效引用。

**G2 — pass 判据未链接既有机制。** `runtime-verify.md:214-250` **已定义完整判据**：Phase 7（mandatory verification 缺失 → ERROR，Status 不可 PASS）+ Phase 8（`Verification Status: PASS | FAIL`，任一 mandatory verification 失败含未闭合 validation gap → FAIL）。Phase 6 的 "regression verification passed" 与之语义相同却无引用。

→ 结论：**pass 判据存在，是链接缺失**。按用户决策 (a)（有判据才用 `passed`、不新增 gate），修 G1+G2 后 `phase("6").passed` 即合法，**无需新增执行机制**。

### 1.3 code-review 违反自己声明的真源

`workflows/code-review.md:58-69` 的 `### Target Branch Resolution` 5 条，与 `templates/runtime/runtime-code-review.md:67-117`（Phase 1）**完全重复**，且 runtime 侧更完整（分支来源表 + 7 条规则 + 候选采集顺序 + `cc{date}` 处理）。

而 workflow 第 60-61 行**自己声明了真源**：

> "(Contract: resolve each project's target branch per runtime Phase 1; ASK the user rather than guessing when a branch is missing/ambiguous.)"

即：已声明真源在 runtime，正文又抄了一遍。

`workflows/code-review.md` 去 frontmatter 后 **99 行**（`RFC-0003` 上限 100），加 `## Phases` 必然超限。

---

## 2. Goal

1. **Phase 成为一等机器契约**：id / name / activation / declares 四要素结构化，绑定 runtime 的 Phase 章节。
2. **条件执行对 agent 可见**：prompt 渲染时注入完整 Phase 表（含 Activation）。
3. **跨 Phase 依赖可判定**：`active` / `completed` / `passed` 三状态语义固定，机器可校验。
4. **Phase 产出责任可查**：`Declares ⊆ Workflow Outputs` 单向 ERROR 门禁。
5. **修复两处既有破损**：code-review 重复内容、bugfix Phase 6 的 G1/G2。

**非目标**：不拆 Phase 文件（P75 议题，本次只建立契约，拆不拆是后续独立决策）；
不改 Phase 的执行语义与步骤；不引入新执行机制（不新增 gate）；不重命名任何 Phase id；
不压缩 `prepare` / `external-review`（用户决策：最小压缩，不做 workflow-specific exception）。

---

## 3. Design Decisions（用户 2026-09-28 逐条定案）

### 3.1 边界：YAML 决定"是什么/何时/依赖/产出"，Markdown 决定"怎么做"

```text
workflow.md
  ├─ 1~8 段：稳定的人类可读正文
  └─ 9. ## Phases：契约入口（固定 3 行，不做 workflow-specific 例外）
        ↓
config/workflows/<name>.yaml → phases:     ← Phase Contract 结构真源
        ↓  phase.id ↔ runtime `# Phase <id> — <name>` 绑定
prompt_builder 渲染注入 → agent 实际看到
```

**不写成「表体放 YAML 因为它是机器契约」**——避免 `workflow.md → config.yaml → runtime.md → prompt` 的多「半真源」。定位是：**Workflow 的 Phase Contract 是结构化配置；Runtime Phase 正文是执行规范；二者通过 Phase ID 绑定。**

### 3.2 Activation 三状态语义（硬规则）

| 表达式 | 语义 |
|---|---|
| `phase("<id>").active` | 该 Phase 本次运行被启用 |
| `phase("<id>").completed` | 该 Phase 按其执行规范正常结束 |
| `phase("<id>").passed` | 该 Phase **定义的验证 / gate / acceptance 判据**成功 |

**硬规则**：`phase("<id>").passed` **只能引用定义了明确 pass/fail 判据的 Phase**。
未定义判据却引用 `.passed` → **ERROR**（把语义空缺变成机器可检的契约错误）。
**不得**把 `passed` 静默降级为 `completed`，**不得**为满足引用而凭空新增 gate。

### 3.3 逐 Phase 列出，禁止区间合并

正式 Contract **必须逐 Phase 列出**，不允许 `1–3` 这类范围。理由：若允许区间，
机器须额外解释「`1–3` 是 1,2,3 还是名为 `1–3` 的 group」，一旦其中某个 Phase 有独立
Activation 就需重新解释区间含义 → 退化为 "Phase Range DSL"，不值得。

**视觉压缩允许**：渲染时 `always` / `—` 可显示为紧凑形式，但**契约数据仍逐条**。

### 3.4 Declares 单向约束

```text
Phase Declares  ⊆  Workflow Outputs     ← ERROR（防止 Phase 产生野生产物）
Workflow Outputs ⊆ Phase Declares       ← 不检查
```

**语义区分**（用户定案）：
- `Phase Declares` = 该 Phase 对该 artifact 的**直接产出责任**（Phase 完成时该 artifact 应已产生/更新）
- `Workflow Outputs` = workflow 对外声明的**最终输出集合**（可由多个 Phase 共同贡献，或为最终汇总产物）

不做反向检查的实测依据：多数 workflow 是「多 Phase → 少产物」结构
（`bugfix` 12 Phase → 4 Outputs、`external-review` 8 → 2、`code-review` 6 → 1）。
Completion Report 类汇总产物若强制反向覆盖，会产生大量无意义声明以迎合 validator。

### 3.5 `## Phases` 固定 3 行入口

```markdown
## Phases

Phase execution contract is defined by the workflow configuration.
The configured Phase contract MUST match the Runtime Phase structure.
```

表体由 `config/workflows/<name>.yaml → phases` 在渲染时注入 prompt。
**所有 workflow 一致，不做 workflow-specific 例外。**

---

## 4. Config Schema

```yaml
# config/workflows/bugfix.yaml
version: 1
name: bugfix
workflow: workflows/bugfix.md
runtime: templates/runtime/runtime-bugfix.md

phases:
  - id: "1"
    name: Issue Analysis
  - id: "2"
    name: Reproduction
  - id: "3"
    name: Root Cause Analysis
  - id: "4"
    name: Fix Planning
  - id: "4.5"
    name: Approval Gate
    activation: "WHEN mode.approval_gate"
  - id: "4.6"
    name: Branch
    activation: "WHEN mode.phases ∋ branch"
  - id: "5"
    name: Implement
  - id: "6"
    name: Regression Verification
    pass_criterion: "Verification Status = PASS (runtime-verify Phase 7/8 criteria)"
  - id: "6.5"
    name: Commit
    activation: "WHEN mode.phases ∋ commit"
  - id: "6.6"
    name: Submit MR
    activation: "WHEN mode.phases ∋ mr ∧ phase(\"6.5\").completed"
  - id: "6.7"
    name: Doc
    activation: "WHEN mode.phases ∋ doc ∧ phase(\"6\").passed"
  - id: "7"
    name: Completion

# declares 可选；只声明「直接产出责任」的文件型产物
# 未列 declares 或声明为 [] 表示该 Phase 无独占产物（不报错）
```

**字段**：

| 字段 | 必填 | 说明 |
|---|---|---|
| `id` | ✓ | Phase 编号，支持小数（`4.5`）；须与 runtime 标题一致 |
| `name` | ✓ | Phase 名；须与 runtime 标题一致 |
| `activation` | | 缺省 = `always`；条件时为 `WHEN <expr>` |
| `declares` | | 缺省 = `[]`；文件型 artifact 列表 |
| `pass_criterion` | | 该 Phase 的 pass/fail 判据；`.passed` 引用它时**必需** |

**Activation 表达式语法（第一版，不做通用表达式语言）**：

```
always
WHEN <源> <运算符> <值> [∧ <依赖条件>]*
源    := mode.<config 键>  |  phase("<id>").<状态>
状态  := active | completed | passed
运算符 := 包含(∋) | 等于(=)
连接符 := ∧
```

禁止自然语言（`when MR is enabled and the branch was committed in Phase 6.5`）——
机器须能解析。

---

## 5. Proposed Changes

### 5.1 Phase Contract 规范文档

| # | 层 | 改动 |
|---|---|---|
| 1 | `governance/policies/phase-contract.md`（新） | Phase Contract 规范：四要素定义、三状态语义表、Activation 表达式语法、Declares 单向约束与语义区分、逐 Phase 强制、**YAML/Markdown 职责边界**（是什么/何时/依赖/产出 vs 怎么做） |
| 2 | `governance/SOURCE_OF_TRUTH.md` | 登记 Phase Contract 为 Phase 相关信息的 SSOT |
| 3 | `rfc/ADR-0006-workflow.md` | 补 Phase 为 workflow 可选契约段（第九段）的定位 |
| 4 | `templates/README.md` | 模板层纪律：`## Phases` 入口固定 3 行；Phase id 命名（支持小数） |

### 5.2 Workflow 第九段

| # | 层 | 改动 |
|---|---|---|
| 5 | 16 个 `workflows/*.md` | 追加 `## Phases` 固定 3 行段（`README.md` 除外）；位置在 `## Runtime` 之后 |
| 6 | `tools/workflow-command-audit.py:36-45` | `WORKFLOW_SECTIONS` 增 `Phases`（九段）；**注意**该清单同时用于"缺失即 BLOCKER"，故所有 workflow 必须同步补齐 |
| 7 | `tools/checks/workflow.py:89-126` | `check_workflow_runtime_section` 扩展：`## Phases` 段必须引用 config（值与 config `phases` 存在性一致） |
| 8 | **`workflows/code-review.md:58-69`** | **最小压缩**：删除 `### Target Branch Resolution` 5 条（与 `runtime-code-review.md:67-117` Phase 1 完全重复，且 workflow:60-61 已自声明真源在 runtime），保留一行契约声明。**99 → 88 行**，加 `## Phases` 3 行 = **91 行**（余 9）。**不放宽 100 行门禁、不做特例** |

### 5.3 Config + 渲染注入

| # | 层 | 改动 |
|---|---|---|
| 9 | 16 个 `config/workflows/*.yaml` | 新增 `phases:` 块（逐 Phase）；`bugfix` 含 5 个条件 Phase + `pass_criterion` |
| 10 | `cli/services/prompt_builder.py:110-138` | 渲染时把 `config.phases` 注入为 `## Phase Contract` 段（紧邻 Runtime Skeleton）；**无条件渲染**（不骨架化）——条件执行与依赖必须始终可见 |
| 11 | `cli/services/prompt_builder.py` | 骨架尾注（`:635-640`）改为指向 Phase Contract 而非单文件 |
| 12 | `templates/prompts/workflow.md` | 模板加 `## Phase Contract` 占位 |

### 5.4 机器校验（`tools/checks/phase_contract.py`，新）

| 校验 | 级别 | 依据 |
|---|---|---|
| **C1** 引用不存在的 Phase id（`phase("9.9")` 而 phases 无 `9.9`） | **ERROR** | 用户定案 |
| **C2** `phase("X").passed` 但 X 无 `pass_criterion` | **ERROR** | 用户定案（§3.2 硬规则） |
| **C3** Phase `declares` 的 artifact 不在 workflow `## Outputs` | **ERROR** | 用户定案（§3.4） |
| **C4** workflow `## Outputs` 未被任何 Phase `declares` | *不报错* | 用户定案 |
| **C5** Phase id 与 runtime `# Phase <id>` 标题**集合一致**（缺/多/编号不符） | **ERROR** | 新增（保证 YAML↔runtime 绑定不漂移） |
| **C6** Phase id 唯一、name 非空 | **ERROR** | 新增 |
| **C7** Activation 表达式可解析（禁止自然语言；`mode.*` 键存在于 bugfix-modes.yaml） | **ERROR** | 新增 |
| **C8** `## Phases` 段存在（九段契约） | **BLOCKER**（audit）/ **ERROR**（check.py） | 复用 §5.2-6 |

接入：`tools/checks/__init__.py` + `tools/check.py`（新增第 16 项）+ pre-commit 可见。

### 5.5 门禁自身的负例测试

今日已三次踩「门禁静默失效」（`proposal-audit` 的 `glob` 非 `rglob`、§P74 F4 `path-audit` 不管 reports 内部引用、`check_outputs_consistency` 的 `if not rt_items: return`）。**每个新校验必须有负例**：

```python
# cli/tests/test_phase_contract.py
- C1 负例：phases 无 9.9，activation 引用 phase("9.9") → 断言报错
- C2 负例：phase("6").passed 而 6 无 pass_criterion → 断言报错
- C3 负例：Phase declares 野生文件 → 断言报错
- C4 负例：Workflow Output 无 Phase 声明 → 断言**不**报错
- C5 负例：YAML 有 7 个 Phase 而 runtime 有 6 个标题 → 断言报错
- C7 负例：activation 写自然语言 → 断言报错
- **真实仓库零 findings**（同 test_protected_paths.test_real_repo_is_clean 范式）
```

### 5.6 bugfix Phase 6 契约破损修复（G1 / G2）

| # | 层 | 改动 |
|---|---|---|
| 13 | `runtime-bugfix.md:248-270` Phase 6 | **G1**：`Invoke: testing / verification` → 改为描述「执行验证工作」（Phase 6 开头已声明不走 main-chain `verify` workflow，故不委托），删除失效 skill 名。**G2**：补 `pass_criterion` 显式引用 `runtime-verify.md` Phase 7/8 的 `Verification Status` 判据 |

**不新增 gate**（用户决策 (a)）；不改动 Phase 6 的执行步骤语义。

---

## 6. 行数影响（实测）

### 6.1 workflow 正文（`RFC-0003` 100 行上限口径：去 frontmatter）

| workflow | 现正文 | +`## Phases` 3 行 | 判定 |
|---|---|---|---|
| code-review | 99 | **91**（先压缩 8 行） | ✓ 余 9 |
| external-review | 93 | 96 | ✓ 余 4 |
| prepare | 94 | 97 | ✓ 余 3 |
| 其余 13 个 | 54–75 | 57–78 | ✓ |

**三行入口固定 + 逐 Phase 数据在 config → 零例外**。

### 6.2 prompt 体积

Phase Contract 表逐 Phase 渲染进 prompt。实测预估：`bugfix` 12 行表 ≈ 700 字符
（vs 当前骨架中 5 个 hotfix-only 条件**完全不可见**）。**这是净增，但增的是
当前缺失的契约信息** —— `prompt-metrics` 须记录变化并确认 `prefix_stable` 仍 16/16。

---

## 7. Validation Plan

1. **契约正确性**：16 个 workflow 的 `phases[].id` 集合 == 对应 runtime 的 `# Phase <id>` 标题集合（逐个断言）
2. **C1–C3 负例**：各构造一个违规 config → 断言门禁 ERROR
3. **C4 不报错**：构造 Output 无 Phase 声明 → 断言 0 error
4. **prompt 可见性**：构建 bugfix prompt，断言含 5 个条件 Phase 的 Activation 与 `phase("6.5").completed` 依赖
5. **C2 回归**：Phase 6 补 `pass_criterion` 前，`phase("6").passed` 应报错；补后应通过（**先红后绿**，证明门禁有效）
6. **行数**：code-review 91 / external-review 96 / prepare 97，其余 ≤78；`check.py` 无 RFC-0003 ERROR
7. **全量门禁**：`check.py` PASS · 全量 CLI 单测 OK · `repo-lint` 0 BLOCKER/0 ERROR · `path-audit` 0 broken · `workflow-command-audit` 0-0-0 · `extensions-lint` 0-0 · `language-gate` PASS
8. **体积**：`prompt-metrics` 记录 Phase Contract 引入的增量 + `prefix_stable` 16/16

---

## 8. Risks

| # | 风险 | 缓解 |
|---|---|---|
| R1 | **八段→九段是全 workflow 契约变更**，漏改即 BLOCKER | §5.2-5/6 同步改 16 文件 + `WORKFLOW_SECTIONS`；`check.py` 立即反映 |
| R2 | **Phase Contract 引入门禁静默失效**（今日已踩三次） | §5.5 每个校验配负例 + 真实仓库零 findings 断言 |
| R3 | `.passed` 语义被误用为 `.completed` 的同义词 | C2 硬门禁 + 规范明文「不得静默降级」 |
| R4 | `activation` 表达式退化为自然语言（不可解析） | C7 强制可解析；规范给出正反例 |
| R5 | Phase Contract 增大了 prompt（bugfix +700 字符） | **这是当前缺失信息的补齐，非浪费**；`prompt-metrics` 记录；若增幅超预期，优先缩短 `name` 而非砍 Phase |
| R6 | 16 个 workflow 的 phases 块 authoring 成本 | 从 runtime 标题机械提取为起点（`# Phase <id> — <name>` 格式实测统一，4.5 需剥条件后缀）；activation 缺省 always，只有 bugfix 5 个需手写 |
| R7 | code-review 压缩误删有效信息 | 逐条比对 runtime Phase 1 确认 5 条全覆盖；归一化 word-diff（P59 Rule 5） |
| R8 | YAML↔runtime 双份数据漂移（两个"半真源"） | C5 集合一致性 ERROR；§3.1 明确定义边界（YAML 是什么/何时/依赖/产出，MD 怎么做） |

---

## 9. 待裁定子决策

| # | 决策点 | 状态 |
|---|---|---|
| ① | 整体方案与三态语义 | ✅ 用户 2026-09-28 定案 |
| ② | `## Phases` 落点（配置为真源 + 九段入口 + 渲染注入） | ✅ 已定案 |
| ③ | 逐 Phase 列出、禁区间合并 | ✅ 已定案 |
| ④ | Declares 单向约束 + 语义区分 | ✅ 已定案 |
| ⑤ | code-review 最小压缩（不放宽门禁、不做特例） | ✅ 已定案（走 ① 压缩） |
| ⑥ | bugfix Phase 6 走 (i) 自执行验证 + 链接既有判据 | ✅ 已定案 |
| ⑦ | **Phase Contract 落文档位置** | ❓ 建议 `governance/policies/phase-contract.md`（与 `proposal-policy.md` 同级）；备选 `rfc/RFC-0005`（runtime 规范）——**Phase 契约跨 workflow+runtime 两层，`policies/` 更合适** |
| ⑧ | **`phases:` 落 config yaml 还是 workflow frontmatter** | ❓ **已实测关键前提**：100 行门禁剥离 frontmatter（`tools/checks/workflow.py:281` / `workflow-command-audit.py:101`），故 frontmatter **不占行数额度**（`bugfix.md` 全文 89 = frontmatter 20 + 正文 69）。frontmatter 已是机器契约（`inputs`/`outputs`/`next`），`phases` 放此处契约更聚合；代价是 20 → 约 45 行的 frontmatter 偏长。**建议 frontmatter**（聚合契约优先，行数不是约束） |
| ⑨ | 实施分期 | ❓ 建议 S1 = 规范 + config 块 + 门禁 + 负例测试（不渲染注入）；S2 = 九段 + 渲染注入 + code-review 压缩 + G1/G2 修复 |

---

## Review Log

| Role | Verdict | Notes |
|---|---|---|
| User | **Approved** | §3 全部设计决策 2026-09-28 定案；§9 ⑦⑧⑨ 2026-09-29 定案。授权 S1 实施 |

---

## Implementation Record (2026-09-29) — S1

**范围**（用户定案 ⑦⑧⑨）：规范 + 16 workflow frontmatter `phases` 块 + 8 条门禁 +
15 个负例测试。**不含** S2（`## Phases` 九段 / prompt 渲染注入 / code-review 压缩 /
bugfix G1·G2 修复）。

### 交付物

| 文件 | 内容 |
|---|---|
| `governance/policies/phase-contract.md` | 规范 305 行：职责边界 · 四要素 schema · Activation 文法 · 三态语义 + 硬规则 · Declares 单向 · 禁区间合并 · 8 条门禁 · 作者纪律。0 CJK（与其他 6 个 policy 一致） |
| `tools/checks/phase_contract.py` | 8 条门禁，接入 check.py 第 16 项 |
| `cli/tests/test_phase_contract.py` | 15 用例，每条门禁配负例 + 真实仓库零 findings |
| 16 × `workflows/*.md` | frontmatter `phases:` 块，共 117 个 Phase |

### 顺带修两处既有缺陷（C5 门禁在建立过程中暴露）

1. **`runtime-develop.md` 的 `## Phase 1` / `## Phase 2` 无标题** → 骨架化正则
   （`prompt_builder.py:596`，要求标题含 em dash）失配 → **agent 在 prompt 里完全
   看不到这两个阶段**。补标题后骨架恢复 4 个 Phase 标题可见。这是 P76 §1.1 F1 的
   一个实证案例。
2. **`runtime-release.md` 的 `# Phase 5 Dependency Validation` 用空格而非 em
   dash** → 同样不匹配骨架化。统一为 em dash。

### 门禁自证（每条短路 → 对应负例失败 → 还原 15/15 绿）

| 短路 | 结果 |
|---|---|
| C1 引用检查 | 1 项失败 ✓ |
| C2 pass_criterion | 1 项失败 ✓ |
| C3 wild artifact | 1 项失败 ✓ |
| C5 id 集比对 | 1 项失败 ✓ |
| C6 id 唯一 | 1 项失败 ✓ |
| C7 表达式可解析 | 1 项失败 ✓ |

> C3 首次自证失败：短路方式写成 `or ["*"]` 反而让 `any()` 匹配放行。改为真正
> 跳过循环后生效——**短路验证本身也会写错**，与门禁实现一样需要实测。

### 门禁自身的 3 个 bug（首版跑挂后修正）

1. `_PHASE_HEADING` 缺 `re.M` → C5 全量误报（18 error），修正后归零
2. runtime 路径误从 frontmatter 取（权威源是 `config/workflows/*.yaml`）→ C5 全量
   误报；改为先读 config，回退 body 的 `## Runtime`
3. `_parse_phases` 未解 YAML 双引号标量内的转义 → `phase(\"6.5\")` 解析失败；
   新增 `_unquote`

### 已知增量

`repo-lint` WARN 97 → 114，其中 17 条来自新文件（英文代码注释，与既有 `adr.py` 8 /
`repo-lint.py` 16 / `prompt_builder.py` 7 同类）。WARN 级，不在 pre-commit strict
范围（strict 只管 Rule 4 英文区），非质量回归。是否批量转中文注释见后续批次。

### Validation

全量 652 单测 OK（+15）· check.py PASS（2 WARN 为既有开放提案/开放项）·
quick-check OK/findings 0 · path-audit 0 broken · repo-lint 0 BLOCKER/0 ERROR ·
workflow-command-audit 0-0-0 · 16 个 workflow frontmatter YAML 全部合法。

### 过程教训的落地位置（用户 2026-09-29 定：两处）

| 内容 | 位置 | 理由 |
|---|---|---|
| 方法论规则（每条门禁配负例 · 逐条短路自证 · 短路变更本身须验证 · 门禁 bug 是细节假设）+ 上线检查清单 | `governance/policies/quality-gates.md` § "Writing a Gate That Can Be Proven to Fail" | 门禁**作者**的行为规范，读者是写门禁的 AI/人，与既有 `Gate Severity` 同层；`policies/` 是跨层规则落点（`phase-contract.md` 已确立该先例） |
| 本轮实证（6 条短路结果表 · `or ["*"]` 反转实例 · 3 个门禁 bug 的症状表 · 顺带暴露的 2 个内容缺陷） | `governance/memory/ai-system/gate-self-verification.md`（新建，登记进 `ai-system/coding-memory.md` 索引） | 一次性**证据**进 memory，规则进 policy——`MEMORY_GUIDELINES.md` 明写「experience repository, not a rule repository」 |

**未落 `AI_OPERATING_RULES.md`**：那是跨层通用行为约束，而「写门禁要配负例」是具体技术
实践，塞进去会稀释该文件密度。

**未落 `skills/`**：门禁编写不是 skill 能力，是 policy 级纪律。

memory 门禁校验：0 error / 0 warning（三条目均含 `Context`/`Problem`/`Scope`/`Lesson`/
`Solution` 五字段，`Lesson` 为 `MEMORY_REQUIRED`）。

---

## Implementation Record (2026-09-29) — S2

**范围**（用户授权）：`## Phases` 第九段 + prompt 渲染注入 + `code-review` 最小压缩 +
bugfix Phase 6 的 G1/G2。P76 至此 **S1 + S2 全部交付**。

### 核心价值：条件执行首次对 agent 可见

`cli/services/prompt_builder.py` 新增 `_phase_contract_section()`，从 workflow
frontmatter 的 `workflow.phases` 渲染 `## Phase Contract` 表，注入
`templates/prompts/workflow.md` 的 `{{runtime_definition}}` 之后。
**无条件渲染、绝不骨架化** —— 契约的可见性就是它的全部意义。

实测 `bugfix` prompt 现在含 5 个 hotfix-only Phase 的 activation 与跨 Phase 依赖：

```
| 4.5 | Approval Gate     | WHEN mode.approval_gate                | — |
| 4.6 | Branch            | WHEN mode.phases ∋ branch              | — |
| 6.5 | Commit            | WHEN mode.phases ∋ commit              | — |
| 6.6 | Submit MR         | WHEN mode.phases ∋ mr ∧ phase("6.5").completed | — |
| 6.7 | Doc               | WHEN mode.phases ∋ doc ∧ phase("6").passed    | — |
```

此前这些条件只存在于 runtime 的标题后缀与正文 "Activate only when …" 句中，
而骨架化只保留标题与首句 → agent **完全看不到某些阶段可能不执行**。

模块级新增两个辅助函数（`_frontmatter_phases` / `_declares_list`），与门禁
`tools/checks/phase_contract.py` **共用同一套行级解析 + 反转义逻辑** —— prompt 与
check 对契约的解读必须一致，故不复用 yaml.safe_load 而各自实现同一 reader。

### 九段契约

16 个 workflow 追加固定 3 行 `## Phases` 指针段（紧跟 `## Runtime`）；
`tools/workflow-command-audit.py` 的 `WORKFLOW_SECTIONS` 八段→九段
（缺失即 BLOCKER）。

**行数全部达标**（RFC-0003 上限 100）：`prepare` 99 · `external-review` 98 ·
`code-review` 97 · 其余 59–80。

### code-review 最小压缩（超出预期）

删掉与 `runtime-code-review.md` Phase 1 完全重复的 5 条 `Target Branch Resolution`
（runtime 侧更完整：分支来源表 + 7 条规则 + 候选采集顺序 + `cc{date}` 处理），
保留 3 行摘要并显式指向 runtime。**99 → 92 行**（−7，目标 94–95），加 3 行指针后
**97 行**。

### bugfix Phase 6 G1 / G2

- **G1**：`Invoke: testing / verification` 指向 39 个 skills 中**不存在**的名字。
  改为明确「本阶段自行执行回归验证」并说明那两个词指**要做的工作**而非可调用单元
  —— 与 Phase 6 开头「不走 main-chain `verify` workflow」的既有声明一致，不新增
  执行机制。
- **G2**：补 `Success criterion` 段，显式引用 `runtime-verify.md` Phase 7/8 的
  Verification Status 规则（mandatory verification 缺失/失败即非 passed），
  并点明「Phase 6.7 因此不激活」。**复用既有判据，未新增 gate**。

### 门禁自证

| 短路 | 结果 |
|---|---|
| `_phase_contract_section` 永不渲染 | **6 项** prompt-builder 测试失败 ✓ |
| 删除某 workflow 的 `## Phases` 段 | audit **BLOCKER** + **2 项**单测失败 ✓ |
| 还原 | 26 / 26 OK，audit 0 blocker ✓ |

### 体积

`prompt-metrics`：147117 → **161562** 字符（**+3611 tok / +9%**），
`prefix_stable` **16/16** 保持。增量来自 Phase Contract 表 + 九段指针 ——
**补的是此前完全缺失的契约信息**，不是浪费。

### Validation

全量 662 单测 OK（+10）· check.py PASS（2 WARN 为既有开放提案/开放项）·
quick-check OK/findings 0 · path-audit 0 broken · repo-lint 0 BLOCKER/0 ERROR ·
workflow-command-audit 0-0-0 · extensions-lint 0-0 · phase 契约门禁 0 error。

### 未做（明确非目标）

Phase 文件拆分（P75 议题；P76 建立的契约是其前置条件，现已就绪）。

**follow-up 可见**：P75 §3.3 的 Phase 拆分现在有了稳定契约作前置，可重新评估。
