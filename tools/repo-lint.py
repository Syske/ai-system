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
import subprocess
import sys
from pathlib import Path


SKILLS_SUBDIR = "skills"

EXCLUDED_DIRS = {".venv", "node_modules", "__pycache__", "dist", "build", ".git"}


def walk_skill_files(skill_dir, suffix=None):
    """Yield files under a skill dir, skipping generated/vendor dirs."""
    import os

    for dirpath, dirnames, filenames in os.walk(skill_dir):
        dirnames[:] = [
            d for d in dirnames
            if d not in EXCLUDED_DIRS and not d.startswith(".")
        ]
        for name in filenames:
            p = Path(dirpath) / name
            if suffix is None or p.suffix in suffix:
                yield p


def resolve_root(root):
    """Return the ai-system root regardless of whether repo-root points at
    the workspace (containing ai-system/) or at ai-system/ itself.
    """
    if (root / "ai-system").is_dir():
        return root / "ai-system"
    return root


def find_skills(root):
    root = resolve_root(root)
    skills_dir = root / SKILLS_SUBDIR
    if not skills_dir.exists():
        return []
    skills = []
    for d in sorted(skills_dir.iterdir()):
        if not d.is_dir() or d.name.startswith("."):
            continue
        # Container dirs (only nested skill dirs, no own SKILL.md) are not skills.
        if find_entrypoint(d) is None and any(p.is_dir() for p in d.iterdir()):
            continue
        skills.append(d)
    return skills


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

    desc_m = re.search(
        r"^description:\s*(?:\>\s*\n)?\s*(.+)",
        frontmatter,
        re.MULTILINE | re.DOTALL
    )
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
    # Per-file limit: a single file over 1000 lines is a problem;
    # aggregated docs across many reference files are not. Script files
    # (.py/.cjs/.sh) are checked too (S1: closes the lint blind spot that
    # let skill-optimizer's scripts exceed the RFC-0002 per-file budget).
    max_lines = 0
    max_file = None
    for f in walk_skill_files(skill_dir, (".md", ".yaml", ".yml", ".py", ".cjs", ".sh")):
        n = count_lines(f)
        if n > max_lines:
            max_lines = n
            max_file = f
    if max_lines > 1000:
        results.error(
            f"File exceeds 1000 lines: {max_lines} lines ({max_file.name})",
            file=str(skill_dir),
        )
    return max_lines


def check_prohibited_content(skill_dir, skill_name, results):
    # RFC-0002: no Maven command literals outside java-maven (P17).
    # Matches ANY bare `mvn` word, not just `mvn <goal>` — and there is no
    # per-file exemption: mentioning "java-maven" does not legalize command
    # literals. Skills must delegate via prose ("Delegate to java-maven:").
    if skill_name == "java-maven":
        return

    for f in walk_skill_files(skill_dir, (".md",)):
        content = read_file(f)
        lines = content.splitlines()
        for i, line in enumerate(lines):
            if re.search(r"\bmvn\b", line):
                results.warning(
                    f"Maven command literal on line {i+1}: '{line.strip()[:60]}'",
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
    stage_re = re.compile(
        r"^#{1,6}\s+(?:Stage\s+\d+|步骤\s*\d+|第[一二三四五六七八九十]+步|T\d+\s*[:：])",
        re.MULTILINE,
    )
    stages = stage_re.findall(content)
    if len(stages) < 3:
        results.error(f"Only {len(stages)} workflow stages found (minimum 3)", file=str(wf_path))

    # Goal/Steps/Output section markers are an optional convention, not an
    # RFC-0002 requirement; workflows may structure stages differently.
    # Only the "at least 3 stages" check is enforced.


CJK_RE = re.compile(r"[\u4e00-\u9fff]")


def check_language(root, results):
    """Enforce governance/LANGUAGE_CONVENTION.md (方案 A / Batch L1).

    Three rules, all WARN-level (heuristic, human-reviewable):

    1. cli/commands/aic-*.md — Flow-control content (Steps / Guardrails)
       must be English; CJK-only sentences in these sections are flagged.
    2. cli/**/*.py and tools/*.py — code comments must be Chinese per
       documentation.md (LANGUAGE_CONVENTION: code comments → Chinese);
       non-ASCII-free English comment lines are flagged.
    3. governance/*.md (excluding archive/, README.md) — AI-internal
       governance layer must be English per LANGUAGE_CONVENTION;
       documents that are user-facing reports or reference bilingual
       identifiers (proposal-policy, DIRECTORY-RESPONSIBILITY) may carry
       CJK and are exempted below.

    Keep thresholds tolerant to avoid false positives on identifiers.
    """
    root = resolve_root(root)

    # Rule 1: command docs — Steps/Guardrails should be English
    cmd_dir = root / "cli" / "commands"
    if cmd_dir.exists():
        for p in sorted(cmd_dir.glob("aic-*.md")):
            text = read_file(p)
            # Only inspect Steps.. (up to next ## or end) blocks
            for section_name in ("Steps", "Guardrails"):
                m = re.search(rf"^\*\*{section_name}\*\*.*$", text, re.MULTILINE)
                if not m:
                    continue
                # collect the following list items until a blank + ** or EOF
                seg = text[m.end():]
                seg = re.split(r"\n\s*\*\*[A-Z]", seg)[0]
                lines = [ln for ln in seg.splitlines() if ln.strip()]
                cjk_lines = [ln for ln in lines if CJK_RE.search(ln) and len(ln.strip()) > 2]
                if len(cjk_lines) >= 2:
                    results.warning(
                        f"{p.name} {section_name} contains Chinese (LANGUAGE_CONVENTION: "
                        f"flow control must be English; {len(cjk_lines)} lines)",
                        file=str(p),
                    )

    # Rule 2: python comments must be Chinese (documentation.md)
    for base in (root / "cli", root / "tools"):
        if not base.exists():
            continue
        for p in sorted(base.rglob("*.py")):
            if any(x in p.parts for x in EXCLUDED_DIRS):
                continue
            try:
                text = p.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            # 三引号状态机：跳过字符串字面量内部的行（如模板字符串中的
            # `## Purpose`），避免把模板内容误判为注释。
            in_triple = None
            for i, ln in enumerate(text.splitlines(), start=1):
                s = ln.strip()
                # 更新三引号状态
                if in_triple:
                    if in_triple in ln:
                        in_triple = None
                    continue
                for q in ("\"\"\"", "'''"):
                    if q in ln:
                        in_triple = q
                        break
                if in_triple:
                    continue
                if not s.startswith("#"):
                    continue
                # Skip shebang, coding declarations, pure separators
                if s.startswith(("#!/", "# -*-", "# coding", "# ---", "# ==", "# ▸", "# ─")):
                    continue
                body = s.lstrip("#").strip()
                if not body:
                    continue
                # Comment is flagged when it is a real sentence WITHOUT any CJK
                # but longer than a bare label (avoid "# noqa", "# type:" etc.)
                if CJK_RE.search(body):
                    continue
                if re.match(r"^[a-z]+\)?:?\s*$", body):
                    continue  # bare label like "# deps"
                if len(body) < 4:
                    continue
                # Allow inline code-ish/tooling comments
                if re.match(r"^(noqa|type|pragma|region|endregion|TODO|FIXME|XXX)[: ]", body, re.IGNORECASE):
                    continue
                # Allow workflow-section keywords (Purpose/Runtime/Inputs/...)
                # — flow-control terminology is English by convention
                if re.match(
                    r"^(Purpose|Runtime|Preconditions|Inputs|Context|Outputs|"
                    r"Exit Criteria|Next|Trigger|Stopping Conditions|Steps|Guardrails|Workflow)\\b",
                    body,
                ):
                    continue
                results.warning(
                    f"English comment (LANGUAGE_CONVENTION: code comments → Chinese): "
                    f"{p.name}:{i}: {body[:60]}",
                    file=str(p),
                )

    # Rule 3: governance/*.md AND rfc/*.md (ADR/RFC) documents must be
    # English (AI-internal layer). ADR/RFC are Governance-layer records per
    # LANGUAGE_CONVENTION (English is less ambiguous); a Chinese ADR (e.g.
    # ADR-0008 initial draft) must be flagged.
    for target_dir in (root / "governance", root / "rfc"):
        if not target_dir.exists():
            continue
        # Files that legitimately carry CJK are exempt:
        #  - README / index (bilingual navigation)
        #  - policies that are user-facing (proposal-policy, skill-policy)
        #  - standards docs that define WHEN Chinese is used, which carry
        #    bilingual examples by design (documentation, chinese-documentation)
        exempt_names = {
            "README.md",
            "DIRECTORY-RESPONSIBILITY.md",
            "LANGUAGE_CONVENTION.md",
            "proposal-policy.md",
            "skill-policy.md",
        }
        # Sub-directories whose docs define Chinese usage by design
        exempt_subdirs = {"standards"}
        for p in sorted(target_dir.rglob("*.md")):
            if any(x in p.parts for x in EXCLUDED_DIRS):
                continue
            if "archive" in p.parts:
                continue
            if p.name in exempt_names:
                continue
            if any(x in p.parts for x in exempt_subdirs):
                continue
            try:
                text = p.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            # Strip fenced code blocks / tables so CJK inside examples is not
            # counted; flag only when prose sentences carry CJK.
            body = re.sub(r"```.*?```", "", text, flags=re.DOTALL)
            body = re.sub(r"\n\|[^\n]*\|\n", "", body)  # table rows
            cjk_lines = [
                ln for ln in body.splitlines()
                if CJK_RE.search(ln) and len(ln.strip()) > 2
            ]
            if len(cjk_lines) >= 3:
                results.warning(
                    f"{p.name} contains Chinese (LANGUAGE_CONVENTION: "
                    f"AI-internal layer must be English; {len(cjk_lines)} lines)",
                    file=str(p),
                )


def check_line_endings(root, results):
    """Enforce cross-platform line-ending policy (P23, L1 storage layer).

    WARN-level heuristic: text files tracked by git must not mix CRLF/LF.
    The repo canonical ending is LF (see .gitattributes); working trees
    may carry CRLF under Windows via text=auto, but a file that mixes both
    inside one working tree signals two-platform editing and will produce
    noisy diffs.

    Scope: tracked text files (git ls-files) with a text extension;
    skipped: .bat/.ps1 (canonical CRLF), binary-ish files.
    """
    root = resolve_root(root)
    binary_ext = {".png", ".jpg", ".jpeg", ".gif", ".ico", ".woff", ".woff2", ".ttf", ".pyc"}
    crlf_canonical = {".bat", ".ps1"}
    text_ext = {".md", ".py", ".yaml", ".yml", ".json", ".sh", ".js", ".ts", ".txt"}
    try:
        tracked = subprocess.run(
            ["git", "ls-files", "--cached", "--others", "--exclude-standard"],
            cwd=str(root), capture_output=True, text=True, check=True,
        ).stdout.splitlines()
    except Exception:
        return
    for rel in tracked:
        p = root / rel
        if not p.is_file() or p.suffix in binary_ext:
            continue
        if p.suffix not in text_ext and p.suffix not in crlf_canonical:
            continue
        try:
            data = p.read_bytes()
        except OSError:
            continue
        crlf_count = data.count(b"\r\n")
        # true LF-only lines: LF not preceded by CR
        lf_only = data.replace(b"\r\n", b"").count(b"\n")
        if crlf_count and lf_only:
            results.warning(
                f"mixed line endings (CRLF {crlf_count} / LF {lf_only}) — "
                f"same file edited on both Windows and WSL; normalize to LF (P23 L1)",
                file=str(p.relative_to(root)),
            )


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

    check_language(root, results)
    check_line_endings(root, results)

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
