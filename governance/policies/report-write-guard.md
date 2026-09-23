# Report-Write Guard Policy

**Single source** for the "check before you write" rule applied by every Runtime that writes
report files. Runtimes **reference** this policy; they do not restate it (that restatement was
the source of the duplication this policy removes).

## Purpose

Prevent a rerun from silently overwriting an existing report artifact that cannot be recovered.

## Scope

Every Runtime that writes report files into the workspace:

- `templates/runtime/runtime-review.md`
- `templates/runtime/runtime-verify.md`

## Rule

Before writing any report file, check whether the target path already exists. On conflict:

1. Do **NOT** overwrite silently — surface the existing file (path + mtime).
2. Either write to a suffixed name (e.g. `-{HHMMSS}`) or back up the existing file first,
   per the user's choice.
3. Record the outcome in the diagnostic log.

## Rationale

Workspace artifacts live under `workspaces/`, which is **not** a git repository: an overwritten
report is unrecoverable. Origin: a rerun silently overwrote a prior verification report
(T-011, 2026-09-11).

For same-day reruns of *generated* artifact directories, the shared helper
`cli/utils/file.py:unique_dir()` implements the `-N` suffix convention — prefer it over
hand-rolled naming.

## Enforcement

Review-time discipline, checked by the Runtime that writes the report (step 3 above records the
outcome in the diagnostic log, which is the audit trail). No automated gate: the guard applies at
write time inside a workspace, where path existence is a runtime fact.

## Violations

A silent overwrite is a **Major** violation (lost artifact, unrecoverable) — handle per
`governance/violation-rules.md`.