---
name: hotfix-test-doc
description: Generate a HotFix test document (转测文档).
workflow:
  inputs:
    required: [Branch Name]
    optional:
      - name: Project ID
      - name: Document Title
      - name: 发布内容
  next: [None]
---
# Workflow: HotFix Test Doc

## Purpose

Generate a HotFix test document (转测文档) for a committed hotfix branch.

## Runtime

- templates/runtime/runtime-hotfix-test-doc.md

## Preconditions

- BugFix completed in hotfix mode with a committed branch (Phases 4.6/6.5/6.6)
- Regression verification passed

## Inputs

Required:

- Branch Name (source branch of the hotfix fix)

Optional:

- Project ID
- Document Title
- 发布内容 (services, clusters, build branch, version)

## Context

Load only:

- The committed hotfix branch diff (git diff base...HEAD)
- The HotFix 一页纸 template (extensions/hotfix-test-doc/template_content.md)

Never load the entire repository tree into context.

## Outputs

- HotFix test document (转测文档) on Confluence
- 转测文档 markdown (local copy when Confluence API fails)

## Exit Criteria

Success:

- Document created and verified (title, ancestors, no empty cells)

Stop:

- Confluence API fails and local save also fails → report and stop
- Optional recap: reusable lesson this run? → run `memory-capture` skill; none → skip
## Next

- None
