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
| **待处置（已核实为真）** | 5 | 见 6.2 |
| **待处置（未核实）** | 33 | 见 6.3 / 6.4 |

### 6.2 待处置且**已核实为真**（建议作 T5 批次）

| # | 缺陷 | 证据 | 后果 |
|---|---|---|---|
| 1 | `tools/checks/bugfix_modes.py:229` 门禁**执行** provider 的 `submit()` probe | `probe = getattr(mod, CONTRACT_METHOD)("__contract_probe__")` | `check.py` 期间运行第三方 provider 代码 → 非 probe-safe 者产生外部副作用 |
| 2 | `tools/checks/bugfix_modes.py:230` **fail-open**：probe 返回 `None` 即通过 | `if probe is None:` → 通过 | 永远返回 `None` 的 provider 也能过契约门禁（**P60 同族**） |
| 3 | `cli/services/prompt_builder.py:614` `lines.index(line)` 取**首次出现**位置 | `for nxt in lines[lines.index(line) + 1:]` | 同一行文本在模板中重复时，骨架化拼接错位 → prompt 与 Phase 不对应 |
| 4 | `skills/skill-sync/scripts/pull.js:81` shell 字符串内插 | ``execSync(`unzip -o "${tempZip}" -d "${targetDir}"`)`` | `targetDir`（argv）含 `"`/`$(…)`/反引号 → 命令注入 |
| 5 | `skills/deepseek-share-to-md/...`: `save_file()` 无 basename 清洗 | `os.path.join(dest_dir, fname)`，`fname` 来自远端 `file_name` | 远端可控文件名 `../` → 路径穿越写出 `attachments/` 之外 |

### 6.3 待处置（未核实）— 文档层（**两模型共同命中**，信号强）

| 主题 | 证据 |
|---|---|
| 治理索引版本漂移 | `governance/README.md` 称核心规则 v1.3 ↔ `AI_OPERATING_RULES.md` 自称 `Version: 1.6` |
| 优先级冲突 | `karpathy-guidelines.md`「1. Approved Task Card」↔ `SOURCE_OF_TRUTH.md`「1. Contract」（两模型均命中） |
| "单一事实源"双定义 | `ai-coding-rules.md`「Spec is the Single …」↔ SOT Contract-first |
| 归档路径冲突 | `policies/skill-lifecycle.md` `archive/skills/` ↔ `DIRECTORY-RESPONSIBILITY.md` `archived/` |
| 归档语义冲突 | `OPERATIONS.md`「No automatic archival」↔ `skill-lifecycle.md` 将 Archive 标为 `Automated` |
| 已移除命令仍在册 | `README.md` / `OPERATIONS §1.10.2` 仍列 `pack` ↔ `README_MIGRATION.md` 声明已移除 |
| 主链图含 bootstrap | `README.md` 图示 `bootstrap → prepare` ↔ `workflows/README.md`（唯一来源）冷启动与主链分离 |
| 声称的安全门禁无载体 | `policies/security-policy.md` 称 release 含 secret scan 并指向 `review-standard.md`，而后者无该条目 |
| 模板含组织专有内容 | `runtime-hotfix-test-doc.md`（Confluence space key / 内网域名 / 集群名 / `@VerifyPathGuard` / Redis SET）；`tasks-template.md`（Apollo，已泛化）↔ 判定：hotfix 属组织固有，其余待逐一确认 |

### 6.4 待处置（未核实）— 代码层（单侧命中为主）

- `cli`: `main.py` `subprocess.call(..., shell=True)` + 未引号路径（空格路径失效 / 注入面）；`PromptBuilder._resolve_root_placeholders` 未接环境参数（与 `main.py::_config_files` 硬编码 `local.yaml` 互相佐证）；`cli/utils/clipboard.py` 模块级硬依赖 `pyperclip` + 事后无条件 `copy()`
- `tools`: `pre_commit_gate` 调 `check-contract.py` 不带 staged 集（无关漂移也阻断）；`checkstyle-gate` 未接 `suppressions.xml`（注释声称的抑制未生效）；`repo-lint` 三引号状态机不辨同行闭合；`setup.py --env-init` 实际会建目录/软链
- `skills`: `deepseek_share_to_md` 的 `--no-frontmatter` 在文件导出分支被忽略；`spec_updater.py` 写死 `.opencode/skills/…` 路径；`generate_contract.py` 静默吞 `YAMLError`；`validate_fields` 用描述串与字段名做成员判断
- 可能误读（待确认）：`repository-governor` 引用 `tools/*.py` —— 该包只投喂了 `skills/`，`tools/` 不在包内，属**分域盲区**而非缺陷

### 6.5 其余

| 项 | 状态 |
|---|---|
| 135 WARN / 48 INFO | 未逐条裁决（跨模型共同命中已在本节按主题聚类） |
| `previous_record` 精确 `step-1` | 复核为**非缺陷**（`detect_reflection` 显式接受 `prev=None`；step 由遍历 turns 构造、连续） |
| `format-check` FAIL=2 | **既有问题**（与本次无关，worktree 基线比对同为 FAIL=2）；不在 maintain 门禁集内 |
| 真实 TTY 复测 | V8 修复后建议人工复测交互菜单 |

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