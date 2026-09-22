# 外部盲检评审报告 — ai-system（2026-09-21）

- 类型: 外部盲检评审（External Blind Review，第三方模型独立评审）
- 日期: 2026-09-21
- 对象: `/home/syske/ws/ai-workspace/ai-system`（git 跟踪制品：368 文件 / ≈599k tokens）
- 评委: `qwen3.8-max`（阿里，主）+ `glm-5.3`（智谱，交叉）——**跨厂商、互不共享上下文**
- 通道: 已有 `qwen-token-plan-cn` 套餐（**边际成本 0**）；机器时间 ≈ 45 分钟
- 全量留痕: 本次运行的原始产出（8 份评审 + 执行日志 + 241 条发现索引 + 运行手册）为**运行期产物**
  （`outputs/` 与 `temp/`），**按约定不入库、不参与索引**；**本报告即持久记录**（已拣选高价值内容）
- 关联提案: **P60**（门禁自校验）、**P61**（外部盲检纳入运维形式）

---

## 一、一页结论

| 指标 | 值 |
|---|---|
| 评审产出 | 2 评委 × 4 包（文档层 / `cli` / `tools`+`config` / `skills`）= **8 份** |
| 发现 | **241 条**（4 BLOCKER / 54 ERROR / 135 WARN / 48 INFO） |
| 抽检精度 | **≈ 91%**（11 条抽检命中 10；唯一误读属文案歧义，反而促成改写） |
| 已修复真实缺陷 | **11 项**（7 个提交，含 10 个新增回归测试） |
| 成本 | **0**（套餐内） |

**最有价值的结论**：这 11 项**全部逃过了现有全部门禁**——因为它们正是"**门禁自己失效**"类缺陷：
门禁失效时**不产生任何信号**，而内部门禁与作者同源，无法自我发现。这直接催生了 P60（门禁自校验）
与 P61（把外部盲检制度化为运维形式）。

---

## 二、方法：双向交叉盲法（可复用）

**核心设计**：文档层与代码层**各自独立重建**，二者之差即 **doc-vs-reality 缺口**。

| Pass | 投喂 | 禁止投喂 | 目的 |
|---|---|---|---|
| A 文档层 | 根级 README/OPERATIONS + `workflows/` `templates/` `loaders/` `governance/` | 全部代码 | 只看"声称"能否自洽 |
| B1/B2/B3 代码层 | `cli/` · `tools/`+`config/` · `skills/`（各自独立会话） | 全部设计文档 | 只看"实际强制了什么" |
| C 交叉裁决 | A 与 B 结论互投 | 内部结论 | 找矛盾（尤其"文档声称 X / 代码非 X"） |

**盲检卫生（实测必要，缺一即失效）**：

1. **身份脱敏**——包内不得含仓库远端地址/机器用户名（否则外部模型可联网检索到该仓库；
   本次 A 包中确实发现 `github.com:Syske/ai-system`，已替换为占位符）。
2. **排除内部产物**——`reports/` `logs/` `metrics/` `workspaces/` `archived/`、二进制文件
   （内部结论会锚定评审）。
3. **运行隔离**——空目录 + `pi -nt -nc -ne -ns -np --no-session`（禁工具/禁上下文注入/禁扩展技能模板）。
4. **模型独立性**——评委不得与本制品**作者模型同族**（本工作区作者模型为 DeepSeek 系）。
5. **单侧发现必须落位核实**——评委可能改写文件路径（见 §四）。
6. **坏形状重跑 + 后台执行**——大包评审偶发 14 秒返回"文本形式工具调用"
   （判据：耗时 < 1 分钟或含 `<tool_call>`）；单包 6–13 分钟，须后台 + 硬超时。

---

## 三、已修复缺陷（11 项 · 本报告核心）

| # | 缺陷 | 证据（已核实） | 提交 |
|---|---|---|---|
| V1 | **5 个测试方法静默不执行**——定义在模块级 `if __name__ == "__main__":` 块内 → 永不定义、永不收集 | 声明 336 / 收集 **331**；两文件 3→4、16→20 | `5da9f1c` |
| V3 | `repo-lint` 工作流关键词豁免正则 `)\\b` 在 raw 串中为字面反斜杠 → **豁免永不匹配** | 修复后 `Purpose:`/`Workflow`/`Runtime` 命中、`# Purpose` 不命中 | `e30113e` |
| V5 | 危险命令守卫外层 `\b` 使 `rm -rf /` 分支不可达 → **最危险模式漏检** | 修复前 3/3 漏检 → 修复后 **12/12** 用例正确 | `e30113e` |
| V4 | `quick-check` 以 cwd 为仓库根 → **虚假健康结果** | 从 `/tmp` 运行读到本仓真实数字 | `e30113e` |
| V8 | `keys.py` termios 解包索引错位（**交叉评委独家发现**） | 位运算实测：`ECHO`/`IEXTEN`/`ISIG` 未关、input flags 从未清、ispeed 槽被改写 | `f8c984a` |
| V2 | `change_resume.py` 重复 `suggest_change_id`（早期为死代码） | 裁定 P37 带默认参者为权威；实测无参/带参均正常 | `7fb5c50` |
| V6 | `open-cli/SKILL.md` 引用 `./references/CLI-ONESHOT.md`、`CLI-EXPLORER.md`——上游文档**从未入库** | 目录实测只有 SKILL.md；git 历史全仓无该文件记录 | `2adcf4a`（P60 实施中连带修复：加 `./` 规则后必然报 broken） |
| T4-1 | `quick-check` 白名单无 `[BLOCKER]` → **存在 blocker 仍可能 verdict OK** | 修复为正则取括号内词（兼容 `[WARNING ]` 填充形态） | `1eafe15` |
| T4-2 | `checkstyle-gate` rename 守卫 `not p.endswith(" -> ")` **恒真** → 整串被当路径 | 新增 rename 测试用例 | `1eafe15` |
| T4-3 | `checks/workflow.py` 缺键 **fail-open**（`ROOT / ""` == ROOT 恒存在） | 新增 4 例注册表测试 | `1eafe15` |
| T4-4 | `idea-mcp.py` 只查 `isError`，契约实为 `isSuccess` → **编译失败静默 exit 0** | 依 `SKILL.md:105` 契约补判 | `c5cc848` |
| — | **文档层 5 项**：提交约定冲突（`T-<id>` vs 禁止编号）· `repo-lint` 入口文案歧义 · `workspaces/<change-id>` 占位符 · `.aic-workspace.yaml` vs `workspace.yaml` · 模板混入公司专有内容 | 两模型共同命中 3 项；均经原文核实 | `87b673a` |

**门禁结果**：单测 **331 → 346 OK**（+5 静默测试恢复 +10 新增回归）；`check.py` PASS；
`repo-lint` 28 WARN 无新增；`path-audit` 0 broken；`check-contract` exit 0；`quick-check` OK。
（`format-check` 报 FAIL=2 **经 worktree 基线比对证实与本批无关**，为既有问题。）

---

## 四、跨模型情报（操作价值）

| 评委 | 表现 | 采信含义 |
|---|---|---|
| `qwen3.8-max`（主） | 抽检 **6/6 真实**；路径准确 | 可直接引用其证据行 |
| `glm-5.3`（交叉） | **实质对、路径被改写**（称 `cli/services/keys.py`，实为 `cli/utils/menu/keys.py`；`cli/services/clipboard.py` → `cli/utils/clipboard.py`） | **证据列不可直接引用**，必须重新 grep 落位 |

- **交叉价值已实证**：**V8（termios）是交叉评委独家发现**，主评委漏了 → 换族评审确实补盲。
- **共同误读 1 条**（两模型都读错 `repo-lint.md` 的 `Workflow entrypoint | workflow.md`）→
  判定为**文案歧义**并已改写（两模型同错即"文档确有歧义"的证据）。
- 采信规则（已固化）：**两模型共同命中 → 高置信**；**单侧命中 → 逐条落位核实**；**冲突 → 走 Pass C**；
  一切外部结论仍**必须**过 `templates/prompts/external-ai-review.md`（KEEP/REVISE/REJECT/UNVERIFIABLE）。

---

## 五、衍生结论（为什么内部门禁看不见）

本次 11 项里有 5 项是"**门禁自己失效**"，机制上分四类：

1. **无元校验**：门禁检查被检查对象，但无人检查"门禁是否还在工作"（V1 测试收集、T4-1 采集）。
2. **声明式规则写错即静默**：正则/白名单写错不报错，只是"该报的没报"（V3、V5）。
3. **fail-open**：缺键/缺值时退化为"恒通过"而非"报错"（T4-3）。
4. **锚定假设**：路径审计只解析仓库顶层目录引用，技能内相对引用是盲区（open-cli 引用不存在文件未被发现）。

→ 对策见 **P60**（门禁自校验：声明 vs 收集一致性 + 关键规则正反例 + 技能内相对引用）。
→ 制度化见 **P61**（外部盲检纳入运维形式：工作流/命令 + 盲检纪律入库 + 季度节奏）。

---

## 六、存量与未裁决（2026-09-21 复核后更正）

> **更正**：本节初版只登记了「135 WARN / 48 INFO 未逐条裁决」，**漏记了 42 条 BLOCKER/ERROR 级遗留**
> （其中含 16 条已修/已由提案覆盖，26 条为真实待处置）。下表为复核后的完整账目。

### 6.1 全部 BLOCKER/ERROR（58 条）的处置账目

| 状态 | 条数 | 内容 |
|---|---|---|
| 已修复（本会话） | 16 | 嵌套测试方法（V1）· 重复 `suggest_change_id`（V2）· repo-lint 豁免正则（V3）· quick-check cwd（V4）· 危险命令守卫（V5）· open-cli 悬空引用（V6）· termios 索引（V8）· quick-check `[BLOCKER]` 采集 / checkstyle rename / `checks/workflow` fail-open（T4）· idea-mcp `isSuccess`（T4）· 文档层 5 项（提交约定消歧 / repo-lint Files 表 / `workspaces/<project_id>` / `workspace.yaml` / 模板去具体化） |
| 已由提案覆盖 | 4 类 | 提交 `T-<id>` 系统性 → **P62** · 分支命名两形态 → **P63** · spec 前置/ prepare 产物 → **P64** · 验证标记 → **P46** |
| 已修复（T5 批次） | 5 | 见 6.2（门禁契约静态校验 · prompt 骨架定位 · pull.js 命令注入 · save_file 路径穿越） |
| 待处置（未核实） | 33 | 见 6.3 / 6.4 |

### 6.2 待处置且已核实为真 → **已于 T5 批次修复**（`25cb3b6`，+11 回归测试）

| # | 缺陷 | 证据 | 后果 |
|---|---|---|---|
| 1 | `tools/checks/bugfix_modes.py:229` 门禁**执行** provider 的 `submit()` probe | `probe = getattr(mod, CONTRACT_METHOD)("__contract_probe__")` | `check.py` 期间运行第三方 provider 代码 → 非 probe-safe 者产生外部副作用 |
| 2 | `tools/checks/bugfix_modes.py:230` **fail-open**：probe 返回 `None` 即通过 | `if probe is None:` → 通过 | 永远返回 `None` 的 provider 也能过契约门禁（**P60 同族**） |
| 3 | `cli/services/prompt_builder.py:614` `lines.index(line)` 取**首次出现**位置 | `for nxt in lines[lines.index(line) + 1:]` | 同一行文本在模板中重复时，骨架化拼接错位 → prompt 与 Phase 不对应 |
| 4 | `skills/skill-sync/scripts/pull.js:81` shell 字符串内插 | ``execSync(`unzip -o "${tempZip}" -d "${targetDir}"`)`` | `targetDir`（argv）含 `"`/`$(…)`/反引号 → 命令注入 |
| 5 | `skills/deepseek-share-to-md/...`: `save_file()` 无 basename 清洗 | `os.path.join(dest_dir, fname)`，`fname` 来自远端 `file_name` | 远端可控文件名 `../` → 路径穿越写出 `attachments/` 之外 |

### 6.3 文档层遗留 —— 已逐条落位核实 → **已于 T6b 批次修复**（§6.3.1，13 项）

状态说明：✅=核实为真（待修）· ⚠️=需人工裁决措辞 · ❌=误读/非缺陷

| ID | 主题 | 结论 | 证据 |
|---|---|---|---|
| D1 | 治理索引版本漂移 | ✅ | `governance/README.md:9`「(v1.3)」↔ `AI_OPERATING_RULES.md:3`「Version: 1.6」 |
| D2 | 实现依据优先级冲突 | ⚠️ | `karpathy-guidelines.md:88`「1. Approved Task Card」↔ `SOURCE_OF_TRUTH.md:18/49`「1. Contract」+「Contract is Supreme」（两条不同轴：**实现顺序** vs **权威层级**，需在措辞上区分） |
| D3 | "单一事实源"双定义 | ⚠️ | `ai-coding-rules.md:26`「Rule 1: Spec is the Single Source of Truth」↔ SOT Contract-first（同 D2：Spec 定义**行为**，权威层级归 SOT） |
| D4 | 归档路径写错 | ✅ | `policies/skill-lifecycle.md:123` 指向 `archive/skills/<name>/`，而该目录**不存在**；实际归档目录为 `archived/`（`DIRECTORY-RESPONSIBILITY.md:25`） |
| D5 | 归档自动化语义冲突 | ⚠️ | `OPERATIONS.md:491`「No automatic archival」↔ `skill-lifecycle.md:142`「Archive … Automated (linter check)」（需裁决"自动"的含义：lint 建议 vs 实际归档） |
| D6 | 已移除命令仍在册 | ✅ | `tools/pack.py` **不存在**（README_MIGRATION 载明 2026-09-10 移除），但 `README.md:21` 与 `OPERATIONS.md:310/328/339` 仍列 `pack` |
| D7 | 主链图含 bootstrap | ✅ | `README.md:34`「bootstrap → prepare → …」与其自身 `:18`「主链拓扑唯一」及 `workflows/README.md:66`「Change lifecycle main chain」分离原则相悖 |
| D8 | 声称的安全门禁无载体 | ✅ | `policies/security-policy.md:36` 称 release 含 secret scan 并指向 `review-standard.md`；后者与 `runtime-release.md` **均无**该项 |
| D9 | 模板含组织专有内容 | ❌→部分保留 | 仅剩 `runtime-hotfix-test-doc.md`（CoolAcademy / 内网域名 / 集群名 / `@VerifyPathGuard` / Redis SET）——**该 runtime 本身即组织专用流程**，判定为有意为之；`tasks-template.md` 已泛化为「配置中心（如 Apollo / Nacos）」 |

### 6.3.1 T6b 批次修复（2026-09-21）—— 13 项全部落地

**范围**：D1–D8（8 项）+ N2/N3/N4/N8/N9（5 项）= **13**；D9（组织专有模板）判定为**有意为之**，
N1/N5/N6/N7 为误读 → 均不修（见 §6.5）。

| ID | 主题 | 修复 |
|---|---|---|
| D1 | 治理索引版本漂移 | `governance/README.md` **不再复制版本号**（改为"版本以文件为准"）→ 结构性消除漂移，而非改数字 |
| D2 | 实现依据优先级冲突 | `karpathy-guidelines.md` 增 **Axis note**：该列表是**实现顺序**，权威层级归 `SOURCE_OF_TRUTH.md`（Contract is Supreme） |
| D3 | "单一事实源"双定义 | `ai-coding-rules.md` Rule 1 限定作用域为 **for behavior**，并指向 SOT 的权威层级 |
| D4 | 归档路径写错 | `skill-lifecycle.md`：`archive/skills/` → **`archived/skills/`**（与 `DIRECTORY-RESPONSIBILITY.md` 一致） |
| D5 | 归档自动化语义冲突 | 两侧统一为：**linter 自动"检测/建议"**，**归档动作本身受治理**（`OPERATIONS.md` + `skill-lifecycle.md` 措辞对齐） |
| D6 | 已移除命令仍在册 | 清除 `pack` 全部残留（`README.md` 命令清单/目录树、`OPERATIONS.md` 命令分组与示例），并把 "packaging" 表述改为 "asset scaffolding" |
| D7 | 主链图含 bootstrap | 主链箭头链去掉 `bootstrap`，改标为**支撑工作流**（与 `workflows/README.md` 拓扑唯一来源一致） |
| D8 | 声称的安全门禁无载体 | `security-policy.md` §Release 改指**实际载体**：`runtime-release.md` 配置分析清单（硬编码 URL/Token/Secret、日志含 PII/敏感）＋ 扩展扫描器 `extensions/archive-ipd-workspace/scripts/scan_sensitive.py`（明示"未接入 release runtime"） |
| N2 | hotfix 提交后缺验证说明 | `runtime-bugfix.md` Phase 6 明示：**该阶段即 bugfix/hotfix 的验证阶段**，主链 `verify` 不再进入（偏差就地记录） |
| N3 | push 步骤缺口 | Phase 6.5 将 push 变为**显式条件步骤**（仅当后续启用阶段需要远端分支时执行 `git push -u origin <branch>`），与 Phase 6.6 的前置条件对齐 |
| N4 | branch parser 路径写错 | `OPERATIONS.md`：`scripts/branch_parser.py` → **`cli/services/branch_parser.py`**（ai-system 侧实现；`extensions/<name>/scripts/` 为提供者约定，保持不变） |
| N8 | review 路由漂移 | `workflows/review.md` 正文 `## Next` 补齐 `bugfix` / `spec` 两条路由 → **frontmatter 与正文集合完全一致**（`[bugfix, develop, spec, verify]`） |
| N9 | Reflection 适用范围列表遗漏 | `REFLECTION_RULES.md` Scope 列表补齐 5 个实际工作流（`proposal`/`code-review`/`change-impact`/`external-review`/`hotfix-test-doc`）—— 前提已核实：**各 runtime 模板均已含 Reflection 阶段** |

**措辞裁决记录（D2/D3/D5 为 ⚠️ 项）**：三者均按"**两轴分离 / 动作归属分离**"处理 ——
不删任一侧表述，而是在各自位置**标明作用域**（实现顺序 vs 权威层级；自动检测 vs 受治理动作），
避免制造新的"单一说法"而与既有门禁/契约冲突。

**验证**：`check.py` PASS · `repo-lint` 0 ERROR · `path-audit` 0 broken · `workflow-command-audit` 0/0 ·
单测 **430 OK**；另以脚本逐项断言修复效果（含 N8 的集合一致性、D6 的全仓残留扫描）。

### 6.4 代码层遗留 —— 已逐条落位核实 → **已于 T6a 批次修复**（`0606d64`，+18 回归测试）

| ID | 主题 | 结论 | 证据 |
|---|---|---|---|
| C1 | `shell=True` + 未引号路径 | ✅ | `cli/main.py:72-75` `subprocess.call(..., shell=True)`；启动命令由检测路径拼成（空格路径失效 / 注入面） |
| C2 | 环境参数未贯穿 | ✅ | `prompt_builder.py:298` `paths(self.root)` 无环境参数，而 `main.py` 接受 `--environment` → 非 local 环境下 `{workspace_root}` 等渲染错误 |
| C3 | 剪贴板硬依赖且无保护 | ✅ | `cli/utils/clipboard.py` 模块级 `import pyperclip` + `copy()` 无 try；`cli/main.py:275` 生成后**无条件**调用 |
| C4 | pre-commit 检查范围过宽 | ✅（潜在） | `tools/pre_commit_gate.py:133` 调 `check-contract.py` 不传 staged 集 → 全仓校验；当前无漂移故无实际影响 |
| C5 | checkstyle 抑制未接线 | ✅（影响大） | `checkstyle.xml` 头部载明用法 `-c checkstyle.xml -p suppressions.xml`，但 `checkstyle-gate.py` 只传 `-c` → **baseline 抑制清单形同虚设** |
| C6 | 三引号状态机不辨同行闭合 | ✅ | `repo-lint.py:379-391`：行内出现三引号即置位 → **单行 docstring** 之后的注释可能整体漏检 |
| C7 | `--env-init` 有副作用 | ✅ | `tools/setup.py:400-429`：docstring 称「不碰 scaffold/链接」，实际 `:427` 调用 `scaffold()` 创建目录 |
| C8 | `--no-frontmatter` 被忽略 | ✅ | `deepseek_share_to_md.py:477` `-o/--dir` 分支硬编码 `lines = ["---", …]`（仅 `:502` 遵守开关） |
| C9 | 生成脚本路径写死 | ✅ | `spec_updater.py:18` `Path(".opencode/skills/contract-maintainer/scripts/generate_contract.py")` → 实际为 `skills/contract-maintainer/…`，判定恒为假 |
| C10 | 静默吞 YAML 错误 | ✅ | `generate_contract.py:48-50` `except yaml.YAMLError: pass` |
| C11 | 字段校验语义错位 | ✅ | `generate_contract.py:159` 取 `切库规则`（**描述串**）与 `spec["_fields"]`（**字段名列表**）做成员判断 |
| C12 | governor 引用缺失脚本 | ❌ | `tools/repo-lint.py` 等三个脚本**均存在**；该包只投喂了 `skills/`，`tools/` 不在包内 → **分域盲区**，非缺陷 |

### 6.4.1 T6a 实施中的**新发现**（超出盲检主张）

| # | 发现 | 说明 |
|---|---|---|
| 1 | **`suppressions.xml` 不是合法 XML** | 注释内含 `-----------` 分隔线；XML 注释中 `--` 非法 → 该文件**无法被任何 XML 解析器读取**。即使 C5 的接线修好也永不生效（比盲检主张更深一层） |
| 2 | 模板文档的用法本身写错 | 头部原写 `-p suppressions.xml`（checkstyle 的 `-p` 是 **properties** 文件），且 `${config_loc}` 在 checkstyle 10.x **已移除** → 两处均已更正，并改为「配置内 SuppressionFilter + 相对仓根 + `optional=true`」 |
| 3 | **C6 修复暴露 68 条被掩盖的违规** | 单行 docstring 曾让其后的注释整段漏检；修正后 repo-lint 的英文注释 WARN 由 12 → 80（总数 28 → 96），**均为真阳性**（`cli/**/*.py` 与 `tools/*.py` 注释应为中文）。属"暴露存量债"，非质量回退 |

### 6.4.2 **漏记更正**：`is_binary()` 中文误判（BLOCKER，两评委均命中）

| 项 | 内容 |
|---|---|
| 盲检主张 | qwen B3 F-01（BLOCKER）+ glm B2/B3：`is_binary()` 用「解码字符数/字节数 < 0.9」判定 → UTF-8 中文每字 3 字节（比值≈0.33）→ **中文文本被判为二进制** |
| 核实 | ✅ **实测为真**：`"这是一段中文内容…".encode("utf-8")` → `is_binary=True`；纯英文 → False；PNG 头 → True |
| 影响 | `inline_file()` 据此决定附件是否内联 → 含中文附件的分享导出把**文本附件当二进制**处理（该技能的主用例恰是中文内容） |
| **此前状态** | **既未修复、也未登记**：报告 §四 仅以"跨模型共同命中"一笔带过，§六 账目未列入 → **属本报告漏记**（2026-09-21 阻塞性自审发现，由用户指出记录缺失） |
| 处置 | ✅ **已修**：改为「NUL 优先 + 不可解码占比（`errors="replace"` 替换字符比，容忍 4096 边界截断）+ 非打印控制字符占比」；8/8 用例正确、+6 常驻回归测试 |

> 记录纪律教训：**门禁全绿 ≠ 无缺陷**——该缺陷在 `skills/` 脚本内，任何门禁都覆盖不到；
> 而"跨模型共同命中"的条目必须逐条进入 §六 账目（修复 / 遗留 二选一），不得只在叙事情报里提及。

### 6.5 误读清单（6 条）——交叉盲法的必要代价

| ID | 盲检主张 | 实际 |
|---|---|---|
| N1 | `OPERATIONS` 与 `SOURCE_OF_TRUTH` 抢"至上" | 不同轴（governance 覆盖**实现**；Contract 为**权威层级**之顶）→ 仅需措辞澄清 |
| N5 | memory 条目缺必备字段（Date） | 实际条目含 `Date:` / `Priority:`，且 `check.py` 的 memory 字段校验**通过** |
| N6 | `MEMORY_GUIDELINES` 违反"禁绝对路径" | 该处 `/home/<user>/...` 是**占位符形式的反例**（说明什么被禁止） |
| N7 | `release.md` frontmatter `next` 与正文不一致 | `deployment` 属 `NEXT_EXTERNAL`（**门禁设计明确允许**的外部跳转） |
| C12 | 治理技能引用缺失脚本 | 脚本存在，属**分域盲区** |
| N2/N3 部分 | — | 属实但属**文档措辞**级（见 6.3/6.4），非代码缺陷 |

### 6.5 其余

| 项 | 状态 |
|---|---|
| 135 WARN / 48 INFO | 未逐条裁决（跨模型共同命中已在本节按主题聚类） |
| `previous_record` 精确 `step-1` | 复核为**非缺陷**（`detect_reflection` 显式接受 `prev=None`；step 由遍历 turns 构造、连续） |
| `format-check` FAIL=2 | **既有问题**（与本次无关，worktree 基线比对同为 FAIL=2）；不在 maintain 门禁集内 |
| 真实 TTY 复测 | V8 修复后建议人工复测交互菜单 |

### 6.6 2026-09-21 冒烟复跑（P61 验证）新增发现

经 P61 新工作流（`tools/blind-bundle.py` + `templates/prompts/external-blind-review.md` Pass A）复跑
doc 层（136k tokens，单判官，形状校验通过），在复现已知项之外新增：

| ID | 主题 | 证据 |
|---|---|---|
| N-1 | 治理权威冲突（另一处） | `OPERATIONS.md`「Governance always …」↔ `SOURCE_OF_TRUTH.md`「Contract is Supreme」 |
| N-2 | hotfix 提交后缺独立 verify | `OPERATIONS.md`（verify → doc）↔ `runtime-bugfix.md`（无提交后 verify 阶段） |
| N-3 | push 步骤缺口 | `runtime-bugfix.md` MR 阶段要求「committed and pushed」↔ commit 阶段「Do NOT push」，push 未定义 |
| N-4 | branch parser 路径写错 | `OPERATIONS.md`「`scripts/branch_parser.py`」↔ 实际 `cli/services/branch_parser.py` |
| N-5 | memory 条目字段缺失 | `MEMORY_GUIDELINES.md` 要求必备字段 ↔ `memory/java/coding-memory.md` 部分条目缺 `Date` 等 |
| N-6 | 质量门禁自相矛盾 | `policies/quality-gates.md`「No absolute paths」↔ `MEMORY_GUIDELINES.md` 示例 `/home/<user>/` |
| N-7 | frontmatter Next ↔ 正文 Next 不一致 | `workflows/release.md`（frontmatter `next: [develop]` ↔ 正文含 `deployment`） |
| N-8 | 同上 | `workflows/review.md`（frontmatter `next: [bugfix, spec]` ↔ 正文 `verify`/`develop`） |
| N-9 | Reflection 适用范围列表遗漏 | `REFLECTION_RULES.md` 称适用所有工作流 ↔ 列表缺 `code-review`/`change-impact` 等 |

> N-7/N-8 属**可机器校验**的契约漂移（frontmatter ↔ 正文），值得纳入门禁候选；
> N-1..N-9 均为单判官命中，按盲检纪律**需逐条落位核实**后方可计为缺陷。

## 七、复现与资产

**持久记录（入库）**

- 本报告（拣选高价值内容：方法 / 盲检卫生 / 11 项修复 / 跨模型情报 / 衍生结论 / 存量）
- 修复本身：7 个提交 + 10 个新增回归测试（见 §三）
- 诊断日志：`ai-system/logs/`（运行期记录，按约定不入库）

**运行期产物（未入库，需制度化持久化）**

- 投喂包（4 包）与提示词三段、包生成器、运行手册均产于 `temp/` → **易失**
- 本次评审的 8 份产出与 241 条索引产于 `outputs/` → **未入库**
- ⇒ **持久化方案属 P61 §5.5/§5.6 提案内容**（生成器提升为 `tools/blind-bundle.py`、提示词入
  `templates/prompts/external-blind-review.md`、运行手册入 `docs/`）

**两点机制提醒（本次实测）**

1. **`outputs/` 引用不受 `path-audit` 审计**（其扫描目录不含 `outputs`）→ 指向该区的路径即使失效
   也不会报 broken，因此**不应在提交态报告里索引它**。
2. **打包卫生自检（每次必做）**：包内 `reports/|logs/|metrics/` 文件头 = 0；远端地址/用户名 = 0；
   隔离开关齐全（`-nt -nc -ne -ns -np --no-session`）。

---

## 八、结论与定位

- **定位**：外部盲检是**补充独立视角**，**不替代**内部门禁与内部评审；其产出与任何外部结论一样是
  **未验证输入**，逐条核实后方可入库（本次 11 项全部转化为内部修复 + 回归测试）。
- **性价比**：零边际成本、45 分钟机器时间，换回 11 项真实缺陷（含 5 项门禁自失效、1 项安全守卫失效）
  → 足以支撑将其**制度化**（P61）。
- **下一步**：P60/P61 评审 → 批准后实施；未裁决的 135 WARN / 48 INFO 分批处理。

---

## 八、结算（241 条全量处置 — 2026-09-21 收尾）

### 8.1 总账

| 严重度 | 条数 | 处置 |
|---|---|---|
| BLOCKER | 4 | ✅ 全部处置（嵌套测试方法 / `runtime-spec` 路径 / 提交标准冲突 / `is_binary` 中文误判）—— 见 §6 |
| ERROR | 54 | ✅ 已逐条落位核实（§6.3/§6.4）：T1–T6b 批次修复 + 4 类由提案覆盖（P62 / P63 / P64 / P46） |
| WARN | 135 | ✅ 本次收尾：主题级裁决（§8.2） |
| INFO | 48 | ✅ 同上 |
| **合计** | **241** | 每行 = 一次评委产出（双评委重复条目分别计数） |

### 8.2 WARN/INFO（183 条）主题裁决

| 判定 | 条数 | 说明 |
|---|---|---|
| 已修（T1–T6b） | 17 | 与本会话已修批次对应（doc 层措辞、门禁接线、技能脚本修复等） |
| 已由提案覆盖 | 2 | P63（分支命名两形态） |
| 误读 / 非缺陷 | 18 | 例：所称缺失的 `tools`、`cool/*`、`memory-capture`、`AGENTS.md` **实际均存在**；`language-gate` 非 zh 恒 PASS、`extensions-lint` 空规则回退、checkstyle 资产缺失 SKIP 等**均为文档化设计** |
| 已知存量债 | 3 | ADR 索引止于 0007（0008/0009 为独立文件）、ADR 命名两式并存 |
| 文档措辞 | 52 | 加载顺序三处互斥、压缩阈值 50/60/80 分歧、`skill.md` 大小写、`python` vs `python3`、索引计数漂移、`quick-check-{date}` vs `maintain-{date}`、`knowledge` 操作数 3/5 等 → 见残债 **R3** |
| 未核实 | 1 | WARN-17：`develop-start.md` 的 `{{spec_workspace}}` 是否需 PromptBuilder 登记（待确认消费方） |
| **真实·待修** | **90 行 / 67 独立根因** | 本轮修 **7**（§8.3）→ 余 **60** 入残债登记（§8.4） |
| **合计** | **183** ✓ | |

### 8.3 本轮修复（T7 批次：7 项，fail-loud / 健壮性；+8 回归测试）

| # | 项 | 修复 | 实证 |
|---|---|---|---|
| 1 | `JdtFormatCheck.java` 语法解析失败**静默跳过** | 计入 `differ` 并打印 `PARSE-FAIL <file>`（"C2 通过"不再掩盖语法错文件） | 重建 wrapper 后实测：未闭合方法体 → `PARSE-FAIL A.java`，`differ=3`（原实现该文件**无声跳过**） |
| 2 | `cli/services/state_store.py` 读写异常静默吞 | 读/写失败 → stderr WARN（状态记忆丢失不再无声） | 2 测试（损坏 YAML / 不可写路径） |
| 3 | `tools/checks/memory.py` 非 UTF-8 使门禁崩溃 | `errors="replace"` | — |
| 4 | `tools/format-check.py` `--check-commit` 异常静默 | → **WARN**（提交约定未校验必须可见） | — |
| 5 | `skills/contract-maintainer/…/generate_contract.py` 缺键裸 `KeyError` | `_require_keys()` 显式报错（含来源与条目内容） | 2 测试 |
| 6 | `tools/checks/menu.py` dry-run monkeypatch 未恢复 | `finally` 恢复（且只恢复**实际存在**的属性） | 1 测试（前后属性一致） |
| 7 | `skills/deepseek-share-to-md` 无 `?` 时追加 `&ty=r` → 畸形 URL | 查询串感知 `("&" if "?" in url else "?")` | 3 测试 |

### 8.4 残债登记（60 项，按优先级；随任务自然消减）

> 说明：本节**自包含**列出全部残债（投喂包与 241 条索引位于未提交的 `outputs/`，故不在此引用）。

**R1 · 安全 / 审计盲区（4）— ✅ 已于 R1 批次修复（2026-09-21，+23 测试）**

| 项 | 修复 | 实证 |
|---|---|---|
| 上传递归打包**无过滤**（`.git`/`node_modules`/`.env`/隐藏文件） | 策略抽为单一来源 `skills/skill-sync/scripts/sync-policy.js`：排除集（目录含隐藏目录、`.env`/`.DS_Store` 等）+ **疑似凭据/私钥命中即拒传并 `exit 3`**（fail loud，不静默剔除） | 10 项 node 驱动测试（排除集正反例、敏感文件 7 命中 4 不误报） |
| 无协议时回退 **`http://`** 且 key 明文 | `resolveHostUrl()`：无协议**默认 https**；显式 `http://` **默认拒绝**，仅 `AGENT_INSIGHT_ALLOW_INSECURE=1` 放行；pull/push 三处调用点统一 | 三态实测：`https://`→原样、`host`→`https://host`、`http://`→`InsecureHostError`（放行时通过） |
| repo-lint **跳过容器目录** → 嵌套技能永不 lint；三工具口径分裂 | 新增**单一来源** `tools/skill_index.py`（技能 ＝ 含入口的目录，**递归展开容器目录**；容器本身不是技能），`repo-lint`/`repo-metrics`/`dependency-graph` 一律取此口径 | **口径 32 / 33 / 33 → 39 / 39 / 39**（容器 `architecture/` 不再计数，其下 **7 个技能入列**） |
| `skills/` 下脚本**零契约测试** | 新增 `cli/tests/test_skills_contracts.py`（agentdebug 校验契约 11 项 + 枚举口径 4 项）、`cli/tests/test_skill_sync_policy.py`（node 驱动 10 项）；`generate_contract` 缺键契约见 `test_t7_fail_loud.py` | +23 测试 |

**R1 修复顺带暴露并修掉的存量问题**：口径统一后，`skills/architecture/` 下 **7 个技能首次进入 lint 视野**，
其中 **7 个 description 全部 < 100 字符 → 7 个 ERROR**（此前完全不可见，属"修盲区即暴露存量"）→
已按各自职责重写为 202–226 字符的描述；repo-lint 由 `39 skills / 7 ERROR` 恢复 `39 skills / 0 ERROR`。

**R2 · 静默失败 / 可靠性（24）**（残债合计由 60 → **56**：R1 四项已修）

| 项 | 位置 |
|---|---|
| `previous_record` 按精确 `step-1` 匹配非连续序号 → 静默 `None` | `skills/agent-debug-diagnosis/scripts/agentdebug_static.py:389-394` |
| triage 命中首个 ≥2 类型即返回（未取首要） | 同上 `:409-427` |
| `redundant_call` 全局计数 vs 文案"五步窗口" | 同上 `:229-243` |
| `validate` 空 issues 短路 issueRefs 校验 | `agentdebug_validate.py:172-176` |
| `criticalModule="unknown"` 既判非法又特判跳过 | 同上 `:208-224` |
| `classify_action_error` 的 `or/and` 未加括号 | `agentdebug_static.py:270-278` |
| 同日同描述 `mkdir(exist_ok)` **覆写** manifest/report（文档承诺追加 `-N`） | `cli/services/chain.py:91-108`、`skill_launcher.py:232-262` |
| scan 目录名 `scan-YYYYMMDD-HHMMSS` vs 文档 `{yyMMdd}-{descriptor}` | `cli/services/command_hooks.py:197-202` |
| `last_active` 取 dict 末键依赖保序 | `cli/services/wizard/__init__.py:104-107` |
| i18n 硬编码 `zh.yaml` vs MenuConfig 按 locale 加载 | `cli/utils/menu/base.py:25-38` |
| 无 git 根时**上行至文件系统根**扫描 | `cli/services/skill_scan.py:294-309` |
| `FRONTMATTER_NAME` 整文件 search（body 内 `name:` 误取） | 同上 `:31,113-117` |
| `_SECTION_8` 前瞻 `(?=^## 9\.)` → 无 §9 时整段失配 | `cli/services/change_resume.py:17-21` |
| `_parse_next` 取首个命中 token 而非实际后继 | `cli/services/wizard/selection.py:298-323` |
| `_norm_field_name` 与 `menu_config._base` 归一化不一致 | `workflow_reader.py:93-102` / `menu_config.py:127-131` |
| `chain_launcher` 单一 project 注入复数 `Projects` 且绕过校验 | `cli/services/chain_launcher.py:151-158` |
| `change_resume` 未过滤 `../` 拼路径 | `change_resume.py:31-41` |
| 退格哨兵 `"<"` 吞合法输入 | `cli/utils/menu/text.py:146,224` |
| `-c safe.directory=*` 每仓禁用所有权检查 | `cli/services/providers.py:151-162` |
| `_linux_path` 双实现 | `environment.py:157-171` / `providers.py:26-37` |
| `format-check` Lombok 状态机首个 `}` 即重置 | `tools/format-check.py:502-515` |
| checkstyle 增量取整仓 changed 未按 `src_dir` 过滤 | `tools/checkstyle/checkstyle-gate.py:96-100` |
| 交互 `input()` 无 EOF 保护（非 TTY 崩） | `tools/format-jdt-gate.py:270-274,357-372` |
| （另）`urlretrieve` 无校验和 / `context-audit` 窗口硬编码 / `setup.py` `args[i+1]` IndexError / `extensions-init` push 失败仍 return 0 | 见各文件 |

**R3 · 文档措辞（52）** —（加载顺序互斥 / 阈值 50·60·80 / `skill.md` 大小写 / `python` vs `python3` / 索引计数漂移 / `explore` 双份 / `skills/README` 计数 / Token Efficiency ×3 / Report-Write Guard 双源 / 四反引号围栏 …）建议下一维护批次**批量顺手修**。

**R4 · 工具一致性与重构（低优先，随任务消减）** —（`checks/misc.py` 系列：cli/tests 缺失仅 WARN、`tools_readme` 只扫顶层、`ast.walk` 含嵌套 return、timeout 未捕 `TimeoutExpired`；`checks/workflow.py` 导入无兜底；`bugfix_modes` 硬编码阶段集；`checks/menu.py` 不校验 hidden_*；`repo-metrics` 无 schema 校验；`workflow-command-audit` 强度不一致；`generate_contract` 服务匹配混用子串/精确、`deduplicate` 静默保留首个、YAML 值未引号；`pull.js`/`push.js` 双份 `loadConfiguration`、失败无退出码、网络错与 not-found 不分；`index-project` 硬编码 Windows venv；`k8s-logs` 过时快照 + 通道不一致；`k8s_helper` `.status.phase` 掩盖 CrashLoopBackOff；`idea-mcp` SSE 断线吞错；`spec_updater` 硬编码 `DEFAULT_CHANGE`；`maintain-report` closed 大小写敏感；`proposal-audit` `startswith("P")` 含 PROPOSALS.md；`quick-check` 未用 `_parse_summary`；`dependency-graph` 死分支）。
