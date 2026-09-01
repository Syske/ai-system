# Change Proposal: P45 — 运行时语言门禁（completion-time language gate，方案 B 正式化）

| Field | Value |
|---|---|
| Status | **Implemented** |
| Type | Structural（运行时机制，多文件 + 新工具） |
| Author | AI Maintainer |
| Created | 2026-09-01 |
| Reference | 13:54 语言边界专项延后项（方案 B「运行时通用机制」待 pilot 结论）；L1 语言声明优化（2026-09-01，强度统一为 MUST 但无执行层）；Big Pickle（OpenCode Zen Stealth 模型）弱语言跟随导致报告不按约定输出中文；孤儿改动 templates/runtime/runtime-base.md（完成报告按系统语言声明，未提交/未走 §11）；dev-setup-20260901-102222 L1 记录（完成报告误用英文） |
| Process | OPERATIONS §12 Change Management |

---

## 1. Problem（现状问题 / 缺口）

语言规则已在上轮 L1 升级为 **MUST 级**（LANGUAGE_CONVENTION v1.1、AI_OPERATING_RULES §Language Boundary），但**所有保证仍然依赖模型遵循提示词**：

- `repo-lint.py check_language` 只做**静态仓库文件**检查（命令 Steps 英文 / py 注释中文 / governance 英文），**不覆盖运行时生成的报告**。
- LANGUAGE_CONVENTION 的 completion-time self-check 是**自报式**（靠 AI 自觉），无工具、无门禁、失败无记录。
- 实证：Big Pickle（英文主导 + 语言跟随不稳定的 Stealth 模型）直接产出英文报告且无任何环节拦截；此前 dev-setup 也发生过同类偏差（L1 记录）。

结论：语言规则存在「声明层完备、执行层缺失」的结构性缺口——对语言跟随弱的模型，MUST 形同虚设。

## 2. Root-Cause（根因分析）

语言保障缺「执行层」：现有架构只有两环——(a) 声明（约定/总纲/命令/模板，全部进提示词，靠模型遵守）；(b) 静态检查（repo-lint，只管仓库不管运行时产物）。**运行时产物（报告/交互提示）没有校验/门禁环节**——模型生成什么就直接呈现什么。13:54 定论「执行层未按 system language 转换」正是此缺口的早期症状；L1 只治了声明层。

## 3. Options（至少两方案对比）

| 选项 | 含义 | 评估 |
|---|---|---|
| **A. 完成时语言门禁（Recommended）** | Runtime Complete 阶段加入语言自检步骤 + 轻量检测工具 `tools/language-gate.py`（输入报告文本 → 判定语言 == locale → PASS/WARN/FAIL）；FAIL → 自动重写或 WARN+diag log 记录；rules 纳入 LANGUAGE_CONVENTION 与 AI_OPERATING_RULES 引用 | 机制级最小实现：一个工具 + 运行时模板步骤 + 文档引用；不依赖模型自觉；可先试点再全量 |
| B. 渲染层强制转换 | prompt_builder / menu_config 在渲染时强制注入固定段（菜单已按 locale 渲染，双语标题可由渲染层注入） | 只能保证**固定段**语言；**报告正文**是模型生成的，渲染层无法翻译/校验，仍漏掉正文——只能作 A 的补充，不能替代 |
| C. 引入外部翻译/校验服务 | 调用第三方语言服务校验/翻译报告 | 负担大（外部依赖 + 成本 + 隐私），当前仅一台机器一个模型触发，收益未到 |
| D. 维持现状（仅声明 + 自报式 self-check） | 不动 | 已证伪：Big Pickle 事件证明软约束可被穿透，问题会复现 |

## 4. Recommendation（推荐方案 + 理由）

**方案 A**（B 的固定段注入作为 A 的可选补充项，不单独立项）。理由：

1. **直击根因**：补上「运行时产物校验」这一缺失环节，与 L1 声明确认形成「声明 → 校验 → 纠正」闭环。
2. **模型无关**：门禁是启发式工具（语言占比判定），不依赖任何模型的语言跟随能力——Big Pickle 类模型也被兜住。
3. **Evolution Principle**：由真实事件驱动（今日 Big Pickle 报告英文 + 13:54 定论 + 多点复现），非投机。
4. **轻量可回退**：门禁默认 WARN 级先行（误报容忍），自动重写为配置开关；试点链验证后再放量。
5. 顺势解决孤儿改动 `templates/runtime/runtime-base.md`：其内容（完成报告按系统语言 + 双语标题）正是方案 A 的运行时声明部分，作为 Phase 1 并入（无论此前 B 决策选择 B1 保留还是 B2 回退，Phase 1 都会以正式形态引入并提交）。

## 5. Proposed Changes（具体改动清单，待批准实施）

> 仅记录提案，不直接修改；批准后按 OPERATIONS §12 Implement 阶段执行。

1. **runtime-base.md**：Complete 阶段新增「语言自检」子步骤——生成 Completion Report 后以系统语言（`config/menu.yaml → locale`）校验面向用户文本，FAIL → 重写或记录（并入孤儿改动的完成报告声明，统一提交）。
2. **新工具 `tools/language-gate.py`**（轻量启发式，~100 行）：输入报告文本（文件或 stdin）→ 输出三态判定：
   - `locale=zh` 时：面向用户正文 CJK 占比 < 阈值 → FAIL；含双语标题/技术标识符（白名单模式，如 `## 实现总结 / Implementation Summary`）→ 不误判；
   - 支持 `--check`（供运行时调用）、`--list-suspicious`（人审）。
3. **check.py 注册**（可选集成）：不强制——门禁面向运行时产物（logs/报告），不面向仓库静态文件；仅登记 README 工具清单。
4. **LANGUAGE_CONVENTION v1.2 + AI_OPERATING_RULES**：self-check 从「自报式」升级为「运行门禁」——完成时运行语言门禁工具，FAIL → 自动重写（或 WARN + diag log 记录）；引用 `tools/language-gate.py`。
5. **试点链**：maintain + develop 两条链试点 1 个维护周期（含 Big Pickle 会话复测），评估误报率（目标 < 5% 且可解释）后全量铺开。

## 6. Validation Plan（如何验证）

- 单元验证：构造 3 类样例（纯中文报告 → PASS；纯英文报告 → FAIL；双语标题 + 技术标识符混合 → PASS/WARN 不误报）。
- 试点回归：用 Big Pickle 跑一次 maintain，门禁应 FAIL → 触发重写 → 交付中文报告（复现 #24800 类场景的相反方向）。
- 全量门禁：`python3 tools/check.py` / `repo-lint.py` / `path-audit.py` / `unittest cli/tests` 全绿。
- 历史回归：对近 3 份 MAINTENANCE 报告跑门禁，应全部 PASS/WARN 可解释（不新增红线）。
- proposal-audit：P45 登记一致、无新增 ERROR/WARN。

## 7. Risks（风险与缓解）

| 风险 | 缓解 |
|---|---|
| 启发式误报（英文技术标识符被当正文） | 阈值容忍 + 黑/白名单（bilingual headings、路径、命令名）；`--list-suspicious` 供人审面上报 |
| 自动重写引入延迟/不收敛 | 默认 WARN 级（仅记录 + 提示重写），自动重写为开关；试点期不开 |
| 双语标题约定（含英文）被误判为 FAIL | 白名单直接命中该固定模式 |
| 与 L1 声明重复/冲突 | P45 引用 v1.1 声明，仅新增执行层，不重写声明 |
| 试点误报率超预期 | 终止试点、回调阈值，回归纯声明态（方案 D 兜底） |

---

## Review Log

| Reviewer | Decision | Date |
|---|---|---|
| User (AI Maintainer operator) | **Approved**（2026-09-01 会话授权「开始实施」；孤儿改动选 B3 并入 Phase 1） | 2026-09-01 |

## Implementation Record (2026-09-01)

Applied per approval (OPERATIONS §12 → Implement → Validate):

**Phase 1（runtime 声明 + 孤儿改动 B3 并入）**
- `templates/runtime/runtime-base.md`：Complete 阶段语言自检步骤（先合并此前孤儿改动
  「完成报告按系统语言 + 双语标题」，再扩展为 PASS/WARN/FAIL 三步闭环 + 结果记入
diag log）——孤儿改动正式化落地，B3 闭环。

**Phase 2（工具）**
- 新增 `tools/language-gate.py`（~150 行，启发式）：locale 取 config/menu.yaml →
  locale（--locale 可覆盖）；去掉代码块/双语标题白名单/表格分隔线后统计 CJK 占比；
  zh：≥20% PASS / <10% FAIL / 之间 WARN；exit 0/1/2；--list-suspicious 人审。

**Phase 3（工具登记）**
- `tools/README.md`：语言门禁行登记。

**Phase 4（约定升级）**
- `governance/LANGUAGE_CONVENTION.md` v1.1→v1.2：self-check 自报式→运行门禁（呈现前跑
  gate，FAIL→重写再呈现）；Changelog 补记。
- `governance/AI_OPERATING_RULES.md` v1.5→v1.6：Language Boundary 节引用运行时语言门禁
  （governance 层保持全英文，Rule 3 复查 0 新增）。

**Phase 5（试点接入 + 回归）**
- `cli/commands/aic-maintain.md`：Step 4 报告呈现前显式跑 gate（maintain 试点链）。
- 单元样例：纯中文→PASS(0.65)；纯英文→FAIL(0.00, exit 2)；双语标题+技术标识符混合
  →WARN(0.19，可解释)。
- 历史回归：5 份真实文档（08-31/09-01/09-01-logs 维护报告 + P45 提案 + diag log）
  全部 PASS（CJK 占比 0.28-0.56）→ 阈值 0.20/0.10 无历史误报。

**Validation（全量 gate，证据）**:
- `python3 tools/repo-lint.py --repo-root .` → 0 BLOCKER / 0 ERROR / 25 WARN（与基线持平；
  implement 期间临时 26 WARN 为 AI_OPERATING_RULES 混入中文字样，已修复归位）
- `python3 tools/path-audit.py` → OK（工具路径引用闭环：language-gate.py 已存在）
- `python3 tools/check.py` → PASS 3 提示性 WARN（thin-command / 开放提案 6 / action items 4）
- `python3 -m unittest discover -s cli/tests` → Ran 164 tests, **OK**
- `python3 tools/quick-check.py` → OK 0 findings

试点结论（Phase 5 数据）：维护报告类文档 CJK 占比 ≥0.28，门禁阈值留出 ≥8pt 裕度，
误报风险低；Big Pickle 复测待其会话出现（门禁对 0.00 英文报告必 FAIL）。

**R1 补丁（2026-09-01，运行日志核查驱动）**：
- 缺陷：language-gate 步骤写在 runtime-base.md，但 `Extends:` 为文档声明无加载器合并，
  prompt_builder 骨架化只处理 runtime-<name>.md → base 机制对 AI 不可见（develop/prepare
  日志实读清单均无 runtime-base.md）→ 试点链门禁指令实际不生效。
- 修复：`prompt_builder._merge_runtime_base` 解析 `Extends:` 引用、把 base 全文并入骨架化输入
  （base 的 @keep 行自然进入骨架，非 @keep 内容仍被骨架逻辑丢弃，不增体积）；base 语言门禁段
  压缩为单行 `<!-- @keep -->` 标注。
- 单测：test_runtime_skeleton_merges_base_keep（回归保护，unittest 164→165 OK）。
- 验证：develop 骨架实测含 language-gate 步骤；repo-lint 0/0/25、path OK、check PASS 3、
  quick-check OK。