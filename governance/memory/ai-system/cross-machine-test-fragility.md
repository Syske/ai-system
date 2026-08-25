# AI System Cross-Machine Test Fragility Memory


## [AI System] Env-Dependent Tests: Distinguish Resolved Absolute Paths from Dangling Relative Refs

Context:

ai-system is maintained across multiple machines. A test authored and passing on
one machine (where an extensions/ repo entry was absent) was pulled to another
machine where the same entry was present. The caps-injection design (confirmed)
injects present extensions as resolved absolute paths into workflow prompts.

Problem:

`test_dangling_extension_caps_skipped` asserted that NO `extensions/<name>`
literal appears in the prepare/spec/develop prompt. It passed on the origin
machine (extension absent -> path skipped -> no literal) but FAILED on the
pulling machine (extension present -> resolved absolute path injected -> the
regex matched the `extensions/<name>` substring of the absolute path as a false
"dangling ref").

Root Cause:

The assertion regex `extensions/[a-zA-Z0-9_-]+` could not distinguish a DANGLING
RELATIVE ref (`extensions/<name>` leaked unresolved) from the substring of a
RESOLVED ABSOLUTE path (`/mnt/.../extensions/<name>`). The test was env-dependent:
it passed only when the extension was absent, so the fragility was invisible at
the origin machine.

Solution:

Use a path-separator negative lookbehind: `(?<![\\/])extensions/[a-zA-Z0-9_-]+`
so only bare relative (dangling) refs match; a resolved absolute path (preceded
by `/` or `\\`) is not flagged. Separately, re-run the full CLI test suite after
every cross-machine `git pull`, because env-dependent tests pass at origin and
fail downstream where repo/toolchain state differs.

Lesson:

When asserting path literals in generated prompts, distinguish resolved absolute
paths from dangling relative refs with a path-separator negative lookbehind, and
re-run the full test suite after every cross-machine pull — env-dependent tests
pass at the origin machine and fail downstream.

Scope:

- ai-system/cli/tests/ (path-literal assertions in generated prompts)
- ai-system/cli/services/prompt_builder.py (caps injection / _resolve_ref)
- ai-system/config/main-chain-capabilities.yaml (registered extension paths)
