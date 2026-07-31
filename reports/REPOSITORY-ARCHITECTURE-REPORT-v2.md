# Repository Architecture Report v2

> 生成日期: 2026-07-03
> 维护者: Architecture Maintainer

---

## 1. 当前问题 (As-Is Analysis)

### 1.1 职责混杂: ai-system 包含 runtime/

```
ai-system/
  runtime/          ❌ 不应存在于 ai-system
    agents/
    claude/
    opencode/
```

`ai-system/runtime/` 包含 provider adapter 代码 (`index.js`, `opencode.js`, `agents/adapter.js`, `claude/adapter.js`, `opencode/adapter.js`, `opencode/executor.js`)。这些是执行层代码，应全部属于 `ai-runtime/`。

### 1.2 知识泄露到 projects 层

```
projects/openspec-test/.claude/skills/       ❌ 重复
projects/openspec-test/.opencode/skills/     ❌ 重复
projects/pywechat-live-2608/openspec/.opencode/skills/  ❌ 重复
```

openspec 系列技能 (apply-change, archive-change, explore, propose) 在三个地方重复：

| 位置 | 角色 |
|------|------|
| `ai-system/skills/` | 权威来源 (canonical) |
| `projects/openspec-test/.*/skills/` | 重复 |
| `projects/pywechat-live-2608/openspec/.*/skills/` | 重复 |

### 1.3 syske-skills 未纳入体系

```
syske-skills/                        ❌ 游离在最外层
  andrej-karpathy-skills/
  other-skill/
  tr5-skill/
```

这些 skill 被排除在 ai-system 组织之外，导致管理分散。

### 1.4 ai-runtime/ 职责边界模糊

```
ai-runtime/
  agents/           空目录
  claude/           有 settings 文件（合理）
  commands/         空目录
  opencode/         有 node_modules（合理）
  superpowers/      空目录，命名易混淆
```

"superpowers" 命名暗示它与 ai-system 的 superpowers skills 有关，容易造成混淆。

---

## 2. 优化后的目录结构 (To-Be)

```
workspace/
│
├── ai-system/                       # 知识层 - 所有 AI Provider 共享
│   ├── bootstrap/                   #   环境初始化和引导配置
│   ├── cli/                         #   CLI 命令和 dispatcher
│   ├── config/                      #   系统配置
│   ├── governance/                  #   治理规则和策略
│   │   ├── policies/                #     质量门禁/路由策略/安全策略/skill 策略
│   │   └── review-standard.md       #     审查标准
│   ├── logs/                        #   系统日志（知识层操作日志）
│   ├── maintainers/                 #   维护者文档/健康检查
│   ├── metrics/                     #   指标定义和采集
│   ├── reports/                     #   架构报告和分析
│   ├── rfc/                         #   Request For Comments 设计文档
│   ├── routing/                     #   路由定义和管道配置
│   ├── skills/                      #   ★ 所有 Skill 的权威来源
│   ├── templates/                   #   模板（skill/route/spec/test）
│   ├── tools/                       #   系统级工具定义
│   └── workflows/                   #   ★ 所有 Workflow 的权威来源
│
├── ai-runtime/                      # 执行层 - Provider 专属
│   ├── opencode/                    #   OpenCode Runtime
│   │   ├── node_modules/            #     Runtime 依赖
│   │   └── ...                      #     Runtime 配置/缓存/插件
│   ├── claude/                      #   Claude Runtime
│   │   └── settings.json            #     Claude 配置文件
│   ├── codex/                       #   Codex Runtime (预留)
│   ├── gemini/                      #   Gemini Runtime (预留)
│   ├── cursor/                      #   Cursor Runtime (预留)
│   ├── sdk/                         #   各 Provider 共享的 SDK
│   └── scripts/                     #   Runtime 运维脚本
│
├── projects/                        # 业务项目层
│   ├── openspec-test/               #   项目 A
│   ├── pywechat-live-2608/          #   项目 B
│   └── archived/                    #   已归档项目
│
└── projects/                       # 外部业务资源（不参与 AI 系统）
```

---

## 3. ai-system/ 完整目录与职责

```
ai-system/
│
├── bootstrap/                       # 系统初始化
│   ├── ai-bootstrap.yaml            #   AI 系统引导配置
│   └── environment.yaml             #   环境参数
│
├── cli/                             # CLI 命令行工具
│   ├── commands/                    #   命令定义
│   ├── ai-run.js                    #   AI 运行入口
│   ├── ai.js                        #   CLI 主入口
│   └── dispatcher.js                #   命令调度器
│
├── config/                          # 系统全局配置
│
├── governance/                      # 治理体系（所有 Provider 共享）
│   ├── policies/                    #   策略定义
│   │   ├── quality-gates.md         #     质量门禁
│   │   ├── routing-policy.md        #     路由策略
│   │   ├── security-policy.md       #     安全策略
│   │   └── skill-policy.md          #     Skill 管理策略
│   ├── karpathy-guidelines.md       #   编码规范参考
│   ├── repo-lint.md                 #   仓库检查规则
│   ├── review-standard.md           #   审查标准
│   └── violation-rules.md           #   违规处理规则
│
├── logs/                            # 知识层操作日志
│   ├── errors/                      #   错误日志
│   ├── maintainer/                  #   维护操作日志
│   └── runs/                        #   执行记录
│
├── maintainers/                     # 维护文档
│   ├── capability-matrix.md         #   能力矩阵
│   ├── dependency-graph.md          #   依赖关系图
│   ├── duplication-report.md        #   重复检测报告
│   ├── health-check.md              #   健康检查
│   └── weekly-report.md             #   周报
│
├── metrics/                         # 指标系统
│
├── reports/                         # 架构报告
│   ├── architecture-review-2026-07.md
│   ├── MIGRATION-REPORT-v1.md
│   ├── REPOSITORY-OPTIMIZATION-REPORT.md
│   └── REPOSITORY-ARCHITECTURE-REPORT-v2.md   (本文件)
│
├── rfc/                             # 架构决策记录
│   ├── 0001-openspec-integration.md
│   ├── 0002-playbook-architecture.md
│   ├── 0003-java-maven-foundation.md
│   ├── 0004-repository-governance.md
│   ├── RFC-0001-repository-architecture.md
│   ├── RFC-0002-skill-specification.md
│   ├── RFC-0003-workflow-specification.md
│   └── RFC-0004-playbook-specification.md
│
├── routing/                         # AI 路由
│   ├── ai-routing.yaml              #   路由主定义
│   ├── fallback-routing.yaml        #   降级路由
│   └── pipeline-definitions.yaml    #   管道定义
│
├── skills/                          # ★ 所有 Skill 的唯一权威来源
│   ├── brainstorm/                  #   头脑风暴
│   ├── bugfix/                      #   缺陷修复
│   ├── codegraph-helper/            #   代码图谱
│   ├── contract-maintainer/         #   合约维护
│   ├── debug-issue/                 #   问题调试
│   ├── explore-codebase/            #   代码库探索
│   ├── grill-with-docs/             #   文档驱动的压力测试
│   ├── grilling/                    #   方案压力测试
│   ├── implement/                   #   实现技能
│   ├── java-maven/                  #   Java Maven 构建
│   ├── karpathy-guidelines/         #   Karpathy 编码规范
│   ├── mock-test/                   #   模拟测试
│   ├── openspec-apply-change/       #   OpenSpec 应用变更
│   ├── openspec-archive-change/     #   OpenSpec 归档变更
│   ├── openspec-explore/            #   OpenSpec 探索
│   ├── openspec-propose/            #   OpenSpec 提案
│   ├── refactor-safely/             #   安全重构
│   ├── repository-governor/         #   仓库治理
│   ├── repository-maintainer/       #   仓库维护
│   ├── review-changes/              #   变更审查
│   ├── skill-author/                #   Skill 创作
│   ├── spec-updater/                #   规格更新
│   └── task-splitter/              #   任务拆分
│
├── templates/                       # 模板库
│   ├── runtime/                     #   Runtime 模板
│   ├── routing-template.md          #   路由模板
│   ├── skill-template.md            #   Skill 模板
│   ├── spec-template.md             #   规格模板
│   └── test-template.md             #   测试模板
│
├── tools/                           # 系统工具
│
└── workflows/                       # ★ 所有 Workflow 的唯一权威来源
    ├── develop/                     #   开发工作流
    └── index.js                     #   工作流索引
```

### ai-system/ 目录职责清单

| 目录 | 职责 | 共享范围 |
|------|------|---------|
| `bootstrap/` | 环境初始化和引导 | 所有 Provider |
| `cli/` | CLI 命令和调度 | 所有 Provider |
| `config/` | 系统全局配置 | 所有 Provider |
| `governance/` | 治理规则、策略、标准 | 所有 Provider |
| `logs/` | 知识层操作日志（非 Runtime 日志） | 所有 Provider |
| `maintainers/` | 维护者文档、健康检查、能力矩阵 | 所有 Provider |
| `metrics/` | 指标定义和采集 | 所有 Provider |
| `reports/` | 架构报告和分析文档 | 所有 Provider |
| `rfc/` | 架构决策记录（ADR） | 所有 Provider |
| `routing/` | AI 路由定义 | 所有 Provider |
| `skills/` | **所有 Skill 的唯一来源** | 所有 Provider |
| `templates/` | Skill/Route/Spec/Test 模板 | 所有 Provider |
| `tools/` | 系统级工具定义 | 所有 Provider |
| `workflows/` | **所有 Workflow 的唯一来源** | 所有 Provider |

---

## 4. ai-runtime/ 完整目录与职责

```
ai-runtime/
│
├── opencode/                        # OpenCode Runtime
│   ├── node_modules/                #   npm 依赖
│   └── ...                          #   插件/缓存/日志
│
├── claude/                          # Claude Runtime
│   ├── settings.json                #   Claude 配置
│   └── settings.local.json          #   本地覆盖配置
│
├── codex/                           # [预留] Codex Runtime
│
├── gemini/                          # [预留] Gemini Runtime
│
├── cursor/                          # [预留] Cursor Runtime
│
├── sdk/                             # 各 Provider 共享的 SDK
│   └── ...                          #   SDK 包/类型定义
│
└── scripts/                         # Runtime 运维脚本
    └── ...                          #   部署/监控/备份脚本
```

### ai-runtime/ 目录职责清单

| 目录 | 职责 | 说明 |
|------|------|------|
| `opencode/` | OpenCode 执行环境 | node_modules + 插件 + 缓存 |
| `claude/` | Claude 执行环境 | 配置文件 |
| `codex/` | Codex 执行环境 | 预留 |
| `gemini/` | Gemini 执行环境 | 预留 |
| `cursor/` | Cursor 执行环境 | 预留 |
| `sdk/` | 跨 Provider SDK | 共享运行时工具 |
| `scripts/` | Runtime 运维 | 部署/监控/备份 |

### ai-runtime/ 严格禁止

- ❌ 不得包含 `skills/` 目录
- ❌ 不得包含 `workflows/` 目录
- ❌ 不得包含 `governance/` 文件
- ❌ 不得包含 `routing/` 定义
- ❌ 不得包含 `templates/`（运行时本地缓存除外）
- ✅ 只能保存 Runtime、SDK、Package、Node Modules、Scripts、Config、Plugin、Cache、Logs

---

## 5. Skill / Workflow / Governance 归属检查

### 5.1 Skill 归属

| 位置 | 判定 | 操作 |
|------|------|------|
| `ai-system/skills/*` (23个 skill) | ✅ 正确 | 保留 |
| `ai-system/runtime/agents/` | ✅ 空目录，无 skill | 迁移到 ai-runtime |
| `ai-system/runtime/claude/` | ✅ 仅 adapter，无 skill | 迁移到 ai-runtime |
| `ai-system/runtime/opencode/` | ✅ 仅 adapter，无 skill | 迁移到 ai-runtime |
| `ai-runtime/agents/` | ✅ 空目录 | 可删除或保留为扩展点位 |
| `ai-runtime/superpowers/` | ✅ 空目录 | 建议删除或改名 |
| `projects/openspec-test/.claude/skills/*` | ❌ 重复 | 迁移到 ai-system/skills/ |
| `projects/openspec-test/.opencode/skills/*` | ❌ 重复 | 迁移到 ai-system/skills/ |
| `projects/pywechat-live-2608/openspec/.opencode/skills/*` | ❌ 重复 | 迁移到 ai-system/skills/ |
| `syske-skills/andrej-karpathy-skills/skills/*` | ❌ 未纳入体系 | 迁移到 ai-system/skills/ |
| `syske-skills/other-skill/*` | ❌ 未纳入体系 | 迁移到 ai-system/skills/ |
| `syske-skills/tr5-skill/*` | ❌ 未纳入体系 | 迁移到 ai-system/skills/ |

### 5.2 Workflow 归属

| 位置 | 判定 | 操作 |
|------|------|------|
| `ai-system/workflows/*` | ✅ 正确 | 保留 |
| `ai-runtime/**` | ✅ 无 workflow | 无需操作 |
| `projects/**` | ✅ 未发现 workflow | 无需操作 |

### 5.3 Governance 归属

| 位置 | 判定 | 操作 |
|------|------|------|
| `ai-system/governance/*` | ✅ 正确 | 保留 |
| `ai-runtime/**` | ✅ 无 governance | 无需操作 |
| `projects/**` | ✅ 未发现 governance | 无需操作 |

---

## 6. 重复项与冲突检测

### 6.1 重复 Skill: openspec 系列

**发现**: openspec 相关 4 个 skill 存在 4 份拷贝：

| 拷贝位置 | 类型 |
|---------|------|
| `ai-system/skills/openspec-apply-change/` | 权威来源 |
| `projects/openspec-test/.claude/skills/openspec-apply-change/` | 重复 |
| `projects/openspec-test/.opencode/skills/openspec-apply-change/` | 重复 |
| `projects/pywechat-live-2608/openspec/.opencode/skills/openspec-apply-change/` | 重复 |

**迁移方案**:
1. 保留 `ai-system/skills/` 作为权威来源
2. 项目中的 `.claude/skills/` 和 `.opencode/skills/` 改为软链接或引用机制（由 CLI Bootstrap 处理）
3. 如果当前工具不支持软链接，在 AI System CLI 中增加 `bootstrap` 命令，运行时自动将 `ai-system/skills/` 同步到项目的 `.opencode/skills/`

### 6.2 重复配置: ai-runtime/superpowers/

`ai-runtime/superpowers/` 为空目录且命名与 `ai-system` 的 superpowers skills 冲突。

**迁移方案**: 删除 `ai-runtime/superpowers/`。

### 6.3 syske-skills 整合

`syske-skills/` 中的三个 skill 集合应纳入 `ai-system/skills/`:

| 当前路径 | 目标路径 |
|---------|---------|
| `syske-skills/andrej-karpathy-skills/skills/karpathy-guidelines/` | `ai-system/skills/karpathy-guidelines/`（已存在，需要合并） |
| `syske-skills/other-skill/agent-browser/` | `ai-system/skills/agent-browser/` |
| `syske-skills/other-skill/agent-debug-diagnosis/` | `ai-system/skills/agent-debug-diagnosis/` |
| `syske-skills/other-skill/autowork/` | `ai-system/skills/autowork/` |
| `syske-skills/other-skill/index-project/` | `ai-system/skills/index-project/` |
| `syske-skills/other-skill/iterative-optimizer/` | `ai-system/skills/iterative-optimizer/` |
| `syske-skills/other-skill/multi-model-dispatch/` | `ai-system/skills/multi-model-dispatch/` |
| `syske-skills/other-skill/oncall-weekly-report/` | `ai-system/skills/oncall-weekly-report/` |
| `syske-skills/other-skill/outcome-benchmark-generator/` | `ai-system/skills/outcome-benchmark-generator/` |
| `syske-skills/other-skill/routing-benchmark-generator/` | `ai-system/skills/routing-benchmark-generator/` |
| `syske-skills/other-skill/skill-benchmark-generator/` | `ai-system/skills/skill-benchmark-generator/` |
| `syske-skills/tr5-skill/tr5/` | `ai-system/skills/tr5/` |
| `syske-skills/tr5-skill/yapi-openapi/` | `ai-system/skills/yapi-openapi/` |

> **注意**: `karpathy-guidelines` 在 `ai-system/skills/` 和 `syske-skills/` 中同时存在，需要检查内容差异并合并。

### 6.4 ai-system/runtime/ → ai-runtime/ 迁移

`ai-system/runtime/` 中所有内容应迁移至 `ai-runtime/`:

| 当前路径 | 目标路径 |
|---------|---------|
| `ai-system/runtime/index.js` | `ai-runtime/opencode/index.js` (或 `ai-runtime/sdk/`) |
| `ai-system/runtime/opencode.js` | `ai-runtime/opencode/opencode.js` |
| `ai-system/runtime/agents/adapter.js` | `ai-runtime/opencode/adapters/agent.js` |
| `ai-system/runtime/claude/adapter.js` | `ai-runtime/claude/adapter.js` |
| `ai-system/runtime/opencode/adapter.js` | `ai-runtime/opencode/adapter.js` |
| `ai-system/runtime/opencode/executor.js` | `ai-runtime/opencode/executor.js` |

---

## 7. 迁移步骤 (Migration Plan)

### Phase 1: Runtime 迁移 (低风险)

```
Step 1: 创建 ai-runtime 目标目录结构
Step 2: 将 ai-system/runtime/* 全部迁移到 ai-runtime/
Step 3: 删除 ai-system/runtime/（或保留为遗留目录标记）
```

### Phase 2: 项目 Skill 去重 (中风险)

```
Step 4: 确认 ai-system/skills/ 的 openspec skill 为最新版本
Step 5: 删除 projects/ 下所有 .claude/skills/ 和 .opencode/skills/ 中的重复项
Step 6: 在 ai-system/cli/ 中增加 bootstrap 命令
Step 7: 新增项目通过 bootstrap 自动从 ai-system/skills/ 引用技能
```

### Phase 3: syske-skills 整合 (中风险)

```
Step 8: 逐一检查 syske-skills 与 ai-system/skills/ 的重叠
Step 9: 将 syske-skills/ 下所有 skill 重定位到 ai-system/skills/
Step 10: 处理 karpathy-guidelines 的内容合并
Step 11: 确认所有引用 syske-skills 的配置已更新
Step 12: 删除 syske-skills/
```

### Phase 4: ai-runtime 清理 (低风险)

```
Step 13: 删除 ai-runtime/superpowers/（空目录）
Step 14: 评估 ai-runtime/agents/ 的必要性，清理或命名
Step 15: 明确 ai-runtime/commands/ 的用途或删除
```

---

## 8. 风险矩阵

| 风险 | 等级 | 缓解措施 |
|------|------|---------|
| ai-system/runtime/ 的 adapter 被 Active Provider 引用 | 🔴 高 | 迁移前确认引用链，更新 import 路径 |
| 项目中的 .opencode/skills 被 Provider 硬编码路径引用 | 🟡 中 | 迁移后配置 alias 或 symlink |
| syske-skills/karpathy-guidelines 内容差异 | 🟡 中 | 人工 diff 后合并 |
| 迁移后 Provider 加载 skill 路径变化 | 🟡 中 | bootstrap 命令自动处理路径映射 |
| 历史 skill 内容依赖 syske-skills 路径 | 🟢 低 | 保留兼容性 symlink 一个版本周期 |

---

## 9. 设计原理

### 为什么 Brain 与 Runtime 分离

```
┌─────────────────────────────────────────────┐
│  Provider A (OpenCode)  │  Provider B (Claude)  │
│  ┌───────────────────┐  │  ┌───────────────────┐  │
│  │ Skills (link)     │  │  │ Skills (link)     │  │
│  │ Workflows (link)  │  │  │ Workflows (link)  │  │
│  │ Governance (link) │  │  │ Governance (link) │  │
│  └────────┬──────────┘  │  └────────┬──────────┘  │
└───────────┼──────────────└───────────┼──────────────┘
            │                          │
            └──────────┬───────────────┘
                       │
          ┌────────────▼────────────┐
          │     ai-system/          │
          │  Skills / Workflows     │
          │  Governance / Routing   │
          │  Templates / Policies   │
          └─────────────────────────┘
```

**核心论点**: Skill、Workflow、Governance 是**知识资产**，不是运行时实现。OpenCode、Claude、Codex 只是这些知识的消费者。如果 skill 在 runtime 中维护，那么：

- 切换 Provider 需要迁移 skill
- 跨 Provider 复用 skill 需要复制
- 每个 Provider 的 skill 可能不同步

### 为什么 Skill 不能放 Projects

```
projects/
  project-a/
    skills/        ❌ 每个项目维护一套，必然不同步
  project-b/
    skills/        ❌ 不同项目 skill 能力不一致
```

所有项目都共享 AI System，skill 应该在 ai-system 中统一管理。

### 为什么不采用扁平结构

扁平结构 (如把所有内容放在 `ai-system/` 下) 的问题：

- Runtime 代码 (adapter/executor) 和知识代码 (skill/workflow) 耦合
- 新增 Provider 必须修改 ai-system 的目录结构
- 无法独立升级 runtime (升级 opencode 需要动整个 ai-system)

---

## 10. 未来扩展保证

### 新增 AI Provider

```
ai-runtime/
  opencode/       ← 已有
  claude/         ← 已有
  codex/          ← 新增，无需修改架构
  gemini/         ← 新增，无需修改架构
  cursor/         ← 新增，无需修改架构
```

**操作**: 只需在 `ai-runtime/` 下新增目录，无需修改 `ai-system/` 的任何内容。

### 新增项目

```
projects/
  project-a/      ← 已有
  project-b/      ← 新增，无需修改架构
  project-c/      ← 新增，无需修改架构
```

**操作**: 只需在 `projects/` 下新增目录。Skill 和 Workflow 通过 bootstrap 从 `ai-system/` 引用。

### 新增 Skill

```
ai-system/skills/
  my-new-skill/   ← 新增，无需修改架构
```

**操作**: 只需在 `ai-system/skills/` 下新增 skill 目录。所有 Provider 自动可用。

### 新增 Workflow

```
ai-system/workflows/
  my-new-workflow/   ← 新增，无需修改架构
```

**操作**: 只需在 `ai-system/workflows/` 下新增 workflow 目录。

### 架构不变量

| 场景 | 需要修改架构？ | 操作 |
|------|--------------|------|
| 新增 Provider | ❌ 不需要 | `ai-runtime/` 下加目录 |
| 新增项目 | ❌ 不需要 | `projects/` 下加目录 |
| 新增 Skill | ❌ 不需要 | `ai-system/skills/` 下加目录 |
| 新增 Workflow | ❌ 不需要 | `ai-system/workflows/` 下加目录 |
| 修改 Governance | ❌ 不需要 | `ai-system/governance/` 下修改 |
| 修改 Routing | ❌ 不需要 | `ai-system/routing/` 下修改 |

**五年不调整架构的覆盖范围**: 上述 6 种常见变更场景均不需要调整目录结构。

---

## 11. 遗留: templates/runtime/

`ai-system/templates/runtime/` 包含:
- `runtime-develop.md`
- `runtime-maintainer.md`

这些是**知识模板**（指导开发者如何开发和维护 runtime），而不是 runtime 执行代码。**可以保留在 `ai-system/templates/runtime/`**，因为它们是对 runtime 开发的指导文档，属于知识层。

---

## 12. 附录: 目录职责速查表

| 顶层目录 | 一句话职责 |
|----------|-----------|
| `ai-system/` | 所有 AI Provider 共享的知识层 |
| `ai-runtime/` | AI Provider 专属的执行层 |
| `projects/` | 业务项目代码 |
| `projects/`          | 外部业务资源（不参与 AI 系统） |

---

*Report generated by Architecture Maintainer*
*Next review: 2026-10-03*
