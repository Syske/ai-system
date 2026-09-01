# 系统巡检报告 — 2026-09-01（on-demand / workflows）

- 类型: 系统巡检（MAINTENANCE）
- 模式: on-demand
- Scope: workflows（语言边界专项试点）
- 日期: 2026-09-01

---

## 一、工具校验结果（自动生成，AI 核对补充说明）

| quick-check | verdict **OK**（findings 0） |
| lint | Skills: 30 | Files: 30 | BLOCKERS: 0 | ERRORS: 0 | WARNINGS: 25 |
| path | OK: no broken path dependencies |
| extensions | Summary: 0 errors, 0 warnings |

### 指标对比（自动生成，需 AI 核对变化原因）

- 指标快照 maintain-{date}.json 缺失

---

## 二、巡检发现（AI 填写，按严重度分级）

<!-- 高 / 中 / 低 / 信息 -->

### 信息（I）— 语言边界专项发现（本会话 Scope）

- **I1（本会话根因）**：dev-setup / maintain 交互提示呈英文，**不是配置回退**——`config/menu.yaml` locale 仍 `zh`，`config/i18n/zh.yaml` 中文文案在（git working tree 干净验证）。根因指向**执行层未按「system language = zh」规则把英文控制流转成中文交互提示**。
  - 机制证据：`templates/runtime/runtime-dev-setup.md:130` 等模板明确写 "Present the prompt in the system language (config/menu.yaml → locale)"，但模板正文本身是英文控制流；交互语言由执行时 AI 是否遵守该指令决定。
  - maintain **无独立 runtime 模板**（templates/runtime/ 无 runtime-maintain.md），交互直接由 `aic-maintain.md` 正文驱动的执行生成，且该命令此前**无任何「以系统语言呈现交互」的显式约束** → 最易漏转换。
- **I2（试点 A 已落地并通过自测）**：在 `cli/commands/aic-maintain.md` 正文开头追加「Interaction language (mandatory)」约束（交互提示须用 system language=zh；控制流保持英文）。自测通过：`PromptBuilder.build('maintain')` 渲染的 prompt 中已含该约束，且 `config/menu.yaml` locale 仍 zh、模板英文控制流零改动。
- **I3（实测通过）**：在一次真实 maintain 交互中，Mode/Scope 选择的提问与选项描述以中文呈现，符合试点 A 约束。

### 语言规范符合性（默认保留）

- AI 控制流（runtime/workflow 模板正文）保持英文——符合 LANGUAGE_CONVENTION 与 coding-memory `language-boundary.md` 三层边界。
- 用户报告 / 交互提示应中文（按 locale）；本次试点仅约束 maintain 一条命令。

### 已知 warning（存量，非本次引入）

- repo-lint: 25 WARN（语言债清单存量，见 MAINTENANCE-2026-08-08-language-lint-debt.md）。
- workflow-command-audit: [WARN] aic-maintain.md 127 行（thin-command gate，本次追加 3 行后略超阈值，提示性）。

---

## 三、一致性抽查结论（AI 填写，逐项通过/失败）

本会话为语言边界专项（Scope=workflows），执行了与改动相关的抽查：

| 项 | 结果 |
|---|---|
| 语言规范（LANGUAGE_CONVENTION 三层边界） | ✅ 通过 —— 控制流英文 / 交互按 locale / 报告中文 |
| locale 配置一致性 | ✅ `config/menu.yaml` locale=zh；`config/i18n/zh.yaml` 存在 |
| 命令定义可加载性 | ✅ `PromptBuilder.build('maintain')` 渲染成功，正文含交互语言约束 |
| 命令盘点（workflow-command-audit） | ✅ 0 blocker / 15 workflows / 15 commands |
| 路径依赖（path-audit） | ✅ 0 broken |

### 未做项（说明）

- 完整 8 节工作流模板一致性、config/workflows 最小化、state 卫生等**非本 Scope**，未逐项展开（因本会话 scope=workflows 聚焦语言边界；语义完整巡检另需 weekly 全量跑）。

---

## 四、修复动作与建议清单（AI 填写）

| 级别 | 动作 | 状态 |
|---|---|---|
| 已做 | pilot A：aic-maintain.md 追加交互语言约束（3 行） | ✅ 已落地并通过自测 |
| 建议(低) | 若 pilot 验证稳定，将「交互按 locale」约束收敛进全局规范（方案 C，OPERATIONS §11 变更管理），而非逐命令复制 | 待评估 |
| 建议(待定) | 若后续仍现英文交互，回溯运行时通用机制（方案 B：进入交互前先读 locale） | 待 pilot 结论 |
| 说明 | 本机 python shim 问题（`python` 坏解释器 → 用 `python3`）为机器级观察，仅进 per-run diagnostic-log，不入提交态 | 已记录 logs/ |

---

## 五、quick-check 趋势（自动生成）

| 日期 | verdict | findings |
|---|---|---|
| 2026-08-13 | OK | 0 |
| 2026-08-14 | OK | 0 |
| 2026-08-17 | OK | 0 |
| 2026-08-18 | OK | 0 |
| 2026-08-20 | OK | 0 |
| 2026-08-23 | OK | 0 |
| 2026-08-24 | OK | 0 |
| 2026-08-25 | ISSUES | 1 |
| 2026-08-26 | OK | 0 |
| 2026-08-31 | OK | 0 |
| 2026-09-01 | OK | 0 |

## 六、提案状态（自动生成）

- proposal-audit: 0 gate error / 0 warn / 6 开放提案 / 4 open action items
  - 开放: P28-CHANGE-ID-GENERATION.md
  - 开放: P35-PYTHON-INTERPRETER-ROBUSTNESS.md
  - 开放: P36-SETUP-ENV-INIT-SCAFFOLD.md
  - 开放: P37-REQUIRED-INPUTS-TRIAGE.md
  - 开放: P41-TR5-SECTION1-SEMANTICS.md
  - 开放: P42-TR5-TEMPLATE-SKELETON.md
  - P26-MAIN-CHAIN-BRANCH-RULE.md:52 分支扩展 provider（extensions/ 提供者，按需；契约已预留）
  - P26-MAIN-CHAIN-BRANCH-RULE.md:53 CI 增强（git 分支保护，后续）
  - P28-CHANGE-ID-GENERATION.md:42 
  - P28-CHANGE-ID-GENERATION.md:44 D：AI 可选生成（skill 层落点）——触发条件未到
