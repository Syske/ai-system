# Governance Compliance Verification

This document defines how repository compliance is verified against RFCs.
Use during Stage 4 of the workflow.

---

## RFC-0001: Repository Architecture

| Check | Method | Violation |
|---|---|---|
| Six asset types used correctly | Scan all files, classify by directory | Asset in wrong directory |
| Layer rules followed | Dependency graph analysis | Foundation Skill depends on Orchestration |
| Naming conventions followed | Regex check on directory and file names | Non-compliant name |
| Prohibited patterns absent | Grep for mvn in non-java-maven, absolute paths | Prohibited content found |

## RFC-0002: Skill Specification

| Check | Method | Violation |
|---|---|---|
| skill.md exists | File existence check | Missing entrypoint |
| YAML frontmatter present | Regex parse | Missing frontmatter |
| name: matches directory | String comparison | Name mismatch |
| description: 100-1024 chars | Length check | Invalid length |
| ≥ 3 trigger phrases | Keyword scan | Insufficient triggers |
| Anti-triggers present | Keyword scan for "does not" or "not responsible" | Missing anti-triggers |
| Stopping conditions defined | Check for stop/failure conditions | Missing stopping conditions |
| Delegation documented | Check for "delegates to" or "invoke" | Missing delegation |
| No single file exceeds 1000 lines (aggregated reference files exempt) | Per-file line count | Exceeds limit |
| No Maven commands (unless java-maven) | Grep for mvn patterns | Prohibited commands |
| Workflow ≥ 3 stages (if workflow.md exists) | Stage count | Insufficient stages |
| No shared checklist duplication | Compare checklist headings with `.opencode/checklists/` | Duplicate checklist |
| No shared playbook duplication | Cross-reference with `.opencode/playbooks/` | Duplicate knowledge |

## RFC-0003: Workflow Specification

| Check | Method | Violation |
|---|---|---|
| Orchestration-only | Grep for implementation patterns | Contains implementation |
| Skill references exist | Cross-reference with `.opencode/skills/` | Non-existent Skill reference |
| Stopping conditions defined | Check for stop/failure conditions | Missing |
| ≤ 100 lines | Line count | Exceeds limit |
| No embedded knowledge | Cross-reference with Playbooks | Knowledge duplicated |

## RFC-0004: Playbook Specification

| Check | Method | Violation |
|---|---|---|
| Single topic | Heading analysis | Multiple topics |
| No execution instructions | Grep for command patterns | Contains commands |
| No project-specific content | Grep for path patterns | Hardcoded paths |
| Referenced by ≥ 1 Skill | Cross-reference with Skills | Orphaned |

---

## Naming Convention Compliance

| Rule | Check | Violation |
|---|---|---|
| Skill directory: kebab-case | Regex `^[a-z][a-z0-9-]*$` | Invalid name |
| Entrypoint: skill.md | lowercase | SKILL.md (uppercase) |
| RFC: `RFC-NNNN-<title>.md` | Regex | Invalid format |
| ADR: `NNNN-<title>.md` | Regex | Invalid format |
| No spaces in directory names | Grep for space | Space in name |

## Backward Compatibility Compliance

| Rule | Check | Violation |
|---|---|---|
| `.opencode/skills/` Skills not removed | Compare with baseline | Skill removed |
| `.opencode/skills/` Skills not renamed | Compare with baseline | Skill renamed |
| `.opencode/commands/` files not removed | Compare with baseline | Command removed |
| No Skills moved to different directories | Compare with baseline | Skill moved |
