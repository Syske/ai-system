---
description: 评估外部三方 skill 来源 - 克隆仓库、列出 skills、按参考价值分类，产出评估报告供吸收决策
---

评估一个外部三方 skill 来源（如 GitHub 上的 skill 仓库），将其中的 skills 按参考价值分类，产出结构化评估报告，供后续决定是否吸收为原生资产。

**输入**：
- Skill Source URL：三方 skill 仓库的 URL（必填）
- Report Name（可选，默认 `THIRD-PARTY-SKILL-ASSESSMENT-{date}`）

**步骤**

1. **克隆来源**：将仓库浅克隆到临时目录（`git clone --depth 1 <url>`），不进入工作区。

2. **盘点 skills**：列出所有 skill 目录（含 `SKILL.md`/`skill.md` 的目录），记录每个 skill 的名称与 description。

3. **分类评估**：对每个 skill 按参考价值分三类（参考 `reports/THIRD-PARTY-SKILL-ASSESSMENT-2026-08-01.md` 的分类框架）：
   - **高价值**：填补真实缺口，方法论可直接吸收
   - **中价值**：方法论可借鉴，非直接复制
   - **低/无价值**：平台特定 / 个人写作 / 已内化 / 依赖外部工具 / 已废弃

   对照当前 ai-system 已有资产（`skills/`、`governance/standards/`、`templates/runtime/`）判断重叠与缺口。

4. **生成报告**：写入 `reports/THIRD-PARTY-SKILL-ASSESSMENT-{date}.md`，含：
   - 来源与日期
   - 已吸收建议（高价值项 + 落点）
   - 可借鉴建议（中价值项 + 借鉴点）
   - 不吸收项及原因
   - 后续触发条件（Evolution Principle：不预先引入）

5. **清理**：删除临时克隆目录。

**输出**

## Skill Source Assessment Report

- 来源 URL
- Skill 总数与分类统计
- 已吸收建议（高/中价值）
- 不吸收项及原因
- 后续触发条件

**护栏**

- 只评估与分类，**不实施吸收**。吸收决定经用户确认后走 skill-policy。
- 以原生资产重写（skill-policy），不复制三方文件。
- 遵循 Evolution Principle：仅推荐填补真实缺口的吸收，不因"更好"而引入。
