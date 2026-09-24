"""Skill discovery for the skill launcher.

Scans, in priority order:

1. The config-driven extensions root (`layers.skills` in the merged environment config —
   machine layer ~/.config/ai-system/env.yaml first, optional workspace layer
   config/environments/{env}.yaml second; default `{workspace_root}/extensions`).
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
from cli.services.frontmatter import FRONTMATTER_RE, read_frontmatter

FRONTMATTER_NAME = re.compile(r"^name:\s*(.+?)\s*$", re.MULTILINE)
FRONTMATTER_DESC = re.compile(r"^description:\s*(.+?)\s*$", re.MULTILINE)

LOCAL_SUBDIRS = (
    ".opencode/skills",
    ".claude/skills",
    ".agents/skills",
)


def _realpath(path):

    return Path(os.path.realpath(path))


def _single_line_field(text, key):
    """Single-line frontmatter field (usage / trigger), regex fallback."""

    m = re.search(
        rf"^{key}:\s*(.+)$",
        text,
        re.MULTILINE | re.IGNORECASE
    )

    if not m:
        return ""

    value = m.group(1).strip().strip("'\"")

    return re.sub(r"\s+", " ", value)


def _read_frontmatter(skill_path):
    """Parse a SKILL.md frontmatter.

    Uses the shared YAML parser (cli/services/frontmatter.py, P25) so folded
    / literal block scalars (`description: >` / `description: |`) resolve to
    their real text instead of the `>` / `|` marker (2026-09-11: four
    extensions skills showed `— >` in the aic-skill menu). Falls back to the
    legacy single-line regexes for files without a frontmatter block.

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

    data, _ = read_frontmatter(text)

    if not isinstance(data, dict):
        data = {}

    # R2 修复：回退检索**限定在 frontmatter 块内** —— 原实现对整文件 search，
    # 正文里出现 `name:` 行会被误取为技能名。
    block = FRONTMATTER_RE.match(text)
    head = block.group(1) if block else ""

    name = str(data.get("name") or "").strip()

    if not name:

        m = FRONTMATTER_NAME.search(head)

        if m:
            name = m.group(1).strip()

    desc = str(data.get("description") or "").strip()

    if not desc:

        m = FRONTMATTER_DESC.search(head)

        if m:
            desc = m.group(1).strip().strip("'\"")

    desc = re.sub(r"\s+", " ", desc)

    return {
        "name": name or skill_path.parent.name,
        "description": desc,
        "usage": _single_line_field(text, "usage"),
        "trigger": _single_line_field(text, "triggers?"),
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


def _skill_roots(root, environment):
    """Config-driven skill source dirs (skill-groups.yaml → `skill_roots`).

    Placeholders: `{ai_system_root}` → the ai-system root passed in,
    `{workspace_root}` → its parent. `extensions` falls back to the
    environment's `layers.skills` when not configured (per-env flexibility).
    Returns {source: dir} in config order.
    """

    roots = {}

    try:

        from cli.utils.yaml import load_yaml

        root_path = Path(root)

        cfg = load_yaml(
            root_path / "config" / "skill-groups.yaml"
        ) or {}

        for source, raw in (cfg.get("skill_roots") or {}).items():

            raw = str(raw)

            raw = raw.replace(
                "{ai_system_root}",
                str(root_path)
            ).replace(
                "{workspace_root}",
                str(root_path.parent)
            )

            roots[source] = raw

    except Exception:

        pass

    if "extensions" not in roots:
        roots["extensions"] = env.skills_root(
            root,
            environment
        )

    return roots


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
    source is one of the configured `skill_roots` keys (core / extensions /
    ...) plus the built-in "global" | "local".
    """

    environment = environment or env.DEFAULT_ENV

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

    # 配置驱动来源（skill-groups.yaml → skill_roots）：先按配置顺序扫 core /
    # extensions 等已登记目录；extensions 未登记时回退环境 layers.skills。
    for source, source_root in _skill_roots(
        root,
        environment
    ).items():

        for name, meta, path in _skills_in(source_root):
            add(meta, path, source)

    # 内置源（平台标准路径）：global = ~/.agents/skills
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

        # R2 修复：**无 git 根时不上行** —— 原实现会逐级走到文件系统根，
        # 在每一层探测 `{rel}/skills`（大目录树上代价高且结果不可预期）。
        # 有 git 根时仍按原语义上溯至 git 根。
        ascend = git_root is not None

        while True:

            for rel in LOCAL_SUBDIRS:

                for name, meta, path in _skills_in(walker / rel):
                    add(meta, path, "local")

            if not ascend or walker.parent == walker:
                break

            walker = walker.parent

            if git_root is not None and walker == git_root.parent:
                break

    return results
