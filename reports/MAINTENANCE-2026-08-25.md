# 系统巡检报告 — 2026-08-25（on-demand）

- 类型: 系统巡检（MAINTENANCE）
- 模式: on-demand
- Scope: prepare 工作流集成外部扩展 tr5（含受影响区域增量子集：cli / config / governance / reports / skills / templates / workflows + extensions 域）
- 日期: 2026-08-25

---

## 一、工具校验结果（自动生成，AI 核对补充说明）

| quick-check | verdict **OK**（findings 0） |
| lint | Skills: 30 | Files: 30 | BLOCKERS: 0 | ERRORS: 0 | WARNINGS: 25 |
| path | OK: no broken path dependencies |
| extensions | Summary: 0 errors, 0 warnings |

### 指标对比（自动生成，需 AI 核对变化原因）

| 指标 | 上期 | 本期 | 变化 |
|---|---|---|---|
| Skills | 31 | 31 | = |
| Workflows | 15 | 15 | = |
| RFC | 14 | 14 | = |
| Governance | 56 | 57 | +1（governance 目录新增 1 文件，属既有演进，非本次运行引入） |
| Templates | 22 | 22 | = |

---

## 二、巡检发现（AI 填写，按严重度分级）

### 高（0）
无。

### 中（2）
1. **scope 目标不符：tr5 未注册到 prepare 阶段** — `config/main-chain-capabilities.yaml` 中 tr5 仅注册于 `capabilities.spec`，prepare 阶段缺失；与本次 on-demand scope「prepare 需要集成外部扩展 tr5」不符。功能验证确认 prepare 提示词块不含 tr5。→ **已修复**（见第四节 ①），spec 处保留不变。
2. **extensions-lint 隐藏目录误判（工具缺陷）** — `tools/extensions-lint.py --fix-missing-log` 将 `extensions/.git/`、`extensions/.githooks/` 当作扩展并向其写入 OPTIMIZATION_LOG.md 脚手架。误生成文件已手工清除（yapi-openapi 的脚手架为正确产物保留）。→ 已立 **P39**（Proposed，登记 PROPOSALS.md + README 索引）。

### 低（1）
3. **yapi-openapi 缺 OPTIMIZATION_LOG.md**（quick-check WARN 源）→ **已处理**：用户确认后 `--fix-missing-log` 脚手架补齐，quick-check 回落 OK(0)。

### 信息
4. extensions 仓 yapi-openapi 删除/未跟踪混杂状态 —— **已由用户决策关闭**：yapi-openapi 已迁移至 `project-resources/coolcollege-skills/yapi-openapi`，extensions/ 下以软链接接入（保持现状）；本次脚手架的 OPTIMIZATION_LOG.md 实际落在迁移后目标内，extensions-lint 穿透软链检查 0 告警。机器级细节见 per-run diagnostic-log。
6. **tr5 定位澄清（用户确认，登记备查）**：tr5 是公司特有流程——prepare 之后、spec 之前的**技术详细设计文档**；后续 spec 设计基于 tr5 产物展开；spec 阶段对 tr5 仅**被动更新**（历史产物）。注册维持现状（prepare + spec 双注册）。
5. quick-check 趋势：08-13 至 08-24 连续 7 次 OK，08-25 因 yapi-openapi WARN 一度 ISSUES(1)，处理后回落 OK。

---

## 三、一致性抽查结论（AI 填写，逐项通过/失败）

| # | 抽查项 | 结果 |
|---|---|---|
| 1 | workflows/prepare.md 八节齐全且顺序正确（Purpose/Runtime/Preconditions/Inputs/Context/Outputs/Exit Criteria/Next） | ✅ 通过 |
| 2 | main-chain-capabilities.yaml 注册表格式合规（skill/path/desc/enabled，无 re-bloating）；prepare 含 tr5 后渲染正常 | ✅ 通过（修复后复验） |
| 3 | 能力路径解析：`extensions/...` 对 workspace root、`skills/...` 对 ai-system root，均存在（prompt_builder._resolve_ref 存在性优先，不注入悬空路径） | ✅ 通过 |
| 4 | tr5 扩展本体健康：SKILL.md / OPTIMIZATION_LOG.md / scripts / references / agents 齐全；extensions-lint 对 tr5 无告警 | ✅ 通过 |
| 5 | 引用文件存在性（governance/standards、loaders、templates/prompts、cli/commands）：repo-lint + quick-check path 检查 0 broken | ✅ 通过 |
| 6 | 提案索引一致性：P39 登记 PROPOSALS.md + reports/README.md 表；proposal-audit --refresh-index 完成（33 proposals） | ✅ 通过 |
| 7 | 未抽查项（delta 未命中/超 scope）：workflows 注册表全量、AGENTS.md doc-vs-reality、junction/link health、state hygiene——由 08-30 weekly 全量覆盖 | ⏸️ 延后 |

---

## 四、修复动作与建议清单（AI 填写）

| # | 动作 | 级别 | 状态 |
|---|---|---|---|
| ① | `config/main-chain-capabilities.yaml` capabilities.prepare 追加 tr5 注册（desc: TR5 流水线准备阶段入口；spec 处保留不变）；验证：prompt 渲染断言 + CLI 单测 164 OK + repo-lint/quick-check 复验绿 | L1（配置，用户已确认） | ✅ 已实施 |
| ② | `extensions-lint.py --fix-missing-log` 补齐 yapi-openapi/OPTIMIZATION_LOG.md（连带误写 .git/.githooks 的两个文件已清除）；quick-check ISSUES(1) → OK(0) | L1（工具既有用法，用户已确认） | ✅ 已实施 |
| ③ | 立 P39：extensions-lint 枚举过滤隐藏目录（Option A）+ 最小回归验证 | 提案（§12 待审） | 📋 Proposed |
| ④ | extensions 仓 yapi-openapi 混杂状态 → 用户决策：迁移至 `project-resources/coolcollege-skills/` + 软链接接入，保持现状；复验：软链解析 OK、extensions-lint 0 告警 | 用户决策（机器级落地） | ✅ 已关闭 |
| ⑤ | 建议：08-30 weekly 按 next_maintenance 执行全量巡检（覆盖本轮延后的抽查项 + wayfinder TRIAL 评估截止） | 建议 | ⏳ 排期 |

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
| 2026-08-25 | OK | 0 |

## 六、提案状态（自动生成）

- proposal-audit: 0 gate error / 0 warn / 6 开放提案 / 4 open action items
  - 开放: P28-CHANGE-ID-GENERATION.md
  - 开放: P35-PYTHON-INTERPRETER-ROBUSTNESS.md
  - 开放: P36-SETUP-ENV-INIT-SCAFFOLD.md
  - 开放: P37-REQUIRED-INPUTS-TRIAGE.md
  - 开放: P38-WORKFLOW-INTERACTION-AUDIT.md
  - 开放: P39-EXTENSIONS-LINT-HIDDEN-DIRS.md
  - P26-MAIN-CHAIN-BRANCH-RULE.md:52 分支扩展 provider（extensions/ 提供者，按需；契约已预留）
  - P26-MAIN-CHAIN-BRANCH-RULE.md:53 CI 增强（git 分支保护，后续）
  - P28-CHANGE-ID-GENERATION.md:42 
  - P28-CHANGE-ID-GENERATION.md:44 D：AI 可选生成（skill 层落点）——触发条件未到
