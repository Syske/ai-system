# Change Proposal: P73 — code-review 历史重入（选择项目 → 载入历史报告与分支 → 输入新需求）

| Field | Value |
|---|---|
| Status | **Proposed** |
| Type | Capability（为 code-review 增加第二条输入路径：历史重入；含会话元数据 sidecar + 一个候选 provider + 两个可选字段） |
| Author | AI Maintainer |
| Created | 2026-09-24 |
| Reference | 用户 2026-09-24 需求与三答（① 过去的报告 **+** 过去的分支，随后由用户提供新信息 ② 两者都要 ③ 交互对齐主链：选定后直接要新信息，**为空则仅重新加载过去的报告 + 过去分支**）；用户 2026-09-24 补充："code-review 分两条路：1 现状、2 选择项目→加载历史报告和分支→输入新需求"；`governance/outputs-convention.md`；`governance/policies/report-write-guard.md` |
| Process | OPERATIONS §12 Change Management |

---

## 1. Problem

### 1.1 现状事实（实测，带证据）

| # | 事实 | 证据 |
|---|---|---|
| F1 | code-review 只有**一种**输入范围：目标分支 **vs** 基线分支（base 默认 `master`）；无 commit range / 无历史状态选择 | `workflows/code-review.md:11`·`templates/runtime/runtime-code-review.md:164-169` |
| F2 | **不读取任何历史产物**（不读 openspec、不读既往报告）；唯一外部输入是可选 Confluence 页 | `workflows/code-review.md:52-55,83-87` |
| F3 | CLI 参数**进不来**：`_inputs` 的 ignore 集吞掉 `base/change/task/projects/...`，且只渲染 frontmatter 声明的 6 个字段 | `cli/services/prompt_builder.py:455-478,492` |
| F4 | 报告**只记分支名、不记 commit SHA**，且是自由散文 → **不可机器解析**，无"上次审到哪"的锚点 | `workflows/code-review.md:75-77`·`runtime-code-review.md:110,206-208` |
| F5 | 无任何代码/提示词扫描 `outputs/` 作为输入（唯一读它的是 chain 交接清单） | `cli/services/chain.py:166-171`（chain-manifest 读取）；全库 `outputs/` 引用均为写侧 |
| F6 | 历史会话命名**混用**：规范目录 4 个（`260828-vod-scheduler/`、`260911-python-db-manage-fix/`、`260921-external-blind-review/`、`250803-featCommentPermisson-王富国/`）+ 遗留扁平文件 2 个（`20260818-*.md`、`bcc768806-*.md`） | `outputs/code-review/` 实盘 |
| F7 | 输出约定已定义 code-review 的会话目录与"可选机器可读结果"槽位 | `governance/outputs-convention.md:17-31,68-70` |

### 1.2 需求（用户原话，2026-09-24）

> "现在的 code-review 支持可以选择历史产物的能力，类似开发主链。① 过去的报告 + 过去分支，然后让用户提供新的信息（需要做什么：继续 review、review 增量、其他需求）② 两者都要 ③ 类似开发主链：选择后直接让用户提供新的信息，**如果为空，则仅重新加载过去的报告 + 过去分支**。"
> "相当于 code-review 分两条路：1 现状；2 选择项目 → 加载历史报告和分支 → 输入新需求。"

### 1.3 为什么"类似开发主链"不等于照抄某种参数

主链**没有 `--from`/`--stage`**：其复用历史产物的实质是「**统一身份句柄（Change ID / Task ID）+ 重入 + 各阶段前置自检**」，唯一显式重入代码是 `cli/services/change_resume.py`（仅服务 prepare 重入与 verify 路径推导）。因此本需求对应的正确形态是：**给 code-review 一个可点选的历史句柄（会话），选定后由 runtime 载入历史上下文，再接受可选的新指令** —— 即"重入"，而不是新增续跑框架。

---

## 2. Goal

1. **路径 1（现状）保持零行为变化** —— 不选历史时为默认路径，成为向后兼容基线。
2. **新增路径 2（历史重入）**：选择项目 → 点选该项目的历史会话 → runtime 载入**过去的报告 + 过去的分支** → 用户提供**新需求**（继续 review / review 增量 / 其他需求）。
3. **新需求为空 = 仅重载**：只加载历史报告与分支，**不执行审查阶段、不产出 findings**，产出一份声明来源的"重载记录"。
4. 为后续"增量复审"提供**锚点**（分支对 + commit SHA 落盘），但**首版不做 findings 对账**。

---

## 3. Options

### 3.1 Option A — 只加一个自由文本"历史报告路径"字段（最省力）
用户手填历史报告路径。**否**：不可发现（要人记路径）、与既有"点选候选"范式（Change ID / Task ID）不一致、且无法解决 F4（无锚点）。

### 3.2 Option B — 路径 2 = 会话点选 + runtime 载入 + 可选新需求（**推荐**）
- 新增两个**可选**字段：`History Session`（历史会话，候选按项目扫描）、`New Request`（新需求，可为空）。
- 选定后由 **runtime**（而非 wizard）承担"载入"：读 sidecar/报告 → 回填 base/target 分支对 → 按新需求分派行为；**为空则仅重载**。
- 新增会话元数据 sidecar（落盘分支对 + SHA），使"过去的分支"可机器读取。
- 复用既有范式：候选发现抄 `providers.change_dirs/task_ids`；同日重跑复用 `cli/utils/file.py unique_dir()`；写保护沿用 `report-write-guard.md`。

### 3.3 Option C — B + 完整会话清单与 findings 对账/增量引擎
把多次会话的 findings 结构化并对账（新增/已修复/仍存）。**暂不**：需要新的 findings schema、跨会话归并语义与大量历史数据兼容，属独立议题（Evolution Principle：等真实需要）。

### 3.4 Option D — 不动（让用户手工重跑并自己记分支）
不满足需求，且 F4 的锚点缺失会持续造成"增量复审"不可实现。

---

## 4. Recommendation

采用 **Option B**，分两期：

- **S1（本提案范围）**：两个可选字段 + 会话候选 provider + sidecar 记录（分支对 + SHA）+ runtime 重入语义（含空新需求=仅重载）。
- **S2（后续，需另行确认）**：增量复审的执行语义细化（delta 计算、报告章节、与历史 findings 的关系）。

### 4.1 待裁定子决策（每条附建议）

| # | 决策 | 建议 | 理由 |
|---|---|---|---|
| 1 | 会话元数据文件命名 | **复用 outputs-convention 的 `<domain>-report.json` 槽位**（即 `code-review-report.json`），不新增命名 | 约定已定义"可选：机器可读结果"（`outputs-convention.md:22`）；再引入第三个名字＝第二套约定 |
| 2 | 报告名 `review-report.md` 与约定 `<domain>-report.md` 不一致 | **本轮不动**（既有偏差，doc-as-contract） | 改名会波及历史目录与外部引用，与本需求无关 |
| 3 | 候选默认行为 | 单选菜单 + 上次值高亮（`_previous_value` 范式）；**单候选不自动跳过** | 选历史是显式意图，自动采纳易误选 |
| 4 | 是否加 CLI 直传参数 | **不做**（wizard 为输入主通道） | 需同时改 argparse + ignore 集 + declared 过滤三处，且现状 Projects/Review Focus 亦无 flag |
| 5 | 遗留会话（无 sidecar） | 候选可见性降级：无法映射项目则**不入候选**；选中后 AI 读报告尽力回填分支 + WARN，**不 STOP** | 与 P64"旧产物 WARN 不 Stop"先例一致 |
| 6 | 路径 2 是否写主链 `review/<task-id>/` | **不写**，仍只写 `outputs/code-review/` | 避免与主链 review 阶段形成第二套审查契约 |

---

## 5. Proposed Changes

### 5.1 字段设计（两个可选字段）

| 字段 | 必填 | 候选来源 | 语义 |
|---|---|---|---|
| `History Session` | 否 | 按 `Projects` 过滤 `outputs/code-review/*/`（规范目录） | 空 = **路径 1**；非空 = **路径 2**，进入历史重入 |
| `New Request` | 否 | 自由文本 | 空 = **仅重载**；非空 = 按内容执行（继续 review / review 增量 / 其他需求） |

`New Request` 的三种典型语义由 **runtime 解释**（不新造枚举，保持字段为自由文本）：
- 「继续 review」= 同一分支对上补完/继续审查，沿用历史 focus；
- 「review 增量」= 仅审自历史锚点（SHA）以来的差异；**无 SHA 锚点 → 明确追问或声明回退为全量**（不得静默全量）；
- 「其他需求」= 按新范围审，但沿用已载入的历史上下文。

### 5.2 会话元数据（sidecar）

新会话在写报告的同时写机器可读 sidecar（`code-review-report.json`，见 §4.1-①）：

```json
{
  "session": {"descriptor": "vod-scheduler", "created_at": "2026-09-24T10:00:00+08:00",
              "mode": "initial|reentry", "source_session": "260828-vod-scheduler"},
  "projects": [{"id": "user-center-api", "base_branch": "master", "target_branch": "cc20260924_fix-x-api",
                "base_sha": "…", "target_sha": "…", "focus": "全面审查"}]
}
```

- **写**：runtime 报告阶段（与 `review-report.md` 同目录）
- **读**：新 provider（候选扫描）+ runtime（分支回填）
- 历史会话无 sidecar：候选标注 `legacy`，分支由 runtime 读报告尽力回填（§4.1-⑤）

### 5.3 分层改动清单

| 层 | 改动 | 约束/备注 |
|---|---|---|
| workflow `workflows/code-review.md` | frontmatter + 正文 `## Inputs` **同步**加 2 个可选字段；Outputs 增 sidecar；新增「History Re-entry（路径 2）」语义段 | ⚠️ **正文 96/100 行**（RFC-0003 上限）→ 必须**压缩既有文字**换取空间，不得超限（超限 ERROR） |
| runtime `templates/runtime/runtime-code-review.md` | 新增 Phase 1.A「History Re-entry」：选会话 → 读 sidecar/报告 → 回填分支对 → 按 `New Request` 分派（继续 / 增量 / 其他 / **空=仅重载**）；报告头声明来源会话、模式（initial/reentry）与锚点 | 263 行，无硬上限 |
| provider `cli/services/providers.py` | 新增 `review_sessions(wizard, values, project)`：扫 `wizard.outputs_root / "code-review"`，正则 `^\d{6}-` **过滤遗留扁平文件**，读 sidecar 取分支/SHA；目录缺失 → `[]`（不抛错） | 复用 `cli/services/wizard/output.py:_dirs` 范式；`outputs_root` 已可用（`wizard/__init__.py:81`） |
| wizard `cli/services/wizard/fields.py` | `_choices_for` 增分支（gated 于 `project`）；Projects 变更时清空 `History Session`（`_invalidate_dependents`） | 抄 Change ID / Task ID 范式（`providers.py:78-101`） |
| 配置/文案 `config/menu.yaml`、`config/i18n/zh.yaml` | 字段图标 / 说明 / 选项描述 | `workflows/*.md` 与 runtime 模板受 **repo-lint Rule 4 英文纪律**约束（字段名与用户面文案按既有做法处理） |
| 测试 | provider 单测（规范目录列出 / 遗留文件不列 / 缺目录不崩 / sidecar 解析）· frontmatter 一致性 · prompt 渲染断言（`## Inputs` 含新字段）· wizard 新字段不崩 · **路径 1 零回归** | `tools/checks/misc.py:400-421` 会把 cli/tests 全量并入 check.py |
| **不改** | 路径 1 行为 · 报告名 `review-report.md` · 主链 `review` 阶段 · `outputs/` 遗留文件迁移 · CLI 直传参数 | 明确非目标 |

### 5.4 门禁与契约影响

| 门禁 | 影响 |
|---|---|
| `check_frontmatter_consistency`（`tools/checks/workflow.py:339`） | frontmatter 与正文 Inputs 必须一致，否则 ERROR（含 `tools/check-contract.py` pre-commit） |
| `check_workflow_size`（`workflow.py:266`） | 正文 ≤100 行 —— 当前 96 行，**空间是本提案的主要实现约束** |
| repo-lint Rule 4（`tools/repo-lint.py:275-311`） | workflows/runtime 模板英文纪律 |
| `check_build`（`misc.py:189`） | 空 context 构建全部 workflow 不得报错 |
| `check_cli_tests`（`misc.py:400`） | 全量单测通过 |
| `prompt-metrics`（`tools/prompt-metrics.py:27`） | `## Inputs` 位于 `# Task` 之后 → **prefix 稳定性不受影响**（仍应实测确认 16/16） |
| `proposal-audit` | 本提案登记 `reports/PROPOSALS.md`（索引同步） |

---

## 6. Validation Plan

1. **路径 1 零回归**：不选 `History Session` 时，prompt 渲染与产物路径与现状一致（对比测试）
2. **候选发现**：规范目录全部列出；两个遗留扁平文件**不出现**；`outputs/code-review/` 缺失时返回空列表且不崩
3. **空新需求=仅重载**：不执行审查 Phase、不产出 findings；新会话目录内报告头声明 `source_session` 且模式为 `reentry`
4. **分支回填**：用户未改分支时，新报告记录的 base/target 分支对 == 来源会话
5. **增量锚点**：有 SHA 时可声明 delta 范围；无 SHA 时**明确追问或声明回退为全量**（不得静默）
6. **sidecar 往返**：写入后 provider 能读回（幂等；重跑不重复写入同一会话）
7. **门禁**：单测（624 + 新增）全绿 · `tools/check.py` PASS · repo-lint 0 BLOCKER/0 ERROR · path-audit 0 broken · prompt-metrics prefix 16/16
8. **语言/体积**：`workflows/code-review.md` 正文 ≤100 行；`prompt-metrics` 记录 Always Load 体积变化

---

## 7. Risks

| # | 风险 | 缓解 |
|---|---|---|
| R1 | 与主链 `review` 阶段语义重叠（出现第二套"审查"契约） | §4.1-⑥：路径 2 不写 `review/<task-id>/`，仍在 `outputs/code-review/`；身份规则（P62/P63）如需引用则复用，不新造 |
| R2 | 历史报告不可机器解析（无 sidecar 的旧会话） | §4.1-⑤：AI 读报告回填 + WARN，不 STOP；无法映射项目则不列候选 |
| R3 | 增量语义歧义（历史 findings 与新 findings 关系） | 首版**只做锚点 + 声明**，不做对账（Option C 明确排除） |
| R4 | workflow 正文 100 行上限挤压（当前 96） | 压缩既有文字；若确实放不下，把语义细节全部下沉 runtime（workflow 只留字段与一句话） |
| R5 | `outputs/` 不在 git，历史会话可能被清理（与 2026-09-24 事故同源风险） | 报告/sidecar 属工作区态；长期留存需求另立议题（不塞进本提案） |
| R6 | 用户误以为"选择 = 自动续跑" | 报告头与 wizard 说明均显式标注「路径 2 = 载入历史上下文」，空新需求时明确写"仅重载，未执行审查" |

---

## Review Log

| Role | Verdict | Notes |
|---|---|---|
| User | **Pending** | 需求已由用户三答明确（§1.2）；实现前需确认 §4.1 的 6 项子决定 |
