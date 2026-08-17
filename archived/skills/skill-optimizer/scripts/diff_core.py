#!/usr/bin/env python3
"""Generate a self-contained HTML diff viewer for skill optimization iterations.

Uses diff2html (via CDN) for rendering — gets us side-by-side, word-level
highlight, file collapse, synchronized scroll, syntax highlight for free.

Python side: compute unified diffs + content-addressed dedup.
Browser side: diff2html renders, custom shell handles version selection.

Usage (via diff_viewer.py):
    python diff_viewer.py --snapshots ./snapshots -o diff.html
    python diff_viewer.py --base ./v0 --current ./v1 -o diff.html

No dependencies beyond the Python stdlib.
"""

import argparse
import difflib
import hashlib
import json
import os
import re
import sys
from pathlib import Path

from html_report import HTML_TEMPLATE

TEXT_EXTENSIONS = {
    ".md", ".txt", ".json", ".csv", ".py", ".js", ".ts", ".tsx", ".jsx",
    ".yaml", ".yml", ".xml", ".html", ".css", ".sh", ".rb", ".go", ".rs",
    ".java", ".c", ".cpp", ".h", ".hpp", ".sql", ".r", ".toml", ".cfg",
    ".ini", ".env", ".mjs", ".cjs", ".lua", ".pl", ".swift", ".kt",
}
SKIP_DIRS = {"node_modules", ".git", "__pycache__", ".venv", "venv", ".opt", "snapshots", ".DS_Store"}
ALWAYS_INCLUDE = {"SKILL.md", "Makefile", "Dockerfile", "LICENSE", "LICENSE.txt"}


def collect_files(directory: Path) -> dict[str, str]:
    files = {}
    if not directory.is_dir():
        return files
    for root, dirs, filenames in os.walk(directory):
        dirs[:] = sorted(d for d in dirs if d not in SKIP_DIRS)
        for fname in sorted(filenames):
            fpath = Path(root) / fname
            rel = str(fpath.relative_to(directory))
            if fpath.suffix.lower() in TEXT_EXTENSIONS or fname in ALWAYS_INCLUDE:
                try:
                    files[rel] = fpath.read_text(errors="replace")
                except OSError:
                    files[rel] = "(Error reading file)"
    return files


def version_sort_key(name: str):
    parts = re.split(r'[.\-_]', name.lstrip('v'))
    result = []
    for p in parts:
        try:
            result.append((0, int(p)))
        except ValueError:
            result.append((1, p))
    return result


def discover_snapshots(snapshots_dir: Path) -> list[dict]:
    versions = []
    for child in sorted(snapshots_dir.iterdir(), key=lambda p: version_sort_key(p.name)):
        if child.is_dir() and not child.name.startswith('.'):
            if any(child.rglob('*')):
                versions.append({"label": child.name, "files": collect_files(child)})
    return versions


def compute_unified_diff(base_files: dict[str, str], cur_files: dict[str, str]) -> str:
    """Compute a combined unified diff string (git-diff style) for all changed files."""
    all_paths = sorted(set(base_files.keys()) | set(cur_files.keys()))
    parts = []

    for path in all_paths:
        b = base_files.get(path, "")
        c = cur_files.get(path, "")
        if b == c:
            continue

        b_lines = b.splitlines(keepends=True) if b else []
        c_lines = c.splitlines(keepends=True) if c else []

        # Ensure lines end with newline for clean diff
        if b_lines and not b_lines[-1].endswith('\n'):
            b_lines[-1] += '\n'
        if c_lines and not c_lines[-1].endswith('\n'):
            c_lines[-1] += '\n'

        from_path = f"a/{path}" if b else "/dev/null"
        to_path = f"b/{path}" if c else "/dev/null"

        diff_lines = list(difflib.unified_diff(
            b_lines, c_lines,
            fromfile=from_path,
            tofile=to_path,
        ))

        if diff_lines:
            # Add git-style header for diff2html
            parts.append(f"diff --git a/{path} b/{path}")
            if not b:
                parts.append("new file mode 100644")
            elif not c:
                parts.append("deleted file mode 100644")
            parts.extend(line.rstrip('\n') for line in diff_lines)

    return '\n'.join(parts)


def dedup_content(versions: list[dict]) -> dict:
    """Content-addressed dedup for embedding efficiency."""
    blobs: dict[str, str] = {}
    ver_refs = []
    for v in versions:
        refs = {}
        for path, content in v["files"].items():
            h = hashlib.sha256(content.encode()).hexdigest()[:12]
            blobs[h] = content
            refs[path] = h
        ver_refs.append({"label": v["label"], "files": refs})
    return {"blobs": blobs, "versions": ver_refs}


def precompute_diffs(versions: list[dict]) -> dict[str, str]:
    """Pre-compute unified diffs for adjacent version pairs (the common case).

    Returns { "0:1": "diff string", "1:2": "...", ... }
    Other pairs are computed in the browser from blobs on demand.
    """
    diffs = {}
    for i in range(len(versions) - 1):
        key = f"{i}:{i+1}"
        diffs[key] = compute_unified_diff(versions[i]["files"], versions[i+1]["files"])
    # Also precompute first-to-last (common for "total change" view)
    if len(versions) > 2:
        key = f"0:{len(versions)-1}"
        diffs[key] = compute_unified_diff(versions[0]["files"], versions[-1]["files"])
    return diffs


def generate_html(versions: list[dict], skill_name: str = "",
                  default_base: int = 0, default_current: int = -1) -> str:
    if default_current < 0:
        default_current = len(versions) - 1

    deduped = dedup_content(versions)
    pre_diffs = precompute_diffs(versions)

    embedded = {
        "skill_name": skill_name,
        "blobs": deduped["blobs"],
        "versions": deduped["versions"],
        "pre_diffs": pre_diffs,
        "default_base": default_base,
        "default_current": default_current,
    }
    data_json = json.dumps(embedded, ensure_ascii=False)
    return HTML_TEMPLATE.replace("/*__DIFF_DATA__*/", f"const DIFF_DATA = {data_json};")


