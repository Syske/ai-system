# Change Proposal: P28 — Change ID 自动生成（规则 slug 派生优先，AI 可选后续）

| Field | Value |
|---|---|
| Status | **Implemented** |
| Type | Enhancement (wizard 输入减负 + 命名一致性) |
| Author | AI Maintainer |
| Created | 2026-08-21 |
| Reference | 用户需求：首次 Change ID 应默认；变更过程 Change ID 是否由 AI 生成需先评估（评估结论：维持规则默认 A + 本提案） |
| Process | OPERATIONS §12 Change Management |

---

## 1. Problem

1. **首次 Change ID 无默认**：prepare 必填 Change ID，新建 change 须手动输入完整 id（已落地 `{YYYYMM}-` 前缀默认，见下）。
2. **命名负担与一致性**：change 描述（desc）部分依赖人工拟定，多 change 场景易出现命名风格漂移；trace/archive 按目录名解析，格式不稳会破坏对账。
3. **评估结论（2026-08-21）**：AI 生成的真正收益点是 **desc 派生**而非前缀（`YYYYMM-` 是规则事实，保证可追溯）；而 desc 派生**不需要 LLM**——从 Change Request 提取（首段有意义词 → 小写 kebab）是确定性规则，比 LLM 更一致；LLM 进 wizard 是架构级改动（向导层目前零 LLM 依赖），违反 Minimal Change，且自由生成破坏格式纪律。

## 2. 已落地（方案 A：规则默认）

- `ask_text` 支持 `default` 参数（tty 内联默认 / 非 tty `[默认]` 提示 + 空输入回退）。
- Change ID 手动输入时，无既有值（last_change）→ 建议可编辑默认 `{YYYYMM}-`（`change_resume.suggest_change_id()`），用户补 desc 即可；重入/已有值不建议。
- 验证：CLI 123 测试 / check.py PASS / repo-lint 25 WARN 无新增。

## 3. Options（后续增强）

| 选项 | 含义 | 评估 |
|---|---|---|
| **A. 规则默认（已实现）** | `{YYYYMM}-` 前缀 + 用户补 desc | 零成本，格式稳定，本提案基线 |
| **B. 规则 slug 派生（候选）** | 收集 Change Request 后自动提取 desc 生成完整 id（`{YYYYMM}-{slug}`），用户确认 | 确定性、零 LLM；**卡点**：需 Change Request 收集前置（现 required 顺序 `[Change ID, Change Request]`；重排会与 prepare 重入预填 hook 冲突，需一并设计） |
| **C. 向导内 LLM 生成（不推荐现阶段）** | 收集 Change Request 后 LLM 生成 slug | 架构级改动（wizard 引入 AI 推理）、延迟/成本、每次生成不一致、需格式约束+校验+去重 |
| **D. 混合（候选远期）** | A/B 打底 + "AI 生成"可选 | LLM 成本延迟到可选项；落点建议 skill 层（slug 生成 skill）而非 wizard 内嵌 |

## 4. 建议路径

1. **现维持 A**（已实现，门禁全绿）。
2. **B 记入触发条件**：若用户实际体验中"想 desc + 手输"负担仍重，或出现多 change 命名不一致实例 → 评估 B（含 required 顺序重排与重入 hook 的兼容设计）。
3. **C/D 不预引入**（Evolution Principle：不预先引入 LLM 到向导层；触发后再评估 skill 层落点）。

## 5. Open Items（2026-09-05 更新）

- [x] B：规则 slug 派生——**已由 P37 批次 1 实施**（prepare required 改 `[Change Request]`
  前置收集 + `change_resume.suggest_change_id()` 完整 slug `{YYYYMM}-{slug}` + `_manual_default`
  自动派生可编辑）——P28 卡点（Change Request 前置）随 P37 一并解除
- [ ] D：AI 可选生成（skill 层落点）——触发条件未到（不引入 wizard LLM，Evolution Principle）

## 6. Implementation Record (2026-09-05)

方案 A（`{YYYYMM}-` 前缀默认）随本提案早前已落地；方案 B（规则 slug 派生）由 **P37 批次 1**
实施覆盖（prepare `required: [Change Request]` + `suggest_change_id` + `_manual_default` 派生），
2026-09-05 收尾再补中文前导停用词剔除（P37 收尾）。Status → Implemented（PROPOSALS.md 同步）。
C/D 不引入（Evolution Principle）。

## 7. 追加：输入界面中文化（2026-08-25，用户确认实施）

**背景**：用户反馈 Change ID 输入界面（`from openspec/changes/` + `🔀 Change ID (required):`）交互不够友好——
英文 required 标记 + 英文技术路径 note，提示与输入框间隔感强。LANGUAGE_CONVENTION 明确
「Interactive prompts → 中文（跟随 config/menu.yaml locale）」，属用户可见交互层，应中文。

**范围**：全部工作流字段（不只 Change ID）——`required`/`optional` 标记、`field_notes` 说明统一中文化；
字段名本身（Change ID / Task ID 等）**保留英文**（机器契约标识符，输入值即英文，避免「中文标签 + 英文值」错位）。

**实施**（2026-08-25，用户确认后）：
- `cli/services/wizard/fields.py`：suffix `required/optional` → `必填/可选`（title 与 ask_text prompt 同步）
- `config/i18n/zh.yaml` field_notes：Project ID / Workspace ID / Change ID / Task ID / Mode / Operation /
  Workspace / Projects / Branch / Code Reference / Workspace Root 全量中文化（技术路径保留在括号内作参考）
- 验证：CLI 全量测试 OK；渲染确认 title/prompt 中文、字段值仍英文

> 关联：Prompt Anchor 英文化（AI 内部层）与输入界面中文化（用户交互层）分属 LANGUAGE_CONVENTION
> 两个方向，互不冲突——本提案第 6 节只覆盖用户可见交互。
