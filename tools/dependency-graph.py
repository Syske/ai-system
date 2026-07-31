#!/usr/bin/env python3
"""
dependency-graph.py — Skill Dependency Graph Generator

Analyzes Skill-to-Skill references and generates:
  - Text-based dependency tree
  - JSON dependency data (for tooling)
  - DOT format graph (for Graphviz visualization)

Usage:
    python ai-system/tools/dependency-graph.py --repo-root .
    python ai-system/tools/dependency-graph.py --repo-root . --format dot
    python ai-system/tools/dependency-graph.py --repo-root . --format json
    python ai-system/tools/dependency-graph.py --repo-root . --format text (default)
"""

import argparse
import json
import re
import sys
from pathlib import Path
from collections import defaultdict


SKILLS_SUBDIR = "ai-system/skills"


def find_skills(root):
    skills_dir = root / SKILLS_SUBDIR
    if not skills_dir.exists():
        return {}
    skills = {}
    for d in sorted(skills_dir.iterdir()):
        if d.is_dir():
            name = d.name
            entry = d / "skill.md"
            if not entry.exists():
                entry = d / "SKILL.md"
            skills[name] = {
                "path": str(d),
                "entrypoint": str(entry) if entry.exists() else None,
                "lines": 0,
            }
    return skills


def extract_references(skill_name, root):
    skill_dir = root / SKILLS_SUBDIR / skill_name
    if not skill_dir.exists():
        return set()

    refs = set()
    all_skills = find_skills(root)

    for f in skill_dir.rglob("*.md"):
        if not f.is_file():
            continue
        content = f.read_text(encoding="utf-8", errors="ignore")

        for m in re.finditer(r"delegates?\s+to[:\s]+([a-z][a-z0-9-]+)", content, re.IGNORECASE):
            candidate = m.group(1).lower()
            if candidate in all_skills and candidate != skill_name:
                refs.add((candidate, "delegates_to"))

        for m in re.finditer(r"``\s*([a-z][a-z0-9-]+)\s*``|`([a-z][a-z0-9-]+)`", content):
            candidate = (m.group(1) or m.group(2)).lower()
            if candidate in all_skills and candidate != skill_name:
                refs.add((candidate, "references"))

        for m in re.finditer(r"[Ii]nvoke\s+`?([a-z][a-z0-9-]+)`?", content):
            candidate = m.group(1).lower()
            if candidate in all_skills and candidate != skill_name:
                refs.add((candidate, "invokes"))

    return refs


def get_skill_layers(root):
    skills = find_skills(root)
    layers = defaultdict(list)

    for name in skills:
        entry = skills[name]["entrypoint"]
        if not entry:
            layers["unknown"].append(name)
            continue

        content = Path(entry).read_text(encoding="utf-8", errors="ignore").lower()

        if "orchestrates" in content or "delegates to" in content:
            if any(x in content for x in ["openspec", "spec-updater", "contract"]):
                layers["3-orchestration"].append(name)
            else:
                layers["3-orchestration"].append(name)
        elif "mock" in content or "test" in content or "fixture" in content:
            layers["2-test"].append(name)
        elif "maven" in content or "codegraph" in content or "coding" in content:
            layers["1-foundation"].append(name)
        elif "openspec" in name or "spec" in name or "contract" in name or "task" in name:
            layers["2-openspec"].append(name)
        elif "skill" in name:
            layers["meta"].append(name)
        else:
            layers["unknown"].append(name)

    return dict(layers)


def detect_cycles(skills, edges):
    visited = set()
    recursion_stack = set()
    cycles = []

    def dfs(node, path):
        visited.add(node)
        recursion_stack.add(node)

        for target, _ in edges[node]:
            if target not in visited:
                if dfs(target, path + [target]):
                    return True
            elif target in recursion_stack:
                cycle_path = path[path.index(target):]
                cycles.append(" → ".join(cycle_path + [target]))
                return True
        recursion_stack.remove(node)
        return False

    for skill in skills:
        if skill not in visited:
            dfs(skill, [skill])

    return cycles


def generate_text_graph(root, skills, edges, layers):
    lines = []
    lines.append("Skill Dependency Graph")
    lines.append("=" * 60)
    lines.append("")

    layer_order = ["1-foundation", "2-test", "2-openspec", "3-orchestration", "meta", "unknown"]
    layer_names = {
        "1-foundation": "Layer 1 — Foundation",
        "2-test": "Layer 2 — Test",
        "2-openspec": "Layer 2 — OpenSpec",
        "3-orchestration": "Layer 3 — Orchestration",
        "meta": "Layer 4 — Meta",
        "unknown": "Unclassified",
    }

    for layer in layer_order:
        if layer not in layers:
            continue
        label = layer_names.get(layer, layer)
        lines.append(f"\n  {label}")
        lines.append(f"  {'─' * 40}")
        for skill in sorted(layers[layer]):
            refs = edges.get(skill, [])
            if refs:
                dep_str = ", ".join(sorted(set(r for r, _ in refs)))
                lines.append(f"  {skill}  →  [{dep_str}]")
            else:
                lines.append(f"  {skill}  (standalone)")

    cycles = detect_cycles(list(skills.keys()), edges)
    if cycles:
        lines.append(f"\n\n  ⚠ CYCLES DETECTED:")
        for c in cycles:
            lines.append(f"    {c}")

    lines.append("")
    return "\n".join(lines)


def generate_dot(root, skills, edges):
    lines = []
    lines.append("digraph repository {")
    lines.append('  rankdir="LR";')
    lines.append('  node [shape=box, style=rounded];')
    lines.append("")

    for name in sorted(skills.keys()):
        lines.append(f'  "{name}";')

    lines.append("")
    seen = set()
    for source, targets in edges.items():
        for target, rel_type in targets:
            edge = (source, target)
            if edge not in seen:
                lines.append(f'  "{source}" -> "{target}";')
                seen.add(edge)

    lines.append("}")
    return "\n".join(lines)


def generate_json(skills, edges, layers, cycles):
    data = {
        "skills": list(skills.keys()),
        "layers": layers,
        "dependencies": {},
        "cycles": cycles,
    }
    for source, targets in edges.items():
        data["dependencies"][source] = sorted(set(t for t, _ in targets))
    return json.dumps(data, indent=2)


def main():
    parser = argparse.ArgumentParser(description="Skill Dependency Graph Generator")
    parser.add_argument("--repo-root", required=True, help="Repository root directory")
    parser.add_argument("--format", choices=["text", "dot", "json"], default="text",
                        help="Output format")
    args = parser.parse_args()

    root = Path(args.repo_root).resolve()
    if not root.exists():
        print(f"Error: {root} does not exist", file=sys.stderr)
        sys.exit(1)

    skills = find_skills(root)
    edges = {}
    for name in skills:
        refs = extract_references(name, root)
        edges[name] = refs

    layers = get_skill_layers(root)
    cycles = detect_cycles(list(skills.keys()), edges)

    if args.format == "text":
        print(generate_text_graph(root, skills, edges, layers))
    elif args.format == "dot":
        print(generate_dot(root, skills, edges))
    elif args.format == "json":
        print(generate_json(skills, edges, layers, cycles))

    if cycles:
        sys.exit(1)


if __name__ == "__main__":
    main()
