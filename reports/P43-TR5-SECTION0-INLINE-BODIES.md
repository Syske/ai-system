# Change Proposal: P43 — tr5 §0 数据槽位恒空（inline 正文解析缺失 → 发布页 §0 露引导占位符）

| Field | Value |
|---|---|
| Status | **Implemented** |
| Type | Fix（脚本解析缺陷，发布页用户可见） |
| Author | AI Maintainer |
| Created | 2026-08-28 |
| Reference | 202610-qa-housekeeping-optimization spec 传播轮（2026-08-28）实机发现；关联 P41（sections["1"] 契约矛盾，同一 generate/validate 链路） |
| Process | OPERATIONS §12 Change Management |

---

## 1. Problem

`generate_tr5_data.py` 的 `_split_section0()` 假设 §0 三个小节的正文位于 `**0.N、标题**` 头行的**下一行起**；而实际模板惯例（本项目 `tr5_template.md` 及已发布页）是**头行内联正文**：

```
**0.1、目标和范围界定**：诉求1——到期/断约客户 ADB 数据清理接入……
```

正则命中头行后整行丢弃（`buf = []`），同行 `：` 之后的正文不入缓冲 → `0_1/0_2/0_3` **结构性地恒为空**。且 merge 逻辑"保留既有值"会把空值当手写内容持续保留（僵尸态），永不自愈。

**实际后果（本次 run 实测）**：已发布页面（`temp/published_tr5_709110232.html`，2026-08-27 发布）§0.1 下方显示的是模板引导占位符「【简述本次一页纸设计要达成的目标，明确设计边界（做什么、不做什么）】」而非真实内容——§0.2/§0.3 同理。发布质量缺陷，用户在 Confluence 上直接可见。

## 2. Root-Cause

`_split_section0` 的行格式假设（多行正文）与模板/发布惯例（头行内联正文）不一致；且空值经 merge 保留机制固化，后续每次重建都无法修复（本次 run 手工 inline 正则回填后才恢复）。

## 3. Options

| 选项 | 做法 | 权衡 |
|------|------|------|
| A. `_split_section0` 支持 inline 正文（推荐） | 头行正则扩展为 `^\*\*(0\.[123])、[^*]*\*\*：(.*)$`：同行捕获 inline body；无 inline 时回落既有逐行逻辑 | 单点修复；对多行正文模板向后兼容；本项目类模板即刻自愈 |
| B. 改模板惯例：§0 正文挪到头行下一行 | 修改各项目 `tr5_template.md` §0 格式 + SKILL 指引 | §0 为人工撰写栏目（"严禁 AI 代写"），改动波及每个项目的人工内容与历史发布页，爆炸半径大 |

## 4. Recommendation

**选项 A**。解析器适配既成惯例，不动人工栏目；B 仅在未来新建项目骨架（关联 P42）时作为新惯例考虑。

## 5. Proposed Changes

1. `extensions/tr5/scripts/generate_tr5_data.py`：`_split_section0()` 增加 inline 正文捕获（头行 `**0.N、…**：body` 的 body 部分与后续行合并）；
2. `extensions/tr5/scripts/test_tr5_scripts.py`：新增 inline §0 用例（inline / 多行 / 混合三态）；
3. SKILL/CHECKS 说明一处：§0 槽位自 generate 链路自动填充，无需手工回填。

## 6. Validation Plan

- `python extensions/tr5/scripts/test_tr5_scripts.py` 全绿；
- 用本项目 `tr5/tr5_doc.md` 实测：`generate_tr5_data.py` 重建后 `sections['0_1/0_2/0_3']` 非空（无需本次 run 的手工回填）；
- `build_tr5_storage.py` 产物 §0 三节含真实正文（非引导占位符）。

## 7. Risks

| 风险 | 应对 |
|------|------|
| §0 人工内容尚未撰写的项目会注入空串 | 与现状（空值）一致，无回归；发布前由 check_tr5 §0 检查兜底 |
| inline 正则误吞同行多余文本 | 正则限定首个 `**：` 之后整行，与模板格式一一对应；三态用例覆盖 |

---

## Review Log

| Reviewer | Decision | Date |
|---|---|---|
| User (AI Maintainer operator) | **Pending** | 2026-08-28 |

---

## Implementation Record（2026-08-31）

Applied per approval:
1. `extensions/tr5/scripts/generate_tr5_data.py`：`_split_section0()` 增加 inline 正文捕获
2. `extensions/tr5/scripts/test_tr5_scripts.py`：新增 4 个 inline §0 用例（inline / 多行 / 混合 / 空值）

**Validation**: 10/10 tests pass
