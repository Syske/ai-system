# 结构分析报告 / Structure Analysis Report

- 目标 / Target: structure
- 范围 / Scope: governance
- 日期 / Date: 2026-08-01

---

## 一、范围界定 / Scope

分析 AI System 的 `governance/` 目录结构、层级关系、命名规范与引用完整性。覆盖：

- `governance/` 顶层 8 个核心文件（AI_OPERATING_RULES、SOURCE_OF_TRUTH、CONTEXT_LOADING、REPOSITORY_FIRST、REFLECTION_RULES、LANGUAGE_CONVENTION、repo-lint、review-standard、violation-rules、karpathy-guidelines）
- `governance/contracts/`、`policies/`、`standards/`、`memory/`、`archive/` 子目录
- 治理层与外部层（workflows、templates/runtime、tools、loaders、routing、README/OPERATIONS）的引用关系

---

## 二、目录结构 / Directory Structure

```text
governance/
├── AI_OPERATING_RULES.md          # 全局 AI 行为规则（v1.3）
├── SOURCE_OF_TRUTH.md             # 信息源优先级
├── CONTEXT_LOADING.md             # 上下文加载策略
├── REPOSITORY_FIRST.md            # 复用优先
├── REFLECTION_RULES.md            # 反思规则
├── LANGUAGE_CONVENTION.md         # 语言约定
├── repo-lint.md                   # 命名规范
├── review-standard.md             # 评审流程
├── violation-rules.md             # ⚠️ 内容为 Repository Governance 总览
├── karpathy-guidelines.md         # Karpathy 准则
├── README.md                      # 治理索引
├── contracts/
│   └── AI_DEVELOPMENT_CONTRACT.md # 开发契约（v1.1）
├── policies/
│   ├── quality-gates.md           # 质量门禁
│   ├── security-policy.md         # ⚠️ 占位符（5 行）
│   ├── skill-policy.md            # 技能贡献指南
│   └── routing-policy.md          # ⚠️ 内容为 Skill Lifecycle
├── standards/
│   ├── common/                    # 通用标准（12 个）
│   ├── cool/                      # Cool 项目标准（5 个）
│   ├── java/                      # Java 标准（2 个）
│   └── dependency-version.md      # 依赖版本标准
├── memory/
│   ├── MEMORY_GUIDELINES.md       # 记忆指南
│   ├── coding-memory.md           # 记忆索引
│   ├── ai-system/                 # AI 系统经验
│   └── java/                      # Java 经验
└── archive/                       # 已归档（历史中文文档 + 废弃标准）
    ├── common/  cool/  standards/
```

### 统计

- 42 个文件，9 个目录（含 archive）
- active 文件 38 个，archive 文件 4 个

---

## 三、层级关系 / Hierarchy

### 3.1 治理分层（violation-rules.md 定义）

```text
RFCs (Specifications) → Governance Docs (Policies) → ADRs (Decisions) → Tools (Enforcement) → Metrics (Tracking)
```

### 3.2 依赖方向

```text
Workflows/Runtimes  ──引用──▶  Governance（规则）
     ▲                            │
     └────────── 强制执行 ◀───────┘
Tools (repo-lint/metrics) 依据 Governance 规则检查 components
```

---

## 四、主要结构问题 / Key Findings

### F1（高）：`policies/routing-policy.md` 文件名与内容脱节

- 文件内容为 **Skill Lifecycle**（生命周期阶段、Split/Merge 决策）
- README.md 与 governance/README.md 描述其为 "Routing configuration rules"
- 迁移报告显示该文件由 `skill-lifecycle.md` 改名而来，但**内容未同步**
- 后果：路由配置策略无实际文档；SKill 生命周期与 `policies/skill-policy.md`（Contribution Guide）职责重叠

### F2（中）：`violation-rules.md` 文件名与内容脱节

- 文件内容为 **Repository Governance** 系统总览（RFCs→Tools→Metrics 分层）
- README.md 描述其为 "Violation severity classification"（违规严重度分级）
- 迁移报告显示由 `repository-governance.md` 改名而来，内容未同步
- 后果：README 索引描述与实际内容不符；违规分级规则缺失

### F3（中）：`security-policy.md` 是占位符

- 仅 5 行：`> Placeholder: Security policy for the AI Operating System.`
- 但被 README.md、governance/README.md、archived 架构规格引用为正式策略

### F4（中）：`scripts/` 路径引用已失效

- `quality-gates.md`、`review-standard.md`、`routing-policy.md` 引用 `scripts/repo-lint.py` / `scripts/repo-metrics.py`
- 实际工具位于 `tools/`（`tools/repo-lint.py` 等），`scripts/` 目录不存在

### F5（中）：standards-loader 引用 7 个不存在的标准文件

- MISS: `api/rest.md`、`database/sql.md`、`go/go-style.md`、`java/mybatis.md`、`java/spring.md`、`mq/rocketmq.md`、`python/pep8.md`
- 其中 `common/code-quality.md` 已归档（有活跃替代），其余 6 个为扩展预留位但未标注

### F6（低）：README.md 引用已归档的 `common/code-quality.md`

- 该文件已移至 `archive/standards/common/code-quality.md`，README 索引未同步

### F7（低）：memory 索引存在悬空目录引用

- `governance/memory/coding-memory.md` 列出 `python/`、`integration/` 类别
- 实际目录仅有 `ai-system/`、`java/`；`python/`、`integration/` 不存在

### F8（低）：`standards/java/rpc.md` 结构异常

- 仅 8 行，首行标题为 `## RPC`（二级标题，非文档标题），与其它标准（一级标题 + Purpose/Scope 结构）不一致

---

## 五、健康的结构部分 / Healthy Aspects

- 核心规则文档（AI_OPERATING_RULES 等 8 个）命名准确、内容匹配、相互引用闭环
- 运行时模板引用的 governance 文档 100% 存在（14 个引用全部 OK）
- archive/ 归档机制清晰：废弃标准有明确替代声明（code-quality.md → task-quality-checklist.md + clean-code.md）
- 语言约定良好：active 文件基本纯英文，CJK 仅出现在中文写作规范本身与示例中
- 索引（governance/README.md）所列文件全部存在

---

## 六、总结 / Summary

治理层整体结构健康，核心规则与引用闭环可靠。主要问题集中在**历史迁移残留**：两个文件改名后内容未同步（F1/F2）、占位符未完成（F3）、路径未更新（F4/F5/F6）以及索引悬空（F7）。这些不破坏执行正确性，但损害治理文档的可信度与可发现性。
