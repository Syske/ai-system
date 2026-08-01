import re
import sys
from pathlib import Path

AIS = Path(__file__).resolve().parents[1]
WS = AIS.parent

KNOWN_PLACEHOLDER_DEBT = {
    # Reserved directory references in the memory index (targets not yet created)
    "governance/memory/integration/",
    "governance/memory/python/",
    # Historical reference inside a memory entry (describes pre-archive state)
    "governance/standards/common/code-quality.md",
}

FALSE_POSITIVES = {
    "../AuditTypeEnum.java",
    "../ai-runtime/",
    "metrics/baseline-",
    # Generated artifacts referenced by command/runtime docs (produced at run time)
    "../ai-system-pack",
    "config/environments/local.yaml",
    "ai-system/config/environments/context.yaml",
    # Deliberate counter-examples in governance/DIRECTORY-RESPONSIBILITY.md
    "ai-system/skills/foo/report.md",
    "config/governance/",
    "reports/foo-skill/",
}

# Runtime data roots: workspace-level directories that hold project/workspace
# content created at run time. References into these are not source-code
# dependencies, so the audit skips them (unless the target also exists inside
# the AI System repo).
RUNTIME_ROOTS = (
    "methodologies/",
    "workspaces/",
    "projects/",
    "repositories/",
)

PATH_RE = re.compile(
    r"(?:[A-Za-z]:[\\/][^\s`'\")\]，。；;|]+"
    r"|(?:\.\./)+[\w./\-]+"
    r"|(?:ai-system|governance|workflows|templates|skills|loaders|cli|config|tools|"
    r"metrics|reports|methodologies|workspaces|projects|repositories)"
    r"/[\w{}$./*\-]+)"
)


def is_runtime_reference(tok):
    """True if tok points into a runtime data root outside the repo.

    Runtime roots (methodologies/workspaces/projects/repositories) hold
    content created at run time under the workspace root. They are not
    source-code dependencies, so references into them are not audited.
    """

    return tok.startswith(RUNTIME_ROOTS)


def collect_files():

    scan = []

    for d in [
        AIS / "workflows",
        AIS / "templates" / "runtime",
        AIS / "templates" / "prompts",
        AIS / "loaders",
        AIS / "cli" / "commands",
        AIS / "config",
        AIS / "governance",
        AIS / "rfc",
    ]:
        scan += [
            p for p in d.rglob("*")
            if p.is_file() and p.suffix in (".md", ".yaml")
        ]

    scan += [
        AIS / "OPERATIONS.md",
        AIS / "skills" / "implement" / "planning.md",
        AIS / "skills" / "implement" / "SKILL.md",
        AIS / "skills" / "implement" / "workflow.md",
    ]

    return [
        p for p in scan
        if p.exists() and "archived" not in p.parts
    ]


def main():

    missing = {}
    absolute = {}
    checked = 0
    placeholders = 0

    files = collect_files()

    for f in files:

        text = f.read_text(encoding="utf-8", errors="replace")
        rel = str(f.relative_to(WS))

        for m in PATH_RE.finditer(text):

            tok = m.group(0).rstrip(".,;:)`'\"*")

            after = text[m.end():m.end() + 1]

            if "<" in after or after == "{":
                placeholders += 1
                continue

            if "{" in tok or "*" in tok or "$" in tok or "<" in tok:
                placeholders += 1
                continue

            if tok in FALSE_POSITIVES:
                continue

            if re.match(r"[A-Za-z]:", tok):

                if "://" in tok:
                    continue

                if "config/environments" not in rel.replace("\\", "/"):
                    absolute.setdefault(tok, set()).add(rel)

                continue

            if tok.startswith("../"):

                checked += 1

                if not (f.parent / tok).resolve().exists():
                    missing.setdefault(tok, set()).add(rel)

                continue

            checked += 1

            candidates = [AIS / tok, WS / tok]

            if tok.startswith("ai-system/"):
                candidates = [WS / tok]

            if not any(c.exists() for c in candidates):
                if is_runtime_reference(tok):
                    continue
                missing.setdefault(tok, set()).add(rel)

    debt = {t: s for t, s in missing.items() if t in KNOWN_PLACEHOLDER_DEBT}
    broken = {t: s for t, s in missing.items() if t not in KNOWN_PLACEHOLDER_DEBT}

    print(
        f"files={len(files)} refs_checked={checked} "
        f"placeholders={placeholders} known_debt={len(debt)}"
    )

    print()
    print(f"BROKEN ({len(broken)}):")

    for tok in sorted(broken):

        print(f"  {tok}")

        for src in sorted(broken[tok]):
            print(f"      <- {src}")

    print()
    print(f"ABSOLUTE OUTSIDE environments ({len(absolute)}):")

    for tok in sorted(absolute):

        print(f"  {tok}")

        for src in sorted(absolute[tok]):
            print(f"      <- {src}")

    if broken or absolute:
        sys.exit(1)

    print()
    print("OK: no broken path dependencies")


if __name__ == "__main__":
    main()
