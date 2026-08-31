# 系统巡检报告 — 2026-08-26（on-demand）

- 类型: 系统巡检（MAINTENANCE）
- 模式: on-demand
- Scope: extensions/tr5 — 前后端需求区分机制确认（角色=后端；前端仅标记+关联影响评估）
- 日期: 2026-08-26

---

## 一、工具校验结果（自动生成，AI 核对补充说明）

| quick-check | verdict **ISSUES**（findings 1） |
| lint | Skills: 30 | Files: 30 | BLOCKERS: 0 | ERRORS: 0 | WARNINGS: 25 |
| path | ABSOLUTE OUTSIDE environments (0): |
| extensions | Summary: 0 errors, 0 warnings |

### 指标对比（自动生成，需 AI 核对变化原因）

- 指标快照 maintain-{date}.json 缺失
- 说明: maintain-delta 判定 NO_CHANGES（自 2026-08-25 全量巡检后 ai-system 无提交），按规程跳过全量审计与 repo-metrics 快照，仅执行 quick-check + 状态卫生 + 定向 Scope 检查。

---

## 二、巡检发现（AI 填写，按严重度分级）

### 高

无。

### 中

无。

### 低

- **L1. path-audit 误报 BROKEN(1)**: `cli/config/governance/reports/skills/templates/workflows <- ai-system/config/maintenance.yaml`。根因：`config/maintenance.yaml:16` 的 `scope:` 值是斜杠分隔的域清单（delta 增量子集说明），path-audit 将其误判为单一路径解析。自 2026-08-25 起连续 2 个快照 ISSUES，均为同一误报；lint/extensions 实际 0 错误。属工具解析缺陷，非真实断链 → 记录待修，不自行改动。
- **L2. tr5-review 阶段未复核前端标记**: `extensions/tr5/skills/tr5-review/SKILL.md` 的 Gate 4 与人工评审维度（Spec↔TR5 一致性 / 完整性检查）不含"[前端] 标记已覆盖"项。前端标记仅在 Gate 1（prepare 出口）强制，review 出口缺二次校验。属增强建议，非缺陷。
- **L3. check_spec.py 未程序化校验 [前端] 标签**: gate-rules.md 自述"机器可判定为主"，但 check_spec.py 不检查需求类型标签，[前端]/[后端]/[前端依赖] 标记完全依赖 AI 判定。属增强建议。

### 信息

- **I1. 本机 python shim 损坏**（机器级，不入 maintenance.yaml）: `python` 解析到 WSL 下 `/mnt/c/.../pyenv-win/shims/python` bad interpreter，本次运行改用 `python3`。已有开放提案 P35-PYTHON-INTERPRETER-ROBUSTNESS.md 对应此问题。
- **I2. quick-check 连续 2 日 ISSUES** 均由 L1 同一误报贡献，趋势见第五节。

### Scope 定向结论：tr5 扩展前后端区分机制 — **已确认存在且成体系**

角色定义与标签体系完备（`references/field-guide.md` §Frontend vs Backend Boundary）：

| Tag | 处理 | 落点 |
|---|---|---|
| `[前端]` | 仅列出，不设计、不写场景、不拆任务、不估时 | field-guide / spec-design / templates/spec.md |
| `[后端]` | 完整设计 | 同上 |
| `[前端依赖]` | 只设计后端 API（路径/参数/响应/校验） | spec-design.md:165、field-guide |
| `[前后端]` | 拆分为两条，后端全设计，前端打 `[前端]` | field-guide.md:99 |

各阶段覆盖：
1. **prepare**: SKILL.md §2f 标记需求类型 + Gate P4（标签已标记）+ P9（前端 ≤2、后端 ≥80%）✅
2. **Gate 1**: gate-rules.md "✓ 前端需求已标记 [前端]" ✅
3. **spec**: spec-design.md — `[前端]` 前缀、`场景: （前端实现，本角色不涉及）`、混合需求拆分；templates/spec.md 图例 ✅
4. **design**: 后端 only 约束（禁写前端文件路径/组件/路由）；`[前端依赖]` 仅列 API ✅
5. **tasks**: `[前端]` 单行 checkbox，无子项无估时 ✅
6. **TR5 文档**: 前端仅出现在 §1 需求理解（可选 §4），§3/5/6/7/12/13 后端 only ✅
7. **review/publish/develop**: 无前端标记相关条目（见 L2）

结论：与用户要求一致——tr5 扩展已实现"后端全设计、前端只标记+关联影响（[前端依赖] API）"的边界，无需新增机制。

---

## 三、一致性抽查结论（AI 填写，逐项通过/失败）

> on-demand NO_CHANGES：仅执行状态卫生 + Scope 相关抽查。

| 抽查项 | 结果 |
|---|---|
| workspaces/.aic-state.yaml 引用的 3 个项目目录均存在 | ✅ 通过 |
| extensions/tr5 结构完整（SKILL.md + OPTIMIZATION_LOG.md 存在） | ✅ 通过 |
| tr5 标签体系内部一致（field-guide ↔ spec-design ↔ prepare gates ↔ templates/spec.md 四处口径一致） | ✅ 通过 |
| config/maintenance.yaml scope 行被 path-audit 误判为路径 | ❌ 失败（L1 误报，工具侧待修） |

---

## 四、修复动作与建议清单（AI 填写）

| # | 类型 | 内容 | 处置 |
|---|---|---|---|
| F1 | 工具修复 | path-audit.py 对 maintenance.yaml `scope:` 冒号值按域清单解析（或维护 known-debt 白名单），消除连续误报 | ✅ 已确认修复：token 加入 FALSE_POSITIVES（tools/path-audit.py:53-55）；复跑 path-audit BROKEN(0)、quick-check verdict OK（findings=0） |
| F2 | 增强 | tr5-review SKILL.md Gate 4 / 完整性检查增加"前端标记复核"项 | ✅ 已登记：extensions/tr5/OPTIMIZATION_LOG.md 顶部待办条目，待后续实施 |
| F3 | 增强 | check_spec.py 增加 `[前端]`/`[前端依赖]` 标签存在性校验（warning 级） | ✅ 已登记：同上 OPTIMIZATION_LOG 待办条目 |

修复后复验（gate）：path-audit BROKEN(0) / quick-check findings=0 verdict OK / extensions-lint 0 errors 0 warnings。

结构性变更：无。

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
| 2026-08-26 | ISSUES | 1 |

## 六、提案状态（自动生成）

- proposal-audit: 0 gate error / 1 warn / 5 开放提案 / 4 open action items
  - WARN MAINTENANCE-2026-08-25.md: not registered in reports/README.md index (proposal-policy §6)
  - 开放: P28-CHANGE-ID-GENERATION.md
  - 开放: P35-PYTHON-INTERPRETER-ROBUSTNESS.md
  - 开放: P36-SETUP-ENV-INIT-SCAFFOLD.md
  - 开放: P37-REQUIRED-INPUTS-TRIAGE.md
  - 开放: P40-OPENSPEC-CHANGE-NAME-NAMING.md
  - P26-MAIN-CHAIN-BRANCH-RULE.md:52 分支扩展 provider（extensions/ 提供者，按需；契约已预留）
  - P26-MAIN-CHAIN-BRANCH-RULE.md:53 CI 增强（git 分支保护，后续）
  - P28-CHANGE-ID-GENERATION.md:42 
  - P28-CHANGE-ID-GENERATION.md:44 D：AI 可选生成（skill 层落点）——触发条件未到
