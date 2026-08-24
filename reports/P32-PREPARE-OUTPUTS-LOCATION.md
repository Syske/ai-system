# Change Proposal: P32 — prepare 工作流子报告输出位置与 AGENTS.md 约定对齐

| Field | Value |
|---|---|
| Status | **Implemented** |
| Type | Fix（工作流定义 Outputs 位置文本缺陷） |
| Author | AI Maintainer |
| Created | 2026-08-24 |
| Implemented | 2026-08-24 |
| Reference | prepare 运行 202610-public-security-storage-no-ai-parse-optimization：子报告误置 outputs/prepare，发现 prepare.md Outputs 位置与 AGENTS.md / 自身 frontmatter 冲突 |
| Process | OPERATIONS §12 Change Management |

---

## 1. Problem（现状问题 / 缺口）

`ai-system/workflows/prepare.md` 的 Outputs 位置说明内部不一致，且与工作区约定冲突：

- frontmatter(line 15)：`outputs.base: "workspaces/<change-id>/"` —— 指向 workspace。
- body Outputs(line 68)：`sub-reports → outputs/prepare/{yyMMdd}-{desc}/` —— 指向 `outputs/<workflow>/`。
- AGENTS.md Artifact Directory Conventions(line 431–435)：prepare 属 **workspace-scoped 主链**，reports/artifacts 须 **workspace-anchored**，**不得入 `outputs/<workflow>/`**。

后果：本 run 直译 body 行(line 68)，把 6 份 prepare 子报告误置 `outputs/prepare/260824-.../`，脱离 change workspace，且 proposal 相对链接失效。已就地纠正本次产物（移至 `workspaces/<change-id>/reports/`），但**根因（工作流定义文本）未动**，后续 prepare 会复现同一误置。

## 2. Root-Cause（根因分析）

prepare.md body 的 Outputs 位置文本(line 68) 为 **stale**：早于 AGENTS.md "主链 workspace-anchored、不入 outputs/" 约定的细化，未随之更新。frontmatter `outputs.base` 已是 workspace-anchored（正确），body 未对齐，二者矛盾。属单点文本缺陷，非架构问题。

## 3. Options（至少两方案对比）

| 选项 | 含义 | 评估 |
|---|---|---|
| **A. 对齐 body 到 workspace-anchored（Recommended）** | line 68 子报告位置改为 `workspaces/<change-id>/reports/`（与 frontmatter base 一致、与 AGENTS.md 一致） | 最小文本改动；单一来源；与既有产物落点一致；零运行时影响 |
| B. 删除 body 子报告位置说明 | 子报告位置完全交由 AGENTS.md 约定，prepare.md 不再重复 | 去重更彻底，但工作流自身 Outputs 不自描述，可读性下降；AGENTS.md 变更须双地同步心智负担 |
| C. 维持 outputs/prepare 并重分类 prepare 为 projectless | 把 prepare 子报告留在 outputs/ | 否决：prepare 必需 change-id workspace，本质 workspace-scoped，不可 projectless；与 AGENTS.md 主链定义冲突 |

## 4. Recommendation（推荐方案 + 理由）

**方案 A**。理由：最小改动（单行文本）、与 frontmatter `outputs.base` 及 AGENTS.md 主链约定形成单一来源；与本次已纠正的产物落点（`workspaces/<change-id>/reports/`）一致；零契约/运行时影响。B 的去重收益不足以抵消可读性损失，留作后续若 AGENTS.md 与工作流 Outputs 出现第二次重复再评估（Evolution Principle：真实问题驱动）。

## 5. Proposed Changes（具体改动清单，待批准实施）

> 仅记录提案，**不直接修改** ai-system 工作流文件；批准后按 OPERATIONS §12 Implement 阶段执行。

1. `ai-system/workflows/prepare.md` line 68：将 `sub-reports → outputs/prepare/{yyMMdd}-{desc}/` 改为 `sub-reports → workspaces/<change-id>/reports/`（workspace-anchored，与 frontmatter `outputs.base` 对齐）。
2. （核对）prepare.md body Outputs 段其余路径表述：temp sources 已为 `workspaces/<change-id>/temp/`（正确）、Proposal 已为 `workspaces/<change-id>/openspec/changes/<change-id>/proposal.md`（正确），仅 sub-reports 一行需改。
3. 不动 AGENTS.md（约定已正确，是本提案的对齐基准）。
4. 不动 RFC-0003（Workflow Specification 不涉及具体 Outputs 路径，无需修订）。
5. 不创建 ADR（按 rfc/README "When to Create an ADR" 三条件：非 hard-to-reverse、非 surprising、无真实 trade-off——约定已由 AGENTS.md 决定，故 inline/spec 级文本修正即可，无需 ADR）。

## 6. Validation Plan（如何验证）

- `python tools/check.py` / `python tools/repo-lint.py` / `python tools/path-audit.py` 全绿（文本改动无结构影响）。
- `python tools/proposal-audit.py`：P32 登记一致、无新增 WARN。
- 回归：重跑一次 prepare（需 change-id workspace），确认子报告落 `workspaces/<change-id>/reports/`、proposal 相对链接可达。
- `grep -rn "outputs/prepare" ai-system/workflows/` 实施后应无活跃 Outputs 指令（仅历史日志/提案引用）。

## 7. Risks（风险与缓解）

- 风险极低：纯工作流文档文本改动，无运行时/契约/数据影响。
- 缓解：实施时与 frontmatter `outputs.base` 措辞保持一致，避免再次漂移；若将来确有 projectless prepare 需求（目前无），再评估独立 outputs 落点（届时为真实新需求，非本提案范围）。

---

## Review Log

| Reviewer | Decision | Date |
|---|---|---|
| User (AI Maintainer operator) | **Pending** | 2026-08-24 |

---

## Implementation Record

（批准并实施后追加：Applied per approval → 改动清单 → Validation 结果 → Status 置 Implemented + 同步 PROPOSALS.md/README）
