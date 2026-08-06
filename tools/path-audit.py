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
    "../ai-runtime/",
    "metrics/baseline-",
    # Generated artifacts referenced by command/runtime docs (produced at run time)
    "../ai-system-pack",
    "config/environments/local.yaml",
    "ai-system/config/environments/context.yaml",
    # metrics/ is gitignored (runtime snapshots); absent in CI checkouts
    "ai-system/metrics",
    # Deliberate counter-examples in governance/DIRECTORY-RESPONSIBILITY.md
    "ai-system/skills/foo/report.md",
    "config/governance/",
    "reports/foo-skill/",
}

# Example-only references (T2/Batch 2): paths that appear inside doc examples,
# templates, or placeholder snippets — they are illustrative, not real
# dependencies. Kept separate from FALSE_POSITIVES so the distinction stays
# visible.
EXAMPLE_ONLY = {
    # governance/standards/common/cross-project-sync.md: illustrative **/ wildcard
    "../AuditTypeEnum.java",
    # skills/skill-sync/SKILL.md: "upload a skill you built" example target
    "../skill-generator",
    # skills/open-cli/SKILL.md: correct-example paths under ~/.opencli/clis
    "cli/clis/aem/page-views.ts",
    "cli/clis/bilibili/favorites.ts",
    "cli/clis/twitter/lists.yaml",
    # skills/bugfix/feedback-loop.md: "cut inputs/callers/config/data" prose
    "config/data",
    # skills/iterative-optimizer/examples/*: template placeholder
    "skills/my-skill",
    # skills/skill-optimizer/workflow.md: /Users/xxx sample command
    "skills/offline-disk-fault-diagnosis",
    # skills/iterative-optimizer/workflow.md: user-prompt example skill
    "skills/openeuler-docker-fault",
    # skills/index-project/SKILL.md: $HOME/.claude tool path (runtime env)
    "tools/code-indexer/reindex_cli.py",
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
    ]

    # All skill files (T1/Batch 2: previously only skills/implement was
    # scanned, which left repository-governor etc. as an audit blind spot).
    scan += [
        p for p in (AIS / "skills").rglob("*")
        if p.is_file()
        and p.suffix in (".md", ".yaml", ".yml")
        and "archived" not in p.parts
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

            raw_tok = m.group(0)
            tok = raw_tok.rstrip(".,;:)`'\"*")

            after = text[m.end():m.end() + 1]

            if "<" in after or after == "{":
                placeholders += 1
                continue

            # A trailing '*' stripped by rstrip is still a wildcard placeholder
            # (e.g. `rfc\RFC-*`). Check the RAW token before stripping.
            if (
                "{" in tok or "*" in raw_tok or "$" in tok or "<" in tok
            ):
                placeholders += 1
                continue

            if tok in FALSE_POSITIVES:
                continue

            if tok in EXAMPLE_ONLY:
                continue

            if re.match(r"[A-Za-z]:", tok):

                if "://" in tok:
                    continue

                # Self-referential absolute paths: docs describing the ai-system
                # repo's OWN structure (e.g. "count RFCs under
                # D:\\workspace\\ai-workspace\\ai-system\\rfc"). These point at
                # the repo root itself, so they are not "outside environments" —
                # skip by PREFIX match. Do not require target.exists(): the
                # path is a Windows-style absolute path that will never exist
                # on a Linux CI checkout, but the prefix alone proves it
                # references the repo's own tree (not an external env).
                ais_norm = str(AIS).replace("\\", "/").rstrip("/")
                tok_norm = tok.replace("\\", "/").rstrip("/")
                if tok_norm == ais_norm or tok_norm.startswith(ais_norm + "/"):
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
