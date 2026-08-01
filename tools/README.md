# Tools

Automated governance tooling for the AI repository.

| Tool | Purpose |
|------|---------|
| `check.py` | System integrity + runnability gate (9 checks; run after every change) |
| `repo-lint.py` | Structural linter — run before every change |
| `repo-metrics.py` | Health metrics collector and snapshot comparison |
| `dependency-graph.py` | Skill dependency visualizer |
| `path-audit.py` | Path reference integrity audit (skips runtime/placeholder/generated refs) |
| `setup.py` | Environment configuration provision (generates config/environments/*.yaml) |
| `pack.py` | AI System packaging (output dir, zip) |

Run order after a change:

```text
python tools/repo-lint.py --repo-root .
python tools/path-audit.py
python tools/check.py
```
