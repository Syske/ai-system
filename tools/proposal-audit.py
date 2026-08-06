r"""Audit proposals / open action items + enforce proposal-policy gates.

Scans ai-system/reports/ for:

1. Proposal files (P*.md): validates `Status`, consistency with Review Log /
   Implementation Record, and index (PROPOSALS.md) sync per
   governance/policies/proposal-policy.md.
2. Open action items: `- [ ]` checkboxes in MAINTENANCE-* / P* files (live
   leftover sources), excluding historical analysis/migration checklist
   templates.

Gate failures (ERROR) break check.py; leftover proposals / open items are
WARN for the maintenance report.

Usage:
    python tools/proposal-audit.py               # audit (exit 1 on leftover/gate fail)
    python tools/proposal-audit.py --json        # JSON output
    python tools/proposal-audit.py --refresh-index  # rewrite PROPOSALS.md index
"""

import argparse
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent

VALID_STATUSES = {
    "proposed",
    "approved",
    "rejected",
    "implemented",
    "archived",
}

CLOSED_STATUSES = {
    "approved",
    "implemented",
    "rejected",
    "archived",
}

STATUS_LINE = re.compile(
    r"^\|\s*Status\s*\|\s*\*\*(.+?)\*\*",
    re.MULTILINE
)

CREATED_LINE = re.compile(
    r"^\|\s*Created\s*\|\s*([^|]+)",
    re.MULTILINE
)

TITLE_LINE = re.compile(
    r"^# Change Proposal:\s*(?:P\d+|S\d+)\s*[—-]\s*(.+)$",
    re.MULTILINE
)

REVIEW_LOG = re.compile(
    r"^\| User.*?\|\s*\*\*(.+?)\*\*",
    re.MULTILINE
)

IMPL_RECORD = re.compile(r"^## Implementation Record", re.MULTILINE)

OPEN_TODO = re.compile(r"^\s*-\s*\[\s*\]", re.MULTILINE)


def _status(text):

    m = STATUS_LINE.search(text)

    return m.group(1).strip() if m else None


def audit():
    """Return audit dict: proposals (with gate findings) + open_items."""

    reports = ROOT / "reports"

    proposals = []
    errors = []
    warnings = []

    for p in sorted(reports.glob("P*.md")):

        if p.name == "PROPOSALS.md":
            continue

        text = p.read_text(encoding="utf-8", errors="ignore")

        status = _status(text)

        if status is None:

            errors.append(f"{p.name}: missing Status field")

            continue

        if status.lower() not in VALID_STATUSES:

            errors.append(
                f"{p.name}: invalid Status '{status}'"
            )

        review = REVIEW_LOG.search(text)

        has_review_approved = bool(
            review
            and "approved" in review.group(1).lower()
        )

        has_impl = bool(IMPL_RECORD.search(text))

        if (
            status.lower() == "approved"
            and not has_review_approved
        ):
            warnings.append(
                f"{p.name}: Status Approved but Review Log has no Approved"
            )

        if (
            status.lower() == "implemented"
            and not has_impl
        ):
            errors.append(
                f"{p.name}: Status Implemented but no Implementation Record"
            )

        proposals.append({
            "file": p.name,
            "status": status,
        })

    open_items = []

    for p in sorted(reports.glob("*.md")):

        if not (
            p.name.startswith("MAINTENANCE-")
            or p.name.startswith("P")
        ):
            continue

        text = p.read_text(encoding="utf-8", errors="ignore")

        for m in OPEN_TODO.finditer(text):

            line = text[m.start():].splitlines()[0].strip()

            open_items.append({
                "file": p.name,
                "line": text[:m.start()].count("\n") + 1,
                "item": re.sub(r"^\s*-\s*\[\s*\]\s*", "", line),
            })

    return {
        "proposals": proposals,
        "open_items": open_items,
        "errors": errors,
        "warnings": warnings,
    }


def refresh_index():
    """Rewrite reports/PROPOSALS.md index table from P*.md Status fields."""

    reports = ROOT / "reports"

    rows = []

    for p in sorted(reports.glob("P*.md")):

        if p.name == "PROPOSALS.md":
            continue

        text = p.read_text(encoding="utf-8", errors="ignore")

        status = _status(text) or "Proposed"

        created = ""
        cm = CREATED_LINE.search(text)
        if cm:
            created = cm.group(1).strip()

        title = ""
        tm = TITLE_LINE.search(text)
        if tm:
            title = tm.group(1).strip()

        rows.append((status, title, created, p.name))

    header = (
        "| 状态 | 提案 | 创建 | 文件 |\n"
        "|---|---|---|---|\n"
    )

    body = "".join(
        f"| {status} | {title} | {created} | `{name}` |\n"
        for status, title, created, name in rows
    )

    index = reports / "PROPOSALS.md"

    if index.exists():

        text = index.read_text(encoding="utf-8")

        marker = re.compile(
            r"## 提案清单\n.*?\n(?=\n## 当前遗留|\Z)",
            re.DOTALL
        )

        if marker.search(text):

            text = marker.sub(
                "## 提案清单\n\n" + header + body,
                text,
                count=1
            )

        else:

            text = text.rstrip() + "\n\n## 提案清单\n\n" + header + body + "\n"

    else:

        text = (
            "# Proposals Index\n\n"
            "## 提案清单\n\n" + header + body + "\n"
        )

    index.write_text(text, encoding="utf-8")

    print(f"index refreshed: {index} ({len(rows)} proposals)")

    return rows


def main():

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--json",
        action="store_true"
    )

    parser.add_argument(
        "--refresh-index",
        action="store_true"
    )

    args = parser.parse_args()

    if args.refresh_index:

        refresh_index()

        return 0

    result = audit()

    if args.json:

        print(json.dumps(result, ensure_ascii=False, indent=2))

        return 0

    proposals = result["proposals"]
    open_items = result["open_items"]
    errors = result["errors"]
    warnings = result["warnings"]

    print(f"reports/ scanned: {len(list((ROOT / 'reports').glob('*.md')))} files")
    print()

    print(f"GATE ERRORS ({len(errors)}):")

    for e in errors:
        print(f"  ERROR {e}")

    if not errors:
        print("  (none)")

    print()

    print(f"GATE WARNINGS ({len(warnings)}):")

    for w in warnings:
        print(f"  WARN {w}")

    if not warnings:
        print("  (none)")

    print()

    print(f"PROPOSALS NOT CLOSED ({sum(1 for p in proposals if p['status'].lower() not in CLOSED_STATUSES)}):")

    for p in proposals:

        if p["status"].lower() not in CLOSED_STATUSES:
            print(f"  {p['file']}: status={p['status']}")

    print()

    print(f"OPEN ACTION ITEMS ({len(open_items)}):")

    for o in open_items[:15]:
        print(f"  {o['file']}:{o['line']}  {o['item']}")

    if len(open_items) > 15:
        print(f"  ... +{len(open_items) - 15} more")

    print()

    leftover = any(
        p["status"].lower() not in CLOSED_STATUSES
        for p in proposals
    )

    if errors:

        print(f"FAIL: {len(errors)} gate error(s).")

        return 1

    if leftover or open_items:

        print("Leftover proposals / open items found — evaluate before finishing.")

        return 1

    print("OK: no gate errors; no leftover proposals or open action items.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
