# Context / Attention / Architecture 缺口评估与修复报告

- 日期 / Date: 2026-08-08
- 范围 / Scope: 围绕上下文管理、注意力、架构设计规范三个主题的系统缺口评估与 P0/P1/P2 修复
- 性质 / Nature: 评估 + 实施

---

## 一、评估结论(缺口清单)

三主题的**策略层(原则/规范)已相当完整,缺口集中在执行层(工具化/流程化/自动化)**——策略文档不缺,缺的是让策略"被强制执行"的机制。

| 优先级 | 缺口 | 原状 |
|---|---|---|
| P0 | 上下文量化测量 | 40/60/80% 阈值是经验值,无 token 计量工具(此前靠手工分析会话 jsonl) |
| P0 | 会话交接无执行者 | Handoff 模板存在但无 skill/workflow 执行;memory/ 是经验库不含进行中任务 |
| P1 | 注意力无专项规范 | 注意力仅作触发信号散落 3 处,无衰减信号/检查点/中断规则文档 |
| P1 | 架构规范分散 | 模块形状词汇在 skill 内部(vocabulary.md),无 governance 权威源 |
| P2 | ADR 无流程执行 | 有创建标准无评审校验,check.py 不校验 ADR |
| P2 | 设计评审无接受阈值 | 1-5 分与 Approved/Needs Revision 无绑定 |
| P2 | 架构复杂度无自动检测 | repo-lint 只查 layer 依赖/循环,无 workflow 行数门禁 |

## 二、修复交付(P0/P1/P2)

### P0

| 交付物 | 内容 | 验证 |
|---|---|---|
| `tools/context-audit.py` | 会话上下文审计:token 估算(中英/代码加权)、最大消息、ACTIVE vs FULL 双维度、40/60/80 健康分级 | 真实会话:ACTIVE 9.2% GREEN,FULL 78% |
| `skills/handoff/SKILL.md` | 会话交接:按 CONTEXT_RETENTION Keep/Drop 产出摘要 + pi/opencode 双注入(pi 直传指令 / opencode 压缩前发消息) | repo-lint 0 BLOCKER,74 行合规 |

### P1

| 交付物 | 内容 | 验证 |
|---|---|---|
| `governance/ATTENTION_MANAGEMENT.md` | 衰减信号表(6 类)、任务中检查点(每 3 步)、果断中断规则、任务级重置;挂接 Governance References | 全英文,LANGUAGE_CONVENTION 合规 |
| `governance/standards/architecture/module-shape.md` | 深模块词汇表(Module/Interface/Depth/Seam/Adapter)提升为 binding 标准;vocabulary.md 指向它 | 消除双源分叉 |

### P2

| 交付物 | 内容 | 验证 |
|---|---|---|
| `tools/checks/adr.py` | ADR 完整性:编号连续/状态合法/日期/必需段落/README 登记;兼容头格式+表格式 | 7 个存量 ADR 全通过 |
| design-review 阈值 | Verdict Thresholds(Binding):评分→裁决硬映射(≤3/≥3/≥3=Approved;≥4 或 ≤2=Needs Revision;5 或 blocking=Rejected) | — |
| `check_workflow_size` | RFC-0003 ≤100 行门禁 | 实测 241 行测试文件正确 FAIL |

## 三、check.py 检查项(10 → 12)

新增:ADR 完整性、workflow 行数门禁。`context-audit.py` 为分析工具不入门禁。

## 四、关联

- `CONTEXT_LOADING.md`(健康分级)→ `context-audit.py`(量化执行)
- `CONTEXT_RETENTION.md`(保留策略)→ `handoff` skill(交接执行)
- `REFLECTION_RULES.md`(退出反思)→ `ATTENTION_MANAGEMENT.md`(任务中反思)
- `RFC-0001`/design-review(架构)→ `module-shape.md`(统一标准)

## 五、遗留

- memory 条目(会话经验沉淀流程)自动化,未做(需 memory 机制独立设计)
- 跨会话任务状态持久化,未做(当前靠 handoff 摘要人工传递)

---

## 七、追加修复与待办（2026-08-08 晚）

### 已修复（P0）

| 项 | 内容 |
|---|---|
| wizard.py 拆分 | 1235 行 → 6 模块 mixin 包(base/steps/selection/fields/output/analysis),外部 API 不变 |
| 核心服务测试 | skill_launcher/skill_scan 10 用例(源标记/标签/分组/渲染/扫描),cli 测试 31→41 |
| dry-run patch 修复 | wizard 模块化后 patch 目标改为消费模块(selection/fields/output) |
| path-audit 引用修复 | memory/file-contract.md 旧 wizard.py 路径 → 包路径 |

### 待办（触发式,勿主动做）

| 项 | 触发条件 | 来源 |
|---|---|---|
| skills/README "On-Demand(7)" 与实际 14 不符 | 下次 skills 增删时顺手 | 系统评估 |
| reports/README 登记不存在的文件(live-facade-snapshot-risk) | 下次报告维护时 | 系统评估 |
| CI 补 context-audit/dependency-graph/repo-metrics 3 步 | CI 需覆盖审计工具时 | 系统评估 |
| 3 个已知坏引用白名单(memory/integration、python、code-quality) | 创建占位目录或删除引用 | 系统评估 |
| repo-lint 脚本 .py 扫描盲区 | 确认 P10 后扩展 | 系统评估 |
| memory 翻译存量债(#5-7) | 独立工作项 | MAINTENANCE |
| wizard/engine/mutator.py 733 行接近门禁 | 超过 800 行时 | 系统评估 |
