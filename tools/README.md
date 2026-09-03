# Tools

Automated governance tooling for the AI repository.

| Tool | Purpose |
|------|---------|
| `check.py` | System integrity + runnability gate (9 checks; run after every change) |
| `repo-lint.py` | Structural linter — run before every change. Language check (`check_language`) enforces `LANGUAGE_CONVENTION.md`: (1) `cli/commands/aic-*.md` Steps/Guardrails must be English; (2) `cli/**/*.py` + `tools/*.py` comments must be Chinese; (3) `governance/*.md` (excl. archive/, standards/, README, policies) must be English |
| `workflow-command-audit.py` | Workflow & command health auditor — file length (RFC-0003 / thin-command gates), required sections, Next targets, dangling command references, menu.yaml registration |
| `repo-metrics.py` | Health metrics collector and snapshot comparison |
| `context-audit.py` | Session context consumption auditor — token usage, largest messages, ACTIVE vs FULL history, Session Health Level (per CONTEXT_LOADING 40/60/80 thresholds) |
| `dependency-graph.py` | Skill dependency visualizer |
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
| `language-gate.py` | 运行时语言门禁（P45）——校验面向用户文本语言是否匹配 config/menu.yaml → locale；Runtime Complete 阶段呈现前运行（runtime-base「语言自检」步骤），三态 PASS/WARN/FAIL（exit 0/1/2）；`--list-suspicious` 人审可疑行 |
| `format-check.py` | develop 格式与规范泄漏自检（A 层）——纯 python3 无 JDK 依赖；查单行 Javadoc / 中文方法名 / 注释 T-xxx 泄漏 / Map 手工组装 payload（main）/ 4 空格缩进比例；`--changed` 仅查本 change 文件（git status 驱动）、`--check-commit` 查提交 subject；PASS/WARN/FAIL（exit 0/1/2）；接入 runtime-develop Formatting gate |
| `format-jdt-gate.py` | eclipse JDT formatter 干跑门禁（C2）——ToolFactory + eclipse-format.xml（tab=4 space）对源目录干跑（默认不写盘，与 IDEA 默认 Java 格式化同源）；`--apply` 将 formatted 写回源文件（格式基线，配合 `git diff -w` 安全校验）；环境感知：JDK 自动探测（JAVA_HOME/~/.jdks/PATH//usr/lib/jvm，`--java` 可用户提供）、JDT 闭包缺失时交互授权 setup（下载 12 jar 到 ~/.local/lib/jdt-gate + javac 编译 wrapper）/skip/abort；配置持久化 ~/.config/ai-system/env.yaml（runtime.jdt.*）；exit 0=PASS/1=WARN(≤5 文件)/2=FAIL/3=ENV 不可用（apply 模式 exit 0=写回完成）；wrapper 在 tools/jdt-format-gate/（JdtFormatCheck.java + eclipse-format.xml——profile 为团队 IDEA 默认系展开，375 条目，已校准：platform-api 1690 文件 apply 后 check 0 差异） |
| `pack.py` | AI System packaging (output dir, zip) |

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
