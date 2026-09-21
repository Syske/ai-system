# Change Proposal: P58 — projects/ 真实目录 + repositories 源按需 clone

| Field | Value |
|---|---|
| Status | **Implemented** |
| Type | Structural (workspace provisioning 架构) |
| Author | AI Maintainer |
| Created | 2026-09-21 |
| Reference | MAINTENANCE-2026-09-21.md F6（双仓库根机器观察）+ 用户设计指示（2026-09-21：projects 改真实目录，按 repositories 解析项目，缺失先 clone，repositories 先于 projects 初始化和创建；按需 clone） |
| Process | OPERATIONS §12 Change Management |

---

## 1. Problem

1. **projects/ 依赖机器特定的软链/外部目录**：本机 `projects/` 为符号链接 →
   `/mnt/d/workspace/project-resources`（D 盘资源池，87 项），由 `setup.py link_repos`
   「扫描 + 软链」供给，机器/路径强耦合、跨机器不可移植。
2. **双副本分叉风险**（F6）：容器 workspace.yaml 映射指向真实目录
   `/home/syske/ws/projects/<svc>`（7 服务），而 projects/ 软链指向 D 盘池（87 项）；
   两份独立副本（inode 不同）当前 HEAD 一致，一旦分叉，同一 service 按入口不同
   读到不同代码。
3. **repositories/ 未被用于按需供给**：`repositories/`（77 个服务元数据：
   git url / default_branch / technology）已存在，但仅被 dev-setup 读取
   （git URL / 分支 / 技术），没有任何「缺失即 clone」的机制；`setup.py` 只 scaffold
   空目录，77 个 yaml 由外部生成、无校验工具。
4. **无容器 Projects 候选 = 软链目录**：P57 后无容器回退 `projects_dirs` 仍读软链
   指向的 D 盘池（82 项），含非服务杂物（CLAUDE.md/Dockerfile 等），且依赖 D 盘挂载。

## 2. Root-Cause

- 供给模型为「扫描工作区 + 软链指向外部」，把「服务清单」与「本机仓库位置」耦合：
  服务清单的真正事实源应是 `repositories/`（git url 元数据），本地副本应可重建。
- 初始化顺序不满足依赖：`repositories/`（服务清单）应先于 `projects/`（本地副本）
  初始化，当前 setup.py 同一批次 scaffold 两者，无先后/校验关系。

## 3. Options

- **Option A（推荐）— repositories 源 + 按需 clone（真实目录）**：
  1. `repositories/` 先于 `projects/` 初始化和创建（bootstrap 顺序调整 + 生成/校验工具）；
  2. `projects/` 改真实目录（解链，空目录起步）；
  3. 新增统一 repo-ensure（按需 clone）：service_id → 读 `repositories/<id>.yaml`
     git.url → `projects/<id>` 缺失则 `git clone`，已存在则校验/拉取；
  4. Projects 字段候选 = repositories/*.yaml 服务 ∪ projects/ 已 clone 目录
     （有元数据 = 可 clone，不再依赖软链）；
  5. workspace.yaml 映射 path 归一为 `{repository_root}/{service_id}`。
  优点：跨机器可移植、单一事实源、消除双副本分叉；符合 AGENTS.md
  （repositories = 服务元数据，projects = 业务代码权威源）。
  缺点：需要 git + SSH 认证（codeup）；首次 clone 耗时；元数据缺失的服务需先补 yaml。
- **Option B — 保持软链 + 补 repositories 生成工具**：最小改动，但机器/路径耦合与
  双副本风险仍在。
- **Option C — 仅解链 + 手动 clone**：projects 改真实目录但不自动化，供给成本转嫁用户。

## 4. Recommendation

**Option A**。理由：
- 与 AGENTS.md 分层职责一致（repositories = 服务元数据；projects = 业务代码权威源）；
- 消除 F6 双副本分叉与软链机器耦合，换机/CI 可重建；
- repositories/ 元数据已覆盖 77 个真实服务（D 盘池缺失项多为杂物），按需 clone 只补缺失，
  不复制 D 盘池。

## 5. Proposed Changes

1. **初始化顺序**：`tools/setup.py` scaffold 顺序调整为 repositories → projects
   （真实目录）；`repositories/` 增加生成/校验工具（从既有 77 yaml 反推 schema，
   校验 git.url 存在、id 唯一）。
2. **解链**：`projects/` 软链 → 真实目录（本机一次性迁移；D 盘池转为只读参考源，
   不入 projects 供给）。
3. **repo-ensure（按需 clone）**：新增 `tools/repo-ensure.py`（或 cli/services 提供器）：
   - `ensure(service_id)`：读 `repositories/<id>.yaml` → `projects/<id>` 缺失则
     `git clone <url> projects/<id>`（检出 default_branch）；已存在则 `git fetch` 校验；
     元数据缺失 → 报错并提示补 yaml。
4. **候选来源**：`providers.projects_dirs` / `container_services` 之外新增
   `repositories_services()`（repositories/*.yaml 服务名）；Projects 字段候选 =
   `repositories_services() ∪ projects_dirs()`（有元数据优先标注可 clone）。
5. **消费接线**：dev-setup Phase 6（仓库绑定）调用 repo-ensure（缺失即 clone，替代
   「path 缺失 → unavailable」的静默降级）；scan/change-impact 运行前对所选 Projects
   逐个 ensure。
6. **workspace.yaml path 归一**：dev-setup Phase 10 写 `{repository_root}/{service_id}`；
   存量映射（/home/syske/ws/projects/* 绝对路径）迁移为仓库根相对路径。
7. **数据质量**：修正 italent workspace.yaml 中 user-center-api 误填 platform-api
   remote 的抄录错误（顺带）。
8. **测试**：repo-ensure（缺失 clone / 已存在跳过 / 元数据缺失报错）；候选并集；
   setup 顺序（repositories 先于 projects）。

## 6. Validation Plan

- 单测：repo-ensure 三态 + 候选并集 + scaffold 顺序（新增用例）
- `python3 tools/check.py` / `repo-lint.py` / `path-audit.py` 门禁
- 手工链路：本机解链后 bootstrap → repositories 校验 → 选 italent 容器服务 →
  缺失平台即 clone → scan/change-impact 可用；新机器（无 D 盘）同链路
- workspace.yaml 迁移后 `project_repos` 8/8 读通、aic 菜单服务名显示不变

## 7. Risks

- clone 需 SSH 认证可达 codeup；大仓 clone 耗时（可加并发/进度提示）。
- repositories 元数据缺失的服务（如 code-review/tasks/workspace 目录）不可按需 clone，
  需先补 yaml 或标记为非服务。
- 解链迁移会改变现有绝对路径引用（workspace.yaml /home/syske/ws/projects/*、
  可能的外部脚本）→ 一次性回填 + 验证。
- D 盘池不再自动同步，若后续仍用它作源需明确只读定位（避免与 repositories 冲突）。

---

## Review Log

| Reviewer | Decision | Date |
|---|---|---|
| User (AI Maintainer operator) | **Approved** | 2026-09-21 |

---

## Implementation Record (2026-09-21)

Applied per approval (OPERATIONS §12 → Implement → Validate):
1. `tools/repo-ensure.py`（新）：按需 clone —— ensure/check/list/validate 四模式，
   读 repositories/{id}.yaml git.url，缺失即 `git clone`（default_branch），已存在校验，
   元数据缺失报错提示；77 个 yaml 校验全过。
2. `cli/services/providers.py`：新增 `repositories_services()` / `repo_candidates()`
   （元数据 ∪ 本地克隆）；`_repo_path` 相对路径在任意平台解析到 projects_root
   （workspace.yaml 归一为 service id 可移植）。
3. `cli/services/wizard/fields.py`：无容器 Projects 候选 = repo_candidates
   （不再依赖软链资源池）。
4. `tools/setup.py`：BASE_DIRS 顺序调整（repositories 先于 projects，P58 依赖序）。
5. 文档接线：runtime-dev-setup Phase 7 缺失即 repo-ensure clone + Phase 10 path 相对化；
   aic-scan.md Step 1 clone 语义（英文，Rule 1）；tools/README.md 注册。
6. 机器迁移（本机）：projects/ 解链（原软链 → /mnt/d/workspace/project-resources 记录
   于诊断日志）→ 真实目录；7 服务移入（含 italent 4 + security 2 + ipd 图纸）；
   `git worktree repair` 修复全部 worktree 指针（实测 worktree list/status 正常）；
   workspace.yaml + project-context.yaml + 容器 AGENTS.md 路径归一为相对 service id；
   移除空 /home/syske/ws/projects。
7. 数据质量：italent workspace.yaml user-center-api remote 经复核为误报（实际正确），未改。
8. 测试：test_wizard_fields.py +16（repositories_services / repo_candidates 并集 /
   Projects 候选 / repo-ensure 三态 / validate）；test_skill_launcher.py _repo_path
   相对路径契约更新（P58 语义）。
**Validation**: 单测全量 317 OK；repo-lint 28 基线 0 BLOCKER；path-audit 0 broken；
check.py PASS（2 WARN 为既有提案遗留）；quick-check OK；实测迁移后 project_repos 6/6
读通、aic 菜单服务名显示正常、无容器候选 77 个、worktree 完整
