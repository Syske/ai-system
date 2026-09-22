# Change Proposal: P66 — code-review / change-impact 重复追问项目与分支（应按项目信息直接推断）

| Field | Value |
|---|---|
| Status | **Proposed** |
| Type | Structural (wizard 字段派生规则 + 两个工作流输入契约) |
| Author | AI Maintainer |
| Created | 2026-09-21 |
| Reference | 用户反馈 2026-09-21：「aic 的 code-review 和 change-impact 如果前置选择了项目，不应该再让选择项目和分支，应该根据项目信息直接推断」 |
| Process | OPERATIONS §12 Change Management |

## 1. Problem

### 1.1 症状（用户报告）

`aic` 中先选定了项目（容器）后，进入 `code-review` / `change-impact` 仍会被再次要求
**选择项目（服务）** 与 **分支**，而这两类信息在已选项目的容器元数据里**已有权威记录**。

### 1.2 落位证据（代码层）

| # | 事实 | 位置 |
|---|---|---|
| 1 | 二者是**工作流**（非命令），输入取自 workflow frontmatter | `config/workflow-registry.yaml:17,19`；`config/menu.yaml:80,83` |
| 2 | `code-review` 必填 `[Projects]` + 5 可选；`change-impact` 必填 `[Projects, Code Reference]` + 4 可选 | `workflows/code-review.md` / `workflows/change-impact.md` frontmatter |
| 3 | 目标选定后的**预填**只覆盖字面量 `Project ID`/`Workspace ID` | `cli/services/wizard/steps.py:142-153` |
| 4 | 必填字段**不允许 Enter 跳过**（留空即重问） | `steps.py:196-202` |
| 5 | 二者**不在**静默派生白名单 | `steps.py:14-18`（白名单仅 `dev-setup/develop/review/verify/release`） |
| 6 | 运行期派生只填字面量 `Project ID`，并**明确拒绝**把容器 id 填进 `Projects`（语义正确：容器 id ≠ 服务名） | `fields.py:170-172`、`fields.py:157-162` |
| 7 | **P57 交互契约实际未生效**：单候选自动采纳只匹配字面量 `Branch`，而两个工作流的字段名是 `Branch Mapping` / `Base Branch` | `fields.py:235-243`（注释自称 "code-review 交互契约"） |
| 8 | **容器已记录服务与各自分支**：`workspace.yaml` 的 `repository.available[].dev_branch`（抽样 6 个容器：1–4 个服务，**每服务一条分支**） | `workspaces/*/workspace.yaml`；读取逻辑 `providers.container_services`、`providers.branch_candidates` |
| 9 | 交互成本：`code-review` ≈ **9 次**交互（1 项目 + 1 必填 + 5 可选 + 1 输出 + 1 确认）；`change-impact` 同为 ≈9 | 字段层计数（`_fields_for` + 状态机） |

### 1.3 语义澄清（本提案不破坏的一点）

`Projects`（**服务名**，用于定位仓库）与 `Project ID`（**容器 id**，workspaces 目录名）是**两类值**。
`fields.py:157-162` 拒绝把容器 id 填入服务名字段是**正确的**。本提案不推翻该规则，而是补上
「**从容器映射推导服务名**」这条缺失路径。

## 2. Root-Cause

1. **派生规则绑定在字面量字段名上**（`Project ID`/`Workspace ID`/`Branch`），字段名一换即失效
   → 造成 P57 契约对 `Branch Mapping`/`Base Branch` 静默失配（#7）。
2. **缺少"由容器唯一确定"的派生路径**：容器已记录「参与服务 + 每服务分支」（#8），但没有代码把它
   用于 `Projects` / 分支字段的预填。
3. **必填标记阻断跳过**（#4）→ 即使候选只有一个，也必须走一次菜单；`Projects` 更是必填。
4. 二者不在静默派生白名单（#5），且 `change-impact` 的 `Code Reference` 属**真实必填**，
   不应为静默化而降级 → 不能靠"整体静默"解决。

## 3. Options

### 3.1 Option A — 容器唯一确定时派生（**推荐**）

在目标选定后新增一条**通用**规则：凡字段值可由已选容器**唯一确定**者，预填并移出提问列表：

- `Projects` ← 容器映射服务，**当且仅当恰好 1 个**（多服务仍问，属真实选择）；
- 分支字段 ← 已解析服务的 `dev_branch`，**当且仅当容器给出唯一候选**；
- 把「单候选自动采纳」从字面量 `Branch` **泛化**到分支类字段名（`Branch` / `Branch Mapping` /
  分支别名），即真正落实 P57 契约。

优点：**只在无歧义时静默**（不引入猜测）；通用（对所有 workflow/命令生效）；改动小、可逆。

### 3.2 Option B — 把二者加入静默派生白名单

需把必填字段降级：`code-review` 的 `Projects` 可（配合 A）降为可推导；但
`change-impact` 的 `Code Reference`（要分析哪段代码）**不应**降级 → 只能部分适用，且改动面更大。

### 3.3 Option C — 多服务容器：默认全选（减少摩擦，保留选择）

多服务容器的 `Projects` 多选菜单**预勾选容器内全部服务**（Enter 即接受），而非空菜单起步。
用户仍可取消勾选。适用于「审整个变更」的常见意图。

### 3.4 Option D — 抑制"有 frontmatter 默认值"的可选字段提问（**暂缓**）

理论上可让 `Base Branch`（默认 `master`）、`Review Focus`（默认「全面审查」）等不再提问、
仅在 recap 中展示。但这是**全局交互语义变更**（影响所有工作流、可能隐藏用户想改的字段），
建议单独立项评估，不在本提案内实施。

## 4. Recommendation

**A + C 一并实施**（均为"无歧义即推导 / 有歧义给默认值"的安全改进），
**D 暂缓**（单独立项），**B 不采用**（`Code Reference` 不应降级）。

预期效果（`code-review`，单服务容器）：交互 **9 → 约 3**（项目 → recap 确认 → 输出/启动），
且 `Projects`/分支不再二次追问；多服务容器：`Projects` 从"空菜单必选"变为"预勾选全部，Enter 通过"。

## 5. Proposed Changes

| # | 文件 | 变更 |
|---|---|---|
| 1 | `cli/services/wizard/steps.py` | 目标选定后的预填块：增加「容器唯一确定」派生（`Projects` 单服务、分支唯一候选），并把派生字段移出提问列表；保持其余流程不变 |
| 2 | `cli/services/wizard/fields.py` | ① 单候选自动采纳由字面量 `Branch` **泛化为分支类字段名**；② 新增「按服务解析容器分支」的取值辅助（复用 `providers.branch_candidates`） |
| 3 | `cli/services/providers.py` | 如缺：补「按服务取容器分支」的读取辅助（以 `workspace.yaml` `dev_branch` 为准） |
| 4 | 多选默认值（Option C） | `Projects` 多选的默认勾选 = 容器映射服务集合（无映射时保持现状） |
| 5 | 测试 | `cli/tests/`：单服务容器静默派生、多服务容器预勾选、无映射回退追问、分支唯一候选采纳、**字段名泛化回归**（防 P57 失配重演） |

**不改**：`workflows/code-review.md` / `change-impact.md` 的 frontmatter 必填语义（`Code Reference` 保持必填）；
`fields.py:157-162` 的"容器 id 不得填入服务名字段"规则。

## 6. Validation Plan

| # | 场景 | 期望 |
|---|---|---|
| a | 单服务容器 + `code-review` | `Projects` 与分支字段**不再提问**；derived 值出现在 header/recap |
| b | 4 服务容器 + `code-review` | `Projects` 预勾选全部（Enter 通过）；分支按所选服务解析；多选≠1 时**不**静默派生 |
| c | 容器无 `repository.available` 映射 | 回退现状（正常追问），不报错、不空值通过 |
| d | `change-impact` | `Projects` 同上；`Code Reference` **仍需询问**（真实必填） |
| e | 回归 | 既有 `develop/review/verify/release/dev-setup` 静默派生路径不变；扫描 104 组合**无交互死循环**；`check.py`/`repo-lint`/`path-audit`/`workflow-command-audit` 全绿；单测全绿 |
| f | 防复发 | 新增测试断言"字段名泛化"生效（P57 失配形态作为反例） |

## 7. Risks

| 风险 | 缓解 |
|---|---|
| 静默使用了错误的服务/分支 | **仅在唯一确定时**派生；derived 值在 header 与 recap 中可见；recap 提供「逐项修改」回退 |
| 多服务容器预勾选全部导致误审范围扩大 | 默认值可见且可取消；recap 明示；如需严格，可改为"预勾选首个 + 全选提示"（实施时确认） |
| 与 P38 静默派生白名单语义冲突 | 二者互补：白名单是"整体静默"，本提案是"字段级无歧义派生"；不修改白名单集合 |
| `Projects` 语义再次被混淆为容器 id | 保留 `fields.py:157-162` 规则；派生来源是 `container_services`（服务名），非容器 id |
| 字段名继续漂移导致规则再次失配 | 泛化为**类别匹配**而非字面量；并加防复发测试（Validation f） |
| 影响面广（wizard 核心） | 变更限于"预填 + 单候选采纳"两处；全量 dry-run 与 104 组合扫描作为回归门 |

---

## Review Log

| Reviewer | Decision | Date |
|---|---|---|
| User (AI Maintainer operator) | **Pending**（用户于 2026-09-21 反馈问题并提出期望行为） | 2026-09-21 |