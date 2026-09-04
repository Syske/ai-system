# 系统巡检报告 — 2026-09-03（on-demand）

- 类型: 系统巡检（MAINTENANCE，按需）
- 模式: on-demand
- 范围: 评估系统是否需要安装 pi-lens 扩展（pi 包市场的代码质量扩展）
- 日期: 2026-09-03

---

## 一、工具校验结果（自动生成，AI 核对补充说明）

| quick-check | verdict **ISSUES**（findings 1：extensions 根目录缺失，归因见发现-2） |
| lint | Skills: 30 | Files: 30 | BLOCKERS: 0 | ERRORS: 0 | WARNINGS: 25（与 09-01 基线持平，无回归） |
| path | OK: no broken path dependencies（688 引用级校验通过） |
| metrics | 快照已落盘 metrics/maintain-2026-09-03.json |
| extensions | Summary: 1 errors（extensions 仓本机缺失，extensions-lint 无法执行，降级说明见发现-2） |

### 指标对比（自动生成，需 AI 核对变化原因）

本机 metrics 历史快照因 WSL 工作区迁移仅存当日文件，上一快照不可比；以 09-01
维护记录（last_findings：lint 0/0/25、path OK）为文字基线——本期数值与其一致，
**无回归**。迁移后指标基线自本快照重置。

| 指标 | 上期 | 本期 | 变化 |
|---|---|---|---|
| Skills | 30（09-01 记录） | 30 | = |
| Workflows | ? | 15 | 基线重置 |
| RFC | ? | 14 | 基线重置 |
| Governance | ? | 59 | 基线重置 |
| Templates | ? | 22 | 基线重置 |

---

## 二、巡检发现（AI 填写，按严重度分级）

<!-- 高 / 中 / 低 / 信息 -->

### 高

无。

### 中

1. **quick-check ERROR：extensions 根目录缺失（`D:\workspace\extensions`）**。
   归因：WSL 工作区迁移残留——本机 workspaces/ 仅剩 `.aic-state.yaml`，projects
   junction 与 extensions 仓均未落位（机器级观察）。影响：extensions 域巡检
   （extensions-lint / 逐扩展健康检查）本机降级不可执行；quick-check verdict
   因此为 ISSUES。处置：**仅报告不自行修复**（属机器环境操作，需用户授权后
   恢复 extensions 仓），详见修复清单-2。
2. **pi-lens 扩展安装评估：结论为「现在不安装」**。完整分析见第六节专项评估。
   核心理由：与现有门禁链能力重叠、google-java-format 与 IDEA profile/spotless
   双格式权威冲突、自动改写文件绕过变更控制、无真实项目价值证据（演进原则）。

### 低

3. **P47 提案未登记 reports/README.md 索引**（proposal-audit WARN，proposal-policy
   §6）。属单点索引遗漏，确认后可执行 `python3 tools/proposal-audit.py
   --refresh-index` 修复。

### 信息

4. 本机 maintain-delta 判定 **FIRST_RUN**（迁移后首次快照）：按命令规约应触发全量
   审计，但本次为用户指定范围的按需评估，全量审计顺延至下一维护窗口（09-07 weekly
   或提前 on-demand）。
5. 运行日志覆盖核查通过：git 无未提交的 tracked 改动（仅本报告新建文件），无未归因修改。
6. 提案盘面：0 gate error / 1 WARN；开放提案 6（P28/P36/P37/P41/P42/P46），
   open action items 4——与 09-01 记录一致，无漂移。

---

## 三、一致性抽查结论（AI 填写，逐项通过/失败）

本次为窄范围按需巡检（Scope=pi-lens 评估），Step 3 仅执行常开轻量项：

| 检查项 | 结果 |
|---|---|
| 状态卫生（.aic-state.yaml 引用存在性） | ✅ 通过（文件仅含 last_target=maintain + projectless_usage，无失效引用） |
| 运行日志覆盖（未提交改动 vs logs/） | ✅ 通过（tracked 零改动） |
| 提案遗留（proposal-audit + 索引） | ⚠️ 1 WARN（P47 索引遗漏，见发现-3）；6 开放提案与 09-01 一致 |
| 其余一致性项（workflows 八段/注册表瘦身/链接健康/文档-现实对照） | ➖ 本范围未执行，顺延至 09-07 weekly 全量巡检 |
---

## 四、修复动作与建议清单（AI 填写）

| # | 类型 | 内容 | 状态 |
|---|---|---|---|
| 1 | 评估结论 | **不安装 pi-lens**（本机 pi 已装包仅 pi-powerline、pi-web-access，维持现状）；重估触发条件见第六节 | ✅ 用户已确认（2026-09-03） |
| 2 | 机器环境 | 恢复本机 extensions 仓与 projects junction（WSL 迁移收尾），恢复后重跑 quick-check 归零 ERROR | ❌ 本次不授权；结论：`aic extensions-init` 已具备脚手架能力（幂等，产物满足 extensions-lint 要求），待用户择机执行；目录初始化并入 env-init 的整合方向已有开放提案 P36，季度回顾时决策是否提前实施 |
| 3 | 小修 | P47 登记 reports/README.md 索引（`proposal-audit.py --refresh-index`） | ✅ 已执行（refresh-index 更新 PROPOSALS.md 后手工补登 README：P47 行 + 本报告行） |
| 4 | 计划 | 09-07 weekly 窗口补 FIRST_RUN 全量审计（含 extensions 域，若仓库已恢复） | 已登记 maintenance.yaml |

本次未执行任何就地修复（无单点 typo/死链类小修落在授权范围内）。

---

## 五、quick-check 趋势（自动生成）

| 日期 | verdict | findings |
|---|---|---|
| 2026-09-03 | ISSUES | 1 |

迁移后本机仅 1 个快照，趋势基线重置；ERROR 内容为机器级（extensions 仓缺失），
非资产质量回归。

## 六、提案状态（自动生成）

- proposal-audit: 0 gate error / 1 warn / 6 开放提案 / 4 open action items
  - WARN P47-WORKFLOW-PRECONDITIONS-OUTPUTS.md: not registered in reports/README.md index (proposal-policy §6)
  - 开放: P28-CHANGE-ID-GENERATION.md
  - 开放: P36-SETUP-ENV-INIT-SCAFFOLD.md
  - 开放: P37-REQUIRED-INPUTS-TRIAGE.md
  - 开放: P41-TR5-SECTION1-SEMANTICS.md
  - 开放: P42-TR5-TEMPLATE-SKELETON.md
  - 开放: P46-TR5-DEBT-VALIDATION-MARKER.md
  - P26-MAIN-CHAIN-BRANCH-RULE.md:52 分支扩展 provider（extensions/ 提供者，按需；契约已预留）
  - P26-MAIN-CHAIN-BRANCH-RULE.md:53 CI 增强（git 分支保护，后续）
  - P28-CHANGE-ID-GENERATION.md:42 
  - P28-CHANGE-ID-GENERATION.md:44 D：AI 可选生成（skill 层落点）——触发条件未到

---

## 七、专项评估：是否安装 pi-lens 扩展（本次 on-demand 范围）

**评估对象**：pi 包 `pi-lens`（apmantza，v4.1.3，MIT，约 60K 下载/月，23.3 MB，
6 依赖 + 3 peers）——编辑期代码质量扩展：write/edit 后自动跑
secrets/format/autofix/lint/tests 管道；LSP 诊断（36+ 语言；Java=JDT LS+javac，
Python=pyright/ruff）；findings 注入 + lens_diagnostics 工具；read-guard（未读禁改）
与 git-guard（findings 未清禁提交）。本机现状：已装包仅 pi-powerline、pi-web-access。

**结论：现在不安装**。依据：演进原则（无真实项目需求不引入能力）+ Value-Burden
Check（价值证据缺失且负担显著）。

### 负面影响/冲突清单（按影响排序）

| # | 影响 | 级别 | 说明 |
|---|---|---|---|
| 1 | 格式权威冲突 | 高 | Java 智能默认 formatter=google-java-format 且 post-write 自动执行；与 IDEA profile/spotless/JDT 门禁（C2）三方打架；存量 1010/1690 格式差会被放大为「AI 改一处、google 重排一片」 |
| 2 | 自主改写绕过变更控制 | 高 | 未确认的 reformat/autofix 直接落盘，违反 Never modify unrelated code / 确认后修复 / Deviations 记录纪律，commit 归因被污染 |
| 3 | guard 干预工作流 | 中高 | git-guard 按它的 findings 扣 commit/push：存量债（34 FAIL/149 WARN 格式债、53 处中文 log）会被扫出并阻塞提交；read-guard 可能误伤生成文件/脚手架 |
| 4 | 上下文与注意力成本 | 中 | 每轮 findings 注入 + nudge；高频文件操作 run 的 token 消耗上升；与自身门禁形成双诊断信号（相悖 CONTEXT_LOADING / ATTENTION_MANAGEMENT） |
| 5 | 体积/供应链/更新面 | 中 | 23.3 MB + @ast-grep/cli 原生二进制（npm v12 需 approve-scripts）+ tree-sitter WASM；第三方可执行包，更新静默改变会话行为 |
| 6 | 性能开销 | 中低 | JDT LS 每次 JVM 启动 + 索引；WSL 迁移收尾期开销放大；部分版本 bash 调用后也触发检查 |
| 7 | 双门禁裁决分歧 + 处置维护 | 中低 | 规则集不同 → 结论不一致；需维护 per-project suppress/defer 清单 |
| 8 | 跨机配置漂移 | 低 | pi 包机器本地、不入 ai-system 资产，Windows/WSL 两侧易漂移 |

### 能力对价（它确实带来的东西）

编辑期即时 LSP/lint 反馈（门禁期→编辑期左移）、影响级联诊断、symbol_search /
read_symbol 导航。当前栈（Java 主 + Python 工具 + Markdown 文档）已有 Stage-6
门禁链（format-check / jdt-gate / checkstyle / spotless / repo-lint /
language-gate）兑底，「反馈时点差距」尚无真实案例证明是当前痛点。

### 重估触发条件（满足其一再议）

1. 连续出现「agent 编辑引入错误、直到门禁期才暴露」的真实案例，且语言落在
   pi-lens 强项（Python/TS）；
2. 新开 Python/TS 为主的项目；
3. jdt-format-gate 的 IDEA profile 校准完成、格式债清零后，可做「关闭
   formatter/autofix 的纯诊断模式」小仓试点。

### 若仍决定安装的风险缓解底线

项目级安装（不进全局 packages）、项目配置显式关 formatter/autofix（显式配置
优先于智能默认）、opt-in 安全扫描保持关闭、先小仓试点并按 Value-Burden Check
记录价值证据；ai-system 资产不引用该包路径。

---

### 2026-09-04 复核（pi-lens 评估结论时效性判定）

**判定：事实面无需修正，时效面追加状态（触发条件③已达成）。**

1. **事实核实（官方文档，v4.1.3 language-coverage/features 等）**：
   - Java：LSP=JDT LS，dispatch=runners lsp+javac，formatter=google-java-format；
     Java **非 config-first**（未标 config-first），smart default 生效 → post-write
     自动格式化**事实成立**（与评估冲突①一致，无需修正）。
   - 32 formatters 自动检测，显式项目配置优先；`lens_diagnostics`/guard 机制同评估。
2. **触发条件核查**（评估自设重估条件，满足其一再议）：
   - 条件①（真实案例语言在 Python/TS）：未满足（本仓 Java 主，无案例记录）。
   - 条件②（新开 Python/TS 项目）：未满足。
   - **条件③（IDEA profile 校准完成 + 格式债清零 → 纯诊断模式小仓试点）：已达成**——
     C2 profile 已校准定稿（同事版 375 条，1010→721，c7eef0b）+ platform-api 试点
     基线（718 文件 apply，token 0 不一致）+ checkstyle error=0（全仓）。
3. **结论更新**：维持「现在不安装」；按条件③进入**纯诊断模式小仓试点评估窗口**——
   试点最小清单：项目级安装（不进全局）、显式关 formatter/autofix（纯诊断）、
   Java 侧只取 JDT LS/javac 编辑期诊断、2 周观察按 Value-Burden Check 记录价值证据。
   试点与否由业务侧拍板；ai-system 资产不引用该包路径。

**实测复核（2026-09-04 补充，用户确认）**：pi-lens 曾实际安装并试用；用户基于
09-03 评估结论（不安装）已卸载。卸载验证（09-04）：npm 全局、项目级 node_modules、
~/.pi 均无残留——**文件层卸载干净**。⚠️ 运行时层：pi 包在**会话启动时加载**——
卸载后**既有会话仍持有 pi-lens**（post-write 管道/findings 注入仍生效），
**reload 后才真正失效**（用户确认 09-04）→ 既有会话是最后一个可观察窗口。
结论：「不安装」经**实际安装→试用→按评估卸载**验证成立
（评估的 Value-Burden 判定经受住实测）；触发条件③试点窗口因用户实际卸载行为**悬置**
（如需重开，由业务侧提出并附实测观察）。

**受控实验结论（2026-09-04，用户执行，~/ws/temp/lens-probe/LENS-EXPERIMENT.md）**：
- **注入面已失效 / 工具面残留**：写 .java/.md 零注入（卸载前必有 🟡 markdown 警告消失）；
  lens_diagnostics 仍可调（opengrep 171s / jscpd 7s 实跑）——卸载后注入管道已停，
  工具面残留存活（reload 前）。
- **核心对照**（探针 4 类问题：未使用 import / 方法缺修饰词 / @Value 双默认 / 超长行）：
  pi-lens **0/4**（零注入+主动扫描零检出）；门禁链 **4/4**（UnusedImports ERROR、
  LineLength WARN、@Value 双默认 WARN、方法修饰词 WARN）——**修正**：实验初稿称
  「缺修饰词为共同盲区」系探针行尾注释干扰匹配的假象，无注释形态已验证命中（本日第 7 项
  正则亦已容错行尾注释）。
- **负担**：pi-lens 两次扫描约 8 分钟空转（LSP 300s 超时×2 + opengrep 171s）vs 门禁链秒级。
- **判定**：H1/H2 本场景不成立（编辑期前置无实测增量，负担为正）；诚实边界=业务仓内
  （有构建上下文）的增量未覆盖（历史 lens_diagnostics 曾出真实 advisory——MD036/Map 组装，
  与门禁重叠度未量化）。净结论：无构建上下文是 pi-lens 结构性盲区；「不安装」结论
  经实测对照进一步强化。实验纪律合规（临时目录/未触碰业务仓/未 autofix）。
