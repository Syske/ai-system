# Templates — Authoring Rules

Authoring discipline for the assets under this directory. They are consumed by
`cli/services/prompt_builder.py` (prompt skeletons) and by the Runtimes
(`runtime/`, referenced from `config/workflows/*.yaml`).

## Layers

| Directory | Role |
|---|---|
| `prompts/` | Prompt skeletons: `workflow.md`, `command.md`, `skill-launch.md`, `external-ai-review.md`, `tasks-template.md`, `develop-start.md` |
| `runtime/` | Runtime execution templates (phases, checkpoints, gates) — one per workflow/runtime |

## Authoring Rules

1. **Do NOT reflow templates for AI/token gains.** Hard-wrapping at ~80 columns
   is a *human* convention (terminal / git-diff / mail width). Measured
   (2026-09-21): reflowing every prompt template saved **41 chars of 130,975
   (0.03%, ≈10 tokens of ~32.7k)** while introducing **3 lost-space defects** and
   >200-char lines that hurt diffability. Whitespace is not a token lever.
2. **Token size is content, not whitespace.** To shrink prompts, trim content,
   skeletonize, and keep a stable prefix — see
   `governance/CONTEXT_LOADING.md` §Context Budget Discipline, and measure with
   `tools/prompt-metrics.py` (chars / tokens / prefix stability) before and after.
3. **Preserve line structure wherever it carries meaning**: markdown lists,
   paragraph blank lines, code fences, tables, frontmatter, and phase markers
   (`## Phase N`, `@keep`). Never merge across a blank line.
4. **Never reflow code, frontmatter, tables, or YAML** — their line breaks are
   syntax, not cosmetics.
5. **Batch text edits must pass a normalized word-diff** before commit: collapse
   whitespace (`re.sub(r"\s+", " ", text)`) in both the old and new text and
   compare — this is what catches lost spaces from a manual reflow.
6. **Placeholders are contractual**: `{{ai_system_root}}` / `{{workspace_root}}`
   etc. are resolved at render time (`P30`); never rename or drop them.

## Validation

```text
python3 -m unittest cli.tests.test_prompt_builder   # prompt build unit tests
python3 tools/check.py                              # prompt-build smoke (all workflows/commands)
python3 tools/repo-lint.py --repo-root .            # structural + language discipline
```