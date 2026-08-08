"""ADR integrity checks: numbering, status, RFC reference, README registry."""

import re
from pathlib import Path

from .base import ROOT

_RFC_DIR = ROOT / "rfc"
_ADR_RE = re.compile(r"^ADR-(\d{4})-(.+)\.md$")
_STATUSES = {"Accepted", "Proposed", "Deprecated", "Rejected", "Superseded"}


def _parse_readme_table():
    """Parse the ADR table in rfc/README.md into {number: title}."""
    readme = _RFC_DIR / "README.md"
    if not readme.exists():
        return {}
    text = readme.read_text(encoding="utf-8")
    table = {}
    for line in text.splitlines():
        m = re.match(r"\|\s*ADR-(\d{4})\s*\|\s*([^|]+?)\s*\|\s*([A-Za-z]+)\s*\|", line)
        if m:
            table[int(m.group(1))] = (m.group(2).strip(), m.group(3))
    return table


def check_adr(c):
    """Validate ADR files: numbering, status, RFC reference, README registry."""

    if not _RFC_DIR.exists():
        return

    adr_files = sorted(_RFC_DIR.glob("ADR-*.md"))
    if not adr_files:
        return

    numbers = []
    for p in adr_files:
        m = _ADR_RE.match(p.name)
        if not m:
            c.error(f"ADR file name must match ADR-XXXX-slug.md: {p.name}")
            continue
        num = int(m.group(1))
        numbers.append(num)

        text = p.read_text(encoding="utf-8", errors="replace")

        # Status: accept 'Status: X' header OR '| Status | X |' table row
        status_m = re.search(r"^Status:\s*([A-Za-z]+)", text, re.MULTILINE)
        if not status_m:
            status_m = re.search(r"^\|\s*Status\s*\|\s*\*{0,2}([A-Za-z]+)", text, re.MULTILINE)
        if not status_m:
            c.error(f"{p.name}: missing status (either 'Status:' header or table row)")
        elif status_m.group(1) not in _STATUSES:
            c.error(f"{p.name}: invalid status '{status_m.group(1)}'")

        # Date: accept 'Date:' header OR '| Decided | YYYY-MM-DD |' table row
        date_ok = re.search(r"^Date:", text, re.MULTILINE) or re.search(
            r"^\|\s*(?:Decided|Date)\s*\|\s*\*{0,2}\d{4}-\d{2}-\d{2}", text, re.MULTILINE
        )
        if not date_ok:
            c.error(f"{p.name}: missing date (either 'Date:' header or 'Decided' row)")

        # Required sections
        for section in ("Context", "Decision", "Rationale", "Consequences"):
            if not re.search(rf"^## {section}", text, re.MULTILINE):
                c.warn(f"{p.name}: missing '## {section}' section")

        # References an RFC — optional: ADRs may be standalone architecture
        # decisions (e.g. ADR-0005 Runtime, ADR-0006 Workflow-First) that
        # implement no specific RFC; absence is legitimate and not flagged.

    # Numbering continuity: 1..N with no gaps
    if numbers:
        expected = list(range(1, max(numbers) + 1))
        missing = [n for n in expected if n not in numbers]
        if missing:
            c.warn(f"ADR numbering gap: missing {missing}")

    # README registry: every ADR must be registered
    table = _parse_readme_table()
    for num in numbers:
        if num not in table:
            c.error(f"ADR-{num:04d} not registered in rfc/README.md table")
