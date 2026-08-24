# Proposal Policy

定义 ai-system 变更提案（`reports/P*.md`）的格式、维护流程与门禁。

## 1. 提案格式（Required Template）

每个提案 `reports/P<序号>-<主题>.md` 必须包含以下首部表与章节：

```markdown
# Change Proposal: P<序号> — <主题>

| Field | Value |
|---|---|
| Status | **Proposed** |
| Type | Structural (…) / Fix / Doc |
| Author | AI Maintainer |
| Created | YYYY-MM-DD |
| Reference | 触发来源（如 MAINTENANCE-… 的 F#/S#；用户请求） |
| Process | OPERATIONS §12 Change Management |

---

## 1. Problem        # 现状问题 / 缺口
## 2. Root-Cause     # 根因分析（若适用）
## 3. Options        # 至少两个方案对比（含 Recommended）
## 4. Recommendation # 推荐方案 + 理由
## 5. Proposed Changes  # 具体改动清单
## 6. Validation Plan   # 如何验证
## 7. Risks             # 风险与缓解

---

## Review Log

| Reviewer | Decision | Date |
|---|---|---|
| User (AI Maintainer operator) | **Pending** | YYYY-MM-DD |

---

## Implementation Record (YYYY-MM-DD)   # 实施后追加

Applied per approval (OPERATIONS §12 → Implement → Validate):
1. …（具体改动）
**Validation**: check.py / repo-lint / path-audit 结果
```

**规则**：
- 章节顺序固定（1 Problem → 7 Risks）。
- `Status` 字段、`Review Log`、`Implementation Record` 为机读字段（proposal-audit 解析）。
- Review Log 决策后必须把 `Status` 更新为对应状态（见 §2），并同步 `reports/PROPOSALS.md` 索引。

### 1.1 Sizing Triage

When a routine run discovers a change worth recording, triage by impact surface
(trigger rule: see the **Issue Capture** section in `AI_OPERATING_RULES` — before
recording, JIT-load this file + OPERATIONS §12).

| Category | Criterion | Handling |
|---|---|---|
| In-place minor fix (L1, **no P-proposal**) | Single-point doc-drift / typo / broken link / text alignment; does NOT touch structure/contract/multiple files/standards/new capability | Fix in place after confirmation + record in diagnostic-log + the maintenance report "Fix Actions" section |
| Proposal (via §12) | Touches structure / contract / multiple files / standards / new capability | File a P-proposal per §1 template + register in PROPOSALS.md/README |

> Same threshold as the `maintain` command minor-fix bypass; this section is the
> single source of truth for it.
>
> **Retroactive evidence**: P32 (prepare workflow Outputs location, a single-line text
> alignment) belonged to the in-place minor-fix path but was filed as a full
> P-proposal — the typical over-processing that occurs when this triage rule is
> absent. Future cases of the same kind should take the in-place bypass.

## 2. 状态机（Lifecycle）

| 状态 | 含义 | 触发 |
|---|---|---|
| `Proposed` | 已提出待评审 | 新建提案时 |
| `Approved` | 评审通过，待实施 | Review Log 记录 Approved 后，**应同步 Status** |
| `Rejected` | 评审否决 | Review Log 记录 Rejected |
| `Implemented` | 已实施并验证 | 追加 Implementation Record 后，Status 置为 Implemented |
| `Archived` | 已归档（不实施） | 明确放弃时 |

**规则**：
- Status 与 Review Log / Implementation Record **必须一致**（门禁校验）。
- 已实施提案不删除，保留为历史记录（`PROPOSALS.md` 状态列同步）。

## 3. 维护流程（Process）

1. **发现问题**：实战 / 巡检中发现缺口 → 生成提案（§1 模板）。
2. **索引登记**：在 `reports/PROPOSALS.md` 加一行（状态 Proposed）。
3. **评审**：用户确认方向（Approved / Rejected）。
4. **状态更新**：提案 Status + PROPOSALS.md 同步。
5. **实施**：OPERATIONS §12（Analyze → Propose → Review → Approve → Implement → Validate）。
6. **记录**：追加 Implementation Record，Status → Implemented，PROPOSALS.md 同步。
7. **巡检回收**：每次维护运行 `tools/proposal-audit.py`，评估遗留（Proposed / 未关闭待办）。

## 4. 门禁（Gate）

`tools/proposal-audit.py`（接入 `tools/check.py` 检查项）：

| 检查 | 失败 |
|---|---|
| 提案文件必须含 `Status` 字段 | ERROR |
| `Status` 必须是合法值（Proposed/Approved/Rejected/Implemented/Archived） | ERROR |
| `Approved` 但 Review Log 无 Approved 记录 | WARN |
| `Implemented` 但无 Implementation Record | ERROR |
| `reports/PROPOSALS.md` 索引与提案文件 Status 不一致 | WARN |
| 存在遗留（Proposed / 未关闭 `- [ ]` 待办） | WARN（巡检报告列出） |

## 5. Reference

- OPERATIONS §12（Change Management）
- AI_OPERATING_RULES（Evolution Principle / Minimal Change）

---

## 6. 报告登记纪律（Reports Index Discipline）

`reports/README.md` 是全量报告分类索引（提案/维护/评估/规范/迁移/分析）。
所有新报告必须登记，防止待办失联：

| 报告类型 | 登记位置 | 强制程度 |
|----------|----------|----------|
| 提案 P 系列 | `PROPOSALS.md`（门禁自动校验）+ README 索引 | 强制（proposal-audit ERROR/WARN） |
| MAINTENANCE / 评估 / 季度 / 规范 / 迁移 / analysis | `README.md` 对应分类表 | 强制（proposal-audit WARN） |

**规则**：

1. 新报告写入后**即登记**对应分类表（日期/主题/文件/遗留待办）。
2. 遗留待办有值的报告，闭环后在索引中更新该列。
3. 索引文件本身（`reports/README.md`、`PROPOSALS.md`）不登记。
4. `tools/proposal-audit.py` 校验：reports/ 下存在但未被 README 索引引用的 `.md` 文件 → WARN。
