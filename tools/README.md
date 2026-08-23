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
| `maintain-delta.py` | 巡检增量感知（Q1-1）——对比上次完整巡检后的 git HEAD，判定 FIRST_RUN / NO_CHANGES / CHANGED(受影响区域+建议工具子集)；`--record` 在完整巡检后记录状态（metrics/maintain-delta-state.json，gitignored） |
| `maintain-report.py` | 巡检报告骨架自动生成（Q1-3）——从 quick-check/指标快照/proposal-audit 自动拼装 MAINTENANCE-{date}.md 的校验/对比/趋势/提案四节；非破坏（已存在不覆盖），叙事节留给 AI |
| `pack.py` | AI System packaging (output dir, zip) |

Run order after a change:

```text
python tools/repo-lint.py --repo-root .   # structural + language checks (Rule 1-3)
python tools/path-audit.py
python tools/check.py                     # integrity gate (re-runs repo-lint internally)
```

**Language checks are mandatory on every change** — `repo-lint.py`
`check_language` (LANGUAGE_CONVENTION Rule 1-3) runs in the first step of
this sequence, is re-run by `check.py` (`check_repo_lint`), and is also a
standalone CI step. A change that introduces a language violation fails all
three gates.
