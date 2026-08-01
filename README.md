# AI System — Entrypoint

> Orchestration framework: Workflows (decide what) → Runtimes (execute how)
> → Operating Rules (constrain behaviour) → Standards (define quality) → Skills (provide methods).

---

## Quick Start

```text
ai-system/            ← Governance, specifications, workflows, skills, tools
  workflows/            Workflow entry contracts (README with selection table)
  templates/            Runtime / prompt / asset templates
  loaders/              On-demand loading strategies (standards-loader)
  governance/           Quality gates, lifecycle, review process, conventions
  rfc/                  RFC specifications + Architecture Decision Records
  cli/                  CLI entrypoint (interactive wizard + command generation)

## When Modifying This Repository

1. **Read `governance/repo-lint.md`** — understand naming rules and lint process.
2. **Follow RFCs under `rfc/`** — RFC-0001 (architecture), RFC-0002 (skill spec),
   RFC-0003 (workflow spec), RFC-0004 (playbook spec).
3. **Run `python tools/repo-lint.py --repo-root .`** before proposing structural changes.
   Fix all BLOCKER and ERROR items.
4. **Update the architecture status in reports** if architecture changes were made.
5. **Preserve backward compatibility** for workspace-level tool artifacts
   (`openspec/`, `.opencode/`, `.pi/`). These are platform-managed and must not be modified here.

## Key Rules

| Rule | Source |
|---|---|
| Every Skill needs a `skill.md` with valid YAML frontmatter | RFC-0002 |
| Skills must not exceed 1000 total lines | RFC-0002 |
| Skills must delegate Maven execution to `java-maven` | ADR-0003 |
| Skills must not duplicate shared checklists or playbook content | RFC-0002 |
| Workflows orchestrate; they do not implement | RFC-0003 |
| Playbooks educate; they do not execute | RFC-0004 |

## Quick Reference

```shell
# Lint the repository
python tools/repo-lint.py --repo-root .

# Collect health metrics
python tools/repo-metrics.py --repo-root .

# Compare with previous snapshot
python tools/repo-metrics.py --repo-root . --compare metrics/baseline.json

# Generate dependency graph
python tools/dependency-graph.py --repo-root .

# Check path dependencies
python tools/path-audit.py

# Run the interactive CLI wizard
python -m cli.main
```

| `tools/path-audit.py` | Path dependency integrity check |

## Directory Index

| Path | Content |
|---|---|
| `governance/standards/common/task-quality-checklist.md` | Per-task quality verification baseline |
| `governance/standards/common/ai-coding-rules.md` | AI coding rules |
| `governance/standards/common/clean-code.md` | Clean code conventions |
| `governance/review-standard.md` | Skill review workflow and checklists |
| `governance/repo-lint.md` | Naming rules for all components |
| `governance/violation-rules.md` | Violation classification and severity |
| `governance/karpathy-guidelines.md` | Coding guidelines for LLM agents |
| `governance/AI_OPERATING_RULES.md` | Core operating rules (all workflows) |
| `governance/policies/quality-gates.md` | BLOCKER/ERROR/WARNING/INFO quality definitions |
| `governance/policies/skill-policy.md` | Skill creation and maintenance policy |
| `governance/policies/skill-lifecycle.md` | Skill lifecycle stages |
| `governance/policies/routing-policy.md` | Intent → workflow/skill routing policy |
| `governance/policies/security-policy.md` | Security guidelines |
| `rfc/RFC-0001-repository-architecture.md` | Component definitions and layer model |
| `rfc/RFC-0002-skill-specification.md` | Mandatory components and quality gates |
| `rfc/RFC-0003-workflow-specification.md` | Orchestration rules and prohibitions |
| `rfc/RFC-0004-playbook-specification.md` | Knowledge layer specification |
| `rfc/ADR-0001-*.md` through `ADR-0004-*.md` | Architecture Decision Records |
| `reports/WORKFLOW-OPTIMIZATION-REPORT-2026-07.md` | Workflow optimization analysis |
| `reports/ARCHITECTURE-ASSESSMENT-2026-07.md` | Full architecture assessment |
