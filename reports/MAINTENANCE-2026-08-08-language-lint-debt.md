# Maintenance — Language Check 存量债登记

- 日期 / Date: 2026-08-08
- 范围 / Scope: `repo-lint.py check_language` 新增 Rule 3 后暴露的存量语言违规
- 性质 / Nature: 全部为历史存量,非本次改动引入

## 背景

`repo-lint.py check_language` 原先只检查两类(命令文档 Steps/Guardrails 英文、Python 注释中文),**不覆盖 `governance/*.md` 文档**——导致 governance 层中文文档长期不被发现(LANGUAGE_CONVENTION 要求 Governance 层 MUST English)。

本次新增 **Rule 3**: governance/*.md(豁免 archive/、standards/、README、policies)须英文。规则生效后暴露 8 处存量债。

## 存量债清单(待办,勿新增)

| # | 位置 | 内容 | 性质 |
|---|---|---|---|
| 1 | `cli/commands/aic-scan.md` Steps | 4 行中文 | 命令参数中文说明(用户面向) |
| 2 | `cli/commands/aic-skill-source.md` Steps | 3 行中文 | 命令参数中文说明 |
| 3 | `cli/commands/aic-trace.md` Steps | 4 行中文 | 命令参数中文说明 |
| 4 | `cli/services/interactive.py:31-32` | 英文注释 | 应中文 |
| 5 | `governance/memory/coding-memory.md` | 10 行中文 | 记忆条目索引(中文描述类别) |
| 6 | `governance/memory/ai-system/coding-memory.md` | 5 行中文 | 同上 |
| 7 | `governance/memory/java/coding-memory.md` | 5 行中文 | 同上 |
| 8 | (Rule 1 既有) aic-scan/skill-source/trace 与交互提示 | — | 与 1-3 同源 |
| 9 | `cli/services/menu_config.py:17-18` | 2 行英文注释（Path/str 解析说明） | 应中文 |
| 10 | `cli/tests/test_services.py:17,123` | 2 行英文注释（cli 可导入性、skill 命令模式） | 应中文 |
| 11 | `cli/tests/test_skill_launcher.py:20,83,86` | 3 行英文注释（非 TTY 降级、分组标签、by_index 唯一性） | 应中文 |
| 12 | `cli/tests/test_state_store.py:45,58` | 2 行英文注释（中间路径为 dict、磁盘重载） | 应中文 |
| 13 | `tools/context-audit.py:31,62` | 2 行英文注释（CJK 权重、回退扫描策略） | 应中文 |
| 14 | (Rule 3 新暴露) `governance/memory/ai-system/coding-memory.md` 5 行中文 | 记忆条目索引 | 与 5-7 同源 |
| 15 | (Rule 3 新暴露) `governance/memory/coding-memory.md` 10 行中文 | 记忆条目索引 | 与 5-7 同源 |

## 处置建议

- #1-3: 命令 Steps 中的中文为参数说明,**属用户面向内容**,可接受(与 LANGUAGE_CONVENTION 交互提示用中文一致);或改英文待定
- #4: 低风险,可顺手改为中文注释
- #5-7: memory 索引条目,需按 LANGUAGE_CONVENTION 的 Coding Memory → English 要求翻译,属独立工作项
  → ✅ **已完成（2026-08-23 核验）**：`governance/memory/` 全部文件实测 0 中文字符（coding-memory 45行/0、
    ai-system/coding-memory 13/0、workflow-chain 36/0、java/spring 90/0 等）

**决策:本次仅补全检查规则(防止新增违规),存量债登记不批量修**(最小改动原则)。后续单独处理。

## 补充登记(2026-08-08 晚)

| # | 位置 | 内容 | 性质 |
|---|---|---|---|
| 9 | `rfc/*.md`(ADR/RFC) | repo-lint Rule 3 只查 governance/,不查 rfc/——ADR 中文无自动拦截(ADR-0008 曾 179 处中文,已手工修) | 规则盲区,建议 Rule 3 扩展覆盖 rfc/(ADR 须英文) |
