# AI System Archive Discipline Memory


## [AI System] Archiving a File Requires Cleaning Active References

Context:

`governance/standards/common/code-quality.md` was moved to `governance/archive/standards/common/code-quality.md` and replaced by `task-quality-checklist.md` + `clean-code.md`.

Problem:

After the move, root README.md and loaders/standards-loader.md still referenced `governance/standards/common/code-quality.md`, pointing to a non-existent path.

Root Cause:

Archiving moved the file but did not update the active references in the same change.

Solution:

Remove the archived `common/code-quality.md` reference from standards-loader and README, and create minimal "Reserved" skeleton docs for extension placeholder standards (api/rest, database/sql, go/go-style, java/mybatis, java/spring, mq/rocketmq, python/pep8) so references resolve.

Lesson:

When archiving a file, update or remove every active reference in the same commit; orphaned references silently break tooling and docs. Mark extension-reserved standards explicitly so a missing file is intentional, not an error.

Scope:

- ai-system/governance/archive/
- ai-system/loaders/standards-loader.md
- ai-system/README.md


Related:

- Standard:
  repo-lint.md
