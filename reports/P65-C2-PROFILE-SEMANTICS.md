# Change Proposal: P65 — C2 格式 profile 的语义边界与校准（`lineSplit=120` vs `alignment=0`）

| Field | Value |
|---|---|
| Status | **Proposed** |
| Type | Structural (C2 门禁 profile 契约 + 业务仓格式基线) |
| Author | AI Maintainer |
| Created | 2026-09-21 |
| Reference | 用户指示立案 2026-09-21；来源＝另一会话反馈（"profile 声明 120/不合并，实测却合并成长行，需查清探测用哪个 profile"）；证据落 `tools/README.md` jdt 条目 + `config/maintenance.yaml` "C2 profile 语义边界登记"（§1 已自包含复述实测数据） |
| Process | OPERATIONS §12 Change Management |

## 1. Problem

### 1.1 同一声明与实测行为的直接冲突（本机可复现）

`tools/jdt-format-gate/eclipse-format.xml`（唯一 C2 profile）声明：

| 声明项 | 值 |
|---|---|
| `lineSplit` | **120** |
| `join_wrapped_lines` | **false**（语义直觉："不合并已有折行"） |
| `alignment_for_arguments_in_method_invocation` | **0** |
| `alignment_for_arguments_in_allocation_expression` | **0** |
| `alignment_for_conditional_expression` | **0** |
| `alignment_*` 合计 | **48 项，其中 35 项为 0** |

实测（jdt.core **3.13.0** + JDK 8，`java 1.8.0_502`，夹具 `<120` 与 `>120` 两例）：

| 档位 | `if (true && false`⏎` && true)` | `String.join(..., "aa…",`⏎` "cc…")` |
|---|---|---|
| **真实 profile**（`join_wrapped_lines=false`） | **保留折行** | **合并为单行** |
| 对照 `join_wrapped_lines=true` | 合并 | 合并 |
| 对照 不给该键（JDT 默认） | 合并 | 合并 |
| 超长夹具（合并后 **152 字符 > 120**） | — | **仍合并为 152 字符单行** |

alignment 取值扫描（超长夹具）：**0 / 1 / 5 → 不折行**（152 字符单行）；**17 → 逐参数折行**。

### 1.2 根因分层

1. **`join_wrapped_lines=false` 的作用域比直觉窄**：它只管理**二元/条件表达式**的手工折行
   （上表第一列已证），**不覆盖方法调用参数表**。
2. **参数表由 alignment 管控，而 0 等效"不折行"**：参数一律并入一行，且**不再重新折**——
   因此 `lineSplit=120` 在该构造上**被自身 profile 越过**（JDT 中 `lineSplit` 是**目标行长**，
   受折行策略支配，不是硬约束）。
3. **与"IDEA 默认同源"的表述相互矛盾**：IDEA 默认对已有折行多为"保留"（Keep line breaks），
   而 **JDT 3.13 没有"保留已有折行"这一档**——折行策略只有"折 / 不折 / 如何折"。
   于是同一份代码 **IDEA 里不动、C2 门禁里被合并成长行**。这正是另一会话困惑的直接来源。

### 1.3 后果

| 后果 | 说明 |
|---|---|
| 门禁承诺被误读 | "C2 通过"≠"行 ≤ 120"；把 120 当硬期待会造成**门禁差异 vs 业务不合规**的误判 |
| 无意义大 diff 风险 | 若为了满足 120 而反向调整业务代码，产出的是**JDT 语义驱动的纯格式 diff**（评审成本高、价值低） |
| 存量豁免长期化 | `known-ignore.txt`（现登记 1 个文件 `main/java/.../EnterpriseProvider.java`，路径相对被扫 srcDir）承载"无 fixpoint（format↔format 振荡）"文件；参数布局在该类文件上反复变化是振荡机制之一 → 逃生门可能长期存在 |
| 声明与实效脱钩 | 与 **P60**（门禁自校验：声明 vs 实效必须对账）同族缺陷：声明式配置的能力边界未与文档/期待对账 |

### 1.4 现状（本提案立案前已落的最小记录，不含行为变更）

- `tools/README.md`：jdt 门禁条目已补**语义边界**（不保证 ≤ 120；无法表达 IDEA"保留已有折行"）
- `config/maintenance.yaml`：已登记 C2 语义边界与"改 alignment ＝ profile 校准，需提案 + 业务侧确认"
- **未改动任何 profile 取值、未改任何业务仓基线**

## 2. Root-Cause

| 层 | 根因 |
|---|---|
| profile 数据 | 由"IDEA 风格族"导出的 JDT profile：导出器把大量 alignment 置 0（IDEA 侧由"Keep line breaks"承担的语义，JDT 侧无对应档 → 退化为"不折行"） |
| 门禁契约 | `lineSplit=120` 被当作可执行承诺引用，但未声明其**受折行策略支配**的从属关系 |
| 文档 | "与 IDEA 默认 Java 格式化同源"未区分**风格族一致**与**逐项语义一致**（参数表处二者不一致） |
| 机制 | 缺"配置能力边界"的记录位（P60 通用缺口：声明式配置需与实效对账） |

## 3. Options

### 3.1 Option A — 维持现状 + 明确边界（**立即执行，零基线扰动**，推荐先做）

- 保持 profile 取值不变；把语义边界固化到**门禁可读处**：`tools/README.md`（已补）+
  `config/maintenance.yaml`（已登记）+ 门禁输出/命令文档中**移除 120 的硬承诺表述**。
- 修正"与 IDEA 默认同源"为"**IDEA 风格族导出；参数表语义与 IDEA 不同**"。
- 优点：零 diff、零业务影响、立即消除误判；缺点：门禁差异仍需人工判断（不解决"想保留折行"的诉求）。

### 3.2 Option B — 校准 profile（**能力对齐**，需业务侧确认）

- 改关键 alignment 取值（候选：`alignment_for_arguments_in_method_invocation` /
  `..._in_allocation_expression` / `alignment_for_conditional_expression` 由 0 →
  **17 类"逐参数折行"档**，实测 17 生效）。
- 后果：**业务仓 C2 基线大 diff**（需重跑基线、可能触发大量 NEW-DIFF 拦截）；
  须配 `--apply` 迭代至 fixpoint + `git diff -w` 安全校验，并复核 `known-ignore.txt`。
- 优点：门禁承诺变为"可执行、可判"（行 ≤ 120 与折行布局一致）；
  缺点：一次性大 diff 与评审成本，且**仍不等于 IDEA"保留原折行"**（JDT 只能"逐参数折行"）。

### 3.3 Option C — 换基线器（IDEA 侧为准）

- 以 IDEA 自身格式化器（CLI/headless）作 C2 基线，JDT 仅作辅助比对。
- 优点：与业务侧 IDE 行为真正一致；缺点：引入 IDEA 安装/许可/CI 可行性依赖，跨平台成本高，
  离线与门禁自包含性下降。

### 3.4 Option D（附带决议点）— `known-ignore.txt` 治理

维持"人工基线豁免"机制，但**要求每次豁免附理由 + 季度复核**（与存量债登记纪律一致），
避免逃生门静默长期化。

## 4. Recommendation

**两步走**：

1. **立即执行 Option A**（本次已落记录，仅需补充"移除 120 硬承诺表述"的确认）——零风险、消除误判。
2. **对 Option B 做小样评估后再决策**：选 3 类代表文件（DTO / Service / 测试类）各若干，
   用 2–3 个 alignment 候选值跑干跑差分，量化"文件数 / 差异行数 / 是否收敛（fixpoint）"；
   若 diff 体量与收敛性可接受 → 立 B 的实施任务（业务侧确认后）；否则转 C 评估或维持 A。
3. **Option D 采纳**（豁免附理由 + 季度复核）。

## 5. Proposed Changes

| # | 文件 | 变更 | 归属 |
|---|---|---|---|
| 1 | `tools/README.md` | jdt 条目补语义边界（**已落**）；措辞由"与 IDEA 默认同源"改为"IDEA 风格族导出；参数表语义不同" | A |
| 2 | `config/maintenance.yaml` | C2 语义边界登记（**已落**）；补 Option A 决议与"120 非硬约束" | A |
| 3 | `cli/commands/*` / `templates/runtime/runtime-develop.md` | 凡引用 120 处，明确其**从属**于 profile 折行策略（如有硬表述则改） | A |
| 4 | `tools/jdt-format-gate/eclipse-format.xml` | alignment 取值校准（**待小样评估后**） | B |
| 5 | `tools/jdt-format-gate/known-ignore.txt` | 豁免附理由 + 季度复核（治理） | D |

## 6. Validation Plan

| 选项 | 验证 |
|---|---|
| A | 只读实证：本提案 §1.1 表已可复现（同一夹具 × 三档 profile × alignment 取值扫描）；门禁全绿（`check.py`/`repo-lint`/`path-audit`/`proposal-audit`）；文档断言与 profile 取值一致（`join_wrapped_lines=false`、`alignment=0`，48 项中 35 项为 0） |
| B | 小样评估：3 类文件 × 2–3 候选值 → 输出"文件数/差异行数/是否收敛"对照表；在**一个**业务仓分支试跑 `--apply` + `git diff -w` 安全校验；确认无振荡后再立实施任务（含基线重跑与 `known-ignore.txt` 复核） |
| C | 可行性评估：IDEA headless 在 CI/离线的可用性、许可与镜像成本 → 结论入文档，不实施 |
| D | `known-ignore.txt` 每行附理由；季度巡检列出全部豁免供复核（机制复用现有存量债登记） |

## 7. Risks

| 风险 | 缓解 |
|---|---|
| 采用 B 后业务仓出现大范围格式 diff，干扰在途任务 | 仅在业务侧确认后实施；选低活跃窗口；`--apply` + `git diff -w` 安全校验；分批（先 1 个仓试点） |
| 采用 B 后仍与 IDEA 不一致（JDT 无"保留折行"档），预期再次落空 | §3.2 已明示 B ≠ IDEA 保留语义；若诉求本质是 IDEA 一致 → 应评估 C |
| 仅做 A 导致"想保留折行"的诉求被长期搁置 | A 的同时启动 B 小样评估（§4 第 2 步），产出量化依据供决策 |
| `lineSplit` 被继续当作硬约束引用 | §5 第 3 项显式清理硬表述；并在门禁文档标注"受折行策略支配" |
| 与 P60 同族（声明 vs 实效）分头处理 | 二者同根：P60 提供通用对账机制，本提案提供 C2 领域实例；季度回顾合并评估根因治理 |

---

## Review Log

| Reviewer | Decision | Date |
|---|---|---|
| User (AI Maintainer operator) | **Pending**（用户于 2026-09-21 指示立案） | 2026-09-21 |