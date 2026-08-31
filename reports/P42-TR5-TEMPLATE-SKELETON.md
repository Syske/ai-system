# Change Proposal: P42 — 新增 tr5_template.md 一页纸骨架模板

| Field | Value |
|---|---|
| Status | **Proposed** |
| Type | Structural（新增模板资产） |
| Author | AI Maintainer |
| Created | 2026-08-26 |
| Reference | 202610-qa-housekeeping-optimization tr5-design run（骨架从零反推） |
| Process | OPERATIONS §12 Change Management |

---

## 1. Problem

`extensions/tr5/templates/` 只有 `AGENTS.md / review.md / spec.md / tr5_storage.xml`。`tr5_storage.xml` 是**发布用** storage 模板，不是编写源——但 tr5-design Step 2 要求每个项目创建 markdown 版 `tr5/tr5_template.md`（19 节骨架 + `{{SECTION_XX}}` 占位符），当前只能从 storage XML 反推或从零手写：

- 本次 run 从零写了完整骨架（约 200 行），耗时且需自行摸索标题层级（h3）、占位符命名、图表分发等约定；
- 骨架质量依赖执行者对 SKILL.md 的理解，易漏节/错层级（本次即踩了 h2/h3 坑，见 B1 修复记录）。

## 2. Root-Cause

tr5-design 的「双文件机制」（template 骨架 + sections 内容）缺少与之配套的**初始骨架资产**；templates/ 目录覆盖了发布端（storage XML）却缺编写端入口。

## 3. Options

| 选项 | 做法 | 权衡 |
|------|------|------|
| A. 新增 `templates/tr5_template.md` | 提供 19 节骨架：`### N、` 标题 + §4-§8 占位符（`{{SECTION_04_06}}/{{SECTION_07}}/{{SECTION_08}}`）+ 各节"只放什么/禁止什么"注释 + 图表分发占位 | 一次沉淀、项目直接拷贝；需与 storage XML 节结构保持同步 |
| B. 由 build_tr5_doc.py 自动生成骨架 | 加 `--init` 参数按内置常量生成 | 工具化程度高；但骨架内容变更要改代码，非纯资产 |
| C. 不新增，继续手写 | 维持现状 | 每个项目重复劳动，质量不稳定 |

## 4. Recommendation

**A**（新增静态骨架模板文件）。模板保真由既有 `sync_template.py` + `template_version.json` 机制类比管理（storage XML 已有版本追踪先例）；B 的工具化收益不足以抵消代码耦合。

## 5. Proposed Changes

1. 新增 `extensions/tr5/templates/tr5_template.md`：
   - 19 节 `### N、` 标题（与 tr5_storage.xml h3 结构一一对应，含 §18 双节的 §18/§19 处理说明）；
   - §4-§8 置 `{{SECTION_04_06}}` / `{{SECTION_07}}` / `{{SECTION_08}}` 占位符；
   - 其余各节内嵌灰色引用注释（只放什么/禁止什么，摘自 SKILL.md 布局规则表）；
   - §3 预置 3.1/3.2/3.3 图表槽位示例；
   - 文件头注明来源与同步方式。
2. `skills/tr5-design/SKILL.md` Step 2 补一句：「从 `extensions/tr5/templates/tr5_template.md` 拷贝为 `<project-root>/tr5/tr5_template.md` 后填充」。
3. （可选，随 P41 批次）`sync_template.py` 扩展支持 markdown 骨架的版本登记。

## 6. Validation Plan

- 用本项目现有 `workspaces/202610-qa-housekeeping-optimization/tr5/` 实测：以新模板重建骨架 → 注入本项目 sections → `build_tr5_doc.py --check` 无未替换占位符 → `generate_tr5_data.py` 解析出 20/19 节（含 §0）→ `validate_tr5.py` 0 error。

## 7. Risks

| 风险 | 应对 |
|------|------|
| 骨架与上游 storage 模板演进漂移 | 文件头标注 synced 日期 + template_version.json 同步登记 |
| 项目定制节结构（如合并 §4-§6）与模板不符 | 模板仅含标准结构，定制由项目自行调整（SKILL.md 已有拆分原则说明） |

---

## Review Log

| Reviewer | Decision | Date |
|---|---|---|
| User (AI Maintainer operator) | **Pending**（已批准立项起草，实施待批） | 2026-08-26 |
