---
name: open-cli
description: "Generate CLI adapter files (YAML/TypeScript) for the opencli framework. Use when the user wants to create CLI commands, build adapters for websites or APIs, or interact with the opencli tool. Covers browser-based API discovery, authentication strategy selection, and adapter generation workflows."
---


# OpenCLI Adapter Generator


## Overview


OpenCLI is a CLI framework that wraps website APIs into local command-line tools. This skill guides the agent through discovering APIs via browser exploration, selecting authentication strategies, and generating adapter files (YAML or TypeScript) placed in `~/.opencli/clis/{site}/{command}.yaml|.ts`.


## Workflow Modes


**Quick mode** (single command): for a single command with a known URL + description, follow the
Standard Workflow below directly — create the directory, generate the adapter, verify.


**Full mode** (complex adapters): for complex adapters, work through: browser exploration to
discover the request chain → auth strategy selection (Cookie / Public / Intercept / Header)
→ platform SDK choice (e.g. Bilibili `apiGet` / `fetchJson`) → YAML vs TS selection
→ `tap` step debugging → cascading request patterns.


> Note: the two upstream detail docs previously linked here (`CLI-ONESHOT.md`,
> `CLI-EXPLORER.md`) were **never vendored** into this repository, so the links were removed
> (they were dangling paths — 2026-09-21 external blind review V6 / P60 §5.3). The guidance
> above is the actionable fallback until those docs are vendored.


## Output Specification


All adapter files **must** be written to `~/.opencli/clis/{site}/{command}.yaml` or `.ts`. No other output locations or file formats (`.js`, `.json`, `.md`, `.txt`) are permitted.


Correct examples:
- `~/.opencli/clis/aem/page-views.ts`
- `~/.opencli/clis/twitter/lists.yaml`
- `~/.opencli/clis/bilibili/favorites.ts`


## Supported Formats


| Format | Extension | When to use |
|--------|-----------|-------------|
| YAML | `.yaml` | Simple scenarios (Cookie/Public auth, straightforward flows) |
| TypeScript | `.ts` | Complex scenarios (Intercept capture, Header auth, multi-step logic) |


## Standard Workflow


1. **Create directory**: `mkdir -p ~/.opencli/clis/{site}`
2. **Generate adapter file** at the correct path (YAML or TS)
3. **Verify**: `opencli list | grep {site}` then `opencli {site} {command} {option}`


## Naming Conventions


| Element | Rule | Good | Bad |
|---------|------|------|-----|
| site | Lowercase, hyphens allowed | `aem`, `my-site` | `AEM`, `my_site` |
| command | Lowercase, hyphen-separated | `page-views`, `project-info` | `pageViews`, `project_info` |


## Pre-Generation Checklist


- [ ] Output path is `~/.opencli/clis/{site}/{command}.yaml` or `.ts`
- [ ] Site name is lowercase (no uppercase, no underscores)
- [ ] Command name uses hyphens (no spaces, no underscores)
- [ ] File extension is `.yaml` or `.ts` only
- [ ] Directory `~/.opencli/clis/{site}/` has been created