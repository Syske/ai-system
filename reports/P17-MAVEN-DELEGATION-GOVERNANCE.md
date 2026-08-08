# Change Proposal: P17 — java-maven 委派规范（D1 根治）

| Field | Value |
|---|---|
| Status | **Implemented** |
| Type | Structural (skill content governance) |
| Author | AI Maintainer |
| Created | 2026-08-08 |
| Reference | MAINTENANCE-2026-08-08.md D1 / S1 |
| Process | OPERATIONS §12 Change Management |

---

## 1. Problem

非 java-maven 技能（bugfix、mock-test）在文档中硬编码 Maven 命令（`mvn clean install`、`mvn test -Dtest=...`），违反 `repository-maintainer/governance.md:30`（RFC-0002：No Maven commands unless java-maven）。2026-08-08 已把 5 处 lint 告警替换为委派描述（A2），但：

- 剩余 `mvn -pl <mod> -am test` 形态命令（examples.md、workflow.md、repair.md 等）不在 lint 正则 `mvn\s+(goal)` 覆盖内，仍属硬编码命令知识。
- 各技能委派表述不一致（"via java-maven" / "Delegate to java-maven" / "Invoke java-maven"），无统一规范。

## 2. Root-Cause

RFC-0002 的「No Maven commands」检查只覆盖 `mvn <goal>` 直连形态，且缺乏对委派表述的格式要求；技能作者在文档示例中自然写出完整命令（可读性好），导致命令知识在多技能间复制。

## 3. Options

| Option | 描述 | 优点 | 缺点 |
|---|---|---|---|
| A（推荐） | 定义统一委派规范：非 java-maven 技能内 Maven 执行一律表述为 `Delegate to java-maven: <意图>`（如 "run the affected test"），禁止任何 `mvn` 命令字面量；lint 正则扩展覆盖 `mvn` 任意形态 | 根治重复 + 检查闭环 | 需改写多个示例文件 |
| B | 仅保留现有 A2 修复，其余命令示例不动 | 改动小 | 重复知识残留，规范不统一 |
| C | 把 Maven 命令示例集中迁入 java-maven/commands.md，其他技能引用之 | 单一事实源 | 较大重构 |

## 4. Recommendation

**Option A**：新增 governance 委派规范段落（repository-maintainer/governance.md 或 skills/README.md），统一表述；扩展 repo-lint `check_prohibited_content` 正则覆盖 `mvn` 任意形态（`\bmvn\b`，java-maven 豁免不变）；将 bugfix/mock-test 剩余 `mvn -pl ...` 示例改写为委派表述。Option C 的 commands.md 集中化作为后续增强，不在本提案范围。

## 5. Proposed Changes

1. `repository-maintainer/governance.md`：在 RFC-0002 表后新增「Maven 委派规范」小节——非 java-maven 技能禁止 Maven 命令字面量，统一 `Delegate to java-maven: <意图>` 表述。
2. `tools/repo-lint.py` `check_prohibited_content`：正则 `\bmvn\s+(goal)\b` → `\bmvn\b`（保留 java-maven 豁免与 "playbooks/maven" 引用豁免）。
3. 改写 `skills/bugfix/examples.md`、`skills/bugfix/workflow.md`、`skills/bugfix/repair.md`、`skills/mock-test/workflow.md` 中的 `mvn -pl ...` 示例为委派表述。
4. lint 回归：预期 Maven warnings 覆盖从 5 处扩展到所有 `mvn` 形态，改写后归零。

## 6. Validation Plan

- `python tools/repo-lint.py --repo-root .`：0 BLOCKER/ERROR，无 Maven warnings（java-maven 豁免验证）
- `python tools/check.py`：exit 0
- `grep -rn "\bmvn\b" skills/bugfix skills/mock-test`：仅 java-maven 委派表述，无命令字面量

## 7. Risks

- 正则放宽可能误报文档中讨论性 Maven 表述（如 "never default to clean install" 在 java-maven 自身豁免内；其他技能内此类表述需改写为描述式）。缓解：改写时保留语义，用「full clean install build」类描述替代字面量。
- examples.md 可读性下降（读者需跳转 java-maven）。缓解：委派表述后附 `java-maven/commands.md` 指针。

---

## Review Log

| Reviewer | Decision | Date |
|---|---|---|
| User (AI Maintainer operator) | **Approved** | 2026-08-08 |

---

## Implementation Record (2026-08-08)

Applied per approval (OPERATIONS §12 → Implement → Validate):

1. `tools/repo-lint.py` `check_prohibited_content`：正则 `\bmvn\s+(clean|compile|test|package|verify|install|deploy)\b` → `\bmvn\b`；移除文件级豁免（内容含 "java-maven" 不再跳过检查），java-maven 技能整体豁免保留。
2. `skills/repository-maintainer/governance.md`：新增「Maven Delegation Convention (P17)」小节——统一委派表述 `Delegate to java-maven: <intent>`，禁止命令字面量；RFC-0002 表格措辞同步。
3. 命令字面量改写（全部消除）：`skills/bugfix/examples.md`（6 处）、`skills/bugfix/workflow.md`（3 处）、`skills/bugfix/repair.md`（2 处）、`skills/mock-test/diagnosis.md`（7 处残留）、`skills/mock-test/workflow.md`（1 处）。
4. 规则文档自身字面量改写：`repository-maintainer/governance.md`（2 处）、`repository-maintainer/review.md`（1 处）、`repository-governor/analysis.md`（1 处）——统一为描述性措辞 "Maven CLI"。

**Validation**:
- `python tools/repo-lint.py --repo-root .`：0 BLOCKER / 0 ERROR / 25 WARNINGS（**Maven command literal 0**，无新增）
- `python tools/check.py`：exit 0
- `python tools/path-audit.py`：0 broken
- `python -m unittest discover -s cli/tests`：50 tests OK
