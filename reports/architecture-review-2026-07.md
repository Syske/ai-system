# Architecture Review 2026-07

> This document summarizes the architecture review conducted in July 2026,
> covering the establishment of the Repository Governance system.

---

## Context

The repository had grown to 17 Skills across `.opencode/skills/` without a
formal architecture, governance, or quality control system. Skills duplicated
content, naming was inconsistent, and there was no process for ensuring
long-term maintainability.

## Scope

This review covers:

1. **RFC-0001** — Repository Architecture (component definitions, layer model)
2. **RFC-0002** — Skill Specification (mandatory components, quality gates)
3. **RFC-0003** — Workflow Specification (orchestration rules, prohibitions)
4. **RFC-0004** — Playbook Specification (knowledge layer rules)
5. **Governance system** — quality gates, review process, skill lifecycle
6. **Repository optimization report** — duplication analysis, migration plan
7. **Tooling** — linter, metrics, dependency graph generator

## Architecture Decisions

| ADR | Decision |
|---|---|
| 0001 | OpenSpec as the standard planning layer |
| 0002 | Playbooks as a separate knowledge layer (not embedded in Skills) |
| 0003 | java-maven as a Foundation Skill (sole Maven executor) |
| 0004 | Repository Governance architecture (RFCs + governance + tools) |

## Current State

| Metric | Value |
|---|---|
| Skills | 17 |
| RFCs | 4 |
| ADRs | 4 |
| Governance documents | 5 |
| Tools | 3 (linter, metrics, dep-graph) |
| Repository optimization report | 1 (~960 lines) |

## Open Issues

1. 8 monolithic Skills still use `SKILL.md` naming and lack proper
   frontmatter descriptions — should be migrated to the new standard.
2. 4 Skills exceed 1000 lines — candidates for splitting.
3. No Workflow files exist yet — `ai/workflows/` should be populated.
4. No Playbook files exist yet — `ai/playbooks/` should be populated.
5. Linter and metrics are not yet integrated into CI.

## Recommendations

| Priority | Recommendation |
|---|---|
| **P0** | Add CI integration for `tools/repo-lint.py` — block PRs with BLOCKER/ERROR |
| **P0** | Create first Playbook (`maven.md`) and link it from relevant Skills |
| **P1** | Migrate 8 monolithic Skills to the RFC-0002 standard |
| **P1** | Create first Workflow (`develop`, `bugfix`) |
| **P2** | Split 4 Skills exceeding 1000 lines |
| **P2** | Set up weekly metrics snapshot in CI |

## Reviewers

- Repository Governance (initial review)
