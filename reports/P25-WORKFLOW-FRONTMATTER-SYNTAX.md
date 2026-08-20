# Change Proposal: P25 — 统一 Workflow 资产语法为 SKILL.md frontmatter 约定

| Field | Value |
|---|---|
| Status | **Proposed** |
| Type | Structural (资产语法/契约层) |
| Author | AI Maintainer |
| Created | 2026-08-20 |
| Reference | 用户请求：必填项可管理化 + 讨论「workflows/*.md→*.yaml」与「复用 skill 语法」；MAINTENANCE-2026-08-20 |
| Process | OPERATIONS §12 Change Management |

---

## 1. Problem

1. **workflow 的必填/可选/默认/类型散在 `workflows/*.md` 的 `## Inputs` 散文里**，靠 `workflow_reader.py` 正则解析（`Required:`/`Optional:`/内联 `(default: X)`）。字段元数据（类型/校验/条件必填）无从表达，`必填项管理`、以及 chain/参数系统按需解析（P 系后续：chain 按链声明 `project: required|none`）都缺一个**结构化、可校验**的机器契约。
2. **skill 与 workflow 语法不统一**：Skill 用 `SKILL.md`（YAML frontmatter + markdown 正文，有现成解析 `skill_scan._read_frontmatter`）；Workflow 用纯 markdown 八段。两套资产本可通过同一"frontmatter 契约 + 正文叙事"约定统一，降低心智/维护成本。
3. 若为管理必填项而**把定义迁去 YAML**（`.md→*.yaml` 或塞 `config/workflows/*.yaml`），会破坏唯一语义源，且 `config/workflows/` 按 AI_DEVELOPMENT_CONTRACT §2 是 **Registry-only**，回胀为 A1 反模式（maintain 红线明令禁止）。

## 2. Root-Cause

- `workflows/*.md` 同时承担**机器契约**（Inputs 解析）与**嵌入 prompt 的叙事**（整文件给 AI 当指令，含 Purpose/Context/Outputs/Exit 推理）。当前把机器契约硬编码进 markdown 散文，导致解析脆弱、元数据缺失。
- skill 已确立"frontmatter 契约 + markdown 叙事"形态，workflow 未对齐 → 两套资产语法并存。

## 3. Options

- **Option A — workflows/*.md 全文替换为 *.yaml**
  优点：Inputs 全结构化。缺点：叙事段（Context/Exit/Outputs 散文）只能退化为 YAML 块标量，丢 markdown 渲染且难读；15 个文件全量重写 + reader/audit/scaffold/prompt/repo-lint 全改；踩 §2 单源/A1 红线；非由失败驱动。**不推荐**。
- **Option B — 把必填项塞进 config/workflows/*.yaml**
  优点：快速结构化。缺点：违反 AI_DEVELOPMENT_CONTRACT §2（该目录 Registry-only）+ A1 回胀红线 + 与 workflow .md 双源漂移。**不推荐 / 禁止**。
- **Option C — 复用 SKILL.md 语法：workflows/*.md 顶部加 YAML frontmatter（机器契约），正文保留 markdown 叙事**（**Recommended**）
  优点：格式与 skill 统一；必填/默认/类型/next/runtime 结构化可校验可复用；唯一语义源仍在同一个 `.md` 文件（不新增来源、不踩 §2）；正文叙事与 prompt 渲染不变；改动面小（共享解析器 + 15 个 .md 各加一段 frontmatter，正文基本保留）。缺点：需约定"frontmatter 权威、正文 ## Inputs 可移除或由渲染生成"；属结构性变更须走提案试点。**推荐**。

## 4. Recommendation

采用 **Option C**：将 workflow 资产语法统一为 skill 的 `SKILL.md` 约定（**frontmatter 承载机器契约 + markdown 承载叙事**），并让 skill 与 workflow 共享一个泛化 frontmatter 解析器。

```markdown
---
name: bugfix
description: Diagnose and fix software defects.
workflow:                       # 机器契约（结构化）
  runtime: templates/runtime/runtime-bugfix.md
  inputs:
    - {name: "Project ID", required: true}
    - {name: "Mode", required: false, default: "standard"}
  next: [review, hotfix-test-doc]
---
# Workflow: BugFix
## Purpose / Context / Outputs / Exit Criteria   # 叙事保留，供 prompt
```

- frontmatter = 唯一机器来源；`workflow_reader` 优先读 frontmatter，缺失时回退旧 `## Inputs`（向后兼容、免推倒）。
- 正文 `## Inputs` 是否保留：**以 frontmatter 为唯一来源**，正文不再重复（可过渡期由渲染生成），避免双源漂移。
- chain 侧必填参数/是否需项目在 `chains.yaml` 按链声明，与 workflow frontmatter 解耦。

## 5. Proposed Changes

- [ ] 泛化共享 frontmatter 解析器（基于 `skill_scan._read_frontmatter`，供 skill 与 workflow 共用）
- [ ] `workflow_reader.py` 支持读 frontmatter（inputs/required/optional/defaults），回退旧解析
- [ ] 试点：`workflows/bugfix.md` 加 frontmatter，跑通 reader + `workflow-command-audit` + CLI 测试
- [ ] 试点通过后铺开其余 14 个 workflow 加 frontmatter
- [ ] `workflow-command-audit.py` / `workflow-scaffold.py` 兼容 frontmatter（八段合规演变为「frontmatter 契约 + 正文段」双校验）
- [ ] `prompt_builder` inputs 从 frontmatter 渲染（正文嵌入照旧）
- [ ] `workflow` frontmatter 增 `outputs` 基路径约定（生成报告 → `outputs/<workflow>/{yyMMdd}-<desc>/`；OpenSpec 工件 → `workspaces/<project_id>/openspec/...`），使 main-chain 各工作流产物目录显式、可被 chain-manifest / 外部 skill 解析
- [ ] 文档：`workflows/README.md`、AGENTS 说明统一资产语法；不新增 `config/workflows/*.yaml` 内容

## 6. Validation Plan

- `python tools/check.py` PASS 0（15 workflows 契约仍通过）
- `python tools/workflow-command-audit.py --repo-root .` 0 blocker（frontmatter 后八段/Next 契约仍闭合）
- `python -m unittest discover -s cli/tests`（含新增 frontmatter 解析/回退用例）全过
- 手工：`aic` 选 bugfix，确认输入收集（Project ID 必填、Mode 默认 standard）行为不变；prompt 含叙事正文

## 7. Risks

- **叙事段误被裁**：正文 markdown 必保留（只把机器契约进 frontmatter），review 时逐文件比对正文。
- **双源漂移**：严格"frontmatter 唯一权威"，正文 `## Inputs` 移除或渲染生成；audit 门禁校验两者一致。
- **回退兼容**：reader 保留旧 `## Inputs` 解析分支，过渡期两套并存，试点不通过即回退。
- **范围蔓延**：本提案**不做** `.md→*.yaml` 全替换、**不动** `config/workflows/*.yaml`（架构红线）。

---

## Review Log

| Reviewer | Decision | Date |
|---|---|---|

## Implementation Record (YYYY-MM-DD)

<!-- 实施后追加：改动文件 / 验证结果 / 回归备注 -->
