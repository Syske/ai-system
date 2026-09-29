"""reports/ ownership gate (P74 S1, check.py item 17).

`reports/` holds AI System analysis and governance records. It does not hold
another product's deliverables.

Why this gate exists (2026-09-28, measured): a third-party product's 7-file
business `prepare` report entered `reports/` through a single `chore:` commit.
It was then fully registered in the index — and **no gate complained**, because
`proposal-policy` §6 only requires a report to be *listed*, never to *belong*
there. The artifact was an orphan: zero references anywhere in the repo, no
matching workspace project, one commit, never touched again.

Classification is therefore by **allow-list of category patterns**
(`proposal-policy` §6.1), not by exclusion. An exclusion rule cannot separate
`analysis-*` (a legitimate category, and also a workflow name) from
`prepare-<project>-*` (a workflow's business output) — the first token is a
workflow name in both cases. The allow-list is the only formulation that
distinguishes them, and an unmatched name is reported rather than guessed at.

Checks:

    S1  an entry matches no known category pattern   ERROR
    S2  a directory that looks like a workflow's business output
        (registered workflow name + project-ish suffix)  ERROR (specific hint)
    S3  a subdirectory that is neither `analysis-*` nor `skill-source-*`
        ERROR (multi-file reports have exactly two directory categories)

Every check ships with a negative test in cli/tests/test_reports_scope.py.
"""

import re

from .base import ROOT, load_yaml

_REPORTS = ROOT / "reports"
_REGISTRY = ROOT / "config" / "workflow-registry.yaml"

# Standing index files, exempt from the category pattern check.
EXEMPT_FILES = {"README.md", "PROPOSALS.md"}

# Category patterns (proposal-policy §6.1). Order matters only for the hint.
CATEGORY_PATTERNS = (
    ("proposals", re.compile(r"^P\d+-[A-Z0-9][A-Za-z0-9-]*\.md$")),
    ("maintenance", re.compile(
        r"^(?:MAINTENANCE|EXTENSIONS-MAINTENANCE|DAILY)"
        r"-\d{4}-?\d{2}-?\d{2}[A-Za-z0-9-]*\.md$")),
    # Case-insensitive: `architecture-review-*.md` and
    # `wayfinder-value-reevaluation-*.md` are the same category as
    # `ARCHITECTURE-ASSESSMENT-*.md`; a case-sensitive pattern rejected them.
    ("assessments", re.compile(
        r"^.*(ASSESSMENT|REVIEW|DIAGNOSIS|ANALYSIS|REEVALUATION|"
        r"OPTIMIZATION|REPORT|HANDOVER)"
        r"[-A-Za-z0-9]*\.md$", re.I)),
    ("incidents", re.compile(r"^INCIDENT-\d{4}-\d{2}-\d{2}[A-Za-z0-9-]*\.md$")),
    ("migrations", re.compile(r"^MIGRATION-[A-Za-z0-9-]+\.md$")),
    ("decisions", re.compile(r"^VALUE-BURDEN-DECISION-[A-Za-z0-9.-]+\.md$")),
    ("standards", re.compile(r"^EXTENSION-?STANDARDS[A-Za-z0-9-]*\.md$")),
    # Proposals that predate / sit outside the P-series numbering.
    ("proposals", re.compile(r"^[A-Z0-9-]*-PROPOSAL\.md$")),
    ("analysis", re.compile(r"^analysis-\d{4}-\d{2}-\d{2}-[A-Za-z0-9-]+$")),
    ("skill-sources", re.compile(r"^skill-source-\d{4}-\d{2}-\d{2}-[A-Za-z0-9-]+$")),
)

# Multi-file report directories: exactly these two categories.
DIRECTORY_CATEGORIES = ("analysis", "skill-sources")


def _workflow_names(root):
    data = load_yaml(_REGISTRY)
    if "__error__" in data or not isinstance(data.get("workflows"), dict):
        return set()
    return set(data["workflows"])


def _category(name):
    """Return the category for an entry name, or None."""
    for cat, pat in CATEGORY_PATTERNS:
        if pat.match(name):
            return cat
    return None


def _looks_like_workflow_output(name, workflows):
    """`<workflow>-<something>-<descriptor>/` — a workflow's business product.

    A leading registered workflow name alone is NOT the signal: `analysis-*` is
    both a category and a workflow name. The signal is a workflow name followed
    by a project-ish suffix, which is how per-project run products are named
    (`prepare-beecount-2608`).

    The leading token is matched **non-greedily** (shortest prefix that is a
    registered workflow name). A greedy `[a-z0-9-]+` would swallow the project
    name into the token — `prepare-beecount-2608` yields `prepare-beecount`,
    which is not a workflow, and the check silently misses.
    """
    stem = name.rstrip("/")
    if not workflows:
        return None
    for wf in sorted(workflows, key=len, reverse=True):
        if not stem.startswith(wf + "-"):
            continue
        rest = stem[len(wf) + 1:]
        if rest and "-" in rest:
            return wf, rest
    return None


def check_reports_scope(c, root=None):
    """Verify every entry under reports/ belongs to a declared category."""
    r = ROOT if root is None else root
    reports = r / "reports"

    if not reports.exists():
        return

    workflows = _workflow_names(r)

    for p in sorted(reports.iterdir()):

        name = p.name

        if p.is_file() and name in EXEMPT_FILES:
            continue

        if _category(name):
            continue

        # --- S2: a workflow's business output landed here ---
        hit = _looks_like_workflow_output(name, workflows)
        if hit and p.is_dir():
            wf, rest = hit
            c.error(
                f"reports/{name}: looks like the business output of the "
                f"'{wf}' workflow, not an AI System report — such artifacts "
                f"belong in outputs/{wf}/<yyMMdd>-<descriptor>/ (or "
                f"workspaces/<project-id>/ per the workflow's Outputs). "
                f"See governance/policies/proposal-policy.md §6.1"
            )
            continue

        if p.is_dir():
            # --- S3: a directory outside the two directory categories ---
            c.error(
                f"reports/{name}: directory does not match any category "
                f"pattern. Multi-file reports use analysis-<date>-<topic>/ or "
                f"skill-source-<date>-<skill>/; a single-file report belongs "
                f"directly under reports/ "
                f"(see governance/policies/proposal-policy.md §6.1)"
            )
            continue

        # --- S1: unmatched single file ---
        c.error(
            f"reports/{name}: does not match any report category. Expected "
            f"one of: P<n>-<TOPIC>.md / MAINTENANCE-<date>.md / "
            f"*ASSESSMENT*|*REVIEW*|*DIAGNOSIS*|*ANALYSIS*.md / "
            f"INCIDENT-<date>-*.md / MIGRATION-*.md — or move it to "
            f"outputs/<workflow>/ if it is a business artifact "
            f"(see governance/policies/proposal-policy.md §6.1)"
        )
