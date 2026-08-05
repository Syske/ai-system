"""Skill discovery for the skill launcher.

Scans, in priority order:

1. The config-driven extensions root (`layers.skills` in
   config/environments/{env}.yaml, default `{workspace_root}/extensions`).
   Company/platform skills live here and are NOT auto-discovered by agents
   (the dir name `extensions` is outside the `skills`/`.claude/skills`/
   `.agents/skills` discovery paths) — the launcher loads them explicitly.
2. Global skill root `~/.agents/skills` (shared by opencode and pi).
3. Project-local roots: walk from CWD up to the git worktree root, scanning
   `.opencode/skills`, `.claude/skills`, `.agents/skills`.

Entries are deduplicated by realpath so symlinked roots (e.g.
`~/.config/opencode/skills` → `~/.agents/skills`) produce one entry each.
"""

import os
import re
import subprocess
from pathlib import Path

from cli.services import environment as env

FRONTMATTER_NAME = re.compile(r"^name:\s*(.+?)\s*$", re.MULTILINE)
FRONTMATTER_DESC = re.compile(r"^description:\s*(.+?)\s*$", re.MULTILINE)

LOCAL_SUBDIRS = (
    ".opencode/skills",
    ".claude/skills",
    ".agents/skills",
)


def _realpath(path):

    return Path(os.path.realpath(path))


def _read_frontmatter(skill_path):
    """Parse a SKILL.md frontmatter.

    Returns a dict with at least name/description; includes usage and
    trigger lines when present (for detail preview).
    """

    try:

        text = skill_path.read_text(encoding="utf-8")

    except OSError:

        return {
            "name": skill_path.parent.name,
            "description": "",
            "usage": "",
            "trigger": "",
        }

    name = None

    m = FRONTMATTER_NAME.search(text)

    if m:
        name = m.group(1).strip()

    desc = ""

    m = FRONTMATTER_DESC.search(text)

    if m:
        desc = m.group(1).strip().strip("'\"")
        desc = re.sub(r"\s+", " ", desc)

    usage = ""

    um = re.search(
        r"^usage:\s*(.+)$",
        text,
        re.MULTILINE | re.IGNORECASE
    )

    if um:
        usage = um.group(1).strip().strip("'\"")
        usage = re.sub(r"\s+", " ", usage)

    trigger = ""

    tm = re.search(
        r"^trigger[s]?:\s*(.+)$",
        text,
        re.MULTILINE | re.IGNORECASE
    )

    if tm:
        trigger = tm.group(1).strip().strip("'\"")
        trigger = re.sub(r"\s+", " ", trigger)

    return {
        "name": name or skill_path.parent.name,
        "description": desc,
        "usage": usage,
        "trigger": trigger,
    }


def _skills_in(root):
    """Yield skill metadata dicts for skills directly under root."""

    root = _realpath(root)

    if not root.is_dir():
        return

    seen_names = set()

    for child in sorted(root.iterdir()):

        if not child.is_dir():
            continue

        skill_md = child / "SKILL.md"

        if not skill_md.exists():
            continue

        meta = _read_frontmatter(skill_md)

        name = meta["name"]

        if name in seen_names:
            continue

        seen_names.add(name)

        yield meta["name"], meta, str(skill_md)


def _git_root(start):
    """Return the git worktree root for CWD (or None)."""

    try:

        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            cwd=str(start),
            capture_output=True,
            text=True,
            timeout=10
        )

        if result.returncode != 0:
            return None

        return Path(result.stdout.strip())

    except Exception:

        return None


def scan(root, environment=None, include_local=True):
    """Scan all skill sources.

    Returns a list of dicts:
    {name, description, usage, trigger, path, source}.
    source is one of "extensions" | "global" | "local".
    """

    environment = environment or env.DEFAULT_ENV

    skills_root = env.skills_root(
        root,
        environment
    )

    seen = set()

    results = []

    def add(meta, path, source):

        key = (meta["name"], _realpath(path))

        if key in seen:
            return

        seen.add(key)

        results.append({
            "name": meta["name"],
            "description": meta["description"],
            "usage": meta.get("usage", ""),
            "trigger": meta.get("trigger", ""),
            "path": path,
            "source": source,
        })

    for name, meta, path in _skills_in(skills_root):
        add(meta, path, "extensions")

    home = Path.home()

    global_root = home / ".agents" / "skills"

    for name, meta, path in _skills_in(global_root):
        add(meta, path, "global")

    if include_local:

        start = root

        git_root = _git_root(start)

        if git_root is not None:

            start = git_root

        walker = start

        while True:

            for rel in LOCAL_SUBDIRS:

                for name, meta, path in _skills_in(walker / rel):
                    add(meta, path, "local")

            if walker.parent == walker:
                break

            walker = walker.parent

            if git_root is not None and walker == git_root.parent:
                break

    return results
