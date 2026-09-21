# Change Proposal: P61 — 外部盲检纳入运维形式（External Blind Review as a Maintenance Form）

| Field | Value |
|---|---|
| Status | **Implemented** |
| Type | Structural (new workflow + capability + maintenance form) |
| Author | AI Maintainer |
| Created | 2026-09-21 |
| Reference | `reports/EXTERNAL-BLIND-REVIEW-2026-09-21.md`（持久记录；本次运行原始产出未入库）+ 用户指示"将外部评审作为一种运维形式" |
| Process | OPERATIONS §12 Change Management |

---

## 1. Problem

### 1.1 内部视角存在系统性盲区（本次已实证）

2026-09-21 做了一次**外部盲检**：把 ai-system 制品按层拆包（文档层 / cli / tools+config / skills，
合计 368 文件 ≈ 599k tokens），交给**两个跨厂商模型**独立评审（`qwen3.8-max`、`glm-5.3`，
各自全新会话、互不共享上下文），随后逐条核实。结果：

| 指标 | 值 |
|---|---|
| 产出 | 2 评委 × 4 包 = **8 份评审**（每包 136k–176k tokens） |
| 发现 | **241 条**（4 BLOCKER / 54 ERROR / 135 WARN / 48 INFO） |
| 抽检精度 | **≈ 91%**（11 条抽检命中 10；误读 1 条为文案歧义，反而促成改写） |
| 已修复真实缺陷 | **11 项**（`5da9f1c` `e30113e` `f8c984a` `87b673a` `1eafe15` `7fb5c50` `c5cc848`） |
| 成本 | **0**（走已有 `qwen-token-plan-cn` 套餐）；机器时间 ≈ 45 分钟 |

其中**最刺眼的一点**：这些问题**全部逃过了现有全部门禁**，因为它们正是"门禁自己失效"类
（5 个静默不执行的测试、失效的豁免正则、采集不到 BLOCKER 的健康检查、fail-open 的注册表校验、
漏检 `rm -rf /` 的安全守卫）——内部门禁与作者同源，无法自我发现。

### 1.2 能力缺口：只有"入站闸门"，没有"出站流程"

- 既有 `templates/prompts/external-ai-review.md` 只解决**入站**：外部结论如何被逐条裁决
  （KEEP/REVISE/REJECT/UNVERIFIABLE）——它**不负责**发起一次外部评审。
- **没有工作流/命令**描述"如何发起盲检"（选哪些层、如何脱敏、如何隔离运行、用哪些模型、
  结果放哪、如何采信）。
- **资产易失**：本次的投喂包生成器与运行手册只产于 `temp/`（按约定不提交），协议经验未入库；
  评审原始产出（8 份 + 索引）亦不入库 —— 需持久化的应入 `tools/` `templates/prompts/` `docs/`，
  而非留在不入库区（`outputs/` 引用也不受 `path-audit` 审计）。
- **无节奏**：完全依赖临时起意，`OPERATIONS §9` 的维护形式（weekly/monthly/quarterly）里没有它。

### 1.3 隐性知识未落规范

盲检卫生是本次踩出来的隐性知识，目前只存在于一次性会话里：

1. **身份脱敏**——包内不得含仓库远端地址/机器用户名（否则外部模型可联网检索到该仓库，
   盲检直接失效；本次确实在 A 包中发现 `github.com:Syske/ai-system`）。
2. **排除内部产物**——`reports/` `logs/` `metrics/` 会锚定评审（本次全部排除）。
3. **运行隔离**——必须在空目录 + `-nt -nc -ne -ns -np --no-session` 跑（否则 agent 带工作区上下文）。
4. **模型独立性**——评委不得与本制品作者模型同族（作者模型为 DeepSeek 系 → 评委禁用 DeepSeek）。
5. **单侧发现必须落位核实**——实测交叉评委 glm-5.3 会**改写文件路径**（`cli/services/keys.py`
   实为 `cli/utils/menu/keys.py`），但其"实质"多为真；故证据列不可直接引用。
6. **坏形状重跑**——大包评审偶发 14 秒返回"文本形式工具调用"，判据：耗时 < 1 分钟或含
   `<tool_call>` → 失败重跑；且单包 6–13 分钟，须后台 + 硬超时执行。

## 2. Root-Cause

1. 架构上**只有入站闸门**（`external-ai-review` 属 Operating-Rules/Standards 侧的采信规则），
   缺少**出站工作流**（Workflow 层：定义"做什么"）。
2. 维护体系把"独立评审"视为一次性活动，未登记为维护形式，故无节奏、无资产归属、无验收口径。
3. 盲检的**方法学**（脱敏/隔离/独立性/采信）未被当作标准来写，只存在于实践者记忆里。

## 3. Options

| 选项 | 说明 | 成本 | 评价 |
|---|---|---|---|
| A. 维持临时（状态保持） | 需要时才做 | 0 | 本次的经验与资产会丢失；节奏缺失 → 实际不会发生 |
| **B. 新工作流 + 命令（`aic-external-review`）** | Workflow + Runtime + Prompts + Tool + 薄命令 + 注册三件套 | 中（约 6 个新文件 + 3 处注册） | 能力完整、按需可发起；但若不入维护节奏仍可能被遗忘 |
| **C. 折入 `aic-maintain` 作为 Mode/Scope** | `--mode blind` 或 `Scope=external-review` | 低（改 1 个命令 + 2 个 runtime 模板 + OPERATIONS） | 有节奏；但"独立评审"逻辑塞进维护命令会使其继续膨胀（该命令已有瘦身历史） |
| **D. B + C 组合（推荐）** | 独立命令（随时可发起）+ 维护体系登记形式与节奏（季度 + 重大变更后） | 中 | 能力独立、节奏有保障、职责不混（维护命令只引用，不内联实现） |
| E. 每次 release 都盲检 | 挂在主链 release 后 | 中 | 噪声与成本过高（release 频繁），且与 release 目标（发布）冲突 |

## 4. Recommendation

**采纳 D**。架构落点（对齐 AGENTS.md 分层与"新能力落在最低可能层"原则）：

| 层 | 落点 | 内容 |
|---|---|---|
| **Workflow**（what） | `workflows/external-review.md` | 八段契约：分层打包 → 交叉盲检 → 逐条核实 → 闸门采信 |
| **Runtime**（how） | `templates/runtime/runtime-external-review.md` | 执行生命周期：包制备 / 隔离运行 / 形状校验 / 交叉比对 / 落盘 |
| **Standards/Operating Rules** | `templates/prompts/external-blind-review.md`（提示词）+ OPERATIONS §9 一行 | 盲检纪律 + 维护形式与节奏 |
| **Skills/Tools** | `tools/blind-bundle.py` | 脱敏 + 分域打包（幂等） |
| **Command** | `cli/commands/aic-external-review.md` | 薄命令：选层/选模型/起停/汇总 |
| **注册** | `config/workflows/<name>.yaml` + `workflow-registry.yaml` + `menu.yaml` | 与既有命令一致 |

**价值定位（明确边界）**：外部盲检是**补充独立视角**，**不替代**内部门禁与评审；它的产出与
任何外部结论一样是**未验证输入**，必须逐条核实并过 `external-ai-review.md` 闸门。
节奏建议：**每季度至少一次**（并入 `OPERATIONS §9` 季度集）+ **重大结构变更后按需触发**。

## 5. Proposed Changes

1. **新增工作流**：`workflows/external-review.md`（Purpose/Runtime/Preconditions/Inputs/Context/
   Outputs/Exit Criteria/Next 八段齐全，与 `workflows/README.md` 选择表术语一致）
2. **新增 runtime**：`templates/runtime/runtime-external-review.md`
   （阶段：Bundle → Isolated Run → Shape Check → Cross-Compare → Verify → Gate → Report）
3. **新增命令**：`cli/commands/aic-external-review.md`（thin；Steps 英文、用户可见文本中文）
4. **注册**：`config/workflows/external-review.yaml`（name/workflow/runtime，保持注册表最小）
   + `config/workflow-registry.yaml` + `config/menu.yaml`（默认 `hidden_commands`，AI 按需触发）
5. **提升工具**：运行期包生成器（产于 `temp/`，未入库）→ 提升为 `tools/blind-bundle.py`
   - 分域（doc / cli / tools+config / skills）、排除清单（reports/logs/metrics/workspaces/archived/二进制）、
     **身份脱敏**（远端地址、机器用户名 → 占位符）、Manifest + 目录树 + `FILE:` 分隔头
6. **提示词入库**：`templates/prompts/external-blind-review.md`（Pass A 文档层 / Pass B 代码层 /
   Pass C 交叉裁决三段 + 盲检纪律 + 输出格式 + 自评置信度）
7. **运行手册**：`docs/`（或 skill 内）— 含包体上限（<200K tokens/包）、`pi` 固定盲检开关、
   坏形状判据与重跑、后台 + 硬超时、模型选择与独立性要求、成本估算
8. **治理一处**：`OPERATIONS.md §9` 增列维护形式“外部盲检”（节奏：季度 + 重大变更后），
   并明确**产物分层**（关键：可索引的必须入库）：
   - **入库、可索引**：`reports/EXTERNAL-BLIND-REVIEW-<date>.md`（拣选后的持久报告，
     登记 `reports/README.md` “评估与评审报告”表）——外部结论进入系统历史的唯一载体
   - **不入库、不索引**：投喂包与运行期原始产出（8 份评审、索引、日志）留在运行期区
     按既有约定作为一次性产物；报告内**不得**写入指向这类未入库产物的路径引用
     （`outputs/` 不在 `path-audit` 审计范围，失效引用不会报 broken）
9. **采信纪律固化**（写入提示词/runtime Exit Criteria）：
   - 单侧发现必须**逐条落位核实**（评委可能改写路径）
   - 一律过 `external-ai-review.md`（KEEP/REVISE/REJECT/UNVERIFIABLE），**不得直接采纳**
   - 记录评委模型与版本（可复现性）；禁止使用与本制品作者同族的模型
10. 索引登记：`reports/PROPOSALS.md` + `reports/README.md`

## 6. Validation Plan

- **端到端演练已完成**（本次即事实上的验收）：两评委 4 包 × 2 = 8 份产出、241 条发现、
  11 项修复并全部通过门禁（346 单测 / check.py / repo-lint / path-audit / quick-check）。
- 正式化后按新命令再跑一次，断言：
  1. **包卫生 = 0 泄漏**：`grep` 校验包内无 `reports/|logs/|metrics/` 文件头、无远端地址/用户名
  2. **运行隔离**：`-nt -nc -ne -ns -np --no-session` + 空目录；每包独立会话
  3. **形状校验**：无 `<tool_call>` 且耗时 > 1 分钟（否则重跑）
  4. **注册闭合**：新命令通过 `checks/workflow.py`（注册表三件套）与八段契约校验
  5. **采信闸门**：产出全部经 `external-ai-review.md` 裁决后才可能入库
- 门禁：`check.py` / `repo-lint` / `path-audit` / `quick-check` 全绿、无新增 WARN

## 7. Risks

| 风险 | 缓解 |
|---|---|
| ① 外部模型幻觉 / 路径改写 | 强制逐条落位核实（本次已实证：glm 改写路径但实质为真）；证据列不可直接引用 |
| ② 包制备泄漏仓库身份或内部结论 | 脱敏与排除清单**门禁化**（打包后自动 grep 校验，非人工记忆） |
| ③ 成本随套餐变化（当前 0） | 记录单次 tokens 与成本；套餐失效时降级为"文档层单包 + 单评委"最小方案 |
| ④ 模型可用性/长上下文能力漂移 | 记录模型 id 与版本 + 快照；每季复核模型清单与上下文上限 |
| ⑤ 过度依赖外部评审、削弱内部门禁投入 | 定位写入规范：**补充**而非替代；本轮 11 项修复全部转化为**内部门禁/单测**（见 P60） |
| ⑥ 新工作流造成命令/注册面膨胀 | 命令保持 thin（引用文档）；注册表沿用最小字段；默认 `hidden_commands` 不进用户菜单 |

---

## Review Log

| Reviewer | Decision | Date |
|---|---|---|
| User (AI Maintainer operator) | **Approved**（按 D1–D4 推荐：组合形态 + 季度节奏 + 全套 6 件入库 + 盲检纪律升格为强制） | 2026-09-21 |

---

## Implementation Record (2026-09-21)

Applied per approval (OPERATIONS §12 → Implement → Validate)。

### 产物（6 件 + 3 处注册 + OPERATIONS）

| # | 落点 | 内容 |
|---|---|---|
| 1 | `workflows/external-review.md` | 八段契约 + front-matter（无必填输入、`outputs.base`=`reports/`）；盲检协议摘要与硬停条件 |
| 2 | `templates/runtime/runtime-external-review.md` | Phase 1–8（Scope/Judges → Bundle hygiene → 隔离运行 → 形状校验 → 跨模型对账 → 逐条核实 → 拣选报告 → 入站闸门）+ 执行纪律表 + Reflection/Completion |
| 3 | `cli/commands/aic-external-review.md` | thin 命令：步骤 + Output（两层落盘）+ Guardrails（只读、卫生即门禁、禁同族评委、外部结论未验证） |
| 4 | `tools/blind-bundle.py` | 分域打包（doc/cli/tools-config/skills）+ 排除清单 + **两级身份模型** + `--check` 卫生校验 + `--strict-name` |
| 5 | `templates/prompts/external-blind-review.md` | Pass A/B/C 三段（**2026-09-21 已验证过的原提示词**）+ 盲检纪律 8 条 + 形状校验 + 对账规则 |
| 6 | `OPERATIONS.md §9.4` | 维护形式"外部盲检"：季度 + 重大结构变更后；产物两层落盘 |
| 注册 | `config/workflows/external-review.yaml` · `config/workflow-registry.yaml` · `config/menu.yaml`（`hidden_commands` + `command_fields`） | 与既有命令一致；hidden = AI 按需触发，不进用户菜单 |

### 验证

- **包卫生（D4 门禁化）**：对 ai-system 自建 4 包（doc/cli/tools-config/skills，≈607k tokens）→ `--check` **PASS**
  （0 tier-A 身份泄漏 / 0 排除目录文件头 / 0 二进制）；`--strict-name` 下仓名出现即 **FAIL**（已实测）
- **注册闭合**：`check.py`（注册表 / frontmatter / 八段 / outputs 一致性 / 命令 / 菜单 / wizard dry-run）**PASS**；
  `workflow-command-audit` **0 blockers / 0 warnings**（16 workflows / 14 commands）
- **提示词前缀稳定**：`prompt-metrics` **16/16**
- **单测** 357 OK；`repo-lint` 28 WARN 无新增；`path-audit` 0 broken；`quick-check` OK；`proposal-audit` 0/0
- **端到端冒烟**：依文档化命令重建 doc 层包（136k tokens）+ 按隔离开关启动一次判官运行（后台），
  用于校验 Phase 3/4（隔离 + 形状校验）

### 实施中当场抓到的 4 个问题（都是本次新增机制报出来的）

1. **新卫生门禁抓到自己的假阳性**：裸仓库名 `ai-system` 在本制品内是**合法路径前缀**（doc 层出现 113 次）
   → 改为**两级身份模型**：Tier A（远端 URL / owner-repo / 主机 / 机器用户名 / 家目录）命中即阻断；
   Tier B（仓名）默认仅提示，`--strict-name` 可升为硬失败。
2. **`path-audit` 抓到文档里的"斜杠连写"**：如 `prose/specs/templates/loaders/governance` 被解析为路径
   → 3 处已改成逗号分隔（教训：散文里不要用 `dir/subdir` 串联枚举）。
3. **`prompt-metrics` 的同名覆盖缺陷**（本提案的 workflow/command 同名配对首次暴露）：工作流行被同名命令行静默覆盖
   → 行键改为 `kind:name`，并让稳定前缀的分母只统计工作流（修后 **16/16**）。
4. **workflow↔runtime Outputs 一致性**：`## Outputs` 段里的**散文 bullet** 被当作产物条目
   → 改为"纯列表 + 散文段落"，并在 runtime 增设 `## Output Placement` 承载落盘说明。

### 与提案文本的两处偏差（已记录）

1. **运行手册落点**：提案 §5.7 写 `docs/`（或 skill 内）；实施改为**并入 runtime 模板**
   （ai-system 无 `docs/` 目录；runtime 即"怎么做"的归属层，且避免新增未纳入审计的目录/孤儿文件）。
2. **命令注册形态**：提案写"默认 `hidden_commands`"；实施按 `menu.yaml` 自带说明补齐
   `hidden_commands` + `command_fields`（`check_wizard_dry_run` 会遍历所有命令）。