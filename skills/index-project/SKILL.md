---
name: index-project
description: Reindex the current project's code index with a visible progress bar. Use when the user wants to rebuild or refresh the semantic code search index.
user-invocable: true
disable-model-invocation: true
argument-hint: [--full]
allowed-tools: Bash, Read, Edit
---

# Index Project

Reindex the current project using the code-index CLI with a real-time progress bar.

## Steps

1. **Ensure `.code_index` is in `.gitignore`** before indexing:
   - Read the project's `.gitignore` file (if it exists)
   - If `.code_index` or `/.code_index` is NOT already listed, append `/.code_index` to the `.gitignore`
   - If no `.gitignore` exists, create one with `/.code_index`

2. Run the reindex CLI script via Bash, **probing the venv layout** (POSIX `bin/python`
   vs Windows `Scripts/python`) instead of assuming one of them:

```bash
VENV="$HOME/.claude-code-index-venv"
PY="$VENV/bin/python"                          # POSIX / WSL
[ -x "$PY" ] || PY="$VENV/Scripts/python"      # Windows / Git-Bash
[ -x "$PY" ] || PY="$VENV/Scripts/python.exe"
[ -x "$PY" ] || { echo "venv interpreter not found (bin/python or Scripts/python[.exe]): $VENV" >&2; exit 1; }
"$PY" "$HOME/.claude/tools/code-indexer/reindex_cli.py" $ARGUMENTS
```

- If the user passes `--full` or `full` as an argument, include `--full` in the command
- Otherwise, run without `--full` for an incremental reindex (only changed files)

3. The script shows a live progress bar with:
   - File discovery count
   - Per-file parsing progress with a visual bar
   - Embedding progress
   - Final summary with file counts, chunk counts, and symbol types

## Usage

- `/index-project` — Incremental reindex (fast, only changed files)
- `/index-project --full` — Full reindex from scratch
