# CLI 规范化评估报告（2026-08-06）

**范围**：cli/（13 命令 + 17 个 Python 模块，5168 行）+ config/menu.yaml + tools/checks 门禁
**目的**：评估现状，识别"规范化开发维护"缺口，输出路线图

---

## 1. 现状评分

| 维度 | 评分 | 说明 |
|------|------|------|
| 命令文档结构 | ✅ 良好 | 13/13 frontmatter 统一（description），Inputs/Steps/Output/Guardrails 齐备（explore 有意例外） |
| 配置驱动 | ✅ 良好 | menu.yaml 注册 13/13 命令 + 14/14 工作流；i18n 单语；字段来源三处统一 |
| 命名规范 | ✅ 良好 | aic- 前缀 + kebab-case 全合规；opsx 零残留 |
| 完整性门禁 | ✅ 良好 | check.py 覆盖命令命名/引用/可构建性/wizard dry-run |
| **行为测试** | ❌ 缺失 | 仅完整性冒烟，无字段收集/hook/状态/渲染断言 |
| **文档规范** | ⚠️ 缺口 | 无 cli/README、无开发指南、InteractiveCommand 协议仅存于 docstring |
| **代码组织** | ⚠️ 大文件 | wizard.py 1235 行、menu.py 1264 行（多职责混杂） |
| **字段一致性** | ⚠️ 4 命令缺口 | propose/apply/archive/explore 无 command_fields，与文档位置参数描述不一致 |

---

## 2. 发现的缺口（按严重度）

### 🔴 高优先级

| # | 缺口 | 证据 | 影响 |
|---|------|------|------|
| C1 | **无 CLI 行为测试** | 全仓库无 cli 测试；pyproject 无 test 配置 | 字段收集/hook 注入/状态持久化/渲染输出无回归守护 |
| C2 | **4 命令字段漂移** | propose/apply/archive/explore 无 command_fields，向导收集默认字段 vs 文档描述位置参数 | 文档↔行为不一致的源头 |

### 🟡 中优先级

| # | 缺口 | 证据 | 影响 |
|---|------|------|------|
| C3 | **悬空命令引用** | `/aic-continue`（aic-apply.md:30）、`/aic-new`、`/aic-ff`（aic-explore.md:7）无对应文件 | 文档与命令体系脱节；check.py 不查文档内命令引用 |
| C4 | **大文件 + 职责混杂** | wizard.py 1235 / menu.py 1264（i18n+终端+输入组件+模块级全局态） | 修改风险高、测试难写 |
| C5 | **"实验性"标记未收尾** | aic-apply.md / aic-archive.md description 标 experimental | 规范化程度不一 |

### 🟢 低优先级

| # | 缺口 | 证据 |
|---|------|------|
| C6 | i18n 重复键 "Mode" | zh.yaml:27（maintain）与 zh.yaml:71（skill-optimize）后者覆盖前者 |
| C7 | 硬编码路径 | main.py:284/333（`.ai-system/generated` 相对 CWD）、skill_scan.py（`~/.agents/skills`）、prompt_builder.py（`parents[2]` 推导根目录） |
| C8 | frontmatter 极简 | 命令文档只有 description，无 name/fields（语义分散在文件名+menu.yaml） |

---

## 3. 做得好的（保留）

- 命令文档结构 13/13 统一；check.py 门禁覆盖完整
- 配置驱动程度高（改文案不动代码）；opsx 迁移干净；模块 docstring 齐备
- wizard 已做过分拆（README 自述），InteractiveCommand 有回退协议

---

## 4. 规范化路线图（建议分批）

### Batch C1 — 测试基座（先行，最高收益）

| 项 | 动作 |
|----|------|
| 测试框架 | 复用 skill-optimizer 的 stdlib unittest 模式（无 pytest 依赖） |
| `tests/test_cli_menu.py` | menu.yaml 解析：sections/command_fields/i18n 键完整性（当前 check.py 只做存在性，补语义断言） |
| `tests/test_cli_prompt.py` | prompt_builder：workflow/command 模板渲染断言 |
| `tests/test_cli_state.py` | state_store：读写/默认值/损坏恢复 |
| `tests/test_cli_commands.py` | 命令命名/结构断言（把 check.py 的 check_commands 提升为行为测试） |
| CI 集成 | `.github/workflows/ci.yml` 增加 cli 测试步 |

### Batch C2 — 字段一致性修复

| 项 | 动作 |
|----|------|
| 4 命令补齐 | propose/apply/archive/explore 在 menu.yaml command_fields 注册真实字段（对齐文档 Inputs） |
| 悬空引用清理 | `/aic-continue`、`/aic-new`、`/aic-ff` 删除或标注 planned；check.py 增查文档内命令引用 |
| i18n 去重 | zh.yaml "Mode" 键改名区分（maintain_mode / optimize_mode） |

### Batch C3 — 文档规范化

| 项 | 动作 |
|----|------|
| `cli/README.md` | CLI 架构、命令目录、字段来源三处（menu.yaml/workflows md/代码 providers）说明 |
| `cli/DEVELOPMENT.md` | 新增命令 4 步流程 + InteractiveCommand 协议文档化 + 测试要求 |
| 实验性收尾 | apply/archive 移除 experimental 或升级状态 |

### Batch C4 — 代码组织（季度级）

| 项 | 动作 |
|----|------|
| menu.py 拆分 | i18n 缓存 → menu_i18n.py；终端/VT → menu_terminal.py；输入组件 → menu_input.py |
| wizard.py 瘦身 | 目标选择/字段循环/header 渲染/启动选择分别提取 |
| 硬编码清理 | `.ai-system/generated`、`~/.agents/skills`、`parents[2]` 统一走 environment.py 解析 |

---

## 5. 建议执行顺序

```
Batch C1 (测试基座) → Batch C2 (字段一致) → Batch C3 (文档) → Batch C4 (代码组织)
     ↑ 先行：无测试前，C2-C4 的改动无法安全回归验证
```

**优先级逻辑**：C1 是地基——CLI 已有 5000+ 行代码和 13 命令，但没有行为测试，
后续任何规范化改动（C2-C4）都在裸奔。C1 复用既有 unittest 模式，成本低收益确定。

---

## 7. 待办（Pending，2026-08-06 记录，明日执行）

> **状态更新（2026-08-08）：C1 已全部完成**（menu_config + prompt_builder + state_store，
> 20 用例），并已挂接 check.py（check_cli_tests）+ CI（cli unit tests 步）。
> **C2 已全部完成**：propose/apply/archive/explore 注册 command_fields；同时修复
> MenuConfig 相对路径静默失败缺陷（C2 隐藏根因之一），含 3 条回归测试。
> 剩余：C3 文档规范化、C4 代码组织（季度级）。

**Batch C1 — CLI 测试基座（精简版，预估 20-30 分钟）**

| 项 | 内容 | 用例 |
|----|------|------|
| menu_config | menu.yaml 解析语义断言（sections/command_fields/i18n） | ~8 |
| prompt_builder | workflow/command 模板渲染断言 | ~6 |
| state_store | 读写/默认值/损坏恢复 | ~5 |
| CI | workflow 增加 cli 测试步 | — |

> 全量版（+workflow_reader/main 命令断言）约 40-60 分钟；
> 先做核心 3 模块（配置解析+渲染，风险最高），main 的命令结构已有 check.py 兜底。
> 后续批次：C2 字段一致 → C3 文档 → C4 代码组织。

---

## 8. 交互方案调研与后续优化方向（2026-08-08 记录）

### 调研结论

当前方案（prompt_toolkit 手写菜单层）在功能上是业界先进水平，**不推荐替换**：

- ✅ **做对的**：基于 prompt_toolkit（最成熟底层）；非 TTY 降级（questionary/textual 都没有）；
  Sections 分组 + type-to-filter（questionary 2.1 才刚补上）；enter_selects_current。
- ⚠️ **负债**：手写代码多（原 menu.py 1263 行），维护成本高，新人难上手。
- ❌ **不推荐替换**：questionary 缺非 TTY 降级且同底层；textual 是全屏 TUI，与本项目
  "菜单式向导"定位不符。

### P2/P3 优化方向（待触发）

| 优先级 | 方向 | 触发条件 | 说明 |
|---|---|---|---|
| P2 | 借鉴 questionary 样式/主题 | 视觉统一需求时 | 只借鉴 style 体系，不替换；对齐现有图标体系 |
| P3 | questionary 做独立子命令的新交互 | 新交互需求时 | 非替换现有，渐进去重手写层 |
| P1 ✅ | menu.py 模块化拆分 | 已完成（2026-08-08） | 1263 行 → 6 模块包 base/keys/render/text/select/multi，31 测试守护 |

### 相关

- 调研来源：questionary / prompt_toolkit / textual 对比（2026-08-08）
- 拆分提交：menu.py 模块化（P1）

---

## 6. 结论

CLI 的**结构健康度良好**（配置驱动、命名规范、门禁完整），缺的是**测试基座 + 文档规范**。
"规范化开发维护"的第一优先是 C1（测试），随后 C2（一致性）→ C3（文档）→ C4（结构）。
当前无需结构性重构——大文件是维护性负债，但不是功能缺陷，按季度节奏处理即可。
