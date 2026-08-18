# aic 交互与提示词优化报告 — 2026-08-18

**类型**: AI 系统维护（交互/提示词链路专项优化）
**日期**: 2026-08-18
**范围**: aic CLI 的交互链路（wizard）与提示词生成链路（prompt_builder）
**结论**: 审计 18 项问题，已解决 16 项；分四批推送 `main`（8 commits）

> 本轮由维护巡检延伸：在「aic 其他菜单诊断」基础上，对交互与提示词阶段做系统化审计，产出可执行的优化项并实施。

---

## 1. 问题发现（三份并行审计 + 实证验证）

派 3 个并行 worker 分别审计：
- **prompt_builder.py**（提示词生成链路）
- **wizard/**（交互状态机：steps/fields/output/selection/intake）
- **遗留与一致性**（维护报告遗留、命令文档漂移、check.py 门禁缺口）

审计共发现 **18 项问题**，按严重度分级：
- 🔴 崩溃级 1 项（B1）
- 🟠 高优先级 6 项（H1-H6）
- 🟡 中优先级 8 项（M1、M3-M8）
- 🟢 结构性/低 3 项（意图链、Esc 一致性、三方一致门禁）

关键实证（均在实施前验证）：
- `_create_ai_intent` 无法推断命令时生成空意图 → `steps.py:66 commands[0]` **IndexError**
- CLI 直调 trace 时 prompt 泄漏 `Operation: search`、`Keep Results: False`、`agent: x`
- 字段名注解污染：`Base Branch (default: master)` 成整串字段名
- 必填字段文本模式空 Enter 静默跳过
- save 路径硬编码 CWD 相对 `.ai-system/generated`

---

## 2. 已解决项（16 项）

### 第一批（2026-08-18，commit ce5a103）
| # | 问题 | 修复 |
|---|------|------|
| B1 | AI 引导空意图 → IndexError 崩溃 | 无法推断命令时返回 None + 提示，不创建空意图；+1 测试 |
| H1 | 必填字段可静默留空 | steps 必填 None 重问当前字段（不前进不跳过）|
| H2 | CLI 字段超集泄漏 | PromptBuilder 字段契约：只渲染目标声明字段 + 过滤 None/False/空串；+4 测试 |
| H3 | save 路径硬编码 CWD | 统一 `outputs_root/generated`（环境配置）|
| H4 | 字段名注解污染 | `parse_inputs` 归一化剥 `(...)` 注解 |
| H5 | 默认值格式不统一 | `field_defaults` 支持 `(default:X)` + `; default X;` → bugfix Mode 默认生效 |
| M7 | i18n `Mode` optimize 残留 | 删残留，合并三种语境说明 |

### 第二批（2026-08-18，commit 254cfe5）
| # | 问题 | 修复 |
|---|------|------|
| H6 | back 改上游字段后下游残留旧值 | `_invalidate_dependents`：Projects→Branch、项目→Change/Task 清空；+3 测试 |
| M1 | `_parse_next` 格式敏感 | 遍历全部 bullet 全部 token + `- None` 终止语义 |
| M3 | 意图 kw_map 子串误匹配 | 否定前缀过滤（没有/无/不/非/别）|
| M4 | 项目列表 82 项全量渲染 | `choose` 支持 `max_visible`，`_select_project` 传 10（过滤搜全量）|
| M5 | 3 处命令 Steps 中文语言债 | scan/trace 转英文；skill-source 表格（用户可见）保留 + lint 豁免表格行 |
| M6 | scan `Scan Directory` 矛盾、extensions-init `Workspace Root` 未收集 | Scan Directory 标"CLI 自动填充"；Workspace Root 入 command_fields + i18n |
| M8 | intent 中 workflow 当 command | steps 按 `aic-*.md` 存在性分派 kind |

### 第三批（2026-08-18，commit f8c7519）
| 问题 | 修复 |
|------|------|
| 意图链仅打印 | wizard 返回 5 元组（含 chain）；main 逐命令构建输出 |
| Esc 不一致 | ask_text Esc：有输入先清空，空才返回 BACK（对齐 Backspace）|
| 三方一致门禁 | `workflow-command-audit.py` 新增字段一致检查（文档↔command_fields），0/0 |

### 前序专项（本轮之外的铺垫，2026-08-18 多 commit）
menu 分组重构、scan 入口收敛（impact 移除）、无项目 last_target/自愈、project_required 门控、产物命名统一 `{yyMMdd}`、`max_visible=10`（Projects 多选）——这些为本轮审计铺平了菜单/状态层，单独记录于对应提交。

---

## 3. 明确保留未做（合理设计决策）

| 项 | 理由 |
|----|------|
| M2 `_recommend_workflow` 兜底 prepare | prepare 是主链起点，兜底合理 |
| 占位符 `{date}`/`{yyMMdd}` 代码兜底 | 文档规范（AI 替换目标），代码生成路径已用时间戳无风险；避免过度设计 |

---

## 4. 剩余可选（未实施）

| 项 | 说明 | 建议 |
|----|------|------|
| P22 阶段二遗留 | 向导自动化测试（agent 后真实交互断言）、平台默认环境自动选择 | 较大，走提案 |
| 意图链连续执行 | 当前"依次输出 prompt"→"单会话多命令连续执行" | 需较大交互重构 |
| 大量测试注入 | `_invalidate_dependents`/字段契约等需更多边界用例 | 持续补 |

---

## 5. 指标对比

| Metric | 优化前（08-17）| 优化后（08-18）| Δ |
|--------|--------------|--------------|---|
| repo-lint WARN | 27 | **23** | -4（语言债清偿 + 表格豁免）|
| 测试用例数 | 84 | **87** | +3（H6）；B1/prompt 字段契约等新增组件测试 |
| check.py | PASS 0 warning | PASS 0 warning | — |
| quick-check | OK | OK | — |
| 三方一致门禁 | 无 | 0 blockers / 0 warn | 新增防护 |

---

## 6. 环境备注（记录维护经验）

- 本机 Python shim：`which python` 曾命中 WindowsApps Store 别名（exit 49 静默失败），须用 `pyenv` 绝对路径 `/c/Users/syske/.pyenv/pyenv-win/versions/3.10.11/python`——与研究记录一致。
- 外部会话的 `governance/memory/java/{spring,coding-memory}.md` 在本次多轮会话中持续为未提交状态，属另一会话知识记录，未纳入任何提交。

---

## 7. 维护纪律登记

- 本报告为专项优化记录，后续例行巡检（aic-maintain）可引用本报告索引。
- 建议将「三方字段一致门禁」纳入 OPERATIONS §11 例行校验说明（doc-vs-reality）。
