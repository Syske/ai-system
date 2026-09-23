#!/usr/bin/env python3
"""
repo-metrics.py — Repository Health Metrics

Collects quantitative metrics about the repository structure and outputs
them as JSON. Designed to be run periodically (weekly) to track health
trends.

Usage:
    python ai-system/tools/repo-metrics.py --repo-root <path>
    python ai-system/tools/repo-metrics.py --repo-root . --json
    python ai-system/tools/repo-metrics.py --repo-root . --snapshot <file>
    python ai-system/tools/repo-metrics.py --repo-root . --compare <file>
"""

import argparse
import json
import re
import sys
from pathlib import Path
from collections import defaultdict


SKILLS_SUBDIR = "skills"
WORKFLOWS_SUBDIR = "workflows"


def _metric(snapshot, section, key):
    """从历史快照取指标；缺字段**明确报错**（R4：原为裸 KeyError）。"""

    value = (snapshot or {}).get(section, {}).get(key)

    if value is None:
        raise SystemExit(
            f"repo-metrics: 历史快照缺少指标 {section}.{key}（快照格式可能已变更）"
        )

    return value


def resolve_root(root):
    """Return the ai-system root regardless of whether repo-root points at
    the workspace (containing ai-system/) or at ai-system/ itself.
    """
    if (root / "ai-system").is_dir():
        return root / "ai-system"
    return root


def count_skills(root):
    """叶子技能计数（口径与 `repo-lint.find_skills` 一致 —— `tools/skill_index.py`）。

    R1 修复（2026-09-21）：原实现计顶层目录 → 把容器目录 `architecture/`
    多计为 1 个技能（33 vs repo-lint 的 32），且漏掉其下 7 个嵌套技能。
    """

    import skill_index

    skills, _containers = skill_index.skill_dirs(root)

    return len(skills), [p.name for p in skills]


def count_workflows(root):
    root = resolve_root(root)
    wf_dir = root / WORKFLOWS_SUBDIR
    if not wf_dir.exists():
        return 0, []
    wfs = sorted([p.name for p in wf_dir.glob("*.md") if p.name != "README.md"])
    return len(wfs), wfs


def count_files_in_dir(directory):
    if not directory.exists():
        return 0
    return len(list(directory.rglob("*")))


EXCLUDED_DIRS = {".venv", "node_modules", "__pycache__", "dist", "build", ".git"}


def _walk(base, suffix=None):
    """Yield files under base, skipping generated/vendor dirs."""
    import os

    for dirpath, dirnames, filenames in os.walk(base):
        dirnames[:] = [
            d for d in dirnames
            if d not in EXCLUDED_DIRS and not d.startswith(".")
        ]
        for name in filenames:
            p = Path(dirpath) / name
            if suffix is None or p.suffix in suffix:
                yield p


def count_md_files(root, subdir):
    d = root / subdir
    if not d.exists():
        return 0
    return len(list(d.rglob("*.md")))


def average_skill_size(root):
    skills_dir = root / SKILLS_SUBDIR
    if not skills_dir.exists():
        return 0
    total_lines = 0
    skill_count = 0
    for skill_dir in skills_dir.iterdir():
        if not skill_dir.is_dir():
            continue
        skill_lines = 0
        for f in _walk(skill_dir, (".md", ".py", ".sh", ".yaml", ".yml")):
            try:
                skill_lines += len(f.read_text(encoding="utf-8").splitlines())
            except Exception:
                pass
        if skill_lines > 0:
            total_lines += skill_lines
            skill_count += 1
    return round(total_lines / skill_count) if skill_count > 0 else 0


def get_frontmatter_quality(root):
    skills_dir = root / SKILLS_SUBDIR
    if not skills_dir.exists():
        return {"valid": 0, "missing": 0, "no_desc": 0}

    valid = 0
    missing = 0
    no_desc = 0

    for skill_dir in skills_dir.iterdir():
        if not skill_dir.is_dir():
            continue
        for name in ("skill.md", "SKILL.md"):
            path = skill_dir / name
            if path.exists():
                content = path.read_text(encoding="utf-8")
                if re.match(r"^---\s*\n.*?\n---", content, re.DOTALL):
                    valid += 1
                    if "description:" not in content:
                        no_desc += 1
                else:
                    missing += 1
                break
        else:
            missing += 1

    return {"valid": valid, "missing": missing, "no_desc": no_desc}


def get_skill_sizes(root):
    skills_dir = root / SKILLS_SUBDIR
    if not skills_dir.exists():
        return {}

    sizes = {}
    for skill_dir in sorted(skills_dir.iterdir()):
        if not skill_dir.is_dir():
            continue
        total_lines = 0
        for f in _walk(skill_dir, (".md", ".py", ".sh", ".yaml", ".yml")):
            try:
                total_lines += len(f.read_text(encoding="utf-8").splitlines())
            except Exception:
                pass
        if total_lines > 0:
            sizes[skill_dir.name] = total_lines

    return sizes


def collect_metrics(root):
    root = resolve_root(root)
    n_skills, skill_names = count_skills(root)
    n_workflows, wf_names = count_workflows(root)

    return {
        "timestamp": __import__("datetime").datetime.now().isoformat(),
        "skills": {
            "count": n_skills,
            "names": skill_names,
            "sizes": get_skill_sizes(root),
            "average_size_lines": average_skill_size(root),
        },
        "workflows": {
            "count": n_workflows,
            "names": wf_names,
        },
        "rfc": {
            "count": count_md_files(root, "rfc"),
        },
        "governance": {
            "count": count_md_files(root, "governance"),
        },
        "templates": {
            "count": count_md_files(root, "templates"),
        },
        "quality": {
            "frontmatter": get_frontmatter_quality(root),
        },
    }


def main():
    parser = argparse.ArgumentParser(description="Repository Health Metrics")
    parser.add_argument("--repo-root", required=True, help="Repository root directory")
    parser.add_argument("--json", action="store_true", help="Output JSON")
    parser.add_argument("--snapshot", type=str, help="Save snapshot to file")
    parser.add_argument("--compare", type=str, help="Compare with snapshot file")
    args = parser.parse_args()

    root = Path(args.repo_root).resolve()
    if not root.exists():
        print(f"Error: {root} does not exist", file=sys.stderr)
        sys.exit(1)

    metrics = collect_metrics(root)

    if args.snapshot:
        with open(args.snapshot, "w", encoding="utf-8") as f:
            json.dump(metrics, f, indent=2)
        print(f"Snapshot saved to {args.snapshot}")

    if args.compare:
        with open(args.compare, "r", encoding="utf-8") as f:
            previous = json.load(f)
        deltas = {
            # R4：快照缺字段时给出明确错误，而非裸 KeyError
            "skills_delta": metrics["skills"]["count"] - _metric(previous, "skills", "count"),
            "avg_size_delta": (
                metrics["skills"]["average_size_lines"]
                - _metric(previous, "skills", "average_size_lines")
            ),
        }
        if args.json:
            print(json.dumps({"current": metrics, "previous": previous, "deltas": deltas}, indent=2))
        else:
            print(f"\nMetrics Comparison")
            print(f"{'='*60}")
            print(f"Skills: {_metric(previous, 'skills', 'count')} → {metrics['skills']['count']} ({deltas['skills_delta']:+d})")
            print(f"Avg size: {_metric(previous, 'skills', 'average_size_lines')} → {metrics['skills']['average_size_lines']} ({deltas['avg_size_delta']:+d})")
    else:
        if args.json:
            print(json.dumps(metrics, indent=2))
        else:
            print(f"\nRepository Metrics")
            print(f"{'='*60}")
            print(f"Skills:           {metrics['skills']['count']}")
            print(f"  Avg size:       {metrics['skills']['average_size_lines']} lines")
            if metrics['skills']['sizes']:
                print(f"  Largest:        {max(metrics['skills']['sizes'].values())} lines")
            print(f"Workflows:        {metrics['workflows']['count']}")
            print(f"RFCs:             {metrics['rfc']['count']}")
            print(f"Governance:       {metrics['governance']['count']}")
            print(f"Templates:        {metrics['templates']['count']}")
            print(f"Frontmatter:      {metrics['quality']['frontmatter']['valid']} valid, "
                  f"{metrics['quality']['frontmatter']['missing']} missing")


if __name__ == "__main__":
    main()
