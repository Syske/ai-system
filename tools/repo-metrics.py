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


SKILLS_SUBDIR = "ai-system/skills"
WORKFLOWS_SUBDIR = "ai-system/workflows"


def count_skills(root):
    skills_dir = root / SKILLS_SUBDIR
    if not skills_dir.exists():
        return 0, []
    skills = sorted([d.name for d in skills_dir.iterdir() if d.is_dir()])
    return len(skills), skills


def count_workflows(root):
    wf_dir = root / WORKFLOWS_SUBDIR
    if not wf_dir.exists():
        return 0, []
    wfs = sorted([d.name for d in wf_dir.iterdir() if d.is_dir()])
    return len(wfs), wfs


def count_files_in_dir(directory):
    if not directory.exists():
        return 0
    return len(list(directory.rglob("*")))


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
        for f in skill_dir.rglob("*"):
            if f.is_file() and f.suffix in (".md", ".py", ".sh"):
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
        for f in skill_dir.rglob("*"):
            if f.is_file() and f.suffix in (".md", ".py", ".sh"):
                try:
                    total_lines += len(f.read_text(encoding="utf-8").splitlines())
                except Exception:
                    pass
        if total_lines > 0:
            sizes[skill_dir.name] = total_lines

    return sizes


def collect_metrics(root):
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
            "count": count_md_files(root, "ai-system/rfc"),
        },
        "governance": {
            "count": count_md_files(root, "ai-system/governance"),
        },
        "templates": {
            "count": count_md_files(root, "ai-system/templates"),
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
            "skills_delta": metrics["skills"]["count"] - previous["skills"]["count"],
            "avg_size_delta": metrics["skills"]["average_size_lines"] - previous["skills"]["average_size_lines"],
        }
        if args.json:
            print(json.dumps({"current": metrics, "previous": previous, "deltas": deltas}, indent=2))
        else:
            print(f"\nMetrics Comparison")
            print(f"{'='*60}")
            print(f"Skills: {previous['skills']['count']} → {metrics['skills']['count']} ({deltas['skills_delta']:+d})")
            print(f"Avg size: {previous['skills']['average_size_lines']} → {metrics['skills']['average_size_lines']} ({deltas['avg_size_delta']:+d})")
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
