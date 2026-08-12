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
   - `unavailable`: [service, note...] — 未接入仓库(记录意图 + 原因)
3. ai-system 读取该映射(providers.project_repos),wizard 项目列表显示仓库服务名

## Repository available / unavailable 判定标准

**available** = 可直接操作的仓库,须**全部**满足:

1. 参与当前任务变更(proposal/design 涉及)
2. 本地路径存在且可访问(path 指向真实目录)
3. 有明确开发分支(dev_branch 已 checkout 或可创建)
4. 团队负责(可修改/提交,非只读参考)

**unavailable** = 参与变更但不可直接操作,满足**任一**:

- 路径不可用(缺失/在其他位置未接入)
- 分支未接入(dev_branch 未 checkout)
- 他人负责 / 只读参考
- 仅需了解接口无需改代码

**判定顺序**(新增服务时按序执行):

```
1. 参与当前任务变更?
   ├─ 否 → 不列入 workspace.yaml(只记录任务相关服务)
   └─ 是 → 2
2. 本地路径存在且可访问?
   ├─ 否 → unavailable(note: 路径缺失)
   └─ 是 → 3
3. 有可操作的开发分支?
   ├─ 否 → unavailable(note: 分支未接入)
   └─ 是 → 4
4. 团队负责(可修改提交)?
   ├─ 否 → unavailable(note: 他人负责/只读)
   └─ 是 → available(带完整字段)
```

**格式要求**:

- available 条目必须带 service/path/branch/dev_branch/remote 全字段
- unavailable 条目必须带 note(原因),无原因 → 无法判定,视为待补充

## workspace.yaml 初始化流程

**执行者:AI(开发流程中)**——当开始一个新的 workspace 项目时,AI 在
spec/develop 阶段负责创建并维护 workspace.yaml。

```
触发: 新建 workspace 项目(dev-setup / prepare 阶段识别到
      workspaces/<project_id>/ 无 workspace.yaml)

流程:
 1. 识别项目身份:读 openspec/changes/*/proposal.md 的任务说明,
    提取涉及的服务列表
 2. 对每个服务执行 available/unavailable 判定(见上)
 3. 生成 workspace.yaml:
    - task 段:当前任务 id/service/status/spec_ref
    - repository 段:按判定结果填 available/unavailable
    - specification 段:引用 openspec 主路径
 4. 校验:projects_repos(wizard) 能正确读取;无仓库项目填空映射
 5. 提交:workspace.yaml 是项目元数据,随项目提交(不入 ai-system 仓库)
```

**更新触发**(任务推进时):

- 新服务加入变更 → 按判定标准补充 available/unavailable
- 服务状态变化(分支接入/路径恢复)→ 移入/移出 available
- 任务完成 → task.status 更新为 completed

**禁止**:

- 不手动编造 path/remote(须来自真实仓库)
- 不把未参与变更的服务列入(保持 workspace.yaml 只含任务相关服务)
- 不双源维护(生命周期用 archived/ 目录,不在 workspace.yaml 存 status)

## Rationale

- **物理隔离,逻辑关联**:业务仓库留在 projects/(单一权威源),workspace 只记录"指向哪"
- **无软链脆弱性**:Windows junction 需管理员权限、易失效、git/构建工具兼容差
- **复用已有格式**:pywechat-live-2608/workspace.yaml 已含 repository 映射(2026-07),本决策是"让 ai-system 读取它",非新造格式
- **向后兼容**:无映射的项目显示 "(no repo mapped)",行为不变

## Consequences

- 项目选择时显示映射仓库(用户可确认项目对应的服务)
- 未来可扩展:repo_path_for() 定位仓库、分支提示、远程对比
- workspaces/<id>/contexts/ 保留给运行时状态(session-state.md 等),映射放 workspace.yaml(项目级元数据)
- available/unavailable 有明确判定标准,AI 可在流程中自动维护
- workspace.yaml 初始化由 AI 在项目创建时执行(见上文流程)

## References

- `AGENTS.md` — projects/ 与 workspaces/ 职责边界
- `workspaces/pywechat-live-2608/workspace.yaml` — 映射格式实例
- `cli/services/providers.py` — project_repos() 读取实现
