# Change Proposal: P69 — AI 注释泔水治理（Comment Quality Gate）

| Field | Value |
|---|---|
| Status | **Implemented** |
| Type | Structural（新增工具 + 策略章节扩展 + 新技能 + 门禁注册） |
| Author | AI Maintainer |
| Created | 2026-09-23 |
| Reference | 用户 2026-09-23 两版设计（Java+JavaParser 独立工程 → Python CLI + tree-sitter）+ 三项落位裁决；本仓注释治理现状侦察（§1.2）；`tools/` 职责实测（§4.3）；`reports/P67-STRUCTURAL-SMELL-CAPABILITY.md`（同族不同维度） |
| Process | OPERATIONS §12 Change Management |

---

## 1. Problem

### 1.1 现象

多 Agent（OpenCode / Pi / Codex）+「必须写注释」标准共同作用下，AI 在业务代码里产出**信息增量为零**的注释（下文统称**泔水**）：

```java
// 获取用户
User user = userService.getUser(id);
// 首先，我们需要检查参数是否为空
if (request == null) { ... }
// ==================== 数据处理 ====================
```

危害不在"多几行"，而在**稀释**：有语义的注释（业务规则 / 外部契约 / 并发与性能约束 / 历史原因）被同质噪声淹没，评审者与后续 AI 都失去"该读哪条"的判断力。

### 1.2 现状核查（本仓实证）

**已覆盖的部分（不可重复建设）**

| 位置 | 内容 |
|---|---|
| `governance/standards/common/documentation.md:51` | 禁止单行块 `/** xxx */`（AI 生成时系统性出现） |
| `documentation.md:64` | 禁止注释携带内部流程标识（`T-001` / Change ID） |
| `documentation.md:187` | **禁止名字直译/与字段名重复**（反例 `bsCompensationDataTag` ↔ `补偿数据通道 tag`） |
| `documentation.md:192-193` | Value-Burden 豁免：写不出业务语义的平凡字段可省略注释 |
| `governance/standards/common/clean-code.md:195-200` | **Comments explain Why / Not What**（反例 `// Check if null`） |
| `skills/implement/anti-patterns.md:164-169` | ❌ 禁止重复代码的注释（`// Set userId` / `user.setUserId(id)`） |
| `skills/bugfix/anti-patterns.md:22` | bugfix 中「顺手加注释、重排格式」属多余改动 |
| `tools/format-check.py:240-243` | 单行 Javadoc → **FAIL**（机器强制） |
| `tools/format-check.py:251-254` | 注释内任务编号泄漏 → **FAIL** |
| `tools/format-check.py:327,356` | `@Value` 字段缺行尾注释 → WARN（要求注释**存在**方向） |
| `tools/repo-lint.py:321-323` | `cli/**`、`tools/*.py` 注释必须中文 → WARN |
| `tools/checkstyle/checkstyle.xml:76-82` | Javadoc 结构（warning，只收集不阻断） |

**真正的缺口（本提案要补的）**

| # | 缺口 | 证据 |
|---|---|---|
| G1 | **无分段线/分隔线规则** | 全仓 grep `分隔线\|分割线\|分段线` 零命中（`repo-lint` 对 `# ---` 反向豁免） |
| G2 | **无 AI 套话规则**（首先/接下来/然后/最后/这里我们/下面开始/进行…处理） | 同上，无任何规则 |
| G3 | **无方法级重复注释规则** | 只有字段名直译（`:187`）与 what 类原则（`clean-code.md:195`），无"注释重复方法名"独立条目 |
| G4 | **无 diff 级注释门禁，也无任何清理工具** | grep `comment-lint\|注释清理` 零命中；`review` 技能 12 个 Fowler 味道中无注释类 |
| G5 | **三处「无豁免全量要求」制造源头压力** | `governance/memory/MEMORY_GUIDELINES.md:278`「All VO fields require comments.」（绝对化）· `task-quality-checklist.md:26`「Constants and configuration values have documented meanings」（无豁免）· `documentation.md:182`「All fields must: Include descriptive comments」（豁免是后补的 `:192-193`，属"要求优先、豁免兜底"） |
| G6 | 规则分散在 6+ 文件 | 标准 3 处 + 技能 3 处 + 工具 4 处，**无单一"注释分类"清单**，无法机器核对"标准声明 ↔ 实际检查"一致 |

**好消息**：侦察确认 `templates/prompts/` 与 `skills/` **没有**「为每段加注释」「加中文注释便于理解」这类直接诱导指令（grep `加注释\|写注释\|每段\|便于理解` 在 templates/ 零命中）→ 泔水主要来自 G5 的**压力**与 AI 的**习惯**，不是提示词明文要求。

### 1.3 根因

1. **要求"写"的规则强且绝对，约束"写成什么"的规则原则化**（Why/Not What 是原则，不是可核对的枚举）→ AI 只能靠猜。
2. **检查面只覆盖三件窄事**（单行块 / 任务号 / 注释语言）且**全项目级**（存量债与新增混在一起）；"只删本次 AI 新增的泔水"需要 **diff 级**能力，本仓没有。
3. **缺分类即缺判定**：没有可核对分类，就无法定义"哪些能自动删、哪些只报告"——而**误删有语义注释的代价远高于漏删**。

## 2. Goal

给「注释泔水」一条**保守、可核对、可回归**的闭环：

> 策略（标准）定分类与判定 → 工具（diff 级、确定性规则）出候选 → AI（在场 agent）裁定不确定项
> → **只有确定类**才自动删 → 门禁兜住"没清干净"

**安全底线：宁可漏删，不可误删。**

## 3. Options

### 3.1 Option A — 独立 Java Maven 工程 + JavaParser（用户初版）—— **排除**

① 引入第二技术栈（JDK + Maven + Java Linter 生命周期 + 跨语言 CLI 协议 + Windows 兼容），与本仓纯 Python 工具链不一致；② 违背「知识在 ai-system / 执行随工具链」边界；③ 本仓所有门禁入口都是 `python3 ai-system/tools/xxx.py {src} --changed`，Java 工程无法直接落进 `gates.develop`。

### 3.2 Option B — Python 单文件工具 + 策略章节 + 技能（**采纳**）

```text
ai-system/governance/standards/common/documentation.md   ← 新增 # Comment Quality（分类 + 规则 id，SSOT）
ai-system/governance/standards/common/ai-coding-rules.md ← 新增一句原则（注释默认非必需）
ai-system/config/comment-lint.yaml                       ← 行为参数（形态对齐 config/branch-formats.yaml）
ai-system/tools/comment-lint.py                          ← 新工具（diff 级 · 确定性 · --json · dry-run/apply）
ai-system/tools/README.md                                ← 登记（check_tools_readme 强制）
ai-system/skills/comment-cleaner/SKILL.md                ← AI 侧流程：何时跑 / 如何裁定 REVIEW / 提交纪律
ai-system/config/main-chain-capabilities.yaml            ← gates.develop 注册（形态对齐 format-check-a）
ai-system/templates/runtime/runtime-develop.md           ← 门禁说明段（一行引用）
```

工具**不重复**已有三项检查（单行块 / 任务号 / 注释语言）——分工表写进工具 README 与标准章节。

### 3.3 Option C — 先做 `cli/comment/` 包，稳定后抽到 `tools/` —— **不采纳**

本仓门禁注册与 `tools/README.md` 登记惯例都建立在 `tools/*.py`（单文件）之上；`cli/` 是 `aic` 提示词/服务层（见 §4.3）。

### 3.4 Option D — 纯正则、不引入 parser —— **并入 B 作为降级通道**

`String s = "// 不是注释";`、块注释、JavaDoc 在纯正则下必然误判。B 采用**探测式导入**：`tree_sitter_language_pack.get_parser('java')` 可用则走 AST，否则退到标准库词法状态机（**同一批测试都必须过**）。

## 4. Recommendation

**采纳 Option B**；A 排除；C 不采纳；D 并入 B 作降级路径。

### 4.1 与用户设计的 采纳 / 修正 / 排除

| 用户设计 | 处置 |
|---|---|
| 只处理 git diff 新增行 | ✅ 采纳，复用 `format-check.py:495-523` + `format-jdt-gate.py:149-211` |
| 三级判定 + 「宁可漏删不可误删」 | ✅ 采纳，写进标准章节首句 |
| 六级分类 | ✅ 采纳为**标准章节的枚举**（规则 id 一一对应，§5.1） |
| JavaDoc 默认不动 | ✅ 采纳：MVP 显式跳过 `/**` block_comment |
| MV1 关闭 SAFE_REWRITE | ✅ 采纳（只删不重写） |
| dry-run 必须有、`--json`/文本双输出 | ✅ 采纳 |
| Code Context 输入 | ✅ 采纳：候选携带「注释 / 紧邻代码 / 所属方法 / 所属类」 |
| MVP 砍项清单 | ✅ 采纳为「明确不做」（§8） |
| 规则不写死在代码里、但也不必塞进 config 一堆模式 | ✅ 采纳：**模式在工具内部规则模块**，config 只放行为参数（§5.1） |
| Parser 从第一天就做薄接口（不锁死 JavaParser） | ✅ 采纳：单文件内 `CommentParser` 接口 + `TreeSitterJavaParser` + 标准库降级实现 |
| 独立 Java 工程 + JavaParser | ❌ 排除（§3.1） |
| 工具内直接调 LLM | ⚠️ **修正为 agent-as-judge**：本仓无任何调用 LLM 的工具；develop 阶段本就有 agent 在场且掌握 spec/契约/业务上下文；引 API key/成本/非确定性不划算。`--llm` 仅在将来出现"无 agent 的 CI 批处理"时再评估 |
| `governance` 新增 `comment-policy.md` | ⚠️ **修正**：改为扩展 `documentation.md`（本仓注释内容规则已在此，避免第 4 个来源）；`ai-coding-rules.md` 加**一句原则** |
| `tools/comment-linter/`（parser/rules/fixer 目录） | ⚠️ **修正为单文件** `tools/comment-lint.py`（抽象留在文件内）—— 实测理由见 §4.3 |
| `cli/commands/comment.py` + `cli/services/comment_linter_service.py` | ⚠️ **修正**：本仓 `cli/commands/` 是 `.md` 提示词；`cli/services/**` 无调 `tools/` 先例 → **不引入 Python 服务层**，命令（如需）注册为 hidden command 提示词 |
| `rfc/comment-linter.md` | ❌ 不加：本仓 `rfc/` 是架构级 ADR/RFC；工具级设计的既有载体是 `reports/P*.md` + `tools/README.md` + 技能/标准 |
| `workflows/` 只述调用时机 | ✅ 采纳（本仓落点：`templates/runtime/runtime-develop.md` 门禁段） |
| `templates/` 不动、`loaders/` 不动 | ✅ 采纳 |

### 4.2 落位裁决（**2026-09-23 用户已裁定：三项全部同意**）

| # | 裁定项 | 结论 | 依据 |
|---|---|---|---|
| 1 | 工具形态 | **单文件 `tools/comment-lint.py` + 文件内 parser 抽象**；抽包触发条件见下 | §4.3：第一方工具 29/29 单文件；`tools/<dir>/` 先例仅为 check.py 内部包与**外部工具资产**；`check_tools_readme` 只 glob `tools/*.py`（目录形态会**绕过登记门禁**） |
| 2 | CLI 层 | **不加 Python 服务层**；如需命令 → hidden command 提示词（ADR-0009 惯例） | §4.3：`cli/commands/` 是 `.md` 提示词（`__init__.py` 仅一句 docstring）；`cli/main.py` 单一 argparse 入口、无 per-command 代码分发；`cli/services/**` 无调 `tools/*.py` 先例 |
| 3 | 策略落点 | **补进 `documentation.md` 现有注释章节**（缺口 G1/G2/G3）+ `ai-coding-rules.md` 加一句原则 | 本仓注释内容规则**已**集中在 `documentation.md`、`clean-code.md`、`java/spring.md`；新建 `comment-policy.md` 会形成第 4 个来源 |

**抽包触发条件（书面留档，避免将来遗忘）**：当**第二个语言**（Python/JS/SQL）真的落地，或单文件超出本仓工具量级上限时，才抽 `tools/comment-linter/` 包，**并同步扩 `check_tools_readme` 的扫描口径**（否则新工具会静默绕过登记门禁）。

### 4.3 `tools/` 职责实测（裁定 1/2 的证据）

| 形态 | 实例 | 性质 |
|---|---|---|
| **扁平单文件 `tools/*.py`** | 29 个（`check.py` `repo-lint.py` `path-audit.py` `format-check.py` `format-jdt-gate.py` `proposal-audit.py` …） | **本仓所有第一方工具** |
| `tools/checks/` | 11 个 .py | `check.py` 的**内部检查项包**（涨到 11 项才成包） |
| `tools/jdt-format-gate/` | `JdtFormatCheck.java` + `eclipse-format.xml` + `known-ignore.txt` + `build/` | **外部/自带 Java 工具的资产**，非 Python 包 |
| `tools/checkstyle/` | `checkstyle-gate.py` + `checkstyle.xml` + `suppressions.xml` | 同上：**外部工具资产** + 包装入口 |

**门禁口径**：`tools/checks/misc.py:274-300` `check_tools_readme` 断言「每个 `tools/*.py` 必须登记 `tools/README.md`」，实现为 `glob("tools/*.py")`。

## 5. MVP 实施计划（**目标：第一个版本落地可用**）

### 5.1 命名与规则 id（先定，后续步骤引用）

| 项 | 定名 | 对齐对象 |
|---|---|---|
| 工具 | `tools/comment-lint.py` | `format-check.py` / `path-audit.py` 的动宾命名 |
| 配置 | `config/comment-lint.yaml` | `config/branch-formats.yaml`（命名词根 = 工具名） |
| 标准章节 | `documentation.md` → `# Comment Quality` | 本仓注释内容规则所在文件 |
| 原则一句 | `ai-coding-rules.md` | AI Coding Rules |
| 技能 | `skills/comment-cleaner/SKILL.md` | `skills/<skill>/SKILL.md` |
| 测试 | `cli/tests/test_comment_lint.py` | `cli/tests/` 既有形态 |

**六级分类与稳定规则 id**（标准章节列出语义，工具内部实现模式）：

| 规则 id | 类别 | 动作 | MVP 是否自动改 |
|---|---|---|---|
| `CQ-MEANINGFUL` | 业务规则 / 外部契约 / 兼容性 / 并发 / 性能 / 安全 | **KEEP（白名单优先命中）** | 否 |
| `CQ-SECTION-HEADER` | 分段线/分隔标题（`// ==== 参数校验 ====`） | SAFE_DELETE | ✅ |
| `CQ-AI-NOISE` | 流程套话（首先/接下来/然后/最后/这里我们/下面开始/进行…处理） | SAFE_DELETE | ✅ |
| `CQ-OBVIOUS` | 复述代码（空值判断/返回/遍历/赋值/调用/CRUD） | SAFE_DELETE | ✅ |
| `CQ-DUPLICATE` | 与方法名/字段名重复的注释 | **REVIEW**（MVP 不自动删） | 否 |
| `CQ-UNCERTAIN` | 兜底：无法归类 | REVIEW | 否 |

**判定顺序（写进标准与工具，唯一）**：`CQ-MEANINGFUL` 命中即 KEEP → 否则按 SECTION_HEADER / AI_NOISE / OBVIOUS / DUPLICATE 匹配 → 都不中则 UNCERTAIN(REVIEW)。
**退出码（本仓惯例）**：`0` PASS（无 SAFE_DELETE、无 REVIEW）· `1` WARN（有 REVIEW 待裁定）· `2` FAIL（存在未清理的 SAFE_DELETE）。

### 5.2 步骤（每步独立可验证、可回滚；预计 7 个提交）

| 步 | 内容 | 产物 | 验收（必须实测） |
|---|---|---|---|
| **S1 策略先行** | ① `ai-coding-rules.md` 加一句原则：「注释默认不是必需品，仅在代码本身无法表达业务规则/约束/兼容性原因时添加」② `documentation.md` 新增 `# Comment Quality`：六级分类 + 判定顺序 + 安全原则 + 规则 id 表 ③ 对齐 G5 三处「无豁免全量要求」（`MEMORY_GUIDELINES.md:278`、`task-quality-checklist.md:26`、`documentation.md:182`）④ `config/comment-lint.yaml`（仅行为参数：`scope: git-diff` · `fix.safe_only: true` · `java_doc: skip`） | 4 文件 | 三类缺口在标准中可逐条查到；`check.py` PASS；`language-gate` PASS；**启停不在本 config**（SSOT = `main-chain-capabilities.yaml`） |
| **S2 候选提取** | `tools/comment-lint.py` 骨架 + `CommentParser` 接口 + `TreeSitterJavaParser` + 标准库降级词法：注释候选 = `file/行列/字节范围/文本/紧邻代码/所属方法/所属类`；JavaDoc 显式跳过 | 工具 + 测试 | 4 类反例不误判：`String s = "// 不是注释";` · 块注释内 `//` · JavaDoc · 注解字符串；**AST 通道与降级通道同一批断言都过** |
| **S3 diff 限定** | 只处理 `git diff` 新增行内的注释；非 git 仓/首提交 → 整文件（对齐 `format-check.py` 语义） | 工具 + 测试 | 真 git 仓 fixture（抄 `test_p62_commit_traceability.py`）：**存量注释不被触碰**、新增行注释被识别；`--diff` 与 `--changed` 语义一致 |
| **S4 规则引擎** | 3 类确定规则 + `CQ-MEANINGFUL` 白名单优先 + `CQ-DUPLICATE`/`CQ-UNCERTAIN` → REVIEW；模式写在工具内部规则模块（**不进 config**） | 工具 + 测试 | **安全底线：MEANINGFUL 六类反例各 ≥3 条 → 零误报**；自建 20+ 泔水样本确定类命中 ≥80% |
| **S5 CLI 与安全** | `check`（只读，0/1/2）· `check --json` · `fix --dry-run`（打印 unified diff）· `fix --apply`（仅 SAFE_DELETE）· `--report-only`（永不 2，供 MVP 门禁用） | 工具 + 测试 | `--apply` **幂等**（二次运行零改动）；`--apply` 后 `git diff` **只含注释删除行**；打印实际删除的行 |
| **S6 门禁与登记** | `main-chain-capabilities.yaml` 的 `gates.develop` 注册（形态对齐 format-check-a）；`runtime-develop.md` 门禁段一行；`tools/README.md` 登记 | 3 文件 | **门禁只跑 `check`（只读）**，`cmd: "python3 ai-system/tools/comment-lint.py {src} --diff --report-only"`（MVP 不阻断）；`check.py` PASS（`check_tools_readme` 会抓登记）；模拟 develop 阶段跑一次，报告产出正确并记入诊断日志 |
| **S7 技能** | `skills/comment-cleaner/SKILL.md`（何时跑 / 如何裁定 REVIEW / 必须 dry-run → apply → 跑门禁 → **独立提交**）+ `skills/README.md` 登记（38 → 39）+ `documentation.md` 互引 | 2 文件 | repo-lint 技能门禁通过（frontmatter / 体积 / 80 行拆分规则）；WARN 总数变化可解释 |
| **S8 真实可用性验证** | 在 **8 个业务仓库的已提交历史 diff** 上干跑（只读，不写仓库）+ 1 个真实任务端到端 | Implementation Record | 统计误报/漏报；**据此决定是否去掉 `--report-only` 翻 FAIL**；结果写进 §Implementation Record，Status → Implemented |

### 5.3 「可用」的定义（DoD）

1. **一条命令可跑**：`python3 ai-system/tools/comment-lint.py <src>/ --diff` → 输出「确定可删 / 需裁定 / 保留」三分类 + 退出码。
2. **安全底线达成**：真实 diff 上 `CQ-MEANINGFUL` **误报 0**；SAFE_DELETE 与人工判定吻合 ≥80%。
3. **改代码可控**：`fix --dry-run` 输出可读 unified diff；`fix --apply` 幂等、只删注释、打印所删行。
4. **门禁可用**：`gates.develop` 有条目且**只读不阻断**；`check.py` / `repo-lint` / `path-audit` / `proposal-audit` 全绿；新增测试纳入 564 基线（+N）。
5. **流程闭环**：技能能指导 agent 在 develop 收尾完成「跑 → 裁定 REVIEW → 独立提交」。

## 6. Validation Plan

1. **误删防护（优先于召回率）**：MEANINGFUL 六类反例各 ≥3 条 + 本仓真实例子（`bsCompensationDataTag` 直译边界、`afterCommit` 时序、Redis key 兼容性）→ **零误报**，否则该类退回 REVIEW。
2. **词法正确性**：字符串内 `//` · 块注释嵌套 `//` · JavaDoc · 注解参数字符串 → AST 通道与降级通道**同一批测试**都必须过。
3. **diff 限定**：真 git 仓 fixture —— 存量注释不被触碰，`--apply` 后 `git diff` 只含注释删除。
4. **历史数据标注**：8 个业务仓库已提交历史 diff 干跑（只读）→ 作为"是否翻 FAIL"的依据。
5. **门禁回归**：`check.py` / `repo-lint` / `path-audit` / `proposal-audit` 全绿；`tools/README.md` 登记。
6. **端到端**：选一个真实任务：develop → 门禁 → cleanup 独立提交 → review 复核"没有重要注释被误删"，记录误报/漏报。

## 7. Risks

| 风险 | 缓解 |
|---|---|
| **误删有语义注释**（与能力初衷相反） | 只做确定类；MEANINGFUL 白名单**优先命中**；DUPLICATE/UNCERTAIN 一律 REVIEW；MVP 门禁 `--report-only` 不阻断；`--apply` 需显式调用 + 打印所删行；cleanup 独立提交 + review 复核 |
| tree-sitter 是**隐式环境依赖**（他人机器可能没有） | 探测式导入 + 标准库降级；降级通道跑同一批测试；`tools/README.md` 标注"可选加速依赖" |
| 与既有检查**重复建设** | 分工表：单行块/任务号（format-check）· 注释语言（repo-lint）**不重复**；边界写进工具 README 与标准章节 |
| **JavaDoc 被误删**（API 契约） | MVP 显式跳过 `/**` block_comment |
| 门禁噪声导致 AI 绕过（批量加豁免标记） | 不提供逐行豁免标记；只提供按文件/提交的显式 baseline（对齐 `format-jdt-gate` 的 BASELINE 形态），且 baseline 出现在 review 可见处 |
| **做成大而全平台** | §5 步骤划分 + §8 明确不做清单 |
| 与 P67 边界混淆 | 分维度：P67 管结构（长度/嵌套/复杂度），本提案管注释内容；各自注册门禁，互不改阈值 |
| 单文件将来膨胀 | §4.2 已书面留档抽包触发条件 + 必同步扩 `check_tools_readme` |

## 8. 明确不做（MVP 边界）

❌ Web UI · ❌ 数据库 · ❌ dashboard · ❌ 复杂 NLP · ❌ 多模型路由 · ❌ 自动重写注释（SAFE_REWRITE 关闭）
❌ 全项目历史注释清理（仅 `--diff`；`--all` 只读审计留 V2）· ❌ JavaDoc 自动修改 · ❌ 自动生成注释
❌ 非 Java 语言（Python/JS/SQL 留 V2，届时按 §4.2 抽包）· ❌ 工具内直接调用 LLM · ❌ 独立 Java/Maven 工程
❌ `aic` 用户可见命令（如需只注册 hidden command，V2）· ❌ 新增 RFC/ADR · ❌ 改动 `loaders/` 与 `templates/prompts/`

---

## Review Log

| Reviewer | Decision | Date |
|---|---|---|
| User (AI Maintainer operator) | **Approved** —— 裁定 1/2/3 全部同意（工具单文件 + 文件内 parser 抽象 / 不加 CLI 服务层 / 策略补进既有标准），并要求先出 MVP 落地计划 | 2026-09-23 |
| User (AI Maintainer operator) | **Implemented** —— MVP 八步全部落地并按实测验收（见下）；`--report-only` 是否翻 FAIL **留待用户裁定** | 2026-09-23 |

## Implementation Record

**实施时间**：2026-09-23（MVP 八步；8 个提交）

| 步 | 提交 | 实测验收 |
|---|---|---|
| S1 策略先行 | `c964fcc` | `documentation.md → Comment Quality`（六级分类 + 稳定规则 id + 判定顺序 + 安全原则）· `ai-coding-rules` Rule 12 一句原则 · G5 三处「无豁免全量要求」对齐。**门禁抓到真问题**：`maintenance.yaml` 引用了尚未落地的工具路径 → path-audit FAIL（2 broken）→ 改为不含路径的表述 |
| S1b 去对冲 | `d5bd08a` | `skills/implement/decision.md` 原「Documentation is mandatory, not optional」与标准冲突 → 拆为「声明级文档必需 / 代码级注释默认不写」；术语统一为「**承重注释（load-bearing）**」。**未采纳** runtime-base 加引用（层级错位，且 `standards-loader` 的 Always Load 已覆盖） |
| S2 候选提取 | `e514d7c` | 单文件 + 文件内 parser 抽象（tree-sitter / 标准库词法降级）· 14 测试 · **真实仓两通道完全一致**：housekeeping 1311 / cmdb 5107 / knowledge 22748 条，位置/文本/kind 逐条相同 |
| S3 diff 限定 | `9ed2f14` | 只处理新增行；存量不被触碰；未跟踪整文件视为新增；纯删除不产出；非 git 退化为全量并告警 · 20 测试 |
| S4 规则引擎 | `6045c9b` | 35 测试（承重六类 ×3 = **18 条零误删** · 泔水 26 条按预期命中）· 退出码 0/1/2/3 · 真实代码抽查暴露并修正 3 类误删（枚举常量 / 字段式名词短语 / 句中动词） |
| S5 CLI 与安全 | `9de949f` | `check`/`fix` 子命令 · **fix 默认 dry-run**、`--apply` 只删确定类 · 幂等 · 行尾只剔注释 · 43 测试 · 真 git 仓端到端（check 2 DELETE → dry-run → apply 删 2 条且承重/REVIEW 均保住 → 再 check 无 DELETE） |
| S6 门禁注册 | `807a6a0` | `gates.develop` 加 `comment-lint`（`{src} --diff --report-only`，**只报不拦**）+ runtime-develop 门禁段 · 真仓模拟：DELETE=1 → exit 1 → 清理后 exit 0 |
| S7 技能 | `e85bfcc` | `skills/comment-cleaner/SKILL.md`（策略只引用不复制；排除 review/verify 改码；误报要上报而非绕过）· 技能 38 → **39** |
| S8 真实验证 | 本批 | 见下 |

### S8 真实可用性验证（只读，未写任何业务仓库）

**历史 diff 干跑**：8 个业务仓库各取最近 25 个非合并提交，仅统计该提交新增行内的注释
（`temp/p69-s8-historical-diffs.py`，工具函数复用，一次运行）：

| 仓 | 新增注释 | DELETE | REVIEW | KEEP |
|---|---|---|---|---|
| bs-integration | 41 | 4 | 28 | 9 |
| cmdb-api | 20 | 6 | 4 | 10 |
| housekeeping-service-api | 128 | 1 | 94 | 33 |
| knowledge-api | 41 | 0 | 29 | 12 |
| platform-api | 58 | 6 | 34 | 18 |
| resource-manager | 19 | 0 | 18 | 1 |
| user-center-api | 25 | 0 | 6 | 19 |
| ipd-technical-design-drawings | 0 | 0 | 0 | 0 |
| **合计** | **332** | **17（5.1%）** | **213（64.2%）** | **102（30.7%）** |

**确定可删项全量人工审计（17/17）**：逐条核对 → **0 误删**。命中类型：装饰性分段线（10）·
复述代码（6，如 `构建请求体` 对 `Map<...> requestBody = new HashMap<>()`）· 流程套话（1，
`首先检查 cause 是否为 null` 对 `if (cause == null) {`）。

**审计中发现并已修正的 4 类真误报**（修正后误删类清零，代价是确定可删量 34 → 17）：

| 误报类别 | 例子 | 修正 |
|---|---|---|
| 枚举常量上的注释 | `PENDING, // 待处理` | 新增字段/枚举护栏：这类注释按标准属「必须写且禁止名字直译」→ 名字直译是**需改**不是**可删** → 交 REVIEW |
| 字段式名词短语 | `// 总记录数` 对 `result.setTotalRecords(...)` | 动词必须在**注释开头**（`待处理`/`总记录数`/`尝试查询…` 不再是复述） |
| 句中动词 | `// 尝试查询表是否存在`、`// Step2: 开关判断…` | 同上（句中动词不构成复述句式） |
| **巧合动词链接** | `// 删除转码流` 的下一行是 `deleteRateLimiter.tryAcquire(...)` | 动词只用于识别句式；**链接必须落在名词/标识符**上（`delete` 撞变量名不算复述） |

**召回率**：合成泔水样本 26 条 → 按预期规则命中率 100%（单测断言），确定可删覆盖 15/26（其余
11 条为刻意交 REVIEW 的 DUPLICATE/UNCERTAIN）。真实历史 diff 上确定可删占比 5.1% —— 这是
「宁可漏删」的直接代价，符合提案 §2 的安全底线。

**端到端**：真 git 仓（临时仓）完整走通 `check → fix --dry-run → fix --apply → 独立提交 → 再 check`；
develop 门禁模拟走通（DELETE → exit 1 → 清理后 exit 0）。

### 是否去掉 `--report-only` 翻 FAIL（**用户裁定：维持现状 —— 先观察一段时间**）

**裁定（2026-09-23）**：保持 `--report-only`（只报不拦），**先观察一段时间**；不设时间上限，
触发翻 FAIL 的信号 = 观察期内三项同时成立：① 确定可删项**零误报**（含无新增误报上报）；
② AI 侧 REVIEW 裁定结果稳定（无需频繁把 `DELETE` 改回保留）；③ 用户确认可用于拦截提交。
观察入口：门禁报告（`comment-lint --diff --report-only` 的 DELETE/REVIEW 计数）· 技能要求记录的
误报上报（原文 + 规则 id）· 下一次 maintain 巡检时复核本提案的观察结论。

**当初的建议（保留备查）**：暂不翻，保持只报不拦。判据：① 真实数据里 REVIEW 占新增注释 64%（现阶段需要的是让 AI
按技能逐条裁定，而不是让门禁拦住 2/3 的新注释）；② DELETE 精度虽经 17/17 审计通过，但样本量仍小
（17 条/7 仓）；③ 翻 FAIL 的触发条件建议定为「累计再跑 N 个真实任务后，DELETE 精度仍 100%
且团队确认可用于拦截」。届时只需删掉 `main-chain-capabilities.yaml` 里该门禁 cmd 的 `--report-only`。

### 与提案的偏差（均已披露）

1. `config/comment-lint.yaml` 由 S1 推迟到 S2 落地（避免"无消费者的配置声明"）。
2. 术语由提案期的「信息增量 / Value-Burden」收敛为「**承重注释（load-bearing）**」（用户口径）。
3. `runtime-base.md` 未加引用（按用户确认跳过）。
4. 规则实现细节比提案更保守：动词必须位于注释开头 · 链接必须落在名词/标识符 · 字段/枚举注释不判复述
   —— 三条都是真实代码审计暴露误删后加的，未在提案中预设。

### 未做（按 §8 边界，留 V2）

`aic` hidden command · 非 Java 语言 · `--all` 全仓审计 · 工具内调 LLM · baseline 机制 ·
SAFE_REWRITE（自动重写）· 单文件抽包（触发条件已书面留档于 §4.2）