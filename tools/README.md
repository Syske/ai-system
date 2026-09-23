# Tools

Automated governance tooling for the AI repository.

| Tool | Purpose |
|------|---------|
| `check.py` | System integrity + runnability gate (9 checks; run after every change) |
| `pre_commit_gate.py` | Pre-commit gate Python 主体（.githooks/pre-commit 薄 shim exec 之）——staged 命中 templates/runtime/ + workflows/ 时跑语言检查（repo-lint --files）+ 契约一致性（check-contract）；跨平台（shim 探测 python3/python，Windows Git-Bash 可跑）；可单测（cli/tests/test_pre_commit_gate.py）；exit 0=过 1=拦 |
| `check-contract.py` | Pre-commit contract-consistency subset（workflow ↔ runtime outputs / frontmatter outputs.base）——薄入口，供 .githooks/pre-commit 在 staged 命中 workflows/ 或 templates/runtime/ 时快速拦截漂移（不含 unittest / repo-lint / path-audit）；exit 0=一致 1=漂移 |
| `repo-lint.py` | Structural linter — run before every change. Language check (`check_language`) enforces `LANGUAGE_CONVENTION.md`: (1) `cli/commands/aic-*.md` Steps/Guardrails must be English; (2) `cli/**/*.py` + `tools/*.py` comments must be Chinese; (3) `governance/*.md` (excl. archive/, standards/, README, policies) must be English |
| `comment-lint.py` | 注释质量检查（P69 MVP）：只针对**本次改动新增的 Java 注释**判「确定可删 / 需裁定 / 保留」，策略（六级分类 + 稳定规则 id `CQ-*` + 判定顺序 + 安全原则「宁可漏删不可误删」）见 `governance/standards/common/documentation.md` → Comment Content。**当前阶段 S2：注释候选提取**（字段 file/行列/字符偏移/文本/kind/缩进/前后代码/所属方法/所属类；JavaDoc 标记 skip）。双通道输出必须一致：`tree-sitter-language-pack` 提供语法（**可选加速依赖**，缺失时探测式降级到标准库词法状态机）。**与既有检查分工不重复**：单行块 `/** xxx */` 与注释内任务编号属 `format-check.py`，注释语言属 `repo-lint.py`。用法：`python3 tools/comment-lint.py <path> [--parser auto\|tree-sitter\|stdlib] [--dump-candidates] [--json]`；exit 0=提取成功 2=用法/IO/环境错误（1/2 判定语义在 S4/S5 接入）。单测 `cli/tests/test_comment_lint.py` |
| `skill_index.py` | **技能枚举单一来源**（供 `repo-lint` / `repo-metrics` / `dependency-graph` 共用）——技能 ＝ 含 `SKILL.md`（或 `skill.md`）的目录，**递归展开容器目录**；容器目录（自身无入口、仅承载子技能，如 `skills/architecture/`）**不计为技能**。R1 修复（2026-09-21）：此前三工具三口径（repo-lint 整棵跳过 → 其下 7 个技能永不 lint；repo-metrics/dependency-graph 计顶层目录 → 容器被多计为 1 个）|
| `workflow-command-audit.py` | Workflow & command health auditor — file length (RFC-0003 / thin-command gates), required sections, Next targets, dangling command references, menu.yaml registration |
| `repo-metrics.py` | Health metrics collector and snapshot comparison |
| `context-audit.py` | Session context consumption auditor — token usage, largest messages, ACTIVE vs FULL history, Session Health Level (per CONTEXT_LOADING 40/60/80 thresholds) |
| `dependency-graph.py` | Skill dependency visualizer |
| `blind-bundle.py` | 外部盲检投喂包构建器 + 卫生校验（P61）：按层（doc/cli/tools-config/skills）打包 git 跟踪文件；排除内部结论（reports/logs/metrics/workspaces/archived）与二进制；身份脱敏（远端 owner/repo、主机、机器用户名、家目录 → `<redacted>`）；`--check` 机器校验卫生（tier-A 泄漏/排除目录文件头/二进制），`--strict-name` 把仓库裸名升为硬失败 |
| `path-audit.py` | Path reference integrity audit (skips runtime/placeholder/generated refs) |
| `proposal-audit.py` | Proposal/action-item audit + proposal-policy gate (Status/Review/Implementation consistency) |
| `setup.py` | Environment configuration provision (generates config/environments/*.yaml) |
| `workflow-scaffold.py` | New-workflow scaffold (generates 8-section md + config yaml + runtime skeleton, appends registry) |
| `command-scaffold.py` | New-command scaffold (generates aic-<name>.md + registration checklist) |
| `branch-parser-scaffold.py` | Branch-name parser provider scaffold (init generates contract skeleton + contract tests for the bugfix hotfix mode) |
| `mr-provider-scaffold.py` | MR-submit provider scaffold (init generates contract skeleton + contract tests for the bugfix hotfix mode; e.g. Codeup) |
| `extensions-init.py` | Extensions directory bootstrap — standalone git repo init (.gitignore/README/example skill/remote/committer identity), idempotent |
| `extensions-lint.py` | Extensions domain linter — checks the separate extensions repo (SKILL.md / OPTIMIZATION_LOG.md conventions, no sensitive/compiled artifacts tracked); --fix-missing-log scaffolds logs |
| `quick-check.py` | Read-only quick health check (repo-lint + path-audit + extensions-lint) — seconds, safe at every session; records findings to metrics/quick-check-{date}.json for trend tracking |
| `prompt-metrics.py` | 提示词体积/缓存友好性实测（Q2/R1-R2）——构建全部 workflow+command，记录体积（chars/token）与前缀稳定性到 metrics/prompt-{date}.json；`AIC_FULL_RUNTIME=1` 时 prompt_builder 内嵌全量 runtime（R3 开关） |
| `maintain-delta.py` | 巡检增量感知（Q1-1）——对比上次完整巡检后的 git HEAD，判定 FIRST_RUN / NO_CHANGES / CHANGED(受影响区域+建议工具子集)；`--record` 在完整巡检后记录状态（metrics/maintain-delta-state.json，gitignored） |
| `maintain-report.py` | 巡检报告骨架自动生成（Q1-3）——从 quick-check/指标快照/proposal-audit 自动拼装 MAINTENANCE-{date}.md 的校验/对比/趋势/提案四节；非破坏（已存在不覆盖），叙事节留给 AI |
| `repo-ensure.py` | 按需 clone（P58）——读 {workspace_root}/repositories/{service_id}.yaml 的 git.url，`ensure` 缺失即 clone 到 {repository_root}/{service_id}（已存在则校验，`--pull` 拉取）；`check`/`list`/`validate`（元数据 id 唯一 + git.url 校验）；repositories 源先于 projects 初始化（setup scaffold 顺序），供 dev-setup Phase 7 / scan / change-impact 缺失即补；exit 0=ok 1=未就绪 2=用法错误 |
| `language-gate.py` | 运行时语言门禁（P45）——校验面向用户文本语言是否匹配 config/menu.yaml → locale；Runtime Complete 阶段呈现前运行（runtime-base「语言自检」步骤），三态 PASS/WARN/FAIL（exit 0/1/2）；`--list-suspicious` 人审可疑行 |
| `format-check.py` | develop 格式与规范泄漏自检（A 层）——纯 python3 无 JDK 依赖；查单行 Javadoc / 中文方法名 / 注释 T-xxx 泄漏 / Map 手工组装 payload（main）/ 4 空格缩进比例 / 方法显式访问修饰符（§Visibility）；`--changed` 仅查本 change 文件（git status 驱动）、`--check-commit` 查最近提交（含 T- 须 `type(scope): T-xxx`，规范 commit-content.md）；第 23 项结构相似重复实现（L1，参考 dupehound 方法论：规范化骨架+相似度，仅 --changed 增量模式，存量豁免，WARN 级）；PASS/WARN/FAIL（exit 0/1/2）；接入 runtime-develop Formatting gate。**作用域＝业务仓 src**（门禁恒以 `--changed` 增量运行：存量基线豁免 + 新增精确拦截，同 checkstyle suppressions 模式）；**ai-system 自身不在其门禁作用域**——对 `tools/**`（如 `jdt-format-gate/JdtFormatCheck.java` 这类开发工具）全量扫描会报规则面不适用项（stdout 即接口、最小依赖闭包的 CLI），登记见 `config/maintenance.yaml` |
| `checkstyle/checkstyle-gate.py` | checkstyle **增量门禁**（H2）：git status 驱动只查本 change 的 .java（相对仓根，suppressions 匹配一致）；无改动/非 git 快速 PASS 或全量；`--full` 全量、`--dry-run-list` 调试；error 阻断（exit 1）/ warning 收集（exit 0）；依赖探测 `~/.local/jre17` + `~/.local/lib/checkstyle/*-all.jar`（缺失 exit 3） |
| `checkstyle/` 使用流程 | 预演验证（platform-api 1690 文件）：10848 违反（ERROR 6624/WARN 4224）；存量抑制 = `checkstyle -g -o suppressions.xml -c <xml> <src>` 生成 XPath baseline → TreeWalker 内挂 `SuppressionXpathFilter`；顺序铁律：先 C2 格式基线（LineLength/FileTabCharacter 自愈）后 checkstyle 基线（行/AST 一致，避免抑制失效）；运行资产 `~/.local/lib/checkstyle/checkstyle-10.23.0-all.jar` + `~/.local/jre17`（checkstyle 10.x 需 Java 11+，all jar 取自 GitHub releases） |
| `checkstyle/checkstyle.xml` | 规范闸门规则集初稿（CLI 承载，业务仓零 pom）——正确性类 error（EqualsHashCode/DefaultComesLast/NeedBraces/UnusedImports/AvoidStarImport/命名驼峰/FileTabCharacter/LineLength-120）· 风格类 warn（AbbreviationAsWord/3 大写/Javadoc 结构/EmptyLineSeparator/CyclomaticComplexity-20）；存量治理靠 `suppressions.xml` 抑制后收紧；决策依据 SPOTLESS-FORMAT-GATE-PROPOSAL.md §5.1 |
| `format-baseline.py` | 业务仓格式基线（CLI，零 build 配置）：干净 worktree → C2 apply/check（known-ignore）→ **去注释后 token 级对比**做内容零变化安全证明（状态机词法：字符串/注释互不侵扰）→ 统计与 style: 提交提示；`--check-only` 日常验证；exit 0=通过/1=非干净/2=存在非格式差异（中止） |
| `format-jdt-gate.py` | eclipse JDT formatter 干跑门禁（C2）——ToolFactory + eclipse-format.xml（tab=4 space）对源目录干跑（默认不写盘；profile **即 IDEA 的 Eclipse XML 导出**（2026-09-21 经 sha256 验证与 IDE 导出**逐字节一致**），但**参数表语义仍与 IDEA 不同** —— 属**引擎表达力缺口**而非设置映射错误，见本行末语义边界）；`--apply` 将 formatted 写回源文件（迭代至 fixpoint，配合 `git diff -w` 安全校验）；`--ignore-file` 跳过已知无 fixpoint 边界文件（仓内 known-ignore.txt）；环境感知：JDK 自动探测（JAVA_HOME/~/.jdks/PATH//usr/lib/jvm，`--java` 可用户提供）、JDT 闭包缺失时交互授权 setup（下载 12 jar 到 ~/.local/lib/jdt-gate + javac 编译 wrapper）/skip/abort；配置持久化 ~/.config/ai-system/env.yaml（runtime.jdt.*）；exit 0=PASS/1=WARN(≤5 文件)/2=FAIL/3=ENV 不可用（apply 模式 exit 0=写回完成）；`--changed` 增量差分（P51）：git status 驱动，仅扫本 change 改动文件，JDT hunk × 改动行交集——存量基线豁免（BASELINE 记录诊断日志）、新增行拦截（NEW-DIFF），退出码按新增差异文件数映射；**profile 语义边界（2026-09-21 实证，详见提案 `reports/P65-C2-PROFILE-SEMANTICS.md` 与 `config/maintenance.yaml` 的 C2 语义边界登记）**：`join_wrapped_lines=false` **仅覆盖二元/条件表达式**的手工折行（实测保留），**不覆盖方法调用参数表**——参数表由 `alignment_for_arguments_in_method_invocation=0`（=**不折行**）管控，会把手工折的参数**合并为单行且不再折**，**即使超过 `lineSplit=120`**（实测 152 字符单行）；故本门禁保证的是「与 JDT 在此 profile 下一致」，**不保证行 ≤ 120**，亦**无法表达 IDEA 的「保留已有折行」**（JDT 3.13 无此档）。**根因**：Eclipse 折行模型（`alignment_*`）无法表达 IDEA 排版策略 → 导出必然落为 `alignment=0`（不折行）→ 属**表达力缺口**，故「重新导出 profile」或「改 alignment 取值」都不能达成 IDE 一致（前者为恒等操作，后者差异 +55%~+109%）；另注：**任何单引擎的全量基线都清零不了**（IDEA 自判 39% 文件需重排）→ 门禁正确形态是**增量收敛**（`--changed`：存量豁免 + 新增拦截），见提案 `reports/P65-C2-PROFILE-SEMANTICS.md`；
| `jdt-profile-eval.py` | C2 profile 校准评估器（P65 Option B/C 的量化仪器，**只读**）——对多个候选 profile（在现行 `eclipse-format.xml` 上覆盖 `alignment_*` 等设置）批量干跑，输出「文件数 / 差异文件数 / 差异行数 / **二次格式化收敛性**（有无 format↔format 振荡 → 决定 `known-ignore.txt` 需求）/ 最长行 / >120 列行数」对照表，用于判断「校准某设置会引发多大 diff」「行长 ≤ 120 是否可达」；源目录仅被读取，产物写 `--work`（默认 /tmp/jdt-profile-eval），**绝不写业务仓**；用法 `--src <dir-or-file> [--src …] [--limit N] [--candidates C0,C1,…]`；内置候选 C0-baseline / C1-args17 / C2-args49 / C3-only-mi17 / C1c / C2c；配套 `--ignore-file` 清单 `known-ignore.txt` 的治理：每个豁免条目须紧邻上方一行 `# reason: <理由>（<YYYY-MM-DD> 复核基线）`（单行），由 `tools/checks/jdt_ignore.py` 强制（缺理由/悬空 ERROR、超 180 天 WARN，P65 Option D） |
|
Run order after a change:

```text
python3 tools/repo-lint.py --repo-root .   # structural + language checks (Rule 1-3)
python3 tools/path-audit.py
python3 tools/check.py                     # integrity gate (re-runs repo-lint internally)
```

**Language checks are mandatory on every change** — `repo-lint.py`
`check_language` (LANGUAGE_CONVENTION Rule 1-3) runs in the first step of
this sequence, is re-run by `check.py` (`check_repo_lint`), and is also a
standalone CI step. A change that introduces a language violation fails all
three gates.
