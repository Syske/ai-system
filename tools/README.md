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
| `extensions-init.py` | Extensions directory bootstrap — standalone git repo init (.gitignore/README/example skill/remote/committer identity), idempotent |
| `extensions-lint.py` | Extensions domain linter — checks the separate extensions repo (SKILL.md / OPTIMIZATION_LOG.md conventions, no sensitive/compiled artifacts tracked); --fix-missing-log scaffolds logs |
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
