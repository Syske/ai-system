"""Coding memory structure, format, language, and duplication checks."""

import re
from pathlib import Path

from .base import ROOT

MEMORY_ROOT = ROOT / "governance" / "memory"

MEMORY_INDEX = "governance/memory/coding-memory.md"

CJK_RE = re.compile(r"[\u4e00-\u9fff]")

MEMORY_REQUIRED = ("Lesson",)
MEMORY_RECOMMENDED = ("Context", "Problem", "Solution", "Scope")


def language_violations(files=None):
    """Return [(rel_path, cjk_count)] for memory files carrying CJK.

    Single source for the "AI System memory must be English" rule, shared by
    check.py (full scan) and the pre-commit gate (staged subset).

    Only the ROOT INDEX (`governance/memory/coding-memory.md`) is exempt —
    topic-level files (e.g. `governance/memory/java/coding-memory.md`) carry
    lesson content and MUST be English. (Bug fixed 2026-09-21: the previous
    by-filename exemption let every topic-level `coding-memory.md` through.)
    """

    if files is None:
        candidates = sorted(MEMORY_ROOT.rglob("*.md"))
    else:
        candidates = []
        for f in files:
            p = Path(f)
            if not p.is_absolute():
                p = ROOT / p
            candidates.append(p)

    out = []

    for p in candidates:

        try:
            rel = p.relative_to(ROOT).as_posix()
        except ValueError:
            continue

        if not rel.startswith("governance/memory/"):
            continue

        if rel == MEMORY_INDEX:
            continue

        if p.suffix != ".md" or not p.is_file():
            continue

        try:
            text = p.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue

        cjk = len(CJK_RE.findall(text))

        if cjk:
            out.append((rel, cjk))

    return out


def check_memory(c):
    """Validate governance/memory structure, entry format, and index.

    - Entry files (contain `## [Category]`) must include required fields.
    - The root index (coding-memory.md) must be an index only and only
      reference existing paths.
    - AI System memory must stay English (AI-internal layer).
    - Lesson lines are scanned for cross-file duplication (warning).
    """

    root = MEMORY_ROOT

    if not root.exists():
        return

    lessons = []

    for md in sorted(root.rglob("*.md")):

        rel = md.relative_to(ROOT).as_posix()

        is_index = rel == "governance/memory/coding-memory.md"

        text = md.read_text(encoding="utf-8")

        entries = re.findall(
            r"## \[[^\]]+\].+?(?=\n## |\Z)",
            text,
            re.S
        )

        if is_index:

            if entries:
                c.error(
                    f"memory index {rel}: contains entries; "
                    "coding-memory.md must be an index only"
                )

            for ref in re.findall(
                r"governance/memory/[a-zA-Z0-9_./-]+\.md",
                text
            ):
                if not (ROOT / ref).exists():
                    c.error(
                        f"memory index {rel}: references "
                        f"missing '{ref}'"
                    )

            continue

        for entry in entries:

            fields = set(
                re.findall(r"^([A-Z][A-Za-z ]+):$", entry, re.M)
            )

            for req in MEMORY_REQUIRED:
                if req not in fields:
                    c.error(
                        f"memory {rel}: entry missing "
                        f"required field '{req}'"
                    )

            for rec in MEMORY_RECOMMENDED:
                if rec not in fields:
                    c.warn(
                        f"memory {rel}: entry missing "
                        f"recommended field '{rec}'"
                    )

            lesson = re.search(r"^Lesson:\s*\n\s*(.+)", entry, re.M)

            if lesson:
                lessons.append((rel, lesson.group(1).strip().lower()))

    for rel, cjk in language_violations():

        c.error(
            f"memory {rel}: AI System memory must be English "
            f"({cjk} CJK chars)"
        )

    dup = _find_duplicate_lessons(lessons)

    for group in dup:
        c.warn(
            "memory: similar Lesson across files "
            f"{', '.join(g for g, _ in group)}"
        )


def _find_duplicate_lessons(lessons):
    groups = []

    for i, (rel, text) in enumerate(lessons):

        seen = False

        for g in groups:
            for _, other in g:
                if _similar(text, other):
                    g.append((rel, text))
                    seen = True
                    break
            if seen:
                break

        if not seen:
            groups.append([(rel, text)])

    return [g for g in groups if len(g) > 1]


def _similar(a, b, ratio=0.8):
    if not a or not b:
        return False
    a_tokens = set(a.split())
    b_tokens = set(b.split())
    union = a_tokens | b_tokens
    if not union:
        return False
    jaccard = len(a_tokens & b_tokens) / len(union)
    return jaccard >= ratio
