# Change Proposal: P44 — Worktree 约定完善（项目级隔离 + 生命周期管理）

| Field | Value |
|---|---|
| Status | **Implemented** |
| Type | Structural (workspace convention: worktree 命名/位置/生命周期) |
| Author | AI Maintainer |
| Created | 2026-08-31 |
| Reference | cool-italent-sync-plus dev-setup 提案（outputs/proposal/260831-cool-italent-sync-plus-dev-setup-worktree/solution.md） |
| Process | OPERATIONS §12 Change Management |

---

## 1. Problem（现状问题 / 缺口）

1. **worktree 位置无约定**：现有 3 个 worktree 散落在根 `worktrees/`，无项目归属，与 `worktrees/` = "Git worktree roots for project branches (ephemeral)" 的 AGENTS.md 描述不匹配。
2. **命名不统一**：旧 worktree 命名混合 `-` 和 `_`，部分 service 名重复出现（如 `incentive-api-cc20260630-featCommentPermisson-incentive-api`），无标准模板。
3. **无生命周期管理**：worktree 创建后无清理约定，3 个 prunable 状态的旧 worktree 无人处理，worktrees/ 目录成为"遗忘角落"。
4. **项目级 vs 根级职责未定义**：多项目并行时，根 `worktrees/` 无法区分归属，项目级 worktree 缺乏约定。

## 2. Root-Cause（根因分析）

AGENTS.md 仅描述 `worktrees/` = "Git worktree roots for project branches (ephemeral)"，但未定义：
- worktree 应创建在何处（项目级 or 根级）
- 命名规范（模板 + 校验）
- 生命周期（创建条件 / 清理条件 / 责任方）
- 与 `projects/`（权威源）的关系

导致实践中有先例但无规范，每个新项目各自摸索。

## 3. Options（至少两方案对比）

| 选项 | 含义 | 评估 |
|---|---|---|
| **A. 项目级 worktree + 根级非项目 worktree（Recommended）** | 项目级：`workspaces/<project-id>/worktrees/{service}-{branch}`；非项目级（如 code review）：根 `worktrees/` | 路径即隔离，命名无需加 project-id；符合 AGENTS.md "ephemeral" 语义；已有先例（incentive-api 等） |
| B. 全部放根 worktrees/ | 统一 `worktrees/{project-id}-{service}-{branch}` | 路径长；project 归属不直观；与既有根 worktrees/ 混杂 |
| C. 全部放 workspaces/<project-id>/ 下（不建 worktree） | 直接在 workspace 目录操作 | 失去 git worktree 隔离优势；无法保持 projects/ 干净 |

## 4. Recommendation（推荐方案 + 理由）

**方案 A**。理由：
1. `workspaces/<project-id>/worktrees/` 路径天然隔离项目，命名 `{service}-{branch}` 足够。
2. 与 AGENTS.md "ephemeral" 语义一致：worktree 随项目生命周期创建/销毁。
3. 根 `worktrees/` 保留给非项目场景（code review、临时探索等）。
4. `projects/` 始终保持 master 干净（权威源），开发分支在 worktree 隔离。

## 5. Proposed Changes（变更清单）

### 5.1 规范定义

新增 `governance/workspace-conventions/worktree.md`：

```markdown
# Worktree Convention

## 位置

| 场景 | 路径 |
|---|---|
| 项目开发分支 | `workspaces/<project-id>/worktrees/{service}-{branch}` |
| 非项目（code review / 探索） | `worktrees/{service}-{branch}` |

## 命名

模板：`{service}-{branch}`
- service = 服务名（与 projects/ 下目录名一致）
- branch = 分支名（P26 模板：`cc{date}_ipd_{desc}_{service}`）

## 生命周期

| 阶段 | 条件 | 责任方 |
|---|---|---|
| 创建 | dev-setup 阶段，用户决策使用 worktree | AI 提供步骤，运维执行 |
| 维护 | 开发期间 | 运维/开发者 |
| 清理 | 分支 merged 或 abandon 后 | 运维执行 `git worktree remove` |
| 垃圾回收 | `git worktree prune`（定期） | 运维 |

## 与 projects/ 的关系

- `projects/{service}` 始终保持 master（权威源、干净）
- 开发分支只存在于 worktree，不在 projects/ 切分支
- 同一分支不能同时在两个 worktree checkout
```

### 5.2 AGENTS.md 更新

在 `worktrees/` 行补充：

```
| `worktrees/` | Git worktree roots for project branches (ephemeral); 项目级见 `workspaces/<project-id>/worktrees/` |
```

### 5.3 旧 worktree 清理

- 3 个 prunable worktree（incentive-api / knowledge-api / training-manage-api）执行 `git worktree prune` 清理
- 确认根 `worktrees/` 目录干净后，记录为空

### 5.4 cool-italent-sync-plus 提案路径修正

将 `outputs/proposal/260831-cool-italent-sync-plus-dev-setup-worktree/solution.md` 中的 git 命令统一为项目级路径：

```diff
- cd projects/{service} && git worktree add ../../worktrees/{service}-{branch} {branch}
+ cd projects/{service} && git worktree add ../workspaces/202610-cool-italent-sync-plus/worktrees/{service}-{branch} {branch}
```

## 6. Validation Plan（验证方案）

- [x] `governance/workspace-conventions/worktree.md` 文件存在且内容完整
- [x] AGENTS.md worktrees 描述更新
- [x] 根 `worktrees/` 旧 worktree 已清理（`git worktree list` 确认）
- [x] solution.md 路径已修正
- [x] 约定可在后续项目中复用

## 7. Risks（风险与缓解）

| 风险 | 缓解 |
|---|---|
| 旧 worktree 清理可能丢失未提交内容 | 3 个旧 worktree 均为 prunable（分支已合并或 abandon），无内容损失 |
| 项目级路径较长 | 路径由 AI/脚本生成，用户无需手动输入 |

---

## 审查记录 / Review Log

| Reviewer | Decision | Date |
|---|---|---|
| User (AI Maintainer operator) | **Approved** | 2026-08-31 |

---

## Implementation Record（2026-08-31）

Applied per approval:
1. 新增 `governance/workspace-conventions/worktree.md`
2. 更新 AGENTS.md worktrees 描述
3. 清理 3 个旧 prunable worktree（incentive-api / knowledge-api / training-manage-api）
4. 修正 solution.md 中 git 命令路径

**Validation**: path-audit OK, extensions-lint OK, repo-lint OK
