# Change Proposal: P67 — 结构性坏味道：检测 / 映射 / 劣化门（不含自动重构执行）

| Field | Value |
|---|---|
| Status | **Proposed** |
| Type | Structural (standards + tools + gate wiring + skill 扩展；**不新增 Runtime/Workflow**） |
| Author | AI Maintainer |
| Created | 2026-09-23 |
| Reference | 用户需求「针对格式和注释已有检查能力，但想让 AI 自动发现并重构」+ 4 项增强方案（2026-09-23 会话）；外部依据见 §1.3（已核验，含 2 处修正） |
| Process | OPERATIONS §12 Change Management |

---

## 1. Problem

### 1.1 现状：结构质量问题**没有任何自动检测**

| 层 | 现有能力 | 结构类覆盖 |
|---|---|---|
| 格式/注释/命名 | `tools/format-check.py`（23 项，**develop 强制**）· `format-jdt-gate.py` · `checkstyle-gate.py`（可选环境） | 仅第 23 项「重复实现检测」（相似度 ≥0.85/≥15 token） |
| 复杂度 | `tools/checkstyle/checkstyle.xml:95-97` `CyclomaticComplexity max=20` | **仅 warning，永不阻断**；且依赖 checkstyle 可选环境 |
| 坏味道 | `skills/review/smell-baseline.md`（12 个 Fowler 味道 + 每个的「→ 如何修」处方） | **纯人手评审辅助**：无检测、无计数、无强制力 |
| 重构执行 | `grep -i refactor skills/ workflows/` → **0** | 治理**刻意禁止**机会性重构（`karpathy-guidelines.md:241-251`、`ai-coding-rules.md` Rule 4、`AI_DEVELOPMENT_CONTRACT.md:142`） |
| 结构阈值 | 方法 **≤40 行**（`clean-code.md:54`）· 嵌套 **≤3**（`:68`）· God Object 无数值 | **类大小/方法数：全仓无任何阈值** |

### 1.2 后果（本仓可观测的缺口）

1. **「AI 改动导致结构劣化」无门可拦**：现有门禁管格式/命名/注释，管不了「20 行函数被改成 100 行嵌套 if-else、复杂度 8→25」这类劣化。
2. **坏味道处方有表无触发**：「味道→手法」映射已存在（`smell-baseline.md`）却只在人工 review 时被读到，**没有自动检测来触发它**。
3. **两套阈值风险**：任何新引入的阈值若与 §1.1 既有的 40/3/20 不统一，就重演刚清理完的 R3 病灶（同一判定多套标准）。

### 1.3 外部依据（2026-09-23 核验，一手来源）

| 依据 | 判定 | 对本提案的作用 |
|---|---|---|
| MSR 2026《How do Agents Refactor》(arXiv 2601.20160) | ✅ 准确：86 项目/组；"agent refactorings are **dominated by annotation changes**（agent 最常见 5 类重构全是注解相关），in contrast to the diverse structural improvements typical of developers"；Cursor 是唯一「重构后味道显著增加」的模型 | **支撑 §1.2 缺口 1、2**：AI 缺的是结构改善倾向，光靠"自由发挥"不会补上 |
| AIware 2026《Quality and Security Signals in AI-Generated Python Refactoring PRs》(arXiv 2605.21453) | ✅ 准确但语境不同：24.17% 是**被改文件**引入新 Pylint 问题，**以 convention 级为主**（line too long / 缺 docstring）；仅 22.5% 改动提升某项质量属性 | **反向支撑**：convention 级风险本仓**已被** format-check 覆盖 → 应把同一「确定性反馈」模式**扩展到结构维度**，而非另建体系 |
| Thoughtworks Radar Vol 34（2026-04）**#10 Mapping code smells to refactoring techniques（Trial）** | ✅ 准确，且其原文推荐载体正是我们已有的：用 **Agent Skills / AGENTS.md** 映射味道→手法，并**与 lint 工具集成形成 deterministic feedback** | **支撑 §3 Option B 的形态选择**（映射写进标准 + 挂到门禁） |
| DesigniteJava「F1 98.82%」 | ⚠️ **未证实**（工具真实：MSR 2024 toolbox v2.0、MSR 2026 论文用 v3.0；其人工验证表给的是可测试性味道 P/R ≈ 93.6%，无 98.82% 来源） | **不作为**引入依据；本提案选择复用仓内已有仪器 |
| RefAgent（ICSE 2026，arXiv 2511.03153，多 Agent 规划/执行分离） | ✅ 论文存在 | **不作为**引入依据：诊断/执行的层分离本仓已有（`design-review` 诊断 · `implement` 执行 · `review` 门控），缺的是仪器不是架构 |

## 2. Root-Cause

1. **结构度量缺失**：门禁只建了「文本层」仪器（格式/命名/注释），从未建「结构层」仪器（长度/嵌套/复杂度/类体积）——所以结构问题**不可见**，也就无从拦截。
2. **映射无触发点**：`smell-baseline.md` 的处方靠人读；没有检测信号 → 映射表闲置。
3. **无「劣化」语义**：现有门禁判「是否合规」，不判「**是否变差**」。劣化的定义需要**改动前后对比**（`--changed` 增量语义已有，可复用）。
4. **形态约束**：治理禁止机会性重构（保 diff 可评审）→ 本能力**不能**做成 develop 内自动改写，只能做成独立、需授权的「检测→建议」，执行另论。

## 3. Options

### 3.1 Option A — 全面引入（DesigniteJava + 自动重构执行 + 多 Agent 拆分）

能力最全，但：新增 JVM 工具链依赖（指标未证实）、新增自动改写业务码的路径（与 §2.4 治理冲突）、新增 Runtime/Workflow 层资产。**不建议**（违反 Minimal Change + Evolution Principle）。

### 3.2 Option B — 最小切片：**检测 + 映射 + 劣化门**（不含自动重构执行）**← 推荐**

- **Standards**：把「味道 × 检测信号 × 阈值 × 强制手法」表格化为 SSOT（复用 `smell-baseline.md` 既有处方，不另写）。
- **Tools**：新增结构度量（Java 侧优先复用 checkstyle 已有能力 + CodeGraph MCP 的 `find_large_functions` / `get_architecture_overview`）。
- **Gate**：新增「**无结构劣化**」门（`--changed` 增量下，改动文件的结构指标不得变差）。
- **Skills**：扩展 `skills/review/smell-baseline.md` 为「按严重度排序 → 原子步骤 → 每步跑测试（`java-maven` 既有委托点）→ **只建议不改**」的体检公式。
- **不做**：自动重构执行、多 Agent 运行时、自动回滚。

### 3.3 Option C — 只做映射规则（不写工具、不接门禁）

最省，但**不解决 §1.2 缺口 1**（劣化仍无门可拦），且映射表将**继续闲置**（无检测触发）。**不建议**。

### 3.4 Option D — 暂不实施，只立案登记

依据 Evolution Principle「不得为推测引入能力」：若**尚无真实事故**（如某次 AI 改动把复杂度/行数显著抬高），正确动作是立案等触发。**与 B 不互斥**：可「立案 + 先做零依赖的一半（映射表格化到标准）」，工具与门禁等真实触发。

## 4. Recommendation

**采纳 Option B，并按 §4.1 与 §4.2 分两段落地。**

理由：B 用**最低层改动**（Standards + Tools + Gate + 扩展现有 skill）拿到「结构可见 → 有强制手法 → 劣化即拦」三件事，不动 Runtime/Workflow、不引入新 JVM 依赖、不碰治理对「顺手重构」的禁令。

### 4.1 阈值口径（**前置裁决，避免再造标准**）

| 指标 | 本提案立场 |
|---|---|
| 方法长度 | **沿用仓内既有 ≤40 行**（`clean-code.md`）。用户的「≤80」与仓内一份**未采纳待审提案**（`reports/MAINTENANCE-2026-08-06-method-comment-convention.md:122`「propose（待审）…期间 80 行实践已落地」）冲突 → **并入该提案一并裁决**，本提案不新增第二套数 |
| 嵌套深度 | 沿用 **≤3 层**（`clean-code.md:68`） |
| 圈复杂度 | 沿用 **≤20**（checkstyle），但把「**劣化**」定为阻断项（升幅超阈值即拦），而非现在的「仅 warn」 |
| 类大小 / 方法数 | **新增**（仓内空白）：建议类 ≤500 行、方法数 ≤10（God Object 信号）—— 数值与上表**同一处裁决**，写入 `clean-code.md` 作为唯一来源 |

### 4.2 触发条件（Evolution Principle 守卫）

工具与门禁（`structure-audit.py` + 劣化门）**在出现真实触发后再实施**；映射表格化（Standard 侧，零依赖、无新资产）可先行。

## 5. Proposed Changes

1. **`governance/standards/common/smell-to-refactoring.md`（新）**：味道 × 检测信号 × 阈值 × 强制手法 表（SSOT）；
   `clean-code.md` 增补类大小/方法数阈值并与该表互引；`review-checklist.md` 引用该表（不复制）。
2. **`tools/structure-audit.py`（新，条件触发后）**：对 `--changed`（或指定路径）计算方法长度/嵌套深度/方法数/类行数/圈复杂度 → JSON；
   Java 侧**优先复用** `checkstyle.xml`（已在环境内）+ 需要时补 module；Python/资产侧用 `ast`。
3. **劣化门**：注册进 `config/main-chain-capabilities.yaml` `gates.develop`（+ review 引用），形态对齐 `format-check-a`：
   FAIL = 结构**净劣化**（改动文件指标变差且超阈值）；WARN = 接近阈值。**首版只拦不放行**，不做自动回滚（回滚按 Change Control L 级走）。
4. **`skills/review/smell-baseline.md`（扩展）**：加「排序 → 原子步骤 → 每步 `mvn test`（`java-maven` 既有委托点）→ 仅建议」公式；
   `templates/runtime/runtime-review.md` 的 Phase 3 引用该表格（不复制）。
5. **交叉引用**：`design-review`（设计期诊断）与本节（代码期诊断）分工写明；**不合并**、**不新增 workflow/skill**。
6. **索引登记**：`reports/PROPOSALS.md` + `reports/README.md`。

## 6. Validation Plan

- **映射表可执行性**：对 `clean-code.md` 既有阈值逐条给出「检测信号 + 手法」，无空项。
- **劣化门真假例**（实施阶段）：构造「20 行 → 100 行嵌套」（应 FAIL）与「等价重构复杂度不变」（应 PASS）两例，跑门禁本体断言退出码。
- **增量语义**：在既有业务仓 `--changed` 试跑，确认**存量不被判负**（对齐 R2/R4 的增量门禁经验）。
- **依赖降级**：checkstyle 不可用时按现有可选门禁惯例 → WARN 而非崩（对齐 P65/既有 `--skip` 语义）。
- **门禁全绿**：`check.py` / `repo-lint` / `path-audit` / `workflow-command-audit` / `proposal-audit` / 单测。

## 7. Risks

| 风险 | 缓解 |
|---|---|
| 新增阈值与既有 40/3/20 分叉（R3 病灶复发） | §4.1 强制「同一处裁决 + 单一来源写入 `clean-code.md`」，本提案不另设数 |
| 「劣化门」误拦合理重构（如 Extract Method 让单方法变长？不可能；但类体积可能上升） | 只判**净劣化**（多指标方向化 + 允许「一处变差一处变好」的显式豁免，需评审留痕） |
| 工具口径与 checkstyle / IDE 不同源（P65 同类教训） | 优先复用 checkstyle 已有配置；不新建第二套复杂度算法 |
| 依赖可选环境（checkstyle/JDT）导致门禁静默失效 | 采纳现有可选门禁的 `--skip`/环境门禁语义 + 不可用时 WARN（fail-loud，不静默 PASS） |
| **无真实事故即施工**（Evolution Principle） | §4.2 触发条件：工具/门禁待真实触发；Standard 侧先行的部分零依赖、零新资产 |
| 与治理「禁止机会性重构」冲突 | 形态限定为「检测 + 建议」，**执行需独立授权**；不新增自动改写路径 |
| 与 P50（实现后置确认）、P46（验证标记）等重叠 | 互补：P67 管**结构维度**；交叉引用，不合并 |

---

## Review Log

| Reviewer | Decision | Date |
|---|---|---|
| User (AI Maintainer operator) | **Approved（立案，2026-09-23）** — 范围限定 §3.2 Option B；阈值与实施触发见 §4.1/§4.2 | 2026-09-23 |