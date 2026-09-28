# Change Proposal: P75 — runtime 模板体量治理（体量门禁 + 报告模板外提 + 契约下沉 base）

| Field | Value |
|---|---|
| Status | **Proposed** |
| Type | Structural（模板层资产体量契约）+ Fix（门禁缺口） |
| Author | AI Maintainer |
| Created | 2026-09-28 |
| Reference | 用户 2026-09-28 指示「逐个巡检超过 10k 的运行时模板，给出优化建议和方案」；`templates/README.md`（P59 作者纪律：token 不是杠杆、不得为 token 折行）；`rfc/RFC-0003` §体量门禁（workflow 侧 100 行）；`cli/services/prompt_builder.py:502-600`（`_merge_runtime_base` + `_skeletonize_runtime` + `@keep` 机制）；`governance/REFLECTION_RULES.md`（Reflection SSOT） |
| Process | OPERATIONS §12 Change Management |

---

## 1. Problem（巡检事实，带证据）

### 1.1 盘面：`templates/runtime/` 18 个文件，5 个超 10K 字节

| 文件 | 字节 | 行 | Phase 数 | 结构完整度 | 骨架化后进 prompt |
|---|---|---|---|---|---|
| `runtime-release.md` | 14721 | **641** | 9 | Outputs✓ Completion✓ Reflection✓ | 1100 字符 |
| `runtime-develop.md` | 13989 | 335 | 4 | Outputs✓ **Completion✗** Reflection✓ | 728 |
| `runtime-dev-setup.md` | 12488 | 497 | 10 | Outputs✓ Completion✓ Reflection✓ | 1219 |
| `runtime-spec.md` | 10991 | 485 | 8 | Outputs✓ Completion✓ Reflection✓ | 1432 |
| `runtime-bugfix.md` | 10358 | 381 | 7 | Outputs✓ **Completion✗** Reflection✓ | 1838 |

余 13 个文件 171–346 行，均在合理区间。

### 1.2 事实一：token 早已不是问题（**先排除错误动机**）

`prompt_builder._skeletonize_runtime`（`cli/services/prompt_builder.py:535-600`）把
runtime 全文压成 Phase 骨架（标题 + 每 Phase 首条要求 + 全量模板路径引用）。实测：

- 5 个大文件进 prompt 的仅 **728–1838 字符**（`release` 骨架 25 行 / `bugfix` 33 行）
- 全 16 个 workflow 提示词合计 **81152 字符**（`prompt-metrics` 2026-09-28 快照）
- `prefix_stable` 16/16

且 P59（`templates/README.md` Rule 1）已实测：全文折行仅省 41 字符 / 130975（**0.03%**）
却引入 3 处丢空格缺陷 + 200 字符长行。**「为省 token 瘦身」不成立**，
`templates/README.md` Rule 2 明写「Token size is content, not whitespace」。

→ 因此本提案的动机是**可维护性与结构一致性**，不是 token。**任何"折行/压缩措辞"
类改动明确排除**（P59 已否决且有实测数据）。

### 1.3 事实二：runtime 侧完全没有体量门禁（根因）

`RFC-0003` 为 workflow 定义定了 **100 行硬门禁**（`tools/checks/workflow.py:280-291`，
超限 **ERROR**），实测生效（`reports/P73` §5.4 记载「`workflows/code-review.md` 正文
96/100 行，空间是本提案的主要实现约束」——说明这条门禁真实约束了设计）。

但 `templates/runtime/` **无任何体量检查**：

```
grep -rn "runtime" tools/checks/*.py | grep -iE "size|line|len|100"
  → 仅 1 条无关命中（config_yaml.py 的注释里提到 "runtime" 一词）
```

`repo-lint` 对 `templates/runtime/*.md` 只做 **Rule 4 语言纪律**检查
（`tools/repo-lint.py:471-474`），无体量维度。

**后果（已可观测）**：
- `runtime-release.md` 641 行 —— Phase 1 独占 **241 行**（其中 130 行是内嵌的
  逐 Task 审查子流程 + 两份报告模板），Phase 9 独占 89 行
- `runtime-external-review.md`（181 行）**未声明 `Extends: runtime-base.md`**
  —— 16 个文件中唯二的例外（另一个是 `runtime-base.md` 自身），却仍逐字重复
  Governance 8 行 + Reflection 9 行。它继承不到 base 的契约（P45 语言门禁、
  On Complete 诊断日志、Completion Report 语言要求），是**静默的契约缺失**

### 1.4 事实三：三类异质膨胀混在一个文件里

对 5 个大文件做结构拆解（排除标题/空行/分隔）：

| 文件 | 总行 | Governance | Reflection | 内嵌 markdown 报告模板 | 剩余真实流程 |
|---|---|---|---|---|---|
| `runtime-release.md` | 641 | 8 | 9 | **100** | 524 |
| `runtime-develop.md` | 335 | 8 | 9 | 0 | 318 |
| `runtime-dev-setup.md` | 497 | 8 | 9 | 0 | 480 |
| `runtime-spec.md` | 485 | 8 | 9 | 0 | 468 |
| `runtime-bugfix.md` | 381 | 14 | 9 | 0 | 358 |

**三类性质完全不同的问题**：

- **P1 无门禁** → 模板只增不减，结构漂移无告警（`develop` / `bugfix` 缺 Completion 段
  已实际发生；`external-review` 缺 `Extends` 已实际发生）
- **P2 报告模板内嵌** → `release` 的 100 行 markdown 报告模板
  （`review-{task-id}.md` 52 行 + `release-branch-review.md` 48 行）+ SQL/Apollo 示例
  是**产物格式**，不是执行流程。当前混在 runtime 里，使 Phase 1 膨胀到 241 行
- **P3 跨文件逐字重复** → 15 个非 base 文件各重复 Governance 8 行（**126 行**）
  + 14 个各重复 Reflection 9 行（**126 行**）= **252 行逐字冗余**。且
  Reflection 的实质内容在 `governance/REFLECTION_RULES.md`（128 行 SSOT，
  含 Reflection Checklist 5 项 + Iron Law + Output Format）中**已完整存在**

重复度实测（`cat *.md | sort | uniq -c`，≥4 次且非平凡行）：

```
16 ×  - AI Operating Rules: governance/AI_OPERATING_RULES.md
16 ×  - Repository First: governance/REPOSITORY_FIRST.md
16 ×  - Source of Truth: governance/SOURCE_OF_TRUTH.md
16 ×  - Context Loading: governance/CONTEXT_LOADING.md
16 ×  - Reflection Rules: governance/REFLECTION_RULES.md
15 ×  Standards are loaded according to loaders/standards-loader.md.
15 ×  Before declaring completion, execute Reflection according to governance/REFLECTION_RULES.md.
15 ×  Record the Reflection Report in the Completion output.
15 ×  Context is loaded according to governance/CONTEXT_LOADING.md.
14 ×  Do NOT modify code during Reflection.
14 ×  1. Simpler implementation possible?
```

---

## 2. Goal

1. **P1 止血**：runtime 侧有体量门禁，超限必须响亮（治「只增不减」）。
2. **P2 归位**：报告/清单模板从 runtime 剥离到模板层专属目录（治 release 241 行 Phase 1）。
3. **P3 收敛**：base 已声明的契约不再逐字重复（治 252 行冗余 + `external-review` 契约缺失）。
4. **契约可见性不回退**：任何下沉的内容必须在 prompt 中**仍然可见**（`@keep` 机制已具备）。

**非目标**：不改 Phase 划分与执行语义（除 P2 的模板外提、P3 的逐字段移除）；
不折行/不压缩措辞（P59 已实测否决）；不改 workflow 侧文件；不动 `runtime-base.md`
的契约内容本身。

---

## 3. Options

### 3.1 方案 A — 只补体量门禁（Fix 级，最小）

在 `tools/checks/workflow.py`（或新 `tools/checks/runtime_size.py`）加 runtime 体量检查。
阈值建议（按实际体量定标，非照搬 workflow 的 100）：

| 区间 | 动作 | 依据 |
|---|---|---|
| ≤ 400 行 | 通过 | 13/18 个文件在此区间，是当前常态 |
| 401–600 | **WARN** + 提示拆分方向 | `dev-setup` 497 / `spec` 485 在此 |
| > 600 | **ERROR** | 仅 `release` 641 超限 |

- ✅ 零内容改动、零风险；把「无告警」变成「有告警」，止血
- ❌ 不解决 P2/P3；`release` 仍需人工处置才能过 ERROR

### 3.2 方案 B — 报告模板外提（Structural）

把 runtime 内嵌的报告/清单模板移到模板层新目录，runtime 改为引用。

落点候选（**待裁定**）：
- `templates/reports/`（新目录，与 `prompts/` 平级）—— 语义最准（产物格式 ≠ 提示骨架 ≠ runtime）
- `templates/prompts/`（复用现目录）—— 但 `prompts/` 现有 8 个文件全是
  **prompt 骨架**（`workflow.md` / `command.md` / `tasks-template.md`），
  塞入报告格式会混淆两类资产（`prompt_builder` 只读 `prompts/`，误放有加载风险）

`release` 外提后可从 **641 → ~490 行**（−100 报告模板 − 若干示例），落到 WARN 区间。

- ✅ 治 P2；`release` 显著改善；产物格式有了单一权威位置
- ⚠️ 需确认外提后 agent 仍会 Read 引用文件（`_skeletonize_runtime` 已给出
  「Full runtime template: <path> (read the phase's section…)」的按需读取范式，
  报告模板同理可行）
- ⚠️ 新增目录 = 新的门禁/索引义务（呼应 P74 的教训：**新增资产位置必须同步门禁**）

### 3.3 方案 C — 契约下沉 base（Structural）

移除 15 个文件里逐字重复的 Governance 段（126 行）与 14 个文件里逐字重复的
Reflection 段（126 行），改为 `runtime-base.md` 统一规定，各文件只留差异
（如 `bugfix` 的 Iron Law、hotfix-only 分支说明）。

**可行性已实测确认**：`prompt_builder._merge_runtime_base`
（`cli/services/prompt_builder.py:502-530`）会解析 `Extends:` 并把 base 全文
追加为骨架化输入，base 中的 `<!-- @keep -->` 行**会进入 prompt 骨架**。
实测 `runtime-knowledge` 的骨架确实带上了 base 的 P45 语言门禁 `@keep` 行：

```
  Before presenting, the Runtime runs the language gate (P45):
  `python3 tools/language-gate.py <report-file>` — PASS → present; …
```

即：把 Reflection 要求写进 base 并打 `@keep`，agent 在 prompt 里**看得见**。

**必须同步的两处硬伤**：
1. `runtime-external-review.md` 补 `Extends: - runtime-base.md`（否则它继承不到任何契约）
2. `runtime-hotfix-test-doc.md` 有 Governance 但 Reflection 正文为 0 行 —— 需确认是有意省略

- ✅ 治 P3；消除 252 行冗余；顺带修 `external-review` 契约缺失
- ⚠️ **风险**：Reflection 是 completion 强制项。若从各文件删除而 base 的 `@keep`
  写得不显眼，agent 可能跳过 → 必须实测 prompt 骨架里可见
- ⚠️ 15 文件批量改动，需归一化 word-diff 复核（P59 Rule 5）

### 3.4 方案 D — 拆 Phase / 重划 runtime 边界（不推荐）

把 `release` 的 Phase 1.Y（逐 Task 分支审查，130 行）拆成独立 runtime 或 skill。
❌ 反驳：Phase 1.Y 是 release 的**质量闸门**（Exit Criteria 依赖它），
拆出去会割裂 Preconditions→Exit Criteria 契约闭环。且 P73 已显示
`workflows/code-review.md` 被 100 行门禁挤到 96/100 —— **runtime 侧也在逼近
「细节下沉」的方向，但方向应是「模板下沉」而非「Phase 拆分」**。

---

## 4. Recommendation

**三步走，A → B → C，每步独立可交付、独立可回滚**：

| 步骤 | 方案 | 层级 | 治 | 风险 | 依赖 |
|---|---|---|---|---|---|
| **A1** | 体量门禁（400 WARN / 600 ERROR） | Fix | P1 | 极低 | 无 |
| **A2** | `release` 报告模板外提（解 600 ERROR 阻塞） | Structural | P2 | 低 | B 落点裁定 |
| **B** | 全量报告模板外提 + `templates/reports/` 门禁同步 | Structural | P2 | 中 | A2 |
| **C** | 契约下沉 base + `external-review` 补 `Extends` | Structural | P3 | 中高 | C 的 `@keep` 实测 |

**理由**：

1. **先止血再优化**：A1 零风险、立即生效，且能让 B/C 的收益变成**门禁可见的数字**
   （外提后 `release` 从 ERROR 降到 WARN 是可验证的，而非"感觉清爽了"）。
2. **动机必须正名**：明确写入提案「token 不是动机」（§1.2 有实测数据）。
   否则后续执行者会误以为省 token 而做折行/压缩改动 —— **P59 已否决该路径并有数据**。
3. **A2 先于 B**：`release` 是唯一超 600 的文件，不先解它，A1 的 ERROR 会让
   门禁立刻红。最小切口是**只外提那 100 行报告模板**，不碰 Phase 1.Y 的流程逻辑。
4. **C 放最后且要实测**：Reflection 是 completion 强制项，下沉后 prompt 可见性
   必须实测验证（`_merge_runtime_base` + `@keep` 机制已有先例可用）。
5. **Minimal Change**：三步各自独立，不打包。A1 今天就能做且零风险。

---

## 5. Proposed Changes（待批准实施）

### 5.1 A1 — 体量门禁

| # | 层 | 改动 | 备注 |
|---|---|---|---|
| 1 | `tools/checks/runtime_size.py`（新） | 遍历 `templates/runtime/*.md`，去 frontmatter 后计行；>600 → `c.error`；401–600 → `c.warn` + 提示「考虑外提报告模板至 `templates/reports/`（见 P75 §3.2）」 | 新建独立 check 而非塞进 `workflow.py`（后者语义是 workflow 契约） |
| 2 | `tools/checks/__init__.py` + `tools/check.py` docstring | 接入 check.py（新增第 16 项） | 须在 pre-commit hook 可见 |
| 3 | `governance/policies/` 或 `rfc/RFC-0003` | 记录 runtime 体量口径（为何不用 100：runtime 承载多 Phase + 按需读取的产物格式） | 口径写进治理，避免后人按 workflow 的 100 硬套 |
| 4 | 测试 | ①600+ → error；②401–600 → warn；③`runtime-base.md` 自身也计入；④阈值边界（400/401/600/601） | — |

### 5.2 A2 / B — 报告模板外提

| # | 层 | 改动 | 备注 |
|---|---|---|---|
| 5 | 新建 `templates/reports/`（落点待裁定 §8-②） | 迁入 `runtime-release.md` 的 2 份报告模板（100 行）+ SQL/Apollo 示例 | 目录定位写进 `templates/README.md` Layers 表 |
| 6 | `templates/runtime/runtime-release.md` | 模板位置改为引用（`per templates/reports/release-branch-review.md`）；保留「生成什么 / 落哪」的决策句，删除格式细节 | 决策与格式分离 |
| 7 | `templates/README.md` | Layers 表新增 `reports/` 行 + 作者纪律（报告格式 vs runtime 流程的边界） | 呼应 P74 教训：新增资产位置必须同步门禁与文档 |
| 8 | 门禁 | 新目录纳入 `repo-lint` Rule 4 范围判定 + `path-audit` 引用检查 | 漏做 = 新目录成盲区（P74 R2 同类） |
| 9 | 测试 | 外提后 `release` 行数 < 600（门禁转绿）+ 引用路径存在 | — |

### 5.3 C — 契约下沉 base

| # | 层 | 改动 | 备注 |
|---|---|---|---|
| 10 | `templates/runtime/runtime-external-review.md` | **补 `Extends: - runtime-base.md`** | ⚠️ 硬伤：当前继承不到 base 的任何契约 |
| 11 | 15 个非 base 文件 | 移除逐字重复的 Governance 段（126 行） | 保留各自差异（如 `bugfix` 的 Iron Law 保留在 Governance 之后独立成段） |
| 12 | 14 个文件 | 移除逐字重复的 Reflection 段（126 行） | `runtime-hotfix-test-doc.md` Reflection 正文为 0 行 —— 需确认是有意省略还是漏写 |
| 13 | `templates/runtime/runtime-base.md` | 补统一的 Governance 声明 + Reflection 要求（打 `<!-- @keep -->`，参考既有 P45 语言门禁行的写法） | `@keep` 是 prompt 可见性的唯一保障 |
| 14 | **实测（阻塞项）** | 构建 `bugfix` / `release` / `spec` prompt，断言骨架含 Reflection 要求 | 不通过则本步不得合入（Reflection 是 completion 强制项） |
| 15 | 测试 | ①base `@keep` 行出现在各 workflow 骨架；②`external-review` 骨架含 base 契约；③`develop`/`bugfix` 补齐 `Completion` 段（治 §1.3 结构漂移） | — |
| 16 | 归一化 word-diff | 15 文件批量文本改动，按 P59 Rule 5 折叠空白后比对 | 防止丢空格 |

---

## 6. Validation Plan

**A1**：
1. 负例：临时给某 runtime 加 250 行 → check.py 报 WARN；加到 601 → ERROR
2. 真实仓库：`release` 641 → ERROR（预期！A1 落地后门禁会先红，A2 解）
3. 门禁全绿：`check.py` / 630 单测 / `repo-lint` / `path-audit` / `extensions-lint` /
   `workflow-command-audit`

**A2/B**：
4. `release` 行数 641 → **< 400**（若全部外提）或 **< 600**（仅外提报告模板）
5. `prompt-metrics` 实测 `release` 骨架变化（应**基本不变** —— 报告模板本就不在骨架内，
   这正是要验证的点：**外提不得使 agent 失去报告格式**）
6. 门禁：新目录被 Rule 4 / path-audit 覆盖（反证：往新目录放中文散文 → Rule 4 报警）

**C**：
7. **prompt 可见性（阻塞）**：断言 `bugfix`/`release`/`spec` 骨架含 Reflection 要求文本
8. 逐字等价：移除的 252 行内容确实在 base 中存在且被引用（`diff` 复核）
9. `external-review` prompt 骨架含 base 契约（P45 语言门禁行）
10. `prefix_stable` 仍 16/16；`prompt-metrics` 无异常增长

---

## 7. Risks

| # | 风险 | 缓解 |
|---|---|---|
| R1 | **误把「瘦身」当 token 优化** → 后续执行者做折行/压缩措辞 | §1.2 写入实测数据（P59：0.03% 收益 + 3 处缺陷）；`templates/README.md` Rule 1/2 已固化；本提案**明确列为非目标** |
| R2 | **A1 落地后门禁立即红**（`release` 641 > 600） | 预期行为；A1 与 A2 **同批合入**（或 A1 先以 WARN-only 落地观察一周，再升 ERROR）—— §8-① 待裁定 |
| R3 | **C 下沉后 agent 跳过 Reflection**（completion 强制项） | §5.3-14 实测为**阻塞项**，不通过不合入；`@keep` 机制已有实测先例（`runtime-knowledge` 骨架实测） |
| R4 | 15 文件批量文本改动引入丢空格/结构破坏 | P59 Rule 5 归一化 word-diff（§5.3-16） |
| R5 | 新目录 `templates/reports/` 成为门禁盲区 | §5.2-8 显式纳入 Rule 4 + path-audit；反证测试（放中文散文应报警） |
| R6 | 外提后 agent 不再 Read 引用文件 → 报告格式丢失 | §6-5 实测骨架 + 端到端跑一次 release 验证产物；`_skeletonize_runtime` 的按需读取范式可循 |
| R7 | 阈值定标争议（400/600 是否合理） | §8-③ 待裁定；阈值写进治理文档而非只在代码里 |

---

## 8. 待裁定子决策（每条附建议）

| # | 决策点 | 选项 | 建议 |
|---|---|---|---|
| ① | A1 门禁首版强度 | 直接 ERROR / **先 WARN-only 观察再升** / 只对 `release` 单点 ERROR | **先 WARN-only 一周**（避免 §R2 立刻红；观察真实分布后再定档） |
| ② | 报告模板落点 | 新建 `templates/reports/` / 复用 `templates/prompts/` / 就近放 `templates/runtime/reports/` | **新建 `templates/reports/`**（`prompts/` 会被 `prompt_builder` 加载，误放有风险） |
| ③ | 体量阈值 | 400 WARN / 600 ERROR / 500+600 / 其他 | **400 / 600**（依实测分布：13 个 ≤400，两个 401–600，一个 >600） |
| ④ | 三个方案全做还是只做 A | A / A+B / A+B+C | **A+B+C 分三步**（A 零风险；B 解 `release`；C 需实测） |
| ⑤ | C 方案 Reflection 是否下沉 | 下沉 / 保留各文件 | **下沉**（252 行冗余 + `external-review` 契约缺失；但以 §6-7 实测为前置条件） |
| ⑥ | `develop`/`bugfix` 补 `Completion` 段 | 补 / 不补（现状可接受） | **补**（结构漂移是 P1 的实证，且成本 3–5 行） |
| ⑦ | 阈值口径写进哪 | `RFC-0003` 扩写 / `governance/policies/` 新增 / 只在代码注释 | **`RFC-0003` 扩写一节**（体量契约的 SSOT 所在） |

---

## Review Log

| Role | Verdict | Notes |
|---|---|---|
| User | **Pending** | 需裁定 §8 七项子决策。**关键前置澄清**（用户 2026-09-28 讨论中提出）：本提案动机是「可维护性」而非「token」（§1.2 已实测排除 token 动机）；若真实关切是「AI 读太多」，则应改 `prompt_builder` 骨架化策略而非模板 —— 请确认关切点归属 |
