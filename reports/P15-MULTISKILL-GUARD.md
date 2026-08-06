# Change Proposal: P15 — 多-SKILL.md 输入防护（E3 缺陷修复）

| Field | Value |
|---|---|
| Status | **Implemented** |
| Type | Fix (skill-optimizer run_optimizer guard) |
| Author | AI Maintainer |
| Created | 2026-08-06 |
| Reference | E3 实测发现（并行与串行均复现）；P10 `--parallel` 引入背景 |
| Process | OPERATIONS §12 Change Management |

---

## 1. Problem

`run_optimizer` 对包含多个 `SKILL.md` 的输入目录处理存在设计缺陷：
所有 skill 共享同一个 `inner_skill_dir`，每次 `sm.revert_to(new_version)`
都把快照写回该目录 → **顶层 SKILL.md 被最后一个处理者覆盖**。

E3 实测证据（真实 LLM）：

| 模式 | 顶层 SKILL.md 结果 |
|------|-------------------|
| 并行（--parallel） | = 最后完成者（skill-b） |
| 串行（默认） | = 最后遍历者（skill-b） |

> 快照层正确（v1/v2/v3 各自完整），但工作区层互相覆盖——**静默数据污染**，
> 与 --parallel 无关，是"一个 workspace 只处理一个 skill"假设的越界使用。

## 2. 根因

- `skill_files = list(inner_skill_dir.rglob("SKILL.md"))` 会递归收集多个 skill
- `process_skill_file` 内 `SnapshotManager(inner_skill_dir, ...)` 对所有 skill 指向同一目录
- `--parallel`（P10）让多-skill 场景从"可预测的串行覆盖"变成"不确定的并发覆盖"

## 3. 方案（Option B — 拒绝多-skill 输入）

1. **前置 guard**：`run_optimizer` 在解析 input_dir 后、workspace 初始化**之前**，
   统计源目录下 SKILL.md 数量（排除 snapshots/.opt）；>1 时拒绝并提示
   "一次只优化一个 skill"。
2. **保留后置 guard**（既有）：迭代已有 workspace 场景的纵深防御。
3. 不做 per-skill workspace 拆分（Option A，下季度评估）。

**优点**：最小变更、零副作用（拒绝时不创建 workspace、不构造 LLM 客户端、
不发任何 API 调用）、防止静默污染。

## 4. 实施内容

1. `scripts/main.py` — `run_optimizer` 前置 guard（rglob 计数 + 拒绝返回 []）
2. `scripts/tests/test_multiskill_guard.py` — 回归测试（26 个测试全绿）：
   - 多-skill 目录被拒绝且无 workspace 残留
   - 单-skill 输入正常通过 guard

## 5. Validation

- 多-skill 输入：拒绝，`paths=[]`，`project/` 无 `multi-skill-*` 残留 ✅
- 单-skill 输入：正常流程不受影响 ✅
- smoke_test.py：全链路通过 ✅
- 26 unittest 全绿、repo-lint 0/0/9、check.py 0 warning、path-audit 0 broken ✅

## 6. Risks

- **低**：guard 只影响多-SKILL.md 输入（本就是不支持的错误用法）；
  单-skill 与迭代 workspace 行为不变。
- 无流程/注册表/文档变更。

---

## Review Log

| Reviewer | Decision | Date |
|---|---|---|
| User (AI Maintainer operator) | **Approved — Option B**（拒绝多-skill 输入） | 2026-08-06 |

---

## Implementation Record (2026-08-06)

1. `scripts/main.py` — 前置 guard（input_dir 计数检查）。
2. `scripts/tests/test_multiskill_guard.py` — 新增 2 个回归测试。
3. 验证全绿（见 §5）。

**Deviations**: 无。
**Risks**: Option A（per-skill workspace 拆分）留给下季度评估，
届时 `--parallel` 的真实并发价值才能兑现。
