# AI-System 扩展规范确认（命名 / 流程 / 命令）

**来源**：RFC-0001/0002/0003、OPERATIONS §1.10、governance/policies/skill-policy.md、
repo-lint.md、tools/check.py 实际强制项（2026-08-06 核查确认）
**用途**：新增/修改 ai-system 资产时的权威规范速查。

---

## 1. 命名规范（Naming）

| 资产 | 规则 | 强制者 |
|------|------|--------|
| Skill 目录/name | `kebab-case`，**name 必须与目录名完全一致** | repo-lint check_frontmatter |
| Skill 入口文件 | 小写 `skill.md`（**禁止** `SKILL.md` 大写） | RFC-0002 §2.3 |
| Skill 内禁 README.md / index.md | 单一入口原则 | RFC-0002 §2.3 |
| Workflow | `kebab-case`，单字优先（prepare/develop/release） | OPERATIONS §1.10.1 |
| Command 文件 | `aic-<kebab-name>.md`（`aic-` 是 ai-system 命名空间，替代 openspec 的 `opsx-`） | check.py misc（强制 `aic-` 前缀 + kebab-case 正则 `[a-z0-9]+(-[a-z0-9]+)*` + 无 `opsx-` 残留 + 无重名） |
| Field 名 | PascalCase identity 风格（`Project ID` / `Code Reference`） | OPERATIONS §1.10.1 |

---

## 2. Skill 扩展规范（RFC-0002）

### 2.1 文件结构

```
<skill-name>/
  skill.md          # 入口：frontmatter + Purpose/Trigger/Input/Output/
                    #   Workflow 摘要 + Delegation。Max 80 行。
  workflow.md       # skill.md 工作流摘要 >15 行时必须。Max 250 行。
  decision.md       # 决策点 >10 时必须。Max 80 行。
  analysis.md       # 分析工作流。Max 200 行。
  repair.md         # 修复模式。Max 150 行。
  validation.md     # 验证/回归。Max 150 行。
  planning.md       # 规划阶段。Max 150 行。
  checklists.md     # 技能特有 checklist。Max 100 行。
  examples.md       # 端到端示例。Max 250 行。
  anti-patterns.md  # 禁止行为。Max 100 行。
  scripts/          # 可执行脚本（必须幂等）
```

### 2.2 Frontmatter（强制）

```yaml
---
name: <kebab-case，必须匹配目录名>
description: >
  100-1024 字符；含 ≥3 触发短语；含 "Does NOT" 或 "not responsible for" 反触发；
  无 RFC 未记录的额外 key。
---
```

### 2.3 质量门禁（全部须过）

| Gate | 检查 |
|------|------|
| Frontmatter | name 匹配目录、description 100-1024 |
| 单一职责 | 一句话测试 |
| 无禁止内容 | 无 Maven 命令、无硬编码项目路径/组织名 |
| 无重复 | 不与共享 checklist / governance/standards 重复 |
| 依赖无环 | 依赖图无环（真实边：delegates_to/invokes/orchestrates） |
| 单文件 ≤1000 行 | 聚合引用文件豁免 |
| workflow ≥3 阶段 | Stage/步骤 标记 ≥3 |
| 停止条件 | ≥1 正常停止 + ≥1 失败停止 |
| 委托文档化 | 独立时写 `delegates to: none` |

### 2.4 禁止项

- 单文件 >1000 行；内容重复共享资产；内嵌报告模板
- 硬编码 Maven 命令（须委托 java-maven）、项目路径、项目/组织名
- 循环依赖；Foundation 层技能依赖 Orchestration 层
- 引用不存在的技能（delegates to 断链）

---

## 3. Workflow 扩展规范（RFC-0003 + 八段契约）

### 3.1 入口文件（三件套一一对应）

| 文件 | 内容 |
|------|------|
| `workflows/<name>.md` | 八段契约：Purpose / Runtime / Preconditions / Inputs / Context / Outputs / Exit Criteria / Next（顺序固定） |
| `config/workflows/<name>.yaml` | 注册表极简：`version / name / workflow / runtime`（禁 inputs/outputs/next 回潮） |
| `templates/runtime/runtime-<name>.md` | 生命周期细节（Phase/检查点/恢复）——workflow 文件不得含实现逻辑 |

### 3.2 链约束

- Next 目标必须存在（`deployment`/`none` 为集外例外）
- 术语必须用 README 词汇表（Project ID / Task ID / Change ID 等）

---

## 4. 命令扩展规范（OPERATIONS §1.10）

### 4.1 新增命令步骤

```
1. 写 cli/commands/aic-<name>.md（自动发现）
2. config/menu.yaml 注册：sections 下加 {kind: command} 条目
3. 可选：command_fields 定义提示字段
4. 可选：auto_fields / multi_select_fields / command_next 行为标志
5. 文案走 config/i18n/<lang>.yaml（结构 key 稳定，显示文本在 locale）
```

### 4.2 分组

- 变更管理：propose/apply/archive/explore
- 代码分析：scan/trace
- 系统维护：maintain/pack
- 未注册 → 自动落入"其他命令"

---

## 5. 流程门禁（修改后必跑）

| 命令 | 作用 | 失败含义 |
|------|------|----------|
| `python tools/check.py` | 完整门禁：编译 + menu 引用 + registry 链 + 命令命名 + prompt 构建 + wizard 冒烟 + repo-lint | exit 1 = 系统可能不可运行 |
| `python tools/repo-lint.py --repo-root .` | 技能结构/frontmatter/大小/禁止项 | BLOCKER/ERROR = 不可提交 |
| `python tools/path-audit.py` | 全量路径引用（含全部 skills/） | BROKEN/ABSOLUTE = 断链 |
| `python tools/dependency-graph.py --repo-root .` | 依赖环 | 真实环 = exit 1 |
| `python tools/proposal-audit.py` | 提案门禁 + 遗留 action item | gate error = 阻断 |

### 结构性变更流程（OPERATIONS §12）

```
Analyze → Propose(RFC/提案) → Review → Approve → Implement → Validate(repo-lint) → Report
```

### 变更控制（AI_OPERATING_RULES）

- L1 任务内调整：直接应用，记录 Deviations
- L2 方案变更：停止 → 报告 → 确认后继续
- L3 契约级：停止 → 不得实现 → 路由到 spec

---

## 6. CI 强制（.github/workflows/ci.yml）

```
push/PR → compileall + py_compile → repo-lint → path-audit → check.py
        → skill-optimizer unittest(31) → smoke_test
```

---

## 7. 当前基线（2026-08-06 核查）

| 项 | 值 |
|----|-----|
| Skills | 25（含 architecture 容器 7 子技能） |
| Workflows | 14（8 段契约全合规） |
| Commands | 13（aic- 前缀 + kebab 全合规） |
| 单文件 >1000 | 0 |
| 真实依赖环 | 0 |
| path-audit | 0 BROKEN / 0 ABSOLUTE（237 文件） |
| 测试 | 31 unittest + smoke |

---

## 8. 新增资产归属速查（Golden Rule）

> 新增任何东西前先问：属于 Skill / Workflow / Playbook / Knowledge / Template / Checklist？
> 无法分类 → STOP，先经 repository-maintainer 分析。

| 资产类型 | 归属位置 |
|----------|----------|
| 技能 | `skills/<name>/` |
| 工作流契约 | `workflows/` + `config/workflows/` + `templates/runtime/` |
| 命令 | `cli/commands/aic-*.md` + `config/menu.yaml` |
| 规范/标准 | `governance/standards/` |
| 提案/报告 | `reports/P*.md`（登记 PROPOSALS.md 索引） |
| 运维知识 | `governance/memory/`（预留） |
| Playbook | `playbooks/`（**planned**，目录未创建） |
