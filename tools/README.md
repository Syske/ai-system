# Tools

Automated governance tooling for the AI repository.

| Tool | Purpose |
|------|---------|
| `check.py` | System integrity + runnability gate (9 checks; run after every change) |
| `repo-lint.py` | Structural linter — run before every change. Language check (`check_language`) enforces `LANGUAGE_CONVENTION.md`: (1) `cli/commands/aic-*.md` Steps/Guardrails must be English; (2) `cli/**/*.py` + `tools/*.py` comments must be Chinese; (3) `governance/*.md` (excl. archive/, standards/, README, policies) must be English |
| `repo-metrics.py` | Health metrics collector and snapshot comparison |
| `dependency-graph.py` | Skill dependency visualizer |
| `path-audit.py` | Path reference integrity audit (skips runtime/placeholder/generated refs) |
| `proposal-audit.py` | Proposal/action-item audit + proposal-policy gate (Status/Review/Implementation consistency) |
| `setup.py` | Environment configuration provision (generates config/environments/*.yaml) |
| `workflow-scaffold.py` | New-workflow scaffold (generates 8-section md + config yaml + runtime skeleton, appends registry) |
| `command-scaffold.py` | New-command scaffold (generates aic-<name>.md + registration checklist) |
| `pack.py` | AI System packaging (output dir, zip) |

Run order after a change:

```text
python tools/repo-lint.py --repo-root .
python tools/path-audit.py
python tools/check.py
```
