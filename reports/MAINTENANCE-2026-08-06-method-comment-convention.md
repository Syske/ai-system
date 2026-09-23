# Maintenance Report — 2026-08-06 方法长度与注释约定

**Mode**: on-demand
**Scope**: 方法拆分与注释约定的现状核查
**Date**: 2026-08-06
**Trigger**: 拆分 `LiveWatchDetailFetchListener#handle`(134 行→66 行)时,发现"方法行数/字段注释"约定分散且标准不一致,需统一

---

## 1. 现状核查 / Current State

| 来源 | 约定 | 状态 |
|---|---|---|
| `governance/standards/common/clean-code.md` | 方法 ≤40 行(recommended,与本次实践 80 行基准冲突)、单一职责、早返回 | ✅ 存在(基准待统一为 80) |
| `governance/standards/common/documentation.md` | 公共方法须 javadoc(用途/参数/返回值/异常/副作用);**所有字段须描述性注释**;类须 javadoc | ✅ 存在 |
| `governance/standards/common/documentation.md` | 注释用中文(LANGUAGE_CONVENTION) | ✅ 存在 |
| `governance/standards/java/java-alibaba.md` | 命名/Lombok/集合等,**无方法行数、无注释强制** | ⚠️ 部分覆盖 |
| `workflows/bugfix.md` | 无方法/注释约定 | ❌ 无 |
| `skills/bugfix/SKILL.md` | 无方法/注释约定 | ❌ 无 |

## 2. 发现的问题 / Issues

| # | 问题 | 影响 |
|---|---|---|
| I1 | **行数标准冲突**:clean-code 建议 ≤40 行,本次实践统一按 80 行——两个数字不一致,执行者无所适从 | 标准歧义 |
| I2 | **适用范围不清**:≤40 行是否适用于 MQ 消费者/编排方法?按 80 行基准,编排入口拆分后 ≤80 即可 | 边界模糊(已按 80 实践) |
| I3 | **私有方法注释非强制**:documentation.md 仅要求公共方法 javadoc,私有拆分方法无强制要求(本次手动补全 @param/@return) | 质量不统一 |
| I4 | **bugfix 流程无门禁**:bugfix.md / bugfix skill 未引用以上标准,流程本身不检查方法长度/注释 | 流程漏洞 |

## 3. 建议 / Proposal

**目标**:统一"方法长度 + 注释"约定,消除冲突,挂到 bugfix 流程。

### P1: 统一方法行数标准(修改 clean-code.md)

```markdown
## Method Design

Methods should:
- Stay short (recommended ≤80 lines)
- Orchestration / listener entry methods: split into single-responsibility private
  methods; entry method itself should not exceed 80 lines
```

即:**统一按 ≤80 行**(业务方法与编排/入口方法一致),拆分出单一职责的私有方法。

### P2: 私有方法注释要求(修改 documentation.md Method 部分)

```markdown
# Method

Public methods must document: Purpose / Parameters / Return value / Exceptions / Side effects

Private methods split from long methods must at minimum document: Purpose (one line)
```

拆分出的私有方法至少一行用途说明(本次实践已如此)。

### P3: bugfix 流程挂接(修改 bugfix.md / bugfix skill)

在 bugfix skill 的 Fix & Validate 步骤增加:

```markdown
## Fix & Validate
1. Make the minimal fix
2. Method length: split long methods (>80 lines) into
   single-responsibility privates with one-line purpose Javadoc
3. Fields: new fields must carry descriptive comments (documentation.md)
4. Run the failing test to confirm it passes
```

## 4. 状态 / Status

- [x] P1/P2/P3 已评估 → **propose**（2026-08-06，L3 契约级，待 OPERATIONS §12 评审）
- [x] **已实施（2026-09-23，用户裁决 P1′/P2′/P3′）** —— 三处**改造**后落地：
  1. **P1′**（原「统一按 ≤80」）：`clean-code.md` 改为**单一刻度 + 软目标/硬上限** ——
     `target ≤40 lines; hard ceiling 80`，并写明**编排/监听/定时/Controller 入口不豁免**。
     改造理由：全仓只有该标准写过数字（40），「80」仅存于本报告 → 原表述等于**凭一次实践
     把标准整体放宽 2 倍**；且两档规则需要「哪类方法算编排」的启发式判定（正是 I2 的歧义来源，
     会把歧义原样搬进将来的门禁）。软目标/硬上限**不需要判定分类**且可机器判定。
  2. **P2** 原样采纳：`documentation.md` Method 段补「拆分出的私有方法至少一行 Purpose」。
  3. **P3′**（原「把 >80 就拆分写进 bugfix skill」）：`skills/bugfix/SKILL.md` Fix & Validate
     改为**引用标准**（不复制数字）+ 明确**只约束「修复已触碰的方法」**，并写明「发现附近的长方法
     **不**构成拆分许可」（原表述会**授权在 bugfix 里顺手重构**，与 `runtime-bugfix`
     「Avoid unrelated refactoring」/ `bugfix/anti-patterns.md`「Fix in one commit, refactor in a
     separate commit」冲突）。
  4. **报告未提及的真实改动面**：`loaders/standards-loader.md` 原**没有 bugfix 小节**、
     `runtime-bugfix.md` 完全不引用标准 → 新建 `### For runtime-bugfix` 登记 `clean-code.md` +
     `documentation.md`（并注明作用域）。
  **影响**：`governance/standards/common/{clean-code,documentation}.md` · `loaders/standards-loader.md` ·
  `skills/bugfix/SKILL.md`；同时**解锁 P67 §4.1 的阈值口径**（P67 门禁将用硬上限 80 FAIL /
  接近目标 40 WARN）。
- 关联实践:`LiveWatchDetailFetchListener#handle` 已拆分 134→44 行(≤80 达标),私有方法均补一行用途 javadoc,字段注释完整
