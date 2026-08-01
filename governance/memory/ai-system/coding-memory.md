# AI System Coding Memory

Lessons learned for the AI System itself (workflows, runtimes, prompt templates).


## [AI System] Workflow Main Chain Needs a Single Definition

Context:

ai-system/workflows/README.md showed the main chain starting from bootstrap, while config/menu.yaml and OPERATIONS.md §1.2 started from prepare.

Problem:

The same concept (change lifecycle main chain) was defined inconsistently across three documents, causing ambiguity about the entry point.

Root Cause:

The one-time cold start (bootstrap) was mixed into the same chain as the change lifecycle main chain (starting from prepare).

Solution:

Split the main chain into two parts: Cold start (bootstrap) + Change lifecycle main chain (prepare → spec → dev-setup → develop → review → verify → release), and align all three documents.

Lesson:

The AI System main chain / workflow relationship diagram must be maintained from a single source (workflows/README.md) and cross-checked regularly against menu.yaml and OPERATIONS.md.

Scope:

- ai-system/workflows/
- ai-system/config/menu.yaml
- ai-system/OPERATIONS.md


Related:

- Standard:
  LANGUAGE_CONVENTION.md


## [AI System] Runtime Template Language Boundary: English Control Flow / System Language for User Output

Context:

In ai-system/templates/runtime/ and workflows/, the language boundary between AI control-flow instructions and text presented to the user was unclear.

Problem:

Control-flow instructions and embedded user-facing report templates mixed Chinese and English; questions/choices presented to the user were in English, not matching the system-specified language (config/menu.yaml → locale).

Root Cause:

LANGUAGE_CONVENTION covered reports and comments but did not define the language for interactive questions and choices presented to the user.

Solution:

Apply a three-layer boundary: AI control-flow instructions → English; questions/choices/confirmations presented to the user → system-specified language (config/menu.yaml → locale); user report templates → Chinese. Technical identifiers (workflow names / arguments) stay English. Also added an Interactive prompts rule to LANGUAGE_CONVENTION.

Lesson:

When creating or editing runtime/workflow templates, first classify the text (control flow / user interaction / user report), then choose the language accordingly; interactive questions follow the system locale, never hardcode a language.

Scope:

- ai-system/templates/runtime/
- ai-system/workflows/
- ai-system/templates/prompts/


Related:

- Standard:
  LANGUAGE_CONVENTION.md


## [AI System] Filename Must Match Content After Rename

Context:

A governance structure analysis (2026-08-01) found that `policies/routing-policy.md` contained Skill Lifecycle content and `violation-rules.md` contained a Repository Governance overview.

Problem:

After migration renames (`skill-lifecycle.md` → `routing-policy.md`, `repository-governance.md` → `violation-rules.md`), the file contents were not updated. Indexes (governance/README.md, root README.md) described routing/violation rules that did not exist, and the real routing policy had no document.

Root Cause:

Renaming a file without syncing its content creates a filename↔content mismatch that propagates to every index and cross-reference.

Solution:

- Move Skill Lifecycle content to a dedicated `policies/skill-lifecycle.md`.
- Rewrite `routing-policy.md` as the real routing policy (from `routing/ai-routing.yaml`).
- Rewrite `violation-rules.md` as violation severity classification.

Lesson:

When renaming a governance document, update the content to match the new filename in the same change, then verify all indexes (governance/README.md, root README.md) and references in the same commit. Filename is a contract.

Scope:

- ai-system/governance/policies/
- ai-system/governance/README.md


Related:

- Standard:
  repo-lint.md


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
