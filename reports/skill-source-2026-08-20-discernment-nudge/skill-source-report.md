# Skill 来源评估报告: anthropics/skills 的 discernment-nudge

- 日期 / Date: 2026-08-20
- 来源 / Source: https://github.com/anthropics/skills/blob/main/skills/discernment-nudge/SKILL.md
  （所属仓库 https://github.com/anthropics/skills，19 个 skills，Apache 2.0 / 部分 source-available，活跃维护）
- 评估目标 / Target: `discernment-nudge`（答后认知谦逊轻推）
- 报告名称 / Report Name: anthropics/skills/discernment-nudge
- 分类框架 / Framework: `reports/THIRD-PARTY-SKILL-ASSESSMENT-2026-08-01.md`
  （该框架 2026-08-01 曾评估同仓库 17 个 skills，全部判定为"无真实缺口"；
  `discernment-nudge` 与 `academy-guide` 为后来新增，本次评估新增项。）

---

## 一、创建前搜索（Step 0）

- 本地资产扫描（`skills/`, `governance/`, `templates/`, `workflows/`）：
  - grep `discern|epistemic|nudge|humility|humbl|overconfiden`：
    - `skills/` **零命中**；`templates/` 仅命中 `verify` 类流程校验，非用户面向轻推；
    - `governance/REFLECTION_RULES.md` 仅一处 `overconfidence`——其 5 轴自评（accuracy/
      completeness/clarity/actionability/conciseness）是**面向 AI 自身的内部复盘**，
      不是面向用户的答后追问。
  - 结论：**无本地接近匹配**。最接近的是 REFLECTION_RULES 的"证据先行/避免过度自信"
    纪律，但两者作用层不同——本 skill 是**用户可见的答后轻推**，属真实缺口。
- 远端搜索：GitHub 直连不可用（经 127.0.0.1:7897 Clash 代理克隆）；web 查询确认
  `discernment-nudge` 源于 Anthropic AI Fluency 4D 框架（Delegation/Description/
  Discernment/Diligence）的 **Discernment** 能力——评估 AI 产出的质量，与本 skill 描述一致。
  无第三方重复实现。

## 二、来源清单与统计

仓库 19 个 SKILL.md。与 2026-08-01 评估（17 个）比对：新增 **discernment-nudge**、
**academy-guide** 2 项；其余 17 项此前已评估。按参考价值分类：

| 价值 | 数量 | 清单 |
|---|---|---|
| 高价值（填补真实缺口，可直接吸收方法论） | 1 | **discernment-nudge**（答后认知谦逊轻推） |
| 中价值（方法论可借鉴） | 1 | skill-creator 的"描述触发率测量→优化"（沿用 08-01 既有借鉴点，未变化） |
| 低/无价值 | 17 | 其余 17 项（08-01 已评估） + academy-guide（新增，平台特定） |

## 三、discernment-nudge 评估（高价值候选，vetting）

### 3.1 内容审读

- 前 12 行描述即触发规则：给出**用户可能据以行动**的实质性回答（建议/草稿/估算/分析/
  事实性断言/多步论证）时，在收尾前追加 2-3 条**针对答案具体内容**的追问，引导用户
  核查事实、质疑推理、觉察缺失上下文；**每会话至多一次**；并列出完整豁免情形。
- 方法内核（AI Fluency Discernment）：
  1. **Check facts** — 答案中哪些具体断言值得核实、向谁核实；
  2. **Question reasoning** — 逻辑在哪一步值得被追问依据；
  3. **Notice missing context** — 答案因用户未说明而不得不假设了什么。
- 边界清单（When not to）：创意写作/闲聊/可运行代码/简单查询/纯教学解释，以及四类
  "用户已表明不需要"（已要求核实引用、只要快速版、让我检查你的东西、给了素材只求整理）
  和"求观点"——全部明确豁免，防止轻推变成说教（paternalistic）。
- 输出格式：答案先完整给出，空行后以固定引导行 `A few things worth a second look:`
  + 纯文本 bullet，每条 <120 字符、第一人称、可直接回问；无 HTML/标题/emoji；不追加任何尾句。
- 与 08-01 已吸收资产的协同：本 skill 与 `grilling`（设计决策压力测试，用户主动发起）
  **互补不重叠**——grilling 是"实现前压测设计"，本 skill 是"答后轻推反思"，触发时机
  与作用对象不同；与 REFLECTION_RULES 5 轴自评（AI 内部）**分层**——本 skill 作用在
  **用户可见的输出层**。

### 3.2 危险行为扫描

- SKILL.md + LICENSE.txt 共 2 个文件：**无脚本、无 shell 命令、无文件写入、无网络调用、
  无凭据处理、无包安装**。纯提示词方法论，平台无关（不依赖 Claude Code 子进程/API）。
- 维护度：仓库活跃（HEAD 0a64e39，2026-08-18 提交，距今 2 天）；官方 Anthropic 维护。
- 排序：单候选（< 10 上限），description 匹配度高，来源权威且维护。

## 四、可借鉴项（中价值，默认不吸收）

| skill | 借鉴点 | 未吸收原因 |
|---|---|---|
| skill-creator（沿用 08-01 结论） | 描述触发率测量→优化（improve_description.py 基于 eval 结果迭代描述） | 依赖 Claude 平台（`claude -p` 子进程）；本地已有 skill-author / skill-optimizer / skill-benchmark-generator 系列，触发率量化机制缺失，触发条件未到（见第七节） |

## 五、不吸收项及原因（17 项）

| 类别 | 项 | 原因 |
|---|---|---|
| 文档/办公文件 | docx, pdf, pptx, xlsx, doc-coauthoring | 文件格式处理（docx-js/openpyxl/pypdf），技术栈特定，08-01 已判定 |
| 设计/视觉 | frontend-design, canvas-design, theme-factory, algorithmic-art, brand-guidelines | UI/视觉设计，非治理领域，08-01 已判定 |
| Claude 平台/生态 | claude-api, academy-guide（新增） | Anthropic SDK / Claude Academy 学习中心引流，平台绑定 |
| MCP 集成 | mcp-builder | MCP 服务构建，非 ai-system 治理资产 |
| 工程工具 | webapp-testing, internal-comms, slack-gif-creator, web-artifacts-builder | 通用工具（Playwright/内部通讯/GIF），与治理无关 |
| skill 生态 | skill-creator（本体） | eval 循环与 skill-optimizer/author/benchmark 系列重叠，且依赖 `claude -p`（仅借鉴"描述触发率优化"一点） |

## 六、后续触发条件（Evolution Principle：不预先引入）

| 项 | 触发条件 |
|---|---|
| discernment-nudge 吸收 | **本次用户决策**（直接吸收 / 派生扩展 / 新建）。吸收时按 skill-policy 以原生资产重写，落到 `skills/` 或 governance 输出层约定。 |
| 描述触发率量化测量（skill-creator 借鉴点） | 若出现"skill 描述触发不准确"真实问题，且需量化测量时，与 skill-benchmark-generator 整合评估。 |
| 本地是否需要"答案质量轻推"落地载体 | 若确认吸收，落点候选：独立 `skills/discernment-nudge/`（原生重写）或并入现有对话规范。 |

## 七、吸收决策选项（等待用户确认，本报告不执行吸收）

| 选项 | 含义 | 对 discernment-nudge 的建议 |
|---|---|---|
| 直接吸收 | 按匹配 skill 原样吸收（重写为原生资产） | 重写为 `skills/discernment-nudge/`：保留触发/边界/格式内核，按 skill-policy 原生化；零脚本零依赖，落地成本低 |
| 派生扩展 | 复制最接近的本地 skill 修改之 | 以 REFLECTION_RULES 5 轴自评 + AI_OPERATING_RULES "不隐藏不确定性" 为底，扩展出"用户面向答后轻推"一节 |
| 新建 | 确认无接近匹配后全新构建 | 已确认无本地接近匹配；仅当团队认为答案层轻推不适用当前运行模式时选择 |

## 八、最终决策记录（2026-08-20 用户确认）

**决策（初）：暂不吸收**。评估结论（高价值、填补真实缺口、零依赖、官方维护）已记录，
但按 Evolution Principle 不预先引入。

**决策（重新评估，2026-08-20）：纪律化吸收（非 skill 形态）**。
用户重新评估后选择以**规则**形态落地，而非新建 on-demand skill，理由：
1) 轻推是「每个实质性回答的默认行为」而非「按需任务」→ skill 容器错配；
2) 零新资产（Value-Burden 最净）；
3) 与 gate function / P3 外部结论核查同源同层（验证纪律的用户可见输出层），应并入同一规则文件。

**落地**：`governance/AI_OPERATING_RULES.md` 增「Answer-Layer Nudge（答后核查提示）」一节
（Validation/gate 之后），保留：触发（实质性可行动答案）/ 每会话至多一次 /
固定引导 `A few things worth a second look:` + 2-3 条具体短问（查事实/质疑推理/觉察缺失上下文）/
完整豁免清单（防说教）。不新建 skill，不引入脚本/依赖。

本报告保留为评估依据；吸收形态=纪律化规则（非 skill）。

---

## 附：仓库新增项速览

- `academy-guide`（新增，2026-08-18 由 claude-academy-guide 更名）：Claude 产品/学院内容
  引流，平台特定 → 不吸收。
- `skill-creator`（描述更新，新增 eval-viewer/generate_review.py 等）：评估体系加深，仍依赖
  Claude 平台 → 维持 08-01 借鉴点结论。