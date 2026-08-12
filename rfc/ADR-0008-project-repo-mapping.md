# ADR-0008: Project ↔ Repository Logical Mapping

Status: Accepted

Date: 2026-08-08

---

## Context

ai-system 的 workspaces/<project_id>/ 存放 OpenSpec 工件与运行时状态,projects/
存放业务仓库。维护时希望在 workspaces 视角能定位项目的业务代码。候选方案:

1. **软链接迁移**:把 projects/ 下仓库软链到各 workspaces/<id>/projects/(junction)
2. **逻辑映射**:workspaces/<id>/workspace.yaml 记录 service → repo path/branch/remote

## Decision

**采用逻辑映射(Option 2),不迁移、不软链。**

1. `projects/` 保持业务代码权威源(AGENTS.md 契约不变)
2. `workspaces/<project_id>/workspace.yaml` 的 `repository` 段记录映射:
   - `available`: [{service, path, branch, dev_branch, remote}] — 已接入仓库
   - `unavailable`: [service...] — 未接入仓库(记录意图)
3. ai-system 读取该映射(providers.project_repos),wizard 项目列表显示仓库服务名

## Rationale

- **物理隔离,逻辑关联**:业务仓库留在 projects/(单一权威源),workspace 只记录"指向哪"
- **无软链脆弱性**:Windows junction 需管理员权限、易失效、git/构建工具兼容差
- **复用已有格式**:pywechat-live-2608/workspace.yaml 已含 repository 映射(2026-07),本决策是"让 ai-system 读取它",非新造格式
- **向后兼容**:无映射的项目显示 "(no repo mapped)",行为不变

## Consequences

- 项目选择时显示映射仓库(用户可确认项目对应的服务)
- 未来可扩展:repo_path_for() 定位仓库、分支提示、远程对比
- workspaces/<id>/contexts/ 保留给运行时状态(session-state.md 等),映射放 workspace.yaml(项目级元数据)

## References

- `AGENTS.md` — projects/ 与 workspaces/ 职责边界
- `workspaces/pywechat-live-2608/workspace.yaml` — 映射格式实例
