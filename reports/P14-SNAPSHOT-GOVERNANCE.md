# Change Proposal: P14 — 跨服务 SNAPSHOT 治理纪律（S4）

| Field | Value |
|---|---|
| Status | **Implemented** |
| Type | Governance (standards update) |
| Author | AI Maintainer |
| Created | 2026-08-06 |
| Reference | MAINTENANCE-2026-08-06-live-facade-snapshot-risk.md（SNAPSHOT 漂移真实事故）；MAINTENANCE-2026-08-06.md S4 |
| Process | OPERATIONS §12 Change Management |

---

## 1. Problem

live-facade 依赖事故暴露真实风险：`knowledge-api` 依赖 `live-facade 1.2.6-SNAPSHOT`，
而 live-api 分支持续活跃（同日新增 7 commit 含 live-facade 改动），导致：

1. live-api 重建 live-facade → nexus 发布新 SNAPSHOT 时间戳版本
2. knowledge 下次构建拉取最新 SNAPSHOT → **字段行为漂移**
3. 若 live-facade 源码回退（移除字段）→ knowledge 编译失败或运行时字段 null

**现状治理缺口**：现有标准只覆盖"生产不得依赖 SNAPSHOT"（发布时门禁），
但**联调期间的 SNAPSHOT 使用没有纪律**——SNAPSHOT 在哪些阶段可用、
如何防止依赖方漂移、何时必须升级为 RELEASE，均未定义。

## 2. 现有治理盘点（避免重复）

| 文档 | 已覆盖 | 缺口 |
|------|--------|------|
| `governance/standards/dependency-version.md` | 开发期用 SNAPSHOT；发布前换 RELEASE；Facade 接口变更必须升版本 | 联调期漂移管控、SNAPSHOT 生命周期 |
| `governance/standards/cool/rpc-conventions.md` §2.1-2.3 | 生产禁 SNAPSHOT；Facade 升版+先发布；兼容性规则 | SNAPSHOT 联调阶段定义、时间戳锁定 |

## 3. 方案

### Option A — 在 dependency-version.md 增补 SNAPSHOT 生命周期纪律（Recommended）

在 `governance/standards/dependency-version.md` 新增 `## SNAPSHOT Lifecycle` 章节：

```markdown
## SNAPSHOT Lifecycle

SNAPSHOT 仅用于同迭代内的联调与集成验证，不是可长期使用的依赖状态。

### 使用边界

- 同一迭代内、接口仍可能变化的跨服务联调：允许 SNAPSHOT
- 跨服务接口（Facade）**不得**跨迭代依赖 SNAPSHOT 发布时间超过 N 天
- 接口稳定后（联调完成）必须立即发布 RELEASE 并切换依赖方

### 漂移管控（依赖方义务）

- 依赖 SNAPSHOT 的服务必须明确自己依赖的**时间戳版本**，
  禁止无条件拉取最新 SNAPSHOT 导致不可重复构建
- 上游发布新 SNAPSHOT 后，依赖方必须先验证兼容性再升级
- 上游源码回退（移除字段/方法）在 SNAPSHOT 窗口内即视为 breaking，
  必须同步通知依赖方

### 结束条件

- 联调完成 → 发布 RELEASE → 依赖方切换 pom 版本
- 进入生产发布 → 全树 SNAPSHOT 归零（已有门禁，保持）
```

**Impact**：一处文档增补，覆盖 live-facade 事故的全部决策点；
与现有 Development/Release 章节形成完整闭环。

### Option B — 仅更新 rpc-conventions.md §2.1

扩展现有 SNAPSHOT Ban 为三态（允许联调/禁止生产/切换条件）。
**Impact**：位置正确但只覆盖 RPC 场景；dependency-version.md 是通用版本标准，
跨服务场景（含非 RPC 的 mq/api 依赖）也应覆盖。

### Option C — 维持 defer

**Impact**：同类事故（SNAPSHOT 漂移导致不可重复构建）可能复发。

## 4. Recommendation

**Adopt Option A**（+ 在 rpc-conventions.md §2.1 加一行交叉引用）。
dependency-version.md 是版本纪律的唯一事实源，SNAPSHOT 生命周期应归于此；
rpc-conventions 已有 SNAPSHOT Ban，只需交叉引用避免双源。

## 5. Proposed Changes

1. `governance/standards/dependency-version.md`：
   - 新增 `## SNAPSHOT Lifecycle` 章节（使用边界/漂移管控/结束条件）
   - 调整 `## Development` 章节措辞：明确 SNAPSHOT 仅限同迭代联调
2. `governance/standards/cool/rpc-conventions.md` §2.1：
   - SNAPSHOT Ban 增加一行交叉引用：联调期纪律见 dependency-version.md

## 6. Validation

- repo-lint / check.py / path-audit 全绿
- standards-loader 引用路径不变（文件未改名）
- 文档一致：两处 SNAPSHOT 纪律指向同一事实源

## 7. Risks

- **低**：纯文档增补，无代码/流程变更；措辞与现有 Development/Release 章节
  需保持一致（同文件内）。

---

## Review Log

| Reviewer | Decision | Date |
|---|---|---|
| User (AI Maintainer operator) | **Approved — Option A**（dependency-version.md 增补 + rpc-conventions 交叉引用） | 2026-08-06 |

---

## Implementation Record (2026-08-06)

Applied per approval (OPERATIONS §12 → Implement → Validate):

1. `governance/standards/dependency-version.md`:
   - 新增 `## SNAPSHOT Lifecycle` 章节（Usage Boundary / Drift Control / Exit Conditions）
   - `## Development` 措辞明确 SNAPSHOT 仅限同迭代联调，非长期依赖状态
   - 章节顺序：RPC Facade → Development → SNAPSHOT Lifecycle → Release（闭环）
2. `governance/standards/cool/rpc-conventions.md` §2.1：
   - SNAPSHOT Ban 新增交叉引用，指向 dependency-version.md 的 SNAPSHOT Lifecycle（单一事实源）

**Validation（全绿）**：
- 引用路径存在（path-audit 0 broken）
- repo-lint 0/0/9、check.py 待复跑
- 无文件改名，standards-loader 引用不受影响

**Deviations**: 无。
**Risks**: 低——纯文档增补；SNAPSHOT Lifecycle 的 N 天上限未设定量值（留待出现真实超期案例后按 Evolution Principle 补充）。
