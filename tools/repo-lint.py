#!/usr/bin/env python3
"""
repo-lint.py — Repository Governance Linter

Checks the entire ai-system structure against RFC-0001, RFC-0002, and
RFC-0003. Reports BLOCKERs, ERRORs, WARNINGs, and INFOs.

Usage:
    python repo-lint.py --repo-root <path>
    python repo-lint.py --repo-root . --json     # JSON output
    python repo-lint.py --repo-root . --verbose  # Detailed output

Exit codes:
    0 = passed (may have warnings/infos)
    1 = errors found
    2 = blockers found
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path


SKILLS_SUBDIR = "ai-system/skills"


def find_skills(root):
    skills_dir = root / SKILLS_SUBDIR
    if not skills_dir.exists():
        return []
    return sorted(
        [d for d in skills_dir.iterdir() if d.is_dir() and not d.name.startswith(".")]
    )


def find_entrypoint(skill_dir):
    for name in ("skill.md", "SKILL.md"):
        path = skill_dir / name
        if path.exists():
            return path
    return None


def read_file(path):
    try:
        return path.read_text(encoding="utf-8")
    except Exception:
        return ""


def count_lines(path):
    try:
        return len(path.read_text(encoding="utf-8").splitlines())
    except Exception:
        return 0


class Results:
    def __init__(self):
        self.blockers = []
        self.errors = []
        self.warnings = []
        self.infos = []
        self.files_checked = 0

    def blocker(self, msg, file=None):
        self.blockers.append({"severity": "BLOCKER", "message": msg, "file": file})

    def error(self, msg, file=None):
        self.errors.append({"severity": "ERROR", "message": msg, "file": file})

    def warning(self, msg, file=None):
        self.warnings.append({"severity": "WARNING", "message": msg, "file": file})

    def info(self, msg, file=None):
        self.infos.append({"severity": "INFO", "message": msg, "file": file})

    @property
    def passed(self):
        return len(self.blockers) == 0 and len(self.errors) == 0

    def to_dict(self):
        return {
            "passed": self.passed,
            "blockers": self.blockers,
            "errors": self.errors,
            "warnings": self.warnings,
            "infos": self.infos,
            "summary": {
                "skills_checked": 0,
                "files_checked": self.files_checked,
                "blockers": len(self.blockers),
                "errors": len(self.errors),
                "warnings": len(self.warnings),
                "infos": len(self.infos),
            },
        }


def check_frontmatter(skill_dir, results):
    entrypoint = find_entrypoint(skill_dir)
    if entrypoint is None:
        results.blocker(f"No skill.md or SKILL.md found", file=str(skill_dir))
        return None

    results.files_checked += 1
    content = read_file(entrypoint)

    m = re.match(r"^---\s*\n(.*?)\n---", content, re.DOTALL)
    if not m:
        results.blocker(f"No YAML frontmatter in {entrypoint.name}", file=str(entrypoint))
        return None

    frontmatter = m.group(1)
    name_m = re.search(r"^name:\s*(\S+)", frontmatter, re.MULTILINE)
    if not name_m:
        results.blocker(f"Missing 'name:' in frontmatter", file=str(entrypoint))
    else:
        skill_name = name_m.group(1)
        dir_name = skill_dir.name
        if skill_name != dir_name:
            results.error(
                f"name '{skill_name}' does not match directory '{dir_name}'",
                file=str(entrypoint),
            )

    desc_m = re.search(r"^description:\s*>\s*\n(.*?)(?=\n\S|^---)", frontmatter, re.MULTILINE | re.DOTALL)
    if not desc_m:
        results.error(f"Missing 'description:' in frontmatter", file=str(entrypoint))
    else:
        desc = desc_m.group(1).strip()
        desc_len = len(desc)
        if desc_len < 100:
            results.error(f"Description too short: {desc_len} chars (min 100)", file=str(entrypoint))
        elif desc_len > 1024:
            results.error(f"Description too long: {desc_len} chars (max 1024)", file=str(entrypoint))
        else:
            results.info(f"Description: {desc_len} chars (OK)", file=str(entrypoint))

    return entrypoint


def check_skill_size(skill_dir, results):
    total = 0
    for f in skill_dir.rglob("*"):
        if f.is_file() and f.suffix in (".md", ".py", ".sh", ".yaml", ".yml"):
            total += count_lines(f)
    if total > 1000:
        results.error(f"Skill exceeds 1000 lines: {total} lines", file=str(skill_dir))
    return total


def check_prohibited_content(skill_dir, skill_name, results):
    if skill_name == "java-maven":
        return

    for f in skill_dir.rglob("*.md"):
        content = read_file(f)
        lines = content.splitlines()
        for i, line in enumerate(lines):
            if re.search(r"\bmvn\s+(clean|compile|test|package|verify|install|deploy)\b", line):
                if "java-maven" not in content and "playbooks/maven" not in content:
                    results.warning(
                        f"Maven command on line {i+1}: '{line.strip()[:60]}'",
                        file=str(f),
                    )
                    break
        for i, line in enumerate(lines):
            if re.search(r'["\']/[A-Za-z]/|["\']C:\\|["\']/home/|["\']/usr/|["\']/workspace/', line):
                results.warning(
                    f"Possible hardcoded path on line {i+1}: '{line.strip()[:60]}'",
                    file=str(f),
                )
                break


def check_workflow_stages(skill_dir, results):
    wf_path = skill_dir / "workflow.md"
    if not wf_path.exists():
        entrypoint = find_entrypoint(skill_dir)
        if entrypoint and count_lines(entrypoint) > 80:
            results.warning(
                f"skill.md is {count_lines(entrypoint)} lines but no workflow.md found",
                file=str(entrypoint),
            )
        return

    content = read_file(wf_path)
    stages = re.findall(r"^### Stage \d+", content, re.MULTILINE)
    if len(stages) < 3:
        results.error(f"Only {len(stages)} workflow stages found (minimum 3)", file=str(wf_path))

    stage_blocks = re.split(r"^### Stage \d+", content, re.MULTILINE)[1:]
    for i, block in enumerate(stage_blocks):
        if "**Goal:**" not in block:
            results.warning(f"Stage {i+1} missing **Goal:** section", file=str(wf_path))
        if "**Steps:**" not in block:
            results.warning(f"Stage {i+1} missing **Steps:** section", file=str(wf_path))
        if "**Output:**" not in block:
            results.warning(f"Stage {i+1} missing **Output:** section", file=str(wf_path))


def main():
    parser = argparse.ArgumentParser(description="Repository Governance Linter")
    parser.add_argument("--repo-root", required=True, help="Repository root directory")
    parser.add_argument("--json", action="store_true", help="Output JSON")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")
    args = parser.parse_args()

    root = Path(args.repo_root).resolve()
    if not root.exists():
        print(f"Error: {root} does not exist", file=sys.stderr)
        sys.exit(2)

    results = Results()
    skills = find_skills(root)

    for skill_dir in skills:
        entrypoint = check_frontmatter(skill_dir, results)
        if entrypoint:
            skill_name = skill_dir.name
            check_skill_size(skill_dir, results)
            check_prohibited_content(skill_dir, skill_name, results)
            check_workflow_stages(skill_dir, results)

    if args.json:
        print(json.dumps(results.to_dict(), indent=2))
    elif args.verbose:
        print(f"\nRepository Lint Report")
        print(f"{'='*60}")
        print(f"Skills checked: {len(skills)}")
        print(f"Files checked:  {results.files_checked}")
        print("")
        for item in results.blockers + results.errors + results.warnings + results.infos:
            tag = item["severity"].ljust(8)
            loc = f" [{item['file']}]" if item["file"] else ""
            print(f"  [{tag}] {item['message']}{loc}")
        print(f"\nSummary: {len(results.blockers)} blockers, {len(results.errors)} errors, "
              f"{len(results.warnings)} warnings, {len(results.infos)} infos")
    else:
        print(f"Skills: {len(skills)} | Files: {results.files_checked} | "
              f"BLOCKERS: {len(results.blockers)} | ERRORS: {len(results.errors)} | "
              f"WARNINGS: {len(results.warnings)}")
        if results.blockers:
            for b in results.blockers:
                print(f"  [BLOCKER] {b['message']}")
        if results.errors:
            for e in results.errors:
                print(f"  [ERROR] {e['message']}")

    if results.blockers:
        sys.exit(2)
    elif results.errors:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
