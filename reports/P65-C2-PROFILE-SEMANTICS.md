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

| # | 文件 | 变更 | 归属 | 状态 |
|---|---|---|---|---|
| 1 | `tools/README.md` | jdt 条目补语义边界；措辞由"与 IDEA 默认同源"改为"**IDEA 风格族导出；参数表语义与 IDEA 不同**"；并把语义边界出处由 gitignored 日志改为**本提案 + `config/maintenance.yaml`** | A | ✅ **已执行** 2026-09-21 |
| 2 | `config/maintenance.yaml` | C2 语义边界登记（含"120 非硬约束"与"改 alignment 属 profile 校准"） | A | ✅ **已执行** 2026-09-21 |
| 3 | `templates/runtime/runtime-develop.md`（`format-jdt-c2` 条目）+ `tools/format-jdt-gate.py`（docstring） | 明确**参数表语义与 IDEA 不同**、`lineSplit=120` **非硬约束**（受折行策略支配） | A | ✅ **已执行** 2026-09-21 |
| 4 | `tools/jdt-format-gate/eclipse-format.xml` | alignment 取值校准（**待小样评估后**） | B | ⏳ 待决 |
| 5 | `tools/jdt-format-gate/known-ignore.txt` | 豁免附理由 + 季度复核（治理） | D | ⏳ 待决 |

**A 项执行时的核查结论**：`cli/commands/*`、`config/main-chain-capabilities.yaml`、
`config/environments/*` 中**未发现**任何把 120 当硬约束的表述（检索 `120` / `lineSplit` 无命中）
→ A 的动作实际只落在上表 1–3 三处；未改动任何 profile 取值、未触碰业务仓。

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

## B 小样评估结果（2026-09-21 执行；只读，未改 profile、未碰业务仓）

**仪器**：新增 `tools/jdt-profile-eval.py`（可复用，后续校准同用；只读源目录，产物写 `/tmp`）
+ 回归测试 `cli/tests/test_jdt_profile_eval.py`（9 项，含「候选键必须存在于现行 profile」守护）。

### ① 全仓规模（C0 现行 profile vs C1 = 参数表 0 → 17）

| 仓库 | 源目录 | files | C0 differ / diffLines | C1 differ / diffLines | Δ diffLines |
|---|---|---|---|---|---|
| housekeeping-service-api | `housekeeping-service/src/main/java` | 58 | 44 / 5065 | 54 / **9386** | **+4321（+85%）** |
| housekeeping-service-api | `housekeeping-common/src/main/java` | 42 | 18 / 989 | 25 / **1714** | **+725（+73%）** |
| platform-api | `src/main/java` | 1535 | 614 / 70117 | 791 / **146380** | **+76263（+109%）** |
| knowledge-api | `knowledge-web/src/main/java` | 102 | 87 / 13732 | 98 / **21345** | **+7613（+55%）** |
| knowledge-api | `knowledge-service/src/main/java` | 546 | 294 / 90464 | 378 / **159729** | **+69265（+77%）** |

### ② 压力样本（8 个「续行最多」文件；含二次格式化收敛性）

| 候选 | files | differ | diffLines | Δ | 二次 differ（收敛） | 最长行 | >120 行 |
|---|---|---|---|---|---|---|---|
| C0-baseline | 8 | 8 | 8551 | +0 | **0** | 3903 | 501 |
| C1-args17 | 8 | 8 | 13868 | +5317 | **0** | 3903 | 175 |
| C2-args49 | 8 | 8 | 13868 | +5317 | **0** | 3903 | 175 |
| C3-only-mi17（最小改动） | 8 | 8 | 13501 | +4950 | **0** | 3903 | 190 |
| C1c-args17+cond17 | 8 | 8 | 13932 | +5381 | **0** | 3903 | 174 |
| C2c-args49+cond17 | 8 | 8 | 13932 | +5381 | **0** | 3903 | 174 |

### ③ 结论（数据驱动）

1. **存量基线本就巨大**：platform-api 1535 个文件中 **614 个**与现行 profile 有差异（70,117 行）
   —— 业务仓代码并非按此 profile 书写（IDEA 风格），门禁完全依赖 `--changed` 增量语义豁免存量。
   这解释了 `known-ignore.txt` 机制为何必要。
2. **B 使格式差异近乎翻倍**（+55% ~ **+109%**）：存量豁免机制不变，但**增量噪声显著上升**
   —— 被改动文件里**既有的参数折行**都会变成 NEW-DIFF 命中，开发者会被更多格式差异拦截。
3. **收敛性良好（0 振荡）**：所有候选二次格式化 `differ=0` → B 的 fixpoint 风险低
   （`known-ignore.txt` 不必因 B 扩容，至少在这些仓与样本上如此）。
4. **「行 ≤ 120」仍不可达**：B 把 >120 行从 501 降到约 175（**-65%**，确有收益），
   但样本中仍存在 **3903 字符**的极端长行（字符串/枚举常量），任何 alignment 设置都无法消除。
5. **C2 与 C1 统计相同**（13868/175）：17 与 49 在本样本上差异行数一致（缩进层级不同、行数相同）。

### ④ 建议（待用户裁决）

| 选项 | 数据支持度 | 建议 |
|---|---|---|
| **A（已执行）** | 零成本、已消除误读 | **维持** |
| **B 全量实施** | 差异 +55%~+109%、噪声上升、收益仅「参数逐行」 | **暂缓**；若推进须业务侧确认 + 低活跃窗口 + 分批 |
| **B 最小化（仅 MI=17）** | 最小改动仍 +4950 行（样本）/噪声同源 | 仅当「参数逐行」是硬诉求时考虑 |
| **C（换基线器）** | B 无法达成 IDEA 一致与 ≤120 的根本解 | 建议**先做可行性评估**（IDEA headless 在 CI/离线的可用性、许可与镜像成本） |
| **D（`known-ignore.txt` 治理）** | 与 B 无关，独立价值 | **建议采纳**（豁免附理由 + 季度复核） |

**评估副产物**：`tools/jdt-profile-eval.py` 成为可复用仪器 —— 未来任何 profile 校准决策
都可先出这张表再定。

---

## C 可行性评估结果（2026-09-21 执行；本机实测 + 只读）

### ① 环境事实（本机，无需新增安装）

| 项 | 值 |
|---|---|
| IDE | **IntelliJ IDEA 2026.2.0.1**，`build IU-262.8665.337`，**`productCode: IU` = Ultimate** |
| 安装位置 | Windows 侧（WSL 通过 interop 调用）；WSL 侧已有其配置目录 |
| 自带 CLI | **`bin/format.bat`** → `format` 命令（另有 `inspect.bat`）：`-s <code style xml>` / `-r` / **`-d|-dry`（干跑仅回状态）** / `-m <mask>` / `-charset` / `-allowDefaults` |
| 跨路径读取 | **接受 UNC 路径**（实测 `\\wsl.localhost\Ubuntu-24.04\…` → 正常检查）→ **免拷贝**，可直接读 WSL 内仓库 |

### ② 实测结果

| 指标 | 实测值 | 含义 |
|---|---|---|
| 全仓吞吐 | **1535 文件 / 82 秒**（含约 26s 启动） | CI 可用（非阻塞级） |
| 存量判定 | **595 / 1535（39%）文件「Needs reformatting」** | 与 JDT 现行 profile 的 **614 文件 / 70,117 行** 同量级 |
| 退出码 | **恒为 0**（含 "Needs reformatting" 时） | ⚠️ **无法直接用作门禁判据**，须解析 stdout（英文 `Needs reformatting` / `Formatted well`）→ 集成脆弱 |
| 许可 | 本机已激活，运行无提示 | ⚠️ Ultimate 需许可；CI/他人机器构成约束（Community 是否同带该 CLI 未验证） |
| 权威 code style | 业务仓 `.idea/` **无** `codeStyles/Project.xml`；本机 IDE **无** `codeStyleSettings.xml` | ⚠️ **「IDEA 一致」并不自动达成** —— IDE 用**出厂默认**，而默认下仍有 39% 文件需重排 |

### ③ 结论与细化选项

| 细化选项 | 评价 |
|---|---|
| **C1（推荐，最小路径）** | `JdtFormatCheck.java` 头注释**本就写着**「profile 建议用 IDEA 导出的 Eclipse XML Profile 替换」，而 IDEA 支持 **Export → Eclipse XML Profile** → 在 IDE 内**一次人工操作**导出，**覆盖 `eclipse-format.xml`**：门禁栈**完全不变**（JDT，退出码语义/增量差分/豁免机制全部沿用），设置与开发者 IDE 同源；**无许可、无跨平台、无 stdout 解析问题**。导出后用 `tools/jdt-profile-eval.py` 量化新基线（仪器已就绪） |
| **C2（不推荐）** | 直接以 IDEA CLI 作门禁：技术可行（干跑/UNC/吞吐均 OK），但**退出码恒 0**、Ultimate 许可、Windows/WSL interop 绑定、仍需自备 code style XML |
| **维持 A / D 治理** | 与 C 无冲突，可并行 |

**评估副产物**：Profile 出处查明 —— 现行 `eclipse-format.xml` 基底是 **Eclipse `Default` profile（version 21，375 设置）**，仅部分校准为「IDEA 风格族」→ 与 IDE 出厂默认的参数表语义相异（§1 已证）。这解释了「为何存量差异这么大」。

---

## D 采纳与实施（2026-09-21，已完成）

`known-ignore.txt`（C2 门禁的**逃生门**）治理落地，**零 Java 改动**（Java wrapper 本就跳过 `#` 注释行）：

| 项 | 内容 |
|---|---|
| 清单格式 | 每个路径条目**紧邻上方**必须一行 `# reason: <理由>（<YYYY-MM-DD> 复核基线）`（**单行**） |
| 强制机制 | 新增 `tools/checks/jdt_ignore.py`（注册进 `check.py`）：缺理由 / 缺日期 / **悬空理由**（条目被删而理由留存）→ **ERROR**；复核基线 **> 180 天** → **WARN**（季度复核信号自动化） |
| 测试 | `cli/tests/test_jdt_ignore_check.py`（+8）：合规 / 缺理由 / 缺日期 / 过期 / 悬空 / 纯注释 / 真实清单受治 |
| 文档 | `tools/README.md`（治理约定）+ `config/maintenance.yaml`（决议登记） |

**效果**：豁免不再是无声逃生门 —— 每条豁免都带理由与复核期限，且**过期自动告警**（把"季度复核"从人的记忆变成门禁信号）。
---

## C1 验证结果（2026-09-21，用户执行 IDE 导出）—— **C1 无效（且被否定），并更正一处推断**

### ① 事实：导出文件与现行 profile **逐字节完全一致**

| 项 | 值 |
|---|---|
| 用户导出文件 | `…/WXWork/…/2026-09/Default.xml`（40,842 bytes，mtime 2026-09-03 11:33） |
| sha256（导出） | `d120900b43c41fbcd7c830e8f1c61b7f152ad37726a3eb87c0925d0c6f8a3ee1` |
| sha256（仓内 `eclipse-format.xml`） | **`d120900b43c41fbcd7c830e8f1c61b7f152ad37726a3eb87c0925d0c6f8a3ee1`（同）** |
| 设置级比对 | 375 项，**无任何差异**（仅导出/仓内一致） |
| mtime 吻合 | 与 `c7eef0b`（2026-09-03「C2 profile 校准定稿」）同日 → 仓内文件即该次导出产物 |

**结论**：**现行 C2 profile 本来就是 IDEA 的 Eclipse-XML 导出**。故「重新导出覆盖」是**恒等操作**，
不可能改变任何语义 → **C1 不是解法**（而是已被验证为同一物）。

### ② 更正上一节的推断（本提案内部）

上一节"C 可行性评估"曾推断：现行 profile 基底是 **Eclipse `Default` profile（仅部分校准）**。
**该推断错误** —— 文件名/profile 名 `name="Default"` 只是 **IDEA 导出方案的名字**，
内容是 **IDEA 的 Java code style 经 Eclipse-XML 映射后的结果**。以本节实测（byte-identical）为准。

### ③ 根因最终定位：**表达力缺口**，而非设置映射错误

- IDEA 的导出**忠实**地把 IDEA 设置写成 Eclipse 设置；但 Eclipse 的折行模型（`alignment_*`）
  **无法表达 IDEA 的排版策略**（尤其「保留已有折行 / Keep line breaks」这类语义）→
  导出必然落为 `alignment_for_arguments_in_method_invocation=0`（对 JDT 即**不折行**）。
- 于是同一份代码：**IDEA 不动**（其引擎保留手工折行）、**JDT 合并参数折行且可越过 `lineSplit=120`**。
  §1 的"矛盾"由此完全闭合：**不是配置错，是两套引擎的表达力差**。
- 推论：**任何"把 IDEA 设置导出给 Eclipse/JDT 用"的路线都先天受限**（含 B）。

### ④ C2 亦不能"清零"，而这不影响门禁设计正确性

- C2（用 IDEA 引擎做基线）实测：**IDEA 自己也判 595/1535（39%）文件「Needs reformatting」**
  → 业务代码与**任何单引擎的全量基线**都不一致（开发者实际是"只格式化改动行"的增量习惯）。
- 因此门禁的**正确形态就是增量收敛**：现行 `--changed` 语义（存量豁免 + 新增拦截）**是对的**；
  「全量清零」不是可达目标，也不该是目标。

### ⑤ 最终建议（P65 收口）

| 选项 | 最终判定 |
|---|---|
| **A 维持 + 明确边界** | ✅ 已执行；**维持**（语义边界已固化，误读已消除） |
| **B 校准 profile** | ❌ **数据否定**：差异 +55%~+109%、≤120 不可达，且（本节）证明是**表达力**问题而非取值问题 |
| **C1 重导出覆盖** | ❌ **恒等操作**（byte-identical）→ 无效 |
| **C2 用 IDEA 引擎做门禁** | ⏸️ **按需可选**（唯一"与 IDE 同源"路径）：代价＝退出码恒 0（须解析 stdout）、Ultimate 许可、WSL interop 绑定、~82s/1535 文件；且仍不能清零 |
| **D 豁免治理** | ✅ 已采纳并实施（理由 + 180 天复核告警） |

**一句话结论**：C2 门禁的定位不是"让代码与 IDEA 完全一致"（不可达），而是
**"与既有 profile 一致 + 增量收敛"**；若要"与 IDE 行为同源"，唯一路径是引入 **IDEA 引擎（C2）**，
需业务侧明确诉求后再立项。
---

## C2 二审（2026-09-21，用户补充版本信息后的校正）—— 许可不再是障碍，新约束浮现

### ① 用户补充的事实与我上轮的结论校正

| 项 | 事实 | 对结论的影响 |
|---|---|---|
| 用户本人的 IDE | **社区版** | — |
| 本次导出的 XML | 来自**同事的付费版** IDEA | **不影响 profile 有效性**：Java code style 语义不因版本而变（导出内容 = 设置映射）。故 §C1 的 **byte-identical 结论不受影响** |
| 本机（抽查） | Windows 侧 **IU 2026.2.0.1**；WSL 侧 Gateway 后端 **IU 2026.2.2**（`~/.cache/JetBrains/RemoteDev/dist/…`，**自带 `format.sh` + `idea.sh`**） | 说明**Linux 侧 CLI 也存在**，且可在 WSL 原生运行（无需 Windows interop） |
| **我上轮的"许可构成约束"** | ❌ **需更正** | 见 ② |

### ② 许可校正：自 **2025.3 起两个版本已合并为单一产品**

JetBrains 官方（2025-07 公告 / 2025-12 博客 / 文档）：

> "Starting with IntelliJ IDEA 2025.3, we're combining these two editions into a single, unified product:
> IntelliJ IDEA." —— [IntelliJ IDEA as a unified product](https://www.jetbrains.com/help/idea/intellij-idea-single-distribution.html)
> "All the functionality of the Community Edition remains free for non-commercial and commercial use.
> … the extended tooling is accessible in the Ultimate subscription." —— [JetBrains Blog 2025-12](https://blog.jetbrains.com/idea/2025/12/intellij-idea-unified-release/)

本环境为 **2026.2 = 统一产品**，故 `productCode: IU` 只是**统一发行版**的编号，**不再等价于"付费版"**；
`format` CLI 属随安装包提供的能力（文档将 `format` 列于 CLI 说明，未附订阅前提）→
**C2 的许可障碍不成立**（免费核心功能即可，且允许商用）。

### ③ 新约束（比许可更真实）：CLI 会**后台启动 IDE 实例**，且**已在运行的实例会导致失败**

> "The command-line formatter launches an instance of IntelliJ IDEA in the background and applies the
> formatting. **It will not work if another instance of IntelliJ IDEA is already running.**"
> —— [Format files from the command line](https://www.jetbrains.com/help/idea/command-line-formatter.html)

含义：
- 开发者机器上 IDE 通常**开着** → CLI 门禁**会间歇性失效**（本次实测能跑，是因为当时没有实例运行）。
- 每次调用都要**冷启动一个 IDE 实例**（实测 ~26s）→ 不适合作为**交互式 A 层门禁**，适合 **CI / 批处理**。

### ④ C2 最终判定（理由更新，结论不变）

| 维度 | 判定 |
|---|---|
| 许可 | ✅ **不再是障碍**（统一产品免费核心 + 可商用）—— 撤回上轮该条 |
| 引擎可得性 | ✅ Windows `.bat`、Linux `.sh` 均存在；本机两侧都有 |
| 退出码 | ❌ **恒 0**（含 Needs reformatting）→ 须解析 stdout |
| 运行约束 | ❌ **单实例互斥 + 冷启动 ~26s** → 不适合开发者机上的交互式门禁 |
| 清零能力 | ❌ IDEA 自判 **595/1535（39%）** 文件需重排 → 与任何单引擎全量基线都不一致 |
| **结论** | ⏸️ **仍为"按需可选"，但适用场景收窄为 CI/批处理**（若要"与 IDE 行为同源"）；<br>开发者机上的门禁仍以现行 JDT 栈（A）+ 豁免治理（D）为准 |
---

## Review Log

| Reviewer | Decision | Date |
|---|---|---|
| User (AI Maintainer operator) | **Pending**（用户于 2026-09-21 指示立案） | 2026-09-21 |
| User (AI Maintainer operator) | **Option A 已批准并执行**（零基线扰动）；B（profile 校准）与 C（换基线器）待小样评估后决策；D（`known-ignore.txt` 治理）待决 | 2026-09-21 |
| User (AI Maintainer operator) | **C2 二审（用户补充版本信息）**：① 导出 XML 来自**同事付费版**、用户本人用社区版 → **不影响** profile 有效性（Java code style 语义与版本无关），C1 byte-identical 结论成立；② **撤回**上轮「Ultimate 许可构成约束」——自 **2025.3** 两版合并为单一产品，免费核心功能**可商用**，本环境 2026.2 即统一版；③ 新增真实约束（官方文档）：CLI **后台启动 IDE 实例，且已有实例运行时失效** + 冷启动 ~26s → **不适合交互式门禁，收窄为 CI/批处理**；④ C2 结论不变（按需可选） | 2026-09-21 |
| User (AI Maintainer operator) | **C1 已验证（否决）**：IDE 导出的 `Default.xml` 与仓内 `eclipse-format.xml` **逐字节一致**（sha256 同为 `d120900b…`）→ 现行 profile 本就是 IDEA 导出，重导出为恒等操作；并**更正**上节「Eclipse Default 基底」的错误推断。根因最终定位为**引擎表达力缺口**（Eclipse 折行模型无法表达 IDEA 的保留折行），故 B/C1 皆不可解；C2 记为按需可选 | 2026-09-21 |
| User (AI Maintainer operator) | **Option C 已评估**：技术可行（WSL 可驱动 IDEA `format` CLI、UNC 直读、1535 文件 82s），但**退出码恒 0** + Ultimate 许可 + 无权威 code style（IDE 用出厂默认，39% 文件仍需重排）→ 推荐细化为 **C1：IDE 内一次导出 Eclipse XML Profile 覆盖 `eclipse-format.xml`**（门禁栈不变、设置与 IDE 同源） | 2026-09-21 |
| User (AI Maintainer operator) | **Option D 已采纳并实施**：`known-ignore.txt` 逐条附理由 + 复核日期，`tools/checks/jdt_ignore.py` 强制（缺理由/悬空 ERROR、超 180 天 WARN），+8 测试 | 2026-09-21 |
| User (AI Maintainer operator) | **Option B 已评估**（小样 + 全仓规模，数据见上节）：B 可行且收敛，但差异 +55%~+109%、≤120 仍不可达 → 待用户就「暂缓 / 最小化实施 / 转 C 评估」裁决 | 2026-09-21 |

---

## Implementation Record — Option A（部分实施，2026-09-21）

**范围**：仅文档/语义澄清，**零行为变更**（profile 取值、门禁逻辑、业务仓基线均未改动）。

| 文件 | 变更要点 |
|---|---|
| `tools/README.md` | ① "与 IDEA 默认 Java 格式化同源" → "**IDEA 风格族导出**，但**参数表语义与 IDEA 不同**"；② 语义边界的证据出处由 gitignored 日志改为**本提案**与 `config/maintenance.yaml`（提交物不得索引未提交产物） |
| `templates/runtime/runtime-develop.md` | `format-jdt-c2` 条目补：参数表 `alignment=0` = *no wrap* → 手工折参数被合并、可**超过** `lineSplit=120`；`join_wrapped_lines=false` 仅覆盖二元/条件表达式；**本门禁保证与 profile 一致，不保证行 ≤ 120**（英文，模板层语言约定） |
| `tools/format-jdt-gate.py` | docstring 同步上述语义（中文，tools 脚本注释约定） |

**核查**：`cli/commands/*`、`config/main-chain-capabilities.yaml`、`config/environments/*` 无 120 硬承诺表述；
`outputs/` 在模板中的出现均为**产物落盘约定**（合法），非未提交证据引用。

**门禁**：`check.py` PASS · `repo-lint` 0 ERROR · `path-audit` 0 broken · `proposal-audit` 0/0 ·
`workflow-command-audit` 无新增 · 单测全绿。