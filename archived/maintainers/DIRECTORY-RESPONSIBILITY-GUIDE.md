# Directory Responsibility Guide

> 维护者: Architecture Maintainer
> 版本: v2 (2026-07-03)
> 适用原则: Brain/Runtime 分离，目录职责单一

---

## 三大顶层目录

```
workspace/
├── ai-system/       # 知识层 — 所有 AI Provider 共享的长期资产
├── ai-runtime/      # 执行层 — Provider 专属的执行环境
└── projects/        # 业务层 — 业务项目代码
```

### 黄金法则

> 一个问题出现在哪个目录，决定了它由谁解决、如何解决、以及解决周期的长度。

---

## ai-system/: 目录职责

| 目录 | 一句话职责 | 包含什么 | 不包含什么 |
|------|-----------|---------|-----------|
| `bootstrap/` | 环境初始化和引导 | yaml 配置、初始化脚本 | Runtime 安装包 |
| `cli/` | 命令行入口和调度 | dispatcher、命令处理 | Provider 专属 CLI |
| `config/` | 系统级配置 | 全局配置参数 | Runtime 专属配置 |
| `governance/` | 治理规则和策略 | 质量门禁、安全策略、skill 策略 | CI/CD 管道配置 |
| `logs/` | 知识层操作日志 | 错误日志、维护记录 | Runtime 日志 |
| `maintainers/` | 系统维护文档 | 健康检查、能力矩阵、周报 | 代码实现 |
| `metrics/` | 指标定义 | 指标配置 | 指标数据存储 |
| `reports/` | 架构报告 | 分析文档、迁移计划 | 临时日志 |
| `rfc/` | 架构决策记录 | ADR 文档 | 代码实现 |
| `routing/` | AI 路由定义 | 路由规则、管道定义 | 路由执行引擎 |
| `skills/` | **所有 Skill 的权威来源** | SKILL.md, 脚本, 引用 | Runtime adapter |
| `templates/` | 模板库 | skill/route/spec 模板 | 运行时缓存 |
| `tools/` | 系统工具定义 | 工具描述 | 工具实现 |
| `workflows/` | **所有 Workflow 的权威来源** | workflow.md, index.js | Workflow 执行引擎 |

### 决策速查

```yaml
# 属于 ai-system/:
- 这是知识吗？
- 这是所有 Provider 共享的吗？
- 这是长期资产吗？
- 答案全是 yes → ai-system/

# 不属于 ai-system/:
- 这是某个 Provider 专属的？
- 这是运行时/执行代码？
- 这是临时缓存/日志？
- 任意 yes → 不属于 ai-system/
```

---

## ai-runtime/: 目录职责

| 目录 | 一句话职责 | 包含什么 | 不包含什么 |
|------|-----------|---------|-----------|
| `opencode/` | OpenCode 执行环境 | node_modules, 插件, 缓存 | Skill |
| `claude/` | Claude 执行环境 | settings.json, 配置 | Workflow |
| `codex/` | Codex 执行环境 (预留) | — | Governance |
| `gemini/` | Gemini 执行环境 (预留) | — | Routing |
| `cursor/` | Cursor 执行环境 (预留) | — | Templates |
| `sdk/` | 共享运行时 SDK | 类型定义, 工具函数 | 业务逻辑 |
| `scripts/` | Runtime 运维脚本 | 部署, 监控, 备份 | Skill 逻辑 |

### 红线

```yaml
# 绝对禁止放入 ai-runtime/:
- SKILL.md          → 必须放在 ai-system/skills/
- workflow.md       → 必须放在 ai-system/workflows/
- governance 文件   → 必须放在 ai-system/governance/
- routing 定义      → 必须放在 ai-system/routing/
- 模板 (非缓存)     → 必须放在 ai-system/templates/
```

---

## projects/: 目录职责

| 目录 | 一句话职责 | 包含什么 | 不包含什么 |
|------|-----------|---------|-----------|
| `project-a/` | 业务项目 A | 业务代码 | Skill (引用 ai-system) |
| `project-b/` | 业务项目 B | 业务代码 | Workflow (引用 ai-system) |
| `archived/` | 已归档项目 | 历史项目 | AI 配置 |

### 红线

```yaml
# 绝对禁止放入 projects/:
- skills/          → 统一放 ai-system/skills/
- workflows/       → 统一放 ai-system/workflows/
- governance/      → 统一放 ai-system/governance/
- routing/         → 统一放 ai-system/routing/
```

---

## 新增内容决策树

```
要新增的内容
    │
    ▼
是 Skill / Workflow / Governance / Routing / Template / RFC?
    │                    │
    ├─ yes ──────────────┤
    │                    │
    ▼                    ▼
ai-system/              是 Provider 专属的执行代码 / SDK / 配置 / 缓存?
                         │                    │
                         ├─ yes ──────────────┤
                         │                    │
                         ▼                    ▼
                      ai-runtime/             是业务项目代码?
                                              │            │
                                              ├─ yes ──────┤
                                              │            │
                                              ▼            ▼
                                           projects/      不属于本 workspace
```

---

## 违规处理

| 违规类型 | 示例 | 处理 |
|---------|------|------|
| Skill 在 Runtime | `ai-runtime/opencode/skills/` | 立即迁移至 `ai-system/skills/` |
| Workflow 在 Project | `projects/foo/workflows/` | 立即迁移至 `ai-system/workflows/` |
| Governance 在 Runtime | `ai-runtime/governance/` | 立即迁移至 `ai-system/governance/` |
| Runtime 代码在 ai-system | `ai-system/runtime/` | 立即迁移至 `ai-runtime/` |
| Skill 在 Project | `projects/foo/.claude/skills/` | 迁移至 `ai-system/skills/`，改用引用 |

---

## 相关文档

- [Repository Architecture Report v2](../reports/REPOSITORY-ARCHITECTURE-REPORT-v2.md)
- [Migration Plan v2](../reports/MIGRATION-PLAN-v2.md)

---

*Guide maintained by Architecture Maintainer*
