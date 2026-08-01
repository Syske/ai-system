# AI System File Contract Memory


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
