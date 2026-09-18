# Change Proposal: P55 — methodologies 整体移除（价值资产迁入 ai-system）

| Field | Value |
|---|---|
| Status | **Implemented** |
| Type | Structural（目录移除 + 环境解析/脚手架/配置/引用全量清理） |
| Author | AI Maintainer |
| Created | 2026-09-17 |
| Reference | 用户决策 2026-09-17（非强依赖判定：无代码消费，仅提示词级引用）；价值资产先迁后删；maintenance 日志 maintain-20260917-160000.md |
| Process | OPERATIONS §12 Change Management（用户确认后执行；本提案为追溯归档） |

---

## 1. Problem

`methodologies/`（21 文件，openspec-cn provider 资产）被判定为**非强依赖**：
- 无任何代码消费（`cli/` 仅 environment.py 解析 `methodologies_root` 路径，不读目录内容）；
- `providers.yaml` 的 `methodology.defaultProvider/registry` 为声明式（AI 提示词级语义）；
- 唯一具体文件引用 `tasks-template.md` 属主链任务卡模板（AI 自有资产，非上游方法论资产）；
- spec 工作流实际由 `openspec-cn` CLI + ai-system 自有 skill（propose-openspec/spec-updater）驱动。

同时存在 2 处漂移：`config/environments/local.yaml` 指向不存在的 `/tmp/...` 过期路径；
`interop_contract.yml` 注释引用已迁移的旧 Windows 路径。

## 2. Root-Cause

- methodologies 是"方法论 provider"概念的历史残留：上游 openspec-cn 资产中，真正被主链消费的
  只有任务卡模板（应属 ai-system）与 spec-updater skill（task-splitter 输入契约硬依赖，应随主链版本化）；
  其余（spec/plan 模板、commands、provider 元数据）仅被泛化指令引用，可再生成。
- 无版本管理（无 .git）→ 有价值资产存在丢失风险，需先迁后删。

## 3. Options

| 选项 | 说明 | 取舍 |
|---|---|---|
| A. 建仓版本化 methodologies | 独立 git 仓 | ❌ 非强依赖 + 可再生成，不值得建仓维护 |
| B. 保留目录 | 维持现状 | ❌ 漂移路径 + 双源风险 + 无版本 |
| C. **迁移有价值资产 + 整体删除** | 先迁后删 | ✅ 采用：任务卡模板/关键 skill 随 ai-system 版本化，引用全清 |

## 4. Decision（2026-09-17，用户确认）

**方案 C**：有价值资产先迁入 ai-system，再整体删除 methodologies，清理全部引用。

## Implementation Record (2026-09-17)

1. 迁移资产：
   - `tasks-template.md` → `ai-system/templates/prompts/tasks-template.md`（任务卡单一事实源；
     runtime-spec.md / task-splitter / evidence-levels 引用同步更新）；
   - `spec-updater`（SKILL.md + scripts/spec_updater.py）→ `ai-system/skills/`（task-splitter 输入硬依赖）；
   - `openspec-archive-change`、`openspec-explore` → `ai-system/skills/`（补主链归档/变更前探索缺口，
     On-Demand，skills/README 7→10）；
   - 不迁：openspec-propose（ai-system propose-openspec 已覆盖）、openspec-apply-change（develop/implement 已覆盖）。
2. 引用清理（24 处）：environment.py 解析链 / setup.py 脚手架+env 块 / providers.yaml methodology 段 /
   runtime-spec.md L198 provider 指令 / 10×runtime+bootstrap 环境上下文 methodologies_root /
   path-audit.py RUNTIME_ROOTS+正则 / extensions-init.py / env 模板×2 / local.yaml 过期路径 /
   pywechat runtime.yaml / interop_contract.yml 注释 / AGENTS.md / OPERATIONS.md / tr5 spec-design /
   archive-ipd 文档 / 初始化文档删除。
3. `methodologies/` 整目录删除（21 文件）。

**Validation**：check.py PASS（2 已知 WARN）；repo-lint 0/0/25 基线（后续迁移 skill 后 28，3 个
无 workflow.md 属既有技能架构口径）；path-audit 0 broken；unittest 294 OK；残留 methodolog 命中
均为英文概念词或历史档案。
